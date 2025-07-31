# BHI Filtering Troubleshooting Guide

## Common Issues and Solutions

### 1. "Access is denied" Error

**Symptoms:**

- Error message: `Error reading file: Access is denied. (os error 5)`
- Process stops at the first problematic file

**Causes:**

- File permissions issues
- Files locked by other applications
- Corrupted or invalid image files
- Path too long (Windows limitation)

**Solutions:**

#### A. Check File Permissions

```bash
# Run the test script to check access
python test_bhi_filtering.py "E:/_dataset/_Aristotle_Roufanis/finetune/_tiles"
```

#### B. Run as Administrator

- Right-click on your terminal/command prompt
- Select "Run as administrator"
- Navigate to the Dataset-Forge directory
- Run the script again

#### C. Check for Locked Files

- Close any image viewers or editors that might have the files open
- Check Task Manager for processes that might be using the files
- Restart your computer if necessary

#### D. Move Files to Different Location

- Copy the folder to a shorter path (e.g., `C:\temp\images`)
- Try the BHI filtering on the copied folder

### 2. Model Loading Issues

**Symptoms:**

- IC9600 model fails to download or load
- Warning messages about model loading

**Solutions:**

- Check internet connection (model is downloaded from GitHub)
- The script will automatically skip IC9600 if the model fails to load
- You can still use Blockiness and HyperIQA metrics

### 3. Memory Issues

**Symptoms:**

- Out of memory errors
- Process becomes very slow

**Solutions:**

- Reduce batch size (try 4 or 2 instead of 8)
- Process smaller batches of files
- Close other applications to free up memory

## Improved Error Handling

The BHI filtering has been updated with better error handling:

1. **File Reading Errors**: Files that can't be read are skipped instead of crashing the process
2. **Model Loading**: IC9600 model failures are handled gracefully
3. **File Operations**: Move/delete operations have error handling
4. **Progress Reporting**: Better feedback on what's happening

## Usage Tips

### 1. Start with Report Mode

Always test with report mode first to see what would be filtered:

```
Action: report
Dry run: Yes
```

### 2. Use Lower Thresholds

Start with lower thresholds to see more results:

```
Blockiness: 0.3
HyperIQA: 0.3
IC9600: 0.3
```

### 3. Process in Smaller Batches

If you have many files, consider:

- Processing subfolders separately
- Using smaller batch sizes
- Running during off-peak hours

### 4. Backup Your Data

Always backup your original data before running destructive operations (move/delete).

## Test Script Usage

Run the test script to diagnose issues:

```bash
# Test a specific folder
python test_bhi_filtering.py "path/to/your/folder"

# Or run interactively
python test_bhi_filtering.py
```

The test script will:

- Check folder access permissions
- Test reading sample image files
- Provide specific error messages
- Suggest solutions

## Getting Help

If you continue to have issues:

1. Run the test script and share the output
2. Check the specific error messages
3. Try with a different folder to isolate the issue
4. Consider file system permissions and antivirus software interference
