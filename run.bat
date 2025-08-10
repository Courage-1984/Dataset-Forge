@echo off
echo Setting up optimized CUDA environment for Dataset Forge...

REM CUDA Memory Management Optimizations
set PYTORCH_NO_CUDA_MEMORY_CACHING=1
set PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128,expandable_segments:True

REM Performance Optimizations
set CUDA_LAUNCH_BLOCKING=0
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1

REM GPU Memory Optimization
set CUDA_MEMORY_FRACTION=0.9

REM Windows-specific CUDA multiprocessing fix
set PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128,expandable_segments:True,roundup_power2_divisions:8

@REM echo CUDA optimizations applied:
@REM echo   - Memory caching disabled for better fragmentation handling
@REM echo   - CUDA allocator configured for optimal memory management
@REM echo   - Thread optimization for PyTorch operations
@REM echo   - GPU memory fraction set to 90%%
@REM echo   - Windows CUDA multiprocessing compatibility enabled

REM Activate the virtual environment
call venv312\Scripts\activate

REM Run Dataset Forge via CLI entry point (preferred)
@REM dataset-forge

REM Fallback: run main.py if CLI entry point is not available
py main.py 