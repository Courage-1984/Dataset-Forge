# BHI Filtering Thresholds Implementation Guide

## Overview

This guide explains the comprehensive BHI filtering implementation with suggested and default thresholds that has been integrated project-wide in Dataset Forge.

## Key Features

### ✅ **Default Thresholds**

- Configurable default thresholds stored in session state
- Automatic fallback to hardcoded defaults if session state unavailable
- Consistent thresholds across all BHI filtering operations

### ✅ **Preset Configurations**

- **Conservative**: Less aggressive filtering (thresholds: 0.3)
  - Good for: High-quality datasets, minimal filtering
- **Moderate**: Balanced filtering (thresholds: 0.5)
  - Good for: General purpose, default recommendation
- **Aggressive**: More aggressive filtering (thresholds: 0.7)
  - Good for: Low-quality datasets, strict filtering

### ✅ **Project-Wide Integration**

- Menu system integration with preset selection
- Settings menu for threshold configuration
- API functions for programmatic use
- Backward compatibility with existing code

## Usage Methods

### 1. **Menu Interface (Recommended)**

#### Access BHI Filtering

```
Main Menu → Analysis & Validation → BHI Filtering (Blockiness, HyperIQA, IC9600)
```

#### Threshold Selection

The menu now provides 5 options:

1. **Conservative** - Less aggressive filtering (thresholds: 0.3)
2. **Moderate** - Balanced filtering (thresholds: 0.5)
3. **Aggressive** - More aggressive filtering (thresholds: 0.7)
4. **Custom** - Set your own thresholds
5. **Use Current Defaults** - Use saved default thresholds

#### Configuration via Settings

```
Main Menu → System & Settings → User Preferences → Configure BHI Filtering Thresholds
```

Options available:

- Set individual thresholds (Blockiness, HyperIQA, IC9600)
- Apply preset configurations
- View current settings

### 2. **Programmatic API**

#### Using Default Thresholds

```python
from dataset_forge.actions.bhi_filtering_actions import run_bhi_filtering_with_defaults

# Uses thresholds from session state
results = run_bhi_filtering_with_defaults(
    input_path="path/to/images",
    action="move",
    batch_size=8
)
```

#### Using Preset Configurations

```python
from dataset_forge.actions.bhi_filtering_actions import run_bhi_filtering_with_preset

# Use conservative preset
results = run_bhi_filtering_with_preset(
    input_path="path/to/images",
    preset_name="conservative",
    action="move"
)

# Use aggressive preset
results = run_bhi_filtering_with_preset(
    input_path="path/to/images",
    preset_name="aggressive",
    action="delete"
)
```

#### Using Custom Thresholds

```python
from dataset_forge.actions.bhi_filtering_actions import run_bhi_filtering

# Custom thresholds
custom_thresholds = {
    "blockiness": 0.4,
    "hyperiqa": 0.6,
    "ic9600": 0.5
}

results = run_bhi_filtering(
    input_path="path/to/images",
    thresholds=custom_thresholds,
    action="report"
)
```

#### Utility Functions

```python
from dataset_forge.actions.bhi_filtering_actions import (
    get_default_bhi_thresholds,
    get_bhi_preset_thresholds
)

# Get current default thresholds
defaults = get_default_bhi_thresholds()
print(f"Current defaults: {defaults}")

# Get preset thresholds
conservative = get_bhi_preset_thresholds("conservative")
moderate = get_bhi_preset_thresholds("moderate")
aggressive = get_bhi_preset_thresholds("aggressive")
```

### 3. **Analysis Actions Integration**

The analysis actions module now supports enhanced BHI filtering:

```python
from dataset_forge.actions.analysis_actions import bhi_filtering

# Use preset
results = bhi_filtering(
    input_path="path/to/images",
    preset="conservative",
    action="move"
)

# Use defaults (no thresholds parameter)
results = bhi_filtering(
    input_path="path/to/images",
    action="report"
)
```

## Configuration

### Session State Structure

The BHI filtering thresholds are stored in `session_state.user_preferences`:

```python
user_preferences = {
    # ... other preferences ...

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
```

### Threshold Validation

All thresholds are validated to ensure they are within the valid range (0.0 to 1.0):

- Values below 0.0 are clamped to 0.0
- Values above 1.0 are clamped to 1.0
- Invalid inputs default to 0.5

## Implementation Details

### Files Modified

1. **`dataset_forge/menus/session_state.py`**

   - Added BHI filtering thresholds to user preferences
   - Added suggested threshold presets

2. **`dataset_forge/menus/bhi_filtering_menu.py`**

   - Enhanced menu with preset selection
   - Added threshold validation
   - Improved user experience with better prompts

3. **`dataset_forge/actions/settings_actions.py`**

   - Added BHI filtering threshold configuration
   - Added preset application options
   - Updated user preferences display

4. **`dataset_forge/actions/bhi_filtering_actions.py`**

   - Added utility functions for threshold management
   - Enhanced main function to use defaults when no thresholds provided
   - Added preset and default wrapper functions

5. **`dataset_forge/actions/analysis_actions.py`**
   - Enhanced BHI filtering function with preset support
   - Improved integration with new threshold system

### New Functions

#### Core Functions

- `get_default_bhi_thresholds()` - Get thresholds from session state
- `get_bhi_preset_thresholds(preset_name)` - Get thresholds for specific preset
- `run_bhi_filtering_with_preset()` - Run filtering with preset configuration
- `run_bhi_filtering_with_defaults()` - Run filtering with default thresholds

#### Menu Functions

- `show_threshold_presets()` - Display available presets
- `get_thresholds_from_preset()` - Get thresholds based on user choice
- `get_custom_thresholds()` - Get custom thresholds from user input
- `configure_bhi_thresholds()` - Configure thresholds in settings

## Best Practices

### 1. **Start with Report Mode**

Always test with report mode first to see what would be filtered:

```python
results = run_bhi_filtering_with_preset(
    input_path="path/to/images",
    preset_name="moderate",
    action="report"
)
```

### 2. **Use Appropriate Presets**

- **Conservative (0.3)**: For high-quality datasets where you want minimal filtering
- **Moderate (0.5)**: For general purpose use, good starting point
- **Aggressive (0.7)**: For low-quality datasets that need strict filtering

### 3. **Configure Defaults**

Set your preferred default thresholds in the settings menu for consistent behavior across sessions.

### 4. **Validate Results**

Always review the results before performing destructive operations (move/delete).

## Troubleshooting

### Common Issues

1. **Thresholds Not Applied**

   - Check that session state is properly initialized
   - Verify threshold values are in valid range (0.0-1.0)

2. **Preset Not Found**

   - Invalid preset names default to "moderate"
   - Check available presets: `["conservative", "moderate", "aggressive"]`

3. **Session State Unavailable**
   - Functions fall back to hardcoded defaults
   - Check import paths and module availability

### Testing

Run the test script to verify implementation:

```bash
python test_bhi_thresholds.py
```

This will test:

- Threshold function functionality
- Session state integration
- Threshold validation
- Preset configurations

## Migration Guide

### For Existing Code

Existing code using `run_bhi_filtering()` will continue to work:

```python
# Old way (still works)
results = run_bhi_filtering(
    input_path="path/to/images",
    thresholds={"blockiness": 0.5, "hyperiqa": 0.5, "ic9600": 0.5},
    action="move"
)

# New way (uses defaults if no thresholds provided)
results = run_bhi_filtering(
    input_path="path/to/images",
    action="move"  # Will use default thresholds
)
```

### For New Code

Use the new convenience functions:

```python
# Use defaults
results = run_bhi_filtering_with_defaults(input_path="path/to/images")

# Use preset
results = run_bhi_filtering_with_preset(
    input_path="path/to/images",
    preset_name="conservative"
)
```

## Summary

The BHI filtering implementation now provides:

- **Flexible threshold management** with defaults and presets
- **Project-wide integration** through menu system and API
- **Backward compatibility** with existing code
- **Enhanced user experience** with guided threshold selection
- **Robust validation** and error handling
- **Comprehensive documentation** and testing

This implementation ensures that BHI filtering is accessible, configurable, and consistent across the entire Dataset Forge project.
