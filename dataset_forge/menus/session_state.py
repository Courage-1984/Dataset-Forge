# Session state for Dataset Forge
# Global variables that persist across menu navigation

# Folder paths
hq_folder = None
lq_folder = None

# Parallel processing settings
parallel_config = {
    "max_workers": None,  # None = auto-detect
    "processing_type": "auto",  # "auto", "thread", "process"
    "use_gpu": True,
    "gpu_memory_fraction": 0.8,
    "chunk_size": 1,
    "timeout": None,
    "cpu_only": False,
}

# User preferences
user_preferences = {
    "play_audio": True,
    "show_progress": True,
    "verbose_output": False,
    "auto_save_reports": True,
    "default_batch_size": 8,
    "default_quality": 85,
    "default_tile_size": 512,
    # BHI Filtering thresholds
    "bhi_blockiness_threshold": 0.5,
    "bhi_hyperiqa_threshold": 0.5,
    "bhi_ic9600_threshold": 0.5,
    # BHI Filtering suggested thresholds (for reference)
    "bhi_suggested_thresholds": {
        "conservative": {
            "blockiness": 0.3,
            "hyperiqa": 0.3,
            "ic9600": 0.3,
        },
        "moderate": {
            "blockiness": 0.5,
            "hyperiqa": 0.5,
            "ic9600": 0.5,
        },
        "aggressive": {
            "blockiness": 0.7,
            "hyperiqa": 0.7,
            "ic9600": 0.7,
        },
    },
}

# Operation history
operation_history = []

# Cache for expensive operations
operation_cache = {}
