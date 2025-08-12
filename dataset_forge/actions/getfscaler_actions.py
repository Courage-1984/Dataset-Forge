"""
getfscaler Integration Module for Dataset Forge

This module provides comprehensive integration with getfscaler.exe for kernel detection
and upscaling analysis. It includes proper error handling, output parsing, batch processing,
and configuration management as specified in the getfscaler_integration_guide.md.
"""

import subprocess
import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime
import yaml
from dataclasses import dataclass

from dataset_forge.utils.printing import (
    print_info, print_success, print_warning, print_error, print_header, print_section
)
from dataset_forge.utils.audio_utils import play_done_sound, play_error_sound
from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache
from dataset_forge.utils.color import Mocha


@dataclass
class GetfScalerConfig:
    """Configuration for getfscaler integration."""
    exe_path: str = "getfscaler.exe"
    default_native_height: float = 720.0
    default_crop: int = 8
    timeout_seconds: int = 300
    max_workers: int = 4
    supported_extensions: List[str] = None

    def __post_init__(self):
        if self.supported_extensions is None:
            self.supported_extensions = [
                '.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tga',
                '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv',
                '.vpy', '.py'
            ]


class GetfScalerValidator:
    """Validate inputs and handle errors for getfscaler integration."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def validate_file(self, file_path: Union[str, Path]) -> bool:
        """Validate that the input file exists and is supported."""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check file size
        file_size = file_path.stat().st_size
        if file_size == 0:
            raise ValueError(f"File is empty: {file_path}")

        # Check file extension
        supported_extensions = {
            '.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tga',
            '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv',
            '.vpy', '.py'
        }

        if file_path.suffix.lower() not in supported_extensions:
            self.logger.warning(f"Unsupported file extension: {file_path.suffix}")

        return True

    def validate_parameters(self,
                          native_height: float,
                          native_width: Optional[float] = None,
                          crop: int = 8) -> bool:
        """Validate getfscaler parameters."""

        if native_height <= 0:
            raise ValueError("native_height must be positive")

        if native_width is not None and native_width <= 0:
            raise ValueError("native_width must be positive")

        if crop < 0:
            raise ValueError("crop must be non-negative")

        return True

    def handle_getfscaler_error(self, error: Exception, file_path: str) -> Dict:
        """Handle and categorize getfscaler errors."""
        error_info = {
            'file': file_path,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.now().isoformat()
        }

        if "No attribute with the name" in str(error):
            error_info['category'] = 'missing_plugin'
            error_info['suggestion'] = 'VapourSynth plugin missing. Check installation.'
        elif "timeout" in str(error).lower():
            error_info['category'] = 'timeout'
            error_info['suggestion'] = 'File too large or complex. Try smaller file or different parameters.'
        elif "file not found" in str(error).lower():
            error_info['category'] = 'file_error'
            error_info['suggestion'] = 'Check file path and permissions.'
        else:
            error_info['category'] = 'unknown'
            error_info['suggestion'] = 'Check getfscaler installation and file format.'

        self.logger.error(f"getfscaler error: {error_info}")
        return error_info


class GetfScalerIntegration:
    """Comprehensive getfscaler integration with proper error handling and output parsing."""

    def __init__(self, exe_path: str = "getfscaler.exe"):
        # Try to find the executable in PATH if it's not an absolute path
        if not Path(exe_path).is_absolute():
            import shutil
            exe_in_path = shutil.which(exe_path)
            if exe_in_path:
                self.exe_path = Path(exe_in_path)
            else:
                # Try current directory
                current_dir_exe = Path(exe_path)
                if current_dir_exe.exists():
                    self.exe_path = current_dir_exe
                else:
                    raise FileNotFoundError(f"getfscaler.exe not found in PATH or current directory: {exe_path}")
        else:
            self.exe_path = Path(exe_path)
            if not self.exe_path.exists():
                raise FileNotFoundError(f"getfscaler.exe not found at {exe_path}")
        
        self.validator = GetfScalerValidator()

    def analyze_image(self,
                     image_path: str,
                     native_height: float = 720.0,
                     native_width: Optional[float] = None,
                     crop: int = 8,
                     frame: Optional[int] = None,
                     debug: bool = False) -> Dict:
        """
        Analyze an image to determine the best inverse scaling kernel.

        Args:
            image_path: Path to the image file
            native_height: Target native height
            native_width: Target native width (auto-calculated if None)
            crop: Pixels to crop from edges
            frame: Specific frame to analyze (random if None)
            debug: Enable debug output

        Returns:
            Dictionary containing analysis results
        """
        try:
            # Validate inputs
            self.validator.validate_file(image_path)
            self.validator.validate_parameters(native_height, native_width, crop)

            cmd = [str(self.exe_path), str(image_path), "-nh", str(native_height)]

            if native_width is not None:
                cmd.extend(["-nw", str(native_width)])

            if crop != 8:
                cmd.extend(["-c", str(crop)])

            if frame is not None:
                cmd.extend(["-f", str(frame)])

            if debug:
                cmd.append("--debug")

            print_info(f"Running getfscaler command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode != 0:
                raise RuntimeError(f"getfscaler failed: {result.stderr}")

            parsed_results = self._parse_output(result.stdout)
            
            # Add metadata
            parsed_results['metadata'] = {
                'input_file': image_path,
                'parameters': {
                    'native_height': native_height,
                    'native_width': native_width,
                    'crop': crop,
                    'frame': frame,
                    'debug': debug
                },
                'analysis_timestamp': datetime.now().isoformat()
            }
            parsed_results['success'] = True

            return parsed_results

        except Exception as e:
            error_info = self.validator.handle_getfscaler_error(e, image_path)
            return {
                'error': error_info,
                'success': False
            }

    def _parse_output(self, output: str) -> Dict:
        """Parse getfscaler output into structured data."""
        lines = output.strip().split('\n')

        # Extract basic info
        results = {
            'scalers': [],
            'best_scaler': None,
            'best_error': None,
            'frame_info': {},
            'warnings': []
        }

        for line in lines:
            line = line.strip()

            # Parse frame info
            if line.startswith('Results for frame'):
                match = re.search(r'frame (\d+) \(resolution: ([^,]+), AR: ([\d.]+)', line)
                if match:
                    results['frame_info'] = {
                        'frame': int(match.group(1)),
                        'resolution': match.group(2),
                        'aspect_ratio': float(match.group(3))
                    }

            # Parse scaler results
            elif '|' in line and not line.startswith('-') and 'Scaler' not in line:
                parts = line.split('\t')
                if len(parts) >= 3:
                    scaler_name = parts[0].strip()
                    error_percent = parts[1].strip().replace('%', '')
                    abs_error = parts[2].strip()

                    try:
                        error_percent = float(error_percent)
                        abs_error = float(abs_error)

                        scaler_info = {
                            'name': scaler_name,
                            'error_percent': error_percent,
                            'abs_error': abs_error
                        }
                        results['scalers'].append(scaler_info)

                        # Track best scaler
                        if results['best_scaler'] is None or abs_error < results['best_error']:
                            results['best_scaler'] = scaler_name
                            results['best_error'] = abs_error

                    except ValueError:
                        continue

            # Parse warnings
            elif line.startswith('[WARNING]') or 'WARNING' in line:
                results['warnings'].append(line)

        return results


class BatchGetfScaler:
    """Batch processing capabilities for getfscaler."""

    def __init__(self, exe_path: str = "getfscaler.exe", max_workers: int = 4):
        self.scaler = GetfScalerIntegration(exe_path)
        self.max_workers = max_workers

    def analyze_directory(self,
                         directory: str,
                         file_patterns: List[str] = ["*.png", "*.jpg", "*.jpeg", "*.mp4", "*.mkv"],
                         native_height: float = 720.0,
                         **kwargs) -> Dict[str, Dict]:
        """
        Analyze all matching files in a directory.

        Args:
            directory: Directory to scan
            file_patterns: List of file patterns to match
            native_height: Target native height
            **kwargs: Additional arguments for analyze_image

        Returns:
            Dictionary mapping file paths to analysis results
        """
        directory_path = Path(directory)
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        # Find all matching files
        files = []
        for pattern in file_patterns:
            files.extend(directory_path.glob(pattern))

        if not files:
            print_warning(f"No files found matching patterns: {file_patterns}")
            return {}

        print_info(f"Found {len(files)} files to analyze...")

        # Process files sequentially (getfscaler is CPU intensive)
        results = {}
        for i, file in enumerate(files, 1):
            try:
                print_info(f"Analyzing {i}/{len(files)}: {file.name}")
                result = self.scaler.analyze_image(str(file), native_height=native_height, **kwargs)
                results[str(file)] = result
                print_success(f"✓ Analyzed: {file.name}")
            except Exception as e:
                print_error(f"✗ Failed to analyze {file.name}: {e}")
                results[str(file)] = {'error': str(e), 'success': False}

        return results

    def save_batch_results(self, results: Dict[str, Dict], output_file: str):
        """Save batch analysis results to JSON file."""
        # Add summary statistics
        summary = {
            'total_files': len(results),
            'successful_analyses': len([r for r in results.values() if r.get('success', False)]),
            'failed_analyses': len([r for r in results.values() if not r.get('success', False)]),
            'best_scalers': {},
            'average_errors': {}
        }

        # Collect best scalers and errors
        scaler_counts = {}
        errors = []

        for file_path, result in results.items():
            if result.get('success') and result.get('best_scaler'):
                scaler = result['best_scaler']
                scaler_counts[scaler] = scaler_counts.get(scaler, 0) + 1

                if result.get('best_error'):
                    errors.append(result['best_error'])

        summary['best_scalers'] = scaler_counts
        if errors:
            summary['average_errors'] = {
                'mean': sum(errors) / len(errors),
                'min': min(errors),
                'max': max(errors)
            }

        output_data = {
            'summary': summary,
            'results': results
        }

        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        print_success(f"Batch results saved to: {output_file}")


class ConfigManager:
    """Manage getfscaler configuration."""

    @staticmethod
    def load_config(config_file: str = "getfscaler_config.yaml") -> GetfScalerConfig:
        """Load configuration from YAML file."""
        if not Path(config_file).exists():
            return GetfScalerConfig()

        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)

        return GetfScalerConfig(**config_data)

    @staticmethod
    def save_config(config: GetfScalerConfig, config_file: str = "getfscaler_config.yaml"):
        """Save configuration to YAML file."""
        config_data = {
            'exe_path': config.exe_path,
            'default_native_height': config.default_native_height,
            'default_crop': config.default_crop,
            'timeout_seconds': config.timeout_seconds,
            'max_workers': config.max_workers,
            'supported_extensions': config.supported_extensions
        }

        with open(config_file, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)


def find_native_resolution_getfscaler(image_path, lq_path=None, extra_args=None):
    """
    Enhanced getfscaler integration with comprehensive error handling and output parsing.
    
    This function provides a user-friendly interface to getfscaler with proper error handling,
    output parsing, and result presentation.
    """
    print_header("🔧 getfscaler Kernel Detection", color=Mocha.yellow)
    print_info("Analyzing image to determine the best inverse scaling kernel...")

    try:
        # Initialize getfscaler integration
        print_info("🔍 Looking for getfscaler.exe...")
        try:
            scaler = GetfScalerIntegration("getfscaler.exe")
            print_success(f"✅ Found getfscaler.exe at: {scaler.exe_path}")
        except FileNotFoundError as e:
            print_error(f"❌ {e}")
            print_info("💡 Make sure getfscaler.exe is in your PATH or current directory")
            print_info("💡 You can also specify the full path to getfscaler.exe")
            return
        
        # Parse extra arguments
        native_height = 720.0
        native_width = None
        crop = 8
        frame = None
        debug = False
        
        if extra_args:
            # Parse common arguments
            for i, arg in enumerate(extra_args):
                if arg == "-nh" and i + 1 < len(extra_args):
                    try:
                        native_height = float(extra_args[i + 1])
                    except ValueError:
                        print_warning(f"Invalid native height: {extra_args[i + 1]}")
                elif arg == "-nw" and i + 1 < len(extra_args):
                    try:
                        native_width = float(extra_args[i + 1])
                    except ValueError:
                        print_warning(f"Invalid native width: {extra_args[i + 1]}")
                elif arg == "-c" and i + 1 < len(extra_args):
                    try:
                        crop = int(extra_args[i + 1])
                    except ValueError:
                        print_warning(f"Invalid crop value: {extra_args[i + 1]}")
                elif arg == "-f" and i + 1 < len(extra_args):
                    try:
                        frame = int(extra_args[i + 1])
                    except ValueError:
                        print_warning(f"Invalid frame value: {extra_args[i + 1]}")
                elif arg == "--debug":
                    debug = True

        # Analyze the image
        results = scaler.analyze_image(
            image_path,
            native_height=native_height,
            native_width=native_width,
            crop=crop,
            frame=frame,
            debug=debug
        )

        if results.get('success'):
            print_success("✅ getfscaler analysis completed successfully!")
            
            # Display results
            print_section("Analysis Results", char="-", color=Mocha.lavender)
            
            if results.get('frame_info'):
                frame_info = results['frame_info']
                print_info(f"📊 Frame: {frame_info['frame']}")
                print_info(f"📐 Resolution: {frame_info['resolution']}")
                print_info(f"📏 Aspect Ratio: {frame_info['aspect_ratio']}")
            
            if results.get('best_scaler'):
                print_success(f"🏆 Best Scaler: {results['best_scaler']}")
                if results.get('best_error'):
                    print_info(f"📊 Error: {results['best_error']:.10f}")
            
            if results.get('scalers'):
                print_info("\n📋 All Scaler Results:")
                print_info("-" * 60)
                for scaler_info in results['scalers'][:5]:  # Show top 5
                    print_info(f"{scaler_info['name']:<30} {scaler_info['abs_error']:.10f}")
            
            if results.get('warnings'):
                print_warning("\n⚠️  Warnings:")
                for warning in results['warnings']:
                    print_warning(f"  {warning}")
            
            play_done_sound()
            
        else:
            error_info = results.get('error', {})
            print_error(f"❌ getfscaler analysis failed: {error_info.get('error_message', 'Unknown error')}")
            
            if error_info.get('suggestion'):
                print_info(f"💡 Suggestion: {error_info['suggestion']}")
            
            play_error_sound()

    except Exception as e:
        print_error(f"❌ getfscaler integration error: {e}")
        play_error_sound()

    print_info("🔧 getfscaler workflow finished.")


def batch_analyze_getfscaler(directory_path, output_file=None, **kwargs):
    """
    Batch analyze multiple files using getfscaler.
    
    Args:
        directory_path: Directory containing files to analyze
        output_file: Optional output file for results
        **kwargs: Additional arguments for getfscaler
    """
    print_header("🔧 Batch getfscaler Analysis", color=Mocha.yellow)
    
    try:
        batch_scaler = BatchGetfScaler("getfscaler.exe")
        results = batch_scaler.analyze_directory(directory_path, **kwargs)
        
        if output_file:
            batch_scaler.save_batch_results(results, output_file)
        
        # Display summary
        successful = len([r for r in results.values() if r.get('success', False)])
        total = len(results)
        
        print_success(f"✅ Batch analysis completed: {successful}/{total} successful")
        
        if successful > 0:
            # Show most common best scalers
            scaler_counts = {}
            for result in results.values():
                if result.get('success') and result.get('best_scaler'):
                    scaler = result['best_scaler']
                    scaler_counts[scaler] = scaler_counts.get(scaler, 0) + 1
            
            if scaler_counts:
                print_info("\n🏆 Most Common Best Scalers:")
                for scaler, count in sorted(scaler_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
                    print_info(f"  {scaler}: {count} files")
        
        play_done_sound()
        
    except Exception as e:
        print_error(f"❌ Batch analysis failed: {e}")
        play_error_sound()


# Configuration file template
CONFIG_TEMPLATE = """
# getfscaler Configuration File
# This file configures the getfscaler integration for Dataset Forge

exe_path: "getfscaler.exe"
default_native_height: 720.0
default_crop: 8
timeout_seconds: 300
max_workers: 4
supported_extensions:
  - ".png"
  - ".jpg"
  - ".jpeg"
  - ".mp4"
  - ".mkv"
  - ".vpy"
"""


def create_default_config(config_file: str = "getfscaler_config.yaml"):
    """Create a default configuration file."""
    if not Path(config_file).exists():
        with open(config_file, 'w') as f:
            f.write(CONFIG_TEMPLATE)
        print_success(f"Created default configuration file: {config_file}")
    else:
        print_warning(f"Configuration file already exists: {config_file}")


# Export main functions for use in menus
__all__ = [
    'GetfScalerIntegration',
    'BatchGetfScaler',
    'ConfigManager',
    'find_native_resolution_getfscaler',
    'batch_analyze_getfscaler',
    'create_default_config'
]
