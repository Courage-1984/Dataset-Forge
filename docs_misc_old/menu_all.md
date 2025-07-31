##################################################
Image Dataset Utility - Main Menu  
##################################################
[ 1 ] 📂 DATASET
[ 2 ] 📊 ANALYSIS
[ 3 ] 📈 RICH REPORTS
[ 4 ] 💡 AUTOMATED DATASET QUALITY SCORING
[ 5 ] 💾 PROGRESSIVE DATASET VALIDATION
[ 6 ] 🔎 OUTLIER & ANOMALY DETECTION
[ 7 ] ✨ TRANSFORM
[ 8 ] 🍇 AUGMENTATION RECIPES
[ 9 ] 🗂️ METADATA
[ 10 ] 🔍 COMPARISON
[ 11 ] 📝 BATCH RENAME
[ 12 ] 📁 CONFIG
[ 13 ] ⚙️ SETTINGS
[ 14 ] 📦 COMPRESS IMAGES
[ 15 ] 📦 COMPRESS DIRECTORY
[ 16 ] 🔗 LINKS
[ 17 ] 👤 USER PROFILE
[ 18 ] 📓 VIEW CHANGE/HISTORY LOG
[ 19 ] 🔧 CORRECT/CREATE HQ LQ PAIRING
[ 20 ] 🔊 AUTOMATIC HQ/LQ PAIRING (FUZZY MATCHING)
[ 21 ] 🗑️ VISUAL DUPLICATE & NEAR-DUPLICATE DETECTION
[ 0 ] 🚪 EXIT


Enter your choice: 1
--------------------------------------------------
          Dataset Creation & Management
--------------------------------------------------
[ 1 ]  Create Multiscale Dataset
[ 2 ]  Image Tiling
[ 3 ]  Combine Datasets
[ 4 ]  Extract Random Pairs
[ 5 ]  Shuffle Image Pairs
[ 6 ]  Split and Adjust Dataset
[ 7 ]  Remove Small Image Pairs
[ 8 ]  De-Duplicate
[ 9 ]  Batch Rename
[ 10 ]  Extract Frames from Video
[ 11 ]  Images Orientation Organization (Extract by Landscape/Portrait/Square)
[ 0 ]  Back to Main Menu

Enter your choice: 2
--------------------------------------------------
           Dataset Analysis & Reporting
--------------------------------------------------
[ 1 ]  Progressive Dataset Validation (All Checks)
[ 2 ]  Generate HQ/LQ Dataset Report
[ 3 ]  Find HQ/LQ Scale
[ 4 ]  Test HQ/LQ Scale
[ 5 ]  Check Dataset Consistency
[ 6 ]  Report Image Dimensions
[ 7 ]  Find Extreme Image Dimensions
[ 8 ]  Verify Images (Corruption Check)
[ 9 ]  Fix Corrupted Images
[ 10 ]  Find Misaligned Images
[ 11 ]  Find Images with Alpha Channel
[ 12 ]  BHI Filtering (Blockiness, HyperIQA, IC9600)
[ 13 ]  Test Aspect Ratio
[ 0 ]  Back to Main Menu

Enter your choice: 3

=== Rich Reports (HTML/Markdown) ===
Generate a detailed report with plots and sample images.
1. HQ/LQ parent_path workflow
2. Single-folder workflow
0. Return to main menu
Select workflow:

Enter your choice: 4
--------------------------------------------------
        Automated Dataset Quality Scoring         
--------------------------------------------------
[ 1 ]  Run Quality Scoring Workflow
[ 0 ]  Back to Main Menu

Enter your choice:

Enter your choice: 6

Outlier & Anomaly Detection:
Detect images that are very different from the rest using clustering or embedding-based methods.
You can analyze:
  1. HQ/LQ folder pair (flag outliers in both)
  2. Single folder (flag outliers in one set)

Select mode: [1] HQ/LQ pair, [2] Single folder: 

Enter your choice: 7
--------------------------------------------------
              Image Transformations
--------------------------------------------------
[ 1 ]  Downsample Images
[ 2 ]  Convert HDR to SDR
[ 3 ]  Color/Tone Adjustments
[ 4 ]  Hue/Brightness/Contrast Adjustment
[ 5 ]  Grayscale Conversion
[ 6 ]  Remove Alpha Channel
[ 7 ]  Apply Custom Transformations
[ 0 ]  Back to Main Menu

Enter your choice:

Enter your choice: 8
--------------------------------------------------
               Augmentation Recipes
--------------------------------------------------
[ 1 ]  Run Augmentation Pipeline
[ 0 ]  Back to Main Menu

Enter your choice:

Enter your choice: 9
--------------------------------------------------
          EXIF & ICC Profile Management
--------------------------------------------------
[ 1 ]  Scrub EXIF Metadata
[ 2 ]  Convert ICC Profile to sRGB
[ 0 ]  Back to Main Menu

Enter your choice:

Enter your choice: 10
--------------------------------------------------
                 Comparison Tools
--------------------------------------------------
[ 1 ]  Create Comparison Images
[ 2 ]  Create GIF Comparison
[ 3 ]  Compare Folders
[ 0 ]  Back to Main Menu

Enter your choice:

Enter your choice: 11

=== Batch Renaming Utility ===
Enter input folder path (single folder or parent of hq/lq):

Enter your choice: 12
==================================================
         Configuration & Model Management
==================================================
[ 1 ]  Add Config File
[ 2 ]  Load Config File
[ 3 ]  View Config Info
[ 4 ]  Validate HQ/LQ Dataset from Config
[ 5 ]  Validate Val Dataset HQ/LQ Pair
[ 6 ]  Run wtp_dataset_destroyer
[ 7 ]  Edit .hcl config file
[ 8 ]  Run traiNNer-redux
[ 9 ]  Edit .yml config file
[ 10 ]  List/Run Upscale with Model
[ 0 ]  Back to Main Menu

Enter your choice:

Enter your choice: 13
----------------------------------------
                Settings
----------------------------------------
Current HQ Folder: Not Set
Current LQ Folder: Not Set

[1] Set HQ/LQ Folders
[0] Back to Main Menu
Choice:

Enter your choice: 14
##################################################
                 Compress Images
##################################################
Choose input mode:
##################################################
                Select Input Mode
##################################################
[ 1 ]  HQ/LQ paired folders
[ 2 ]  Single folder
[ 0 ]  Cancel

Enter your choice:

Enter your choice: 15
##################################################
                Compress Directory
##################################################
Choose input mode:
##################################################
                Select Input Mode
##################################################
[ 1 ]  HQ/LQ paired folders
[ 2 ]  Single folder
[ 0 ]  Cancel

Enter your choice:

Enter your choice: 16
##################################################
                    Links Menu
##################################################
[ 1 ]  Community Links
[ 2 ]  Personal Links
[ 0 ]  Back

Enter your choice:

Enter your choice: 17
##################################################
                   User Profile
##################################################
[ 1 ]  Profile Management
[ 2 ]  View/Edit Favorites
[ 3 ]  Manage Presets
[ 4 ]  Quick Access Paths
[ 5 ]  View/Edit Settings
[ 0 ]  Back to Main Menu

Enter your choice:

Enter your choice: 18
##################################################
             Change/History Log Menu
##################################################
[ 1 ]  View most recent log
[ 2 ]  Select a log to view
[ 0 ]  Return to main menu

Enter your choice:

Enter your choice: 19
##################################################
           Correct/Create HQ LQ Pairing
##################################################
This tool helps you pair HQ and LQ folders, check alignment, test scale, and correct scale if needed.

Enter path to HQ folder:

Enter your choice: 20
##################################################
     Automatic HQ/LQ Pairing (Fuzzy Matching)     
##################################################
This tool uses perceptual hashes or embeddings to pair HQ and LQ images even if filenames differ.

Enter path to HQ folder:

Enter your choice: 21

=== Visual Duplicate & Near-Duplicate Detection ===
1. HQ/LQ parent_path workflow
2. Single-folder workflow
0. Return to main menu
Select workflow:















All Menu Items:
[1] 📂 DATASET > Create Multiscale Dataset
[2] 📂 DATASET > Image Tiling
[3] 📂 DATASET > Combine Datasets
[4] 📂 DATASET > Extract Random Pairs
[5] 📂 DATASET > Shuffle Image Pairs
[6] 📂 DATASET > Split and Adjust Dataset
[7] 📂 DATASET > Remove Small Image Pairs
[8] 📂 DATASET > De-Duplicate
[9] 📂 DATASET > Batch Rename
[10] 📂 DATASET > Extract Frames from Video
[11] 📂 DATASET > Images Orientation Organization (Extract by Landscape/Portrait/Square)
[12] 📂 DATASET > Back to Main Menu
[13] 📊 ANALYSIS > Progressive Dataset Validation (All Checks)
[14] 📊 ANALYSIS > Generate HQ/LQ Dataset Report
[15] 📊 ANALYSIS > Find HQ/LQ Scale
[16] 📊 ANALYSIS > Test HQ/LQ Scale
[17] 📊 ANALYSIS > Check Dataset Consistency
[18] 📊 ANALYSIS > Report Image Dimensions
[19] 📊 ANALYSIS > Find Extreme Image Dimensions
[20] 📊 ANALYSIS > Verify Images (Corruption Check)
[21] 📊 ANALYSIS > Fix Corrupted Images
[22] 📊 ANALYSIS > Find Misaligned Images
[23] 📊 ANALYSIS > Find Images with Alpha Channel
[24] 📊 ANALYSIS > BHI Filtering (Blockiness, HyperIQA, IC9600) > Back to Main Menu
[25] 📊 ANALYSIS > Test Aspect Ratio
[26] 📊 ANALYSIS > Back to Main Menu
[27] 📈 RICH REPORTS
[28] 💡 AUTOMATED DATASET QUALITY SCORING > Run Quality Scoring Workflow
[29] 💡 AUTOMATED DATASET QUALITY SCORING > Back to Main Menu
[30] 💾 PROGRESSIVE DATASET VALIDATION
[31] 🔎 OUTLIER & ANOMALY DETECTION
[32] ✨ TRANSFORM > Downsample Images
[33] ✨ TRANSFORM > Convert HDR to SDR
[34] ✨ TRANSFORM > Color/Tone Adjustments
[35] ✨ TRANSFORM > Hue/Brightness/Contrast Adjustment > Back to Main Menu
[36] ✨ TRANSFORM > Grayscale Conversion
[37] ✨ TRANSFORM > Remove Alpha Channel
[38] ✨ TRANSFORM > Apply Custom Transformations
[39] ✨ TRANSFORM > Back to Main Menu
[40] 🍇 AUGMENTATION RECIPES > Run Augmentation Pipeline
[41] 🍇 AUGMENTATION RECIPES > Back to Main Menu
[42] 🗂️ METADATA > Scrub EXIF Metadata
[43] 🗂️ METADATA > Convert ICC Profile to sRGB
[44] 🗂️ METADATA > Back to Main Menu
[45] 🔍 COMPARISON > Create Comparison Images
[46] 🔍 COMPARISON > Create GIF Comparison
[47] 🔍 COMPARISON > Compare Folders
[48] 🔍 COMPARISON > Back to Main Menu
[49] 📝 BATCH RENAME
[50] 📁 CONFIG > Add Config File
[51] 📁 CONFIG > Load Config File
[52] 📁 CONFIG > View Config Info
[53] 📁 CONFIG > Validate HQ/LQ Dataset from Config
[54] 📁 CONFIG > Validate Val Dataset HQ/LQ Pair
[55] 📁 CONFIG > Run wtp_dataset_destroyer
[56] 📁 CONFIG > Edit .hcl config file
[57] 📁 CONFIG > Run traiNNer-redux
[58] 📁 CONFIG > Edit .yml config file
[59] 📁 CONFIG > List/Run Upscale with Model
[60] 📁 CONFIG > Back to Main Menu
[61] ⚙️ SETTINGS
[62] 📦 COMPRESS IMAGES
[63] 📦 COMPRESS DIRECTORY
[64] 🔗 LINKS > Community Links
[65] 🔗 LINKS > Personal Links
[66] 🔗 LINKS > Back
[67] 👤 USER PROFILE
[68] 📓 VIEW CHANGE/HISTORY LOG > View most recent log
[69] 📓 VIEW CHANGE/HISTORY LOG > Select a log to view
[70] 📓 VIEW CHANGE/HISTORY LOG > Return to main menu
[71] 🔧 CORRECT/CREATE HQ LQ PAIRING > Back to Main Menu
[72] 🔊 AUTOMATIC HQ/LQ PAIRING (FUZZY MATCHING) > Back to Main Menu
[73] 🗑️ VISUAL DUPLICATE & NEAR-DUPLICATE DETECTION > Back to Main Menu
[74] 🚪 EXIT
