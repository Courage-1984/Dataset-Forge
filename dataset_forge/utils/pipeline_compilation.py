"""
Pipeline compilation utilities for Dataset Forge.

This module provides compilation capabilities for performance-critical code paths
using Numba, Cython, and PyTorch JIT compilation.
"""

import os
import time
import logging
import functools
from typing import Callable, Any, Optional, Dict, List, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import inspect
import tempfile
import subprocess
import sys

# Optional imports for compilation
try:
    import numba
    from numba import jit, cuda, prange
    from numba.core.errors import NumbaWarning
    import warnings

    warnings.filterwarnings("ignore", category=NumbaWarning)
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

try:
    from setuptools import Extension

    CYTHON_AVAILABLE = True
except ImportError:
    CYTHON_AVAILABLE = False

from dataset_forge.utils.memory_utils import (
    clear_cuda_cache,
    to_device_safe,
    tensor_context,
)
from dataset_forge.utils.cache_utils import smart_cache
from dataset_forge.utils.printing import (
    print_info,
    print_warning,
    print_error,
    print_success,
)
from dataset_forge.utils.monitoring import monitor_all

# Lazy imports for heavy libraries
from dataset_forge.utils.lazy_imports import (
    torch,
    numpy_as_np as np,
    cython,
)


class CompilationType(Enum):
    """Types of compilation available."""

    NUMBA = "numba"
    CYTHON = "cython"
    TORCH_JIT = "torch_jit"
    AUTO = "auto"


@dataclass
class CompilationConfig:
    """Configuration for pipeline compilation."""

    compilation_type: CompilationType = CompilationType.AUTO
    enable_numba: bool = True
    enable_cython: bool = True
    enable_torch_jit: bool = True
    parallel: bool = True
    fastmath: bool = True
    cache: bool = True
    debug: bool = False
    optimization_level: int = 3
    target_backend: str = "cpu"  # "cpu", "cuda", "parallel"
    compile_timeout: float = 300.0  # 5 minutes


class NumbaCompiler:
    """
    Numba-based compilation for numerical operations.

    Provides JIT compilation for CPU and GPU operations using Numba.
    """

    def __init__(self, config: Optional[CompilationConfig] = None):
        """
        Initialize Numba compiler.

        Args:
            config: Compilation configuration
        """
        self.config = config or CompilationConfig()
        self.logger = logging.getLogger(__name__)

        if not NUMBA_AVAILABLE:
            raise RuntimeError("Numba not available for compilation")

    def compile_function(
        self,
        func: Callable,
        signature: Optional[str] = None,
        target: str = "cpu",
        **kwargs,
    ) -> Callable:
        """
        Compile a function using Numba.

        Args:
            func: Function to compile
            signature: Numba signature string
            target: Target backend ("cpu", "cuda", "parallel")
            **kwargs: Additional compilation options

        Returns:
            Compiled function
        """
        try:
            if target == "cpu":
                compiled_func = jit(
                    signature,
                    nopython=True,
                    cache=self.config.cache,
                    fastmath=self.config.fastmath,
                    **kwargs,
                )(func)
            elif target == "cuda":
                if not cuda.is_available():
                    raise RuntimeError("CUDA not available for Numba compilation")
                compiled_func = cuda.jit(
                    signature,
                    cache=self.config.cache,
                    fastmath=self.config.fastmath,
                    **kwargs,
                )(func)
            elif target == "parallel":
                compiled_func = jit(
                    signature,
                    nopython=True,
                    parallel=self.config.parallel,
                    cache=self.config.cache,
                    fastmath=self.config.fastmath,
                    **kwargs,
                )(func)
            else:
                raise ValueError(f"Unknown target: {target}")

            self.logger.info(
                f"Successfully compiled {func.__name__} with Numba ({target})"
            )
            return compiled_func

        except Exception as e:
            self.logger.error(f"Failed to compile {func.__name__} with Numba: {e}")
            return func  # Fall back to original function

    def compile_image_processing(self, func: Callable) -> Callable:
        """
        Compile image processing function with optimized signature.

        Args:
            func: Image processing function

        Returns:
            Compiled function
        """
        # Common signature for image processing functions
        signature = "float64[:,:,:](float64[:,:,:], float64, float64)"

        return self.compile_function(
            func, signature=signature, target="parallel", fastmath=True
        )


class CythonCompiler:
    """
    Cython-based compilation for complex operations.

    Provides Cython compilation for Python functions that can benefit
    from static typing and C-level performance.
    """

    def __init__(self, config: Optional[CompilationConfig] = None):
        """
        Initialize Cython compiler.

        Args:
            config: Compilation configuration
        """
        self.config = config or CompilationConfig()
        self.logger = logging.getLogger(__name__)

        if not CYTHON_AVAILABLE:
            raise RuntimeError("Cython not available for compilation")

    def compile_function(
        self, func: Callable, module_name: str = "compiled_module", **kwargs
    ) -> Callable:
        """
        Compile a function using Cython.

        Args:
            func: Function to compile
            module_name: Name for the compiled module
            **kwargs: Additional compilation options

        Returns:
            Compiled function
        """
        try:
            # Create temporary directory for compilation
            with tempfile.TemporaryDirectory() as temp_dir:
                # Generate Cython code
                cython_code = self._generate_cython_code(func, module_name)

                # Write Cython file
                cython_file = os.path.join(temp_dir, f"{module_name}.pyx")
                with open(cython_file, "w") as f:
                    f.write(cython_code)

                # Create setup.py for compilation
                setup_code = self._generate_setup_code(module_name, temp_dir)
                setup_file = os.path.join(temp_dir, "setup.py")
                with open(setup_file, "w") as f:
                    f.write(setup_code)

                # Compile
                result = subprocess.run(
                    [sys.executable, "setup.py", "build_ext", "--inplace"],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=self.config.compile_timeout,
                )

                if result.returncode != 0:
                    raise RuntimeError(f"Cython compilation failed: {result.stderr}")

                # Import compiled module
                import importlib.util

                spec = importlib.util.spec_from_file_location(
                    module_name, os.path.join(temp_dir, f"{module_name}.cpython-*.so")
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                compiled_func = getattr(module, func.__name__)

                self.logger.info(f"Successfully compiled {func.__name__} with Cython")
                return compiled_func

        except Exception as e:
            self.logger.error(f"Failed to compile {func.__name__} with Cython: {e}")
            return func  # Fall back to original function

    def _generate_cython_code(self, func: Callable, module_name: str) -> str:
        """Generate Cython code for a function."""
        # Get function source
        source = inspect.getsource(func)

        # Add Cython imports and type hints
        cython_code = f"""
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

import numpy as np
cimport numpy as np
from libc.math cimport sqrt, exp, log, sin, cos, tan
from libc.stdlib cimport malloc, free

np.import_array()

{source}
"""
        return cython_code

    def _generate_setup_code(self, module_name: str, temp_dir: str) -> str:
        """Generate setup.py code for Cython compilation."""
        return f"""
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

extensions = [
    Extension(
        "{module_name}",
        ["{module_name}.pyx"],
        include_dirs=[np.get_include()],
        extra_compile_args=["-O3", "-march=native", "-ffast-math"],
        extra_link_args=["-O3"],
    )
]

setup(
    ext_modules=cythonize(extensions, compiler_directives={{'language_level': 3}}),
    zip_safe=False,
)
"""


class TorchJITCompiler:
    """
    PyTorch JIT compilation for tensor operations.

    Provides TorchScript compilation for PyTorch-based functions.
    """

    def __init__(self, config: Optional[CompilationConfig] = None):
        """
        Initialize Torch JIT compiler.

        Args:
            config: Compilation configuration
        """
        self.config = config or CompilationConfig()
        self.logger = logging.getLogger(__name__)

    def compile_function(
        self, func: Callable, example_inputs: Optional[List[Any]] = None, **kwargs
    ) -> Callable:
        """
        Compile a function using TorchScript.

        Args:
            func: Function to compile
            example_inputs: Example inputs for tracing
            **kwargs: Additional compilation options

        Returns:
            Compiled function
        """
        try:
            # Create TorchScript module
            if example_inputs:
                # Use tracing
                traced_func = torch.jit.trace(func, example_inputs[0])
            else:
                # Use scripting (requires TorchScript-compatible code)
                traced_func = torch.jit.script(func)

            # Optimize
            if self.config.optimization_level > 0:
                traced_func = torch.jit.optimize_for_inference(traced_func)

            self.logger.info(f"Successfully compiled {func.__name__} with TorchScript")
            return traced_func

        except Exception as e:
            self.logger.error(
                f"Failed to compile {func.__name__} with TorchScript: {e}"
            )
            return func  # Fall back to original function

    def compile_model(
        self, model: torch.nn.Module, example_input: torch.Tensor
    ) -> torch.nn.Module:
        """
        Compile a PyTorch model using TorchScript.

        Args:
            model: PyTorch model to compile
            example_input: Example input tensor

        Returns:
            Compiled model
        """
        try:
            # Trace the model
            traced_model = torch.jit.trace(model, example_input)

            # Optimize
            if self.config.optimization_level > 0:
                traced_model = torch.jit.optimize_for_inference(traced_model)

            self.logger.info(
                f"Successfully compiled model {model.__class__.__name__} with TorchScript"
            )
            return traced_model

        except Exception as e:
            self.logger.error(
                f"Failed to compile model {model.__class__.__name__} with TorchScript: {e}"
            )
            return model  # Fall back to original model


class PipelineCompiler:
    """
    Main pipeline compilation system.

    Provides unified interface for compiling performance-critical code paths
    using multiple compilation backends.
    """

    def __init__(self, config: Optional[CompilationConfig] = None):
        """
        Initialize pipeline compiler.

        Args:
            config: Compilation configuration
        """
        self.config = config or CompilationConfig()
        self.logger = logging.getLogger(__name__)

        # Initialize compilers
        self.numba_compiler = None
        self.cython_compiler = None
        self.torch_compiler = None

        if self.config.enable_numba and NUMBA_AVAILABLE:
            self.numba_compiler = NumbaCompiler(config)

        if self.config.enable_cython and CYTHON_AVAILABLE:
            self.cython_compiler = CythonCompiler(config)

        if self.config.enable_torch_jit:
            self.torch_compiler = TorchJITCompiler(config)

    def compile(
        self,
        func: Callable,
        compilation_type: Optional[CompilationType] = None,
        **kwargs,
    ) -> Callable:
        """
        Compile a function using the specified compilation type.

        Args:
            func: Function to compile
            compilation_type: Type of compilation to use
            **kwargs: Additional compilation options

        Returns:
            Compiled function
        """
        if compilation_type is None:
            compilation_type = self.config.compilation_type

        if compilation_type == CompilationType.AUTO:
            compilation_type = self._auto_detect_compilation_type(func)

        try:
            if compilation_type == CompilationType.NUMBA and self.numba_compiler:
                return self.numba_compiler.compile_function(func, **kwargs)

            elif compilation_type == CompilationType.CYTHON and self.cython_compiler:
                return self.cython_compiler.compile_function(func, **kwargs)

            elif compilation_type == CompilationType.TORCH_JIT and self.torch_compiler:
                return self.torch_compiler.compile_function(func, **kwargs)

            else:
                self.logger.warning(
                    f"Compilation type {compilation_type} not available, using original function"
                )
                return func

        except Exception as e:
            self.logger.error(f"Compilation failed for {func.__name__}: {e}")
            return func

    def _auto_detect_compilation_type(self, func: Callable) -> CompilationType:
        """Auto-detect the best compilation type for a function."""
        func_name = func.__name__.lower()
        source = inspect.getsource(func)

        # Check for PyTorch operations
        if any(keyword in source for keyword in ["torch.", "nn.", "F."]):
            return CompilationType.TORCH_JIT

        # Check for numerical operations
        if any(
            keyword in func_name
            for keyword in ["process", "compute", "calculate", "transform"]
        ):
            return CompilationType.NUMBA

        # Check for complex operations
        if len(source) > 100 or "class" in source:
            return CompilationType.CYTHON

        # Default to Numba for numerical operations
        return CompilationType.NUMBA

    @monitor_all("compile_pipeline")
    def compile_pipeline(
        self,
        pipeline_functions: List[Callable],
        compilation_configs: Optional[List[CompilationType]] = None,
    ) -> List[Callable]:
        """
        Compile a pipeline of functions.

        Args:
            pipeline_functions: List of functions to compile
            compilation_configs: List of compilation types for each function

        Returns:
            List of compiled functions
        """
        if compilation_configs is None:
            compilation_configs = [CompilationType.AUTO] * len(pipeline_functions)

        compiled_functions = []

        print_info(f"Compiling pipeline with {len(pipeline_functions)} functions")

        for i, (func, comp_type) in enumerate(
            zip(pipeline_functions, compilation_configs)
        ):
            print_info(
                f"Compiling function {i+1}/{len(pipeline_functions)}: {func.__name__}"
            )

            compiled_func = self.compile(func, comp_type)
            compiled_functions.append(compiled_func)

        print_success(
            f"Pipeline compilation complete: {len(compiled_functions)} functions compiled"
        )
        return compiled_functions

    def get_compilation_status(self) -> Dict[str, Any]:
        """Get status of compilation backends."""
        return {
            "numba_available": NUMBA_AVAILABLE and self.numba_compiler is not None,
            "cython_available": CYTHON_AVAILABLE and self.cython_compiler is not None,
            "torch_jit_available": self.torch_compiler is not None,
            "config": {
                "enable_numba": self.config.enable_numba,
                "enable_cython": self.config.enable_cython,
                "enable_torch_jit": self.config.enable_torch_jit,
                "parallel": self.config.parallel,
                "fastmath": self.config.fastmath,
                "cache": self.config.cache,
            },
        }


# Global instance
pipeline_compiler = PipelineCompiler()


# Convenience functions
def compile_function(
    func: Callable, compilation_type: CompilationType = CompilationType.AUTO, **kwargs
) -> Callable:
    """Convenience function for function compilation."""
    return pipeline_compiler.compile(func, compilation_type, **kwargs)


def compile_pipeline(
    pipeline_functions: List[Callable],
    compilation_configs: Optional[List[CompilationType]] = None,
) -> List[Callable]:
    """Convenience function for pipeline compilation."""
    return pipeline_compiler.compile_pipeline(pipeline_functions, compilation_configs)


# Pre-compiled utility functions
@jit(nopython=True, cache=True, fastmath=True)
def fast_image_normalize(image: np.ndarray) -> np.ndarray:
    """Fast image normalization using Numba."""
    return (image - image.min()) / (image.max() - image.min() + 1e-8)


@jit(nopython=True, cache=True, fastmath=True)
def fast_gaussian_blur(image: np.ndarray, sigma: float) -> np.ndarray:
    """Fast Gaussian blur using Numba."""
    # Simplified Gaussian blur implementation
    h, w = image.shape[:2]
    result = np.zeros_like(image)

    for i in range(h):
        for j in range(w):
            # Simple 3x3 kernel approximation
            total = 0.0
            count = 0

            for di in range(-1, 2):
                for dj in range(-1, 2):
                    ni, nj = i + di, j + dj
                    if 0 <= ni < h and 0 <= nj < w:
                        weight = exp(-(di * di + dj * dj) / (2 * sigma * sigma))
                        total += image[ni, nj] * weight
                        count += weight

            if count > 0:
                result[i, j] = total / count

    return result


# Decorator for automatic compilation
def auto_compile(compilation_type: CompilationType = CompilationType.AUTO):
    """
    Decorator for automatic function compilation.

    Args:
        compilation_type: Type of compilation to use

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Compile on first call
            if not hasattr(wrapper, "_compiled"):
                wrapper._compiled = compile_function(func, compilation_type)

            return wrapper._compiled(*args, **kwargs)

        return wrapper

    return decorator
