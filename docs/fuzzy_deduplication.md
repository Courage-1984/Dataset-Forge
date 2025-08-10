# Fuzzy Matching De-duplication

## Overview

The Fuzzy Matching De-duplication feature provides advanced duplicate detection using multiple perceptual hashing algorithms with configurable similarity thresholds. This feature consolidates all duplicate detection methods into a single, comprehensive menu.

## Features

### 🔍 Multiple Hash Algorithms

- **pHash (Perceptual Hash)**: Detects duplicates based on image content and structure
- **dHash (Difference Hash)**: Detects duplicates based on edge differences
- **aHash (Average Hash)**: Detects duplicates based on average pixel values
- **wHash (Wavelet Hash)**: Detects duplicates based on wavelet transform
- **Color Hash**: Detects duplicates based on color distribution

### ⚙️ Configurable Thresholds

- **Per-Hash Thresholds**: Set different similarity thresholds for each hash method
- **Conservative Defaults**: Default thresholds optimized for accuracy
- **Flexible Configuration**: Adjust thresholds based on your needs

### 🎯 Multiple Operation Modes

- **Show**: Display duplicates without taking action
- **Copy**: Copy duplicates to a separate folder
- **Move**: Move duplicates to a separate folder
- **Delete**: Permanently delete duplicates (with confirmation)

### 📁 Support for Different Folder Types

- **Single Folder**: Process all images in one folder
- **HQ/LQ Pairs**: Process high-quality and low-quality image pairs
- **Cross-Folder Analysis**: Compare images across multiple folders

## Usage

### Accessing the Menu

1. Navigate to **Main Menu** → **🛠️ Utilities** → **🔍 Fuzzy Matching De-duplication**

### Menu Options

#### 1. 📁 Single Folder Fuzzy De-duplication

Process all images in a single folder to find duplicates.

**Features:**

- Select folder to analyze
- Choose hash methods (pHash, dHash, aHash, wHash, Color Hash)
- Configure similarity thresholds
- Choose operation mode (show/copy/move/delete)

#### 2. 🔗 HQ/LQ Pairs Fuzzy De-duplication

Process high-quality and low-quality image pairs to find duplicates.

**Features:**

- Select HQ and LQ folders
- Analyze pairs for duplicates
- Maintain pair relationships
- Choose operation mode

#### 3. ⚙️ Configure Fuzzy Matching Settings

Customize the fuzzy matching behavior.

**Settings:**

- **Default Hash Methods**: Choose which hash algorithms to use
- **Default Thresholds**: Set similarity thresholds for each hash method
- **Batch Size**: Configure processing batch size for memory optimization
- **Progress Display**: Enable/disable detailed progress information

#### 4. 📊 View Fuzzy Matching Statistics

View statistics about previous fuzzy matching operations.

**Statistics:**

- Total files processed
- Duplicate groups found
- Total duplicates detected
- Processing time
- Hash method effectiveness

## Hash Algorithms Explained

### pHash (Perceptual Hash)

- **Purpose**: Detects duplicates based on image content and structure
- **Best For**: Finding images with similar content but different formats/sizes
- **Default Threshold**: 90% similarity
- **Use Case**: Finding the same image saved in different formats

### dHash (Difference Hash)

- **Purpose**: Detects duplicates based on edge differences
- **Best For**: Finding images with similar edges and contours
- **Default Threshold**: 85% similarity
- **Use Case**: Finding images with similar compositions

### aHash (Average Hash)

- **Purpose**: Detects duplicates based on average pixel values
- **Best For**: Finding images with similar overall brightness
- **Default Threshold**: 80% similarity
- **Use Case**: Finding images with similar lighting conditions

### wHash (Wavelet Hash)

- **Purpose**: Detects duplicates based on wavelet transform
- **Best For**: Finding images with similar frequency components
- **Default Threshold**: 85% similarity
- **Use Case**: Finding images with similar textures

### Color Hash

- **Purpose**: Detects duplicates based on color distribution
- **Best For**: Finding images with similar color palettes
- **Default Threshold**: 75% similarity
- **Use Case**: Finding images with similar color schemes

## Threshold Guidelines

### Conservative (High Accuracy)

- **pHash**: 95%
- **dHash**: 90%
- **aHash**: 85%
- **wHash**: 90%
- **Color Hash**: 80%

### Balanced (Recommended)

- **pHash**: 90%
- **dHash**: 85%
- **aHash**: 80%
- **wHash**: 85%
- **Color Hash**: 75%

### Aggressive (More Duplicates)

- **pHash**: 80%
- **dHash**: 75%
- **aHash**: 70%
- **wHash**: 75%
- **Color Hash**: 65%

## Best Practices

### 1. Start with Conservative Thresholds

- Begin with higher thresholds to avoid false positives
- Gradually lower thresholds if you need to find more duplicates

### 2. Use Multiple Hash Methods

- Combine different hash methods for better accuracy
- pHash + dHash is a good starting combination

### 3. Test with Small Datasets First

- Always test with a small subset before processing large datasets
- Verify the results match your expectations

### 4. Use "Show" Mode First

- Always use "Show" mode to preview duplicates before taking action
- Review the results before copying, moving, or deleting

### 5. Backup Important Data

- Always backup your data before using delete operations
- Use copy/move operations when possible

### 6. Monitor Memory Usage

- Large datasets may require significant memory
- Use appropriate batch sizes for your system

## Performance Considerations

### Memory Usage

- **Small Datasets** (< 1,000 images): Use batch size of 100-500
- **Medium Datasets** (1,000-10,000 images): Use batch size of 50-200
- **Large Datasets** (> 10,000 images): Use batch size of 20-100

### Processing Speed

- **pHash**: Fastest, good for initial screening
- **dHash**: Fast, good for edge-based detection
- **aHash**: Very fast, good for brightness-based detection
- **wHash**: Slower, good for texture-based detection
- **Color Hash**: Medium speed, good for color-based detection

### Accuracy vs Speed Trade-offs

- **High Accuracy**: Use all hash methods with high thresholds
- **Fast Processing**: Use pHash + dHash only
- **Balanced**: Use pHash + dHash + aHash with medium thresholds

## Troubleshooting

### Common Issues

#### No Duplicates Found

- **Cause**: Thresholds too high
- **Solution**: Lower the similarity thresholds
- **Alternative**: Try different hash method combinations

#### Too Many False Positives

- **Cause**: Thresholds too low
- **Solution**: Increase the similarity thresholds
- **Alternative**: Use fewer hash methods

#### Memory Errors

- **Cause**: Batch size too large
- **Solution**: Reduce the batch size
- **Alternative**: Process smaller subsets

#### Slow Processing

- **Cause**: Too many hash methods or large batch size
- **Solution**: Use fewer hash methods or smaller batch size
- **Alternative**: Process in smaller chunks

### Error Messages

#### "No image files found"

- **Cause**: Folder doesn't contain supported image files
- **Solution**: Check folder path and file types

#### "Invalid threshold value"

- **Cause**: Threshold not between 0 and 100
- **Solution**: Use values between 0 and 100

#### "Operation cancelled"

- **Cause**: User cancelled the operation
- **Solution**: Re-run the operation

## Integration with Other Features

### Visual De-duplication

- Use fuzzy matching for initial screening
- Use visual de-duplication for final verification

### File Hash De-duplication

- Use fuzzy matching for content-based duplicates
- Use file hash for exact duplicates

### ImageDedup

- Use fuzzy matching for perceptual duplicates
- Use ImageDedup for advanced duplicate detection

## Technical Details

### Hash Computation

- All hashes are computed using the `imagehash` library
- Hashes are normalized to 64-bit values
- Similarity is calculated using Hamming distance

### Memory Management

- Images are processed in batches to manage memory usage
- Hash values are cached to avoid recomputation
- Memory is cleared after each batch

### Error Handling

- Invalid images are skipped with warnings
- Processing continues even if some images fail
- Comprehensive error reporting and logging

## Future Enhancements

### Planned Features

- **Machine Learning Integration**: Use ML models for better duplicate detection
- **Batch Processing**: Process multiple folders simultaneously
- **Cloud Integration**: Support for cloud storage providers
- **Advanced Filtering**: Filter duplicates by size, date, or other criteria

### Performance Improvements

- **GPU Acceleration**: Use GPU for hash computation
- **Parallel Processing**: Process multiple images simultaneously
- **Caching**: Persistent cache for hash values

## Support

For issues or questions about the Fuzzy Matching De-duplication feature:

1. Check the troubleshooting section above
2. Review the error messages and logs
3. Test with smaller datasets first
4. Verify your folder structure and file types
5. Check the system requirements and dependencies

## Dependencies

The Fuzzy Matching De-duplication feature requires:

- **imagehash**: For perceptual hash computation
- **PIL/Pillow**: For image processing
- **numpy**: For numerical operations
- **tqdm**: For progress tracking

All dependencies are included in the project's `requirements.txt` file.
