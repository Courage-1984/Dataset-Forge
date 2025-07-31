[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Project Architecture

> **Who is this for?**  
> This guide is for contributors, advanced users, and anyone interested in the internal structure and flow of Dataset Forge.

---

## Directory Structure (High-Level)

- **dataset_forge/menus/**: UI layer (CLI menus, user interaction)
- **dataset_forge/actions/**: Business logic (core dataset/image operations)
- **dataset_forge/utils/**: Shared utilities (file ops, memory, parallelism, color, monitoring, etc.)
- **dataset_forge/dpid/**: Degradation Process Implementations (BasicSR, OpenMMLab, Phhofm, Umzi)
- **configs/**: Example and user configuration files
- **reports/**: Report templates for HTML/Markdown output
- **assets/**: Static assets
- **docs/**: Project documentation
- **tests/**: Unit & integration tests
- **tools/**: Developer/user utilities (static analysis, doc merging, env setup, troubleshooting)

---

## Core Architecture Diagram

```mermaid
flowchart TD
    A["CLI Entrypoint (main.py)"] --> B["Main Menu (menus/main_menu.py)"]
    B --> B1["Dataset Management Menu"]
    B --> B2["Analysis & Validation Menu"]
    B --> B3["Augmentation Menu"]
    B --> B4["CBIR Menu"]
    B --> B5["System Monitoring Menu"]
    B --> B6["Umzi's Dataset_Preprocessing Menu"]
    B --> B7["Settings, User Profile, Utilities"]
    B --> B8["Enhanced Metadata Menu"]
    B --> B9["Performance Optimization Menu"]
    B1 --> C1["dataset_forge/actions/dataset_actions.py"]
    B2 --> C2["analysis_actions.py, analysis_ops_actions.py"]
    B3 --> C3["augmentation_actions.py, tiling_actions.py"]
    B4 --> C4["cbir_actions.py, visual_dedup_actions.py"]
    B5 --> C5["monitoring.py, session_state.py"]
    B6 --> C6["umzi_dataset_preprocessing_actions.py"]
    B7 --> C7["settings_actions.py, user_profile_actions.py, ..."]
    B8 --> C8["enhanced_metadata_actions.py"]
    B9 --> C9["performance_optimization_menu.py"]
    C1 --> D["Utils (file_utils, image_ops, memory_utils, ...)"]
    C2 --> D
    C3 --> D
    C4 --> D
    C5 --> D
    C6 --> D
    C7 --> D
    C8 --> D
    C9 --> G
    D --> E["DPID Implementations (dpid/)"]
    E --> F
    E --> E1["Umzi DPID (pepedpid)"]
    D --> F["External Libraries"]
    E --> F
    subgraph "Performance Optimization Utils"
      G1["gpu_acceleration.py"]
      G2["distributed_processing.py"]
      G3["sample_prioritization.py"]
      G4["pipeline_compilation.py"]
    end
    G --> G1
    G --> G2
    G --> G3
    G --> G4
    G1 --> F
    G2 --> F
    G3 --> F
    G4 --> F
    subgraph "Data & Config"
      H1["configs/"]
      H2["reports/"]
      H3["assets/"]
    end
    D --> H1
    D --> H2
    D --> H3
    E --> H1
    E --> H2
    E --> H3
    F --> H1
    F --> H2
    F --> H3
    G --> H1
    G --> H2
    G --> H3
```

---

## Key Modules

- **Menus:** All CLI and user interaction logic. Each menu is modular and uses a robust loop pattern.
- **Actions:** All business logic and core dataset/image operations. Each action is testable and exposed via public APIs.
- **Utils:** Shared utilities for file operations, memory management, parallelism, color schemes, and monitoring.
- **DPID:** Multiple degradation process implementations for HQ/LQ pair generation.

## Menu System Architecture

Dataset Forge uses a standardized menu system with the following characteristics:

### Menu Structure

- **Hierarchical Organization**: Menus are organized in a tree structure with clear parent-child relationships
- **Standardized Pattern**: All menus follow the key-based pattern documented in `.cursorrules`
- **Lazy Loading**: Menu functions are loaded on-demand for fast CLI responsiveness
- **Global Commands**: All menus support help, quit, and navigation commands

### Menu Auditing

The menu system includes comprehensive auditing capabilities:

- **Automatic Discovery**: The menu auditing tool (`tools/log_current_menu.py`) automatically discovers all menu files
- **Path Input Detection**: Identifies menus requiring user input to prevent infinite exploration
- **Analysis Depth**: Configurable exploration depth (default: 4 levels)
- **Reporting**: Generates detailed analysis reports with statistics and recommendations

### Menu Files Location

- **Primary Location**: `dataset_forge/menus/` - Contains all menu implementation files
- **Analysis Output**: `menu_system/` - Contains generated menu analysis reports
- **Configuration**: Menu behavior is controlled by settings in the auditing tool

---

## Specialized Diagrams

<details>
<summary><strong>Caching System Architecture</strong></summary>

```mermaid
flowchart TD
    A[Function Call] --> B{Smart Cache Detection}
    B -->|Model Functions| C[Model Cache]
    B -->|Extract/Compute| D[Disk Cache]
    B -->|Other Functions| E[In-Memory Cache]
    C --> F[TTL + CUDA Management]
    D --> G[Persistent Storage + Compression]
    E --> H[LRU + Statistics]
    F --> I[Cache Management Menu]
    G --> I
    H --> I
    I --> J[Statistics, Validation, Repair, Warmup]
```

</details>

<details>
<summary><strong>Dataset Health Scoring Workflow</strong></summary>

```mermaid
graph LR
A[Input Dataset] --> B[Basic Validation]
B --> C[Quality Metrics]
C --> D[Consistency Checks]
D --> E[Compliance Scan]
E --> F{Health Score}
F -->|>90| G[✅ Production Ready]
F -->|70-90| H[⚠️ Needs Improvement]
F -->|<70| I[❌ Unusable]
```

</details>

---

## See Also

- [Features](features.md)
- [Usage Guide](usage.md)
- [Advanced Features](advanced.md)
- [Troubleshooting](troubleshooting.md)
- [Style Guide](style_guide.md)
