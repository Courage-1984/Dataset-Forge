[← Back to README](../README.md) | [↑ Table of Contents](#dataset-forge-full-documentation) | [→ Next Section](getting_started.md)

---


# Dataset Forge Full Documentation

---

## Index

- [📚 Dataset Forge Documentation Home](#dataset-forge-documentation-home)
  - [📖 Table of Contents](#table-of-contents)
  - [👤 Who is this documentation for?](#who-is-this-documentation-for)
  - [🗺️ Next Steps](#next-steps)

## Getting Started

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [First Run](#first-run)
  - [Special Installation Notes](#special-installation-notes)
  - [Need Help?](#need-help)
  - [See Also](#see-also)

## Features

- [Features (tl;dr)](#features-tldr)
- [Feature Overview](#feature-overview)
  - [⚙️ Core & Configuration](#core-configuration)
  - [📂 Dataset Management](#dataset-management)
  - [🔍 Analysis & Validation](#analysis-validation)
  - [✨ Image Processing & Augmentation](#image-processing-augmentation)
  - [🚀 Performance & Optimization](#performance-optimization)
  - [🛠️ Utilities](#utilities)
  - [🧪 Testing & Developer Tools](#testing-developer-tools)
  - [🎉 Comprehensive Project Completion Status](#comprehensive-project-completion-status)
    - [**Menu System Improvement Plan - FULLY COMPLETED ✅**](#menu-system-improvement-plan-fully-completed)
      - [**Phase 1: Critical Fixes ✅ COMPLETED**](#phase-1-critical-fixes-completed)
      - [**Phase 2: Menu Organization ✅ COMPLETED**](#phase-2-menu-organization-completed)
      - [**Phase 3: User Experience ✅ COMPLETED**](#phase-3-user-experience-completed)
      - [**Phase 4: Performance & Technical ✅ COMPLETED**](#phase-4-performance-technical-completed)
      - [**Phase 5: Testing & Documentation ✅ COMPLETED**](#phase-5-testing-documentation-completed)
    - [**Recent Critical Fixes & Improvements**](#recent-critical-fixes-improvements)
      - [**Test System Optimization ✅ COMPLETED**](#test-system-optimization-completed)
      - [**Performance Enhancements ✅ COMPLETED**](#performance-enhancements-completed)
    - [**Final Achievement Statistics**](#final-achievement-statistics)
  - [🎨 Menu System Excellence](#menu-system-excellence)
    - [**📊 Menu System Statistics**](#menu-system-statistics)
    - [**✅ Menu System Achievements - PROJECT COMPLETED SUCCESSFULLY**](#menu-system-achievements-project-completed-successfully)
    - [**🎯 Menu Organization**](#menu-organization)
- [Features (tl;dr)](#features-tldr)
- [Features (main menus)](#features-main-menus)
  - [⚙️ Core & Configuration](#core-configuration)
  - [📂 Dataset Management](#dataset-management)
    - [🧩 Umzi's Dataset_Preprocessing (PepeDP-powered, July 2025)](#umzis-dataset_preprocessing-pepedp-powered-july-2025)
  - [🔍 Analysis & Validation](#analysis-validation)
  - [✨ Image Processing & Augmentation](#image-processing-augmentation)
  - [🚀 Training & Inference](#training-inference)
  - [🛠️ Utilities](#utilities)
  - [🎨 Catppuccin Mocha Theming Consistency (NEW August 2025)](#catppuccin-mocha-theming-consistency-new-august-2025)
- [Basic analysis](#basic-analysis)
- [Save report to specific location](#save-report-to-specific-location)
- [Verbose output with detailed results](#verbose-output-with-detailed-results)
- [Through tools launcher](#through-tools-launcher)
  - [⚙️ System & Settings](#system-settings)
  - [🔗 Links](#links)
  - [🩺 System Monitoring & Health](#system-monitoring-health)
    - [**Cleanup & Optimization Features**](#cleanup-optimization-features)
  - [🚀 Performance Optimization (NEW July 2025)](#performance-optimization-new-july-2025)
    - [**Performance Optimization Menu**](#performance-optimization-menu)
    - [**Integration Benefits**](#integration-benefits)
  - [⚡ Enhanced Caching System (UPDATED July 2025)](#enhanced-caching-system-updated-july-2025)
    - [**Core Caching Strategies**](#core-caching-strategies)
    - [**Advanced Features**](#advanced-features)
    - [**Cache Management Menu**](#cache-management-menu)
    - [**Automatic Integration**](#automatic-integration)
    - [**Benefits**](#benefits)
    - [**Usage Examples**](#usage-examples)
- [Simple in-memory caching with TTL](#simple-in-memory-caching-with-ttl)
- [Model caching for expensive operations](#model-caching-for-expensive-operations)
- [Smart auto-selection](#smart-auto-selection)
- [Features (expanded/misc)](#features-expandedmisc)
  - [🧪 Comprehensive Test Suite (Updated July 2025)](#comprehensive-test-suite-updated-july-2025)
  - [🔍 Comprehensive Static Analysis Tool (Updated July 2025)](#comprehensive-static-analysis-tool-updated-july-2025)
    - [**Enhanced Analysis Capabilities**](#enhanced-analysis-capabilities)
    - [**Advanced Features**](#advanced-features)
    - [**Usage**](#usage)
- [Run comprehensive analysis (all checks)](#run-comprehensive-analysis-all-checks)
- [Run specific analysis types](#run-specific-analysis-types)
- [View detailed results](#view-detailed-results)
    - [**Output Files**](#output-files)
    - [**Analysis Types**](#analysis-types)
    - [**Integration with Development Workflow**](#integration-with-development-workflow)
    - [**Requirements**](#requirements)
  - [Testing & Validation](#testing-validation)
  - [🧑‍💻 Developer Tools: Static Analysis & Code Quality](#developer-tools-static-analysis-code-quality)
  - [🛠️ Utility Scripts (tools/)](#utility-scripts-tools)
- [🩺 Dataset Health Scoring (NEW July 2025)](#dataset-health-scoring-new-july-2025)
- [🔊 Project Sounds & Audio Feedback](#project-sounds-audio-feedback)
  - [Audio System Architecture](#audio-system-architecture)
  - [Audio Files](#audio-files)
  - [Audio System Features](#audio-system-features)
  - [Audio Usage](#audio-usage)
- [Play audio with automatic fallback handling](#play-audio-with-automatic-fallback-handling)
  - [Audio System Benefits](#audio-system-benefits)
  - [🎨 Comprehensive Emoji System](#comprehensive-emoji-system)
    - [Emoji System Features](#emoji-system-features)
    - [Emoji Categories](#emoji-categories)
    - [Emoji Usage Examples](#emoji-usage-examples)
- [Get description for any emoji](#get-description-for-any-emoji)
- [Find emojis by description](#find-emojis-by-description)
- [Context-aware validation](#context-aware-validation)
- [Smart suggestions](#smart-suggestions)
- [Usage analysis](#usage-analysis)
    - [Emoji System Benefits](#emoji-system-benefits)
  - [🖥️ User Experience and CLI Features](#user-experience-and-cli-features)
  - [🖼️ Visual Deduplication (UPDATED December 2024)](#visual-deduplication-updated-december-2024)
    - [**Major Optimizations (December 2024)**](#major-optimizations-december-2024)
      - [**🚀 Performance Improvements**](#performance-improvements)
      - [**🛠️ Technical Optimizations**](#technical-optimizations)
      - [**🔧 Memory Management**](#memory-management)
      - [**📊 Results & Performance**](#results-performance)
    - [**Workflow Options**](#workflow-options)
      - [**1. CLIP Embedding (Fast, Semantic)**](#1-clip-embedding-fast-semantic)
      - [**2. LPIPS (Slow, Perceptual)**](#2-lpips-slow-perceptual)
    - [**Technical Implementation**](#technical-implementation)
      - [**Chunked Processing Architecture**](#chunked-processing-architecture)
- [Automatic chunk size calculation based on dataset size](#automatic-chunk-size-calculation-based-on-dataset-size)
- [Sequential chunk processing with memory cleanup](#sequential-chunk-processing-with-memory-cleanup)
      - [**Memory Management Strategy**](#memory-management-strategy)
      - [**Error Handling & Fallbacks**](#error-handling-fallbacks)
    - [**Usage Examples**](#usage-examples)
      - [**Basic Usage**](#basic-usage)
- [Navigate to Visual Deduplication](#navigate-to-visual-deduplication)
- [Select workflow](#select-workflow)
- [Enter folder path](#enter-folder-path)
- [Select method](#select-method)
- [Set max images (optional)](#set-max-images-optional)
      - [**Expected Output**](#expected-output)
    - [**Performance Metrics**](#performance-metrics)
    - [**Troubleshooting**](#troubleshooting)
      - [**Common Issues & Solutions**](#common-issues-solutions)
    - [**Advanced Configuration**](#advanced-configuration)
      - [**Chunk Size Optimization**](#chunk-size-optimization)
- [Automatic optimization based on system resources](#automatic-optimization-based-on-system-resources)
- [Manual override if needed](#manual-override-if-needed)
      - [**Memory Management**](#memory-management)
- [Automatic memory cleanup](#automatic-memory-cleanup)
- [Manual cleanup](#manual-cleanup)
    - [**Integration Benefits**](#integration-benefits)
    - [**Future Enhancements**](#future-enhancements)
  - [🔍 Fuzzy Matching De-duplication (NEW - December 2024)](#fuzzy-matching-de-duplication-new-december-2024)
    - [**Key Features**](#key-features)
    - [**Hash Algorithms**](#hash-algorithms)
    - [**Usage Example**](#usage-example)
- [Navigate to Fuzzy Matching De-duplication](#navigate-to-fuzzy-matching-de-duplication)
- [Select operation](#select-operation)
- [Enter folder path](#enter-folder-path)
- [Choose hash methods](#choose-hash-methods)
- [Set thresholds](#set-thresholds)
- [Choose operation mode](#choose-operation-mode)
      - [**Expected Output**](#expected-output)
    - [**Performance Characteristics**](#performance-characteristics)
    - [**Threshold Guidelines**](#threshold-guidelines)
      - [**Conservative (High Accuracy)**](#conservative-high-accuracy)
      - [**Balanced (Recommended)**](#balanced-recommended)
      - [**Aggressive (More Duplicates)**](#aggressive-more-duplicates)
    - [**Integration Benefits**](#integration-benefits)
    - [**Best Practices**](#best-practices)
    - [**Performance Considerations**](#performance-considerations)
      - [**Memory Usage**](#memory-usage)
      - [**Processing Speed**](#processing-speed)
      - [**Accuracy vs Speed Trade-offs**](#accuracy-vs-speed-trade-offs)
    - [**Troubleshooting**](#troubleshooting)
      - [**Common Issues**](#common-issues)
      - [**Error Messages**](#error-messages)
    - [**Integration with Other Features**](#integration-with-other-features)
      - [**Visual De-duplication**](#visual-de-duplication)
      - [**File Hash De-duplication**](#file-hash-de-duplication)
      - [**ImageDedup**](#imagededup)
    - [**Technical Details**](#technical-details)
      - [**Hash Computation**](#hash-computation)
      - [**Memory Management**](#memory-management)
      - [**Error Handling**](#error-handling)
    - [**Future Enhancements**](#future-enhancements)
      - [**Planned Features**](#planned-features)
      - [**Performance Improvements**](#performance-improvements)
    - [**Dependencies**](#dependencies)

## Usage

- [Usage Guide](#usage-guide)
  - [Quick Reference](#quick-reference)
  - [Global Commands & Menu Navigation](#global-commands-menu-navigation)
    - [**Available Global Commands**](#available-global-commands)
    - [**Menu System Excellence**](#menu-system-excellence)
    - [**User Experience Features**](#user-experience-features)
    - [**Example Usage**](#example-usage)
- [...context-aware help screen appears with menu-specific information...](#context-aware-help-screen-appears-with-menu-specific-information)
- [Menu is automatically redrawn](#menu-is-automatically-redrawn)
- [Dataset Forge exits with full cleanup](#dataset-forge-exits-with-full-cleanup)
    - [**Technical Implementation**](#technical-implementation)
  - [Main Workflows](#main-workflows)
    - [📂 Dataset Management](#dataset-management)
    - [🔍 Analysis & Validation](#analysis-validation)
    - [✨ Augmentation & Processing](#augmentation-processing)
    - [🩺 Monitoring & Utilities](#monitoring-utilities)
    - [🧪 Testing & Developer Tools](#testing-developer-tools)
    - [🔍 Static Analysis Tool](#static-analysis-tool)
      - [**Quick Start**](#quick-start)
- [Run comprehensive analysis (all checks)](#run-comprehensive-analysis-all-checks)
- [Run specific analysis types](#run-specific-analysis-types)
- [View detailed results](#view-detailed-results)
      - [**Analysis Types**](#analysis-types)
      - [**Output Files**](#output-files)
      - [**Integration with Development**](#integration-with-development)
      - [**Requirements**](#requirements)
    - [🎨 Catppuccin Mocha Theming Consistency Checker](#catppuccin-mocha-theming-consistency-checker)
      - [**Quick Start**](#quick-start)
- [Basic analysis](#basic-analysis)
- [Save report to specific location](#save-report-to-specific-location)
- [Verbose output with detailed results](#verbose-output-with-detailed-results)
      - [**Analysis Types**](#analysis-types)
      - [**Output**](#output)
      - [**Integration with Development**](#integration-with-development)
      - [**Requirements**](#requirements)
    - [🔧 Enhanced Development with MCP Integration](#enhanced-development-with-mcp-integration)
- [Enhanced Development Routine](#enhanced-development-routine)
  - [⭐ BHI Filtering with Advanced CUDA Optimizations](#bhi-filtering-with-advanced-cuda-optimizations)
    - [**Overview**](#overview)
    - [**Key Features**](#key-features)
      - [**🚀 Advanced CUDA Optimizations**](#advanced-cuda-optimizations)
      - [**📁 Flexible File Actions**](#flexible-file-actions)
      - [**⚙️ Smart Processing Order**](#smart-processing-order)
    - [**Usage Workflow**](#usage-workflow)
    - [**Performance Optimizations**](#performance-optimizations)
      - [**Environment Variables** (automatically set in `run.bat`)](#environment-variables-automatically-set-in-runbat)
      - [**Automatic Optimizations**](#automatic-optimizations)
    - [**Threshold Guidelines**](#threshold-guidelines)
      - [**Conservative (Strict Filtering)**](#conservative-strict-filtering)
      - [**Moderate (Balanced)**](#moderate-balanced)
      - [**Aggressive (Minimal Filtering)**](#aggressive-minimal-filtering)
    - [**Troubleshooting**](#troubleshooting)
      - [**CUDA Memory Errors**](#cuda-memory-errors)
      - [**100% Filtering**](#100-filtering)
      - [**Performance Issues**](#performance-issues)
    - [**Example Output**](#example-output)
    - [**Advanced Configuration**](#advanced-configuration)
      - [**Custom Thresholds**](#custom-thresholds)
- [Custom thresholds](#custom-thresholds)
- [Run with custom thresholds](#run-with-custom-thresholds)
      - [**Preset Thresholds**](#preset-thresholds)
- [Use conservative preset](#use-conservative-preset)
  - [🔍 Fuzzy Matching De-duplication](#fuzzy-matching-de-duplication)
    - [**Quick Start**](#quick-start)
    - [**Hash Algorithms**](#hash-algorithms)
    - [**Threshold Guidelines**](#threshold-guidelines)
      - [**Conservative (High Accuracy)**](#conservative-high-accuracy)
      - [**Balanced (Recommended)**](#balanced-recommended)
      - [**Aggressive (More Duplicates)**](#aggressive-more-duplicates)
    - [**Example Workflow**](#example-workflow)
- [Navigate to Fuzzy Matching De-duplication](#navigate-to-fuzzy-matching-de-duplication)
- [Select operation](#select-operation)
- [Enter folder path](#enter-folder-path)
- [Choose hash methods (comma-separated)](#choose-hash-methods-comma-separated)
- [Set thresholds](#set-thresholds)
- [Choose operation mode](#choose-operation-mode)
      - [**Expected Output**](#expected-output)
    - [**Best Practices**](#best-practices)
    - [**Advanced Configuration**](#advanced-configuration)
      - [**Custom Hash Combinations**](#custom-hash-combinations)
- [Custom hash methods and thresholds](#custom-hash-methods-and-thresholds)
- [Run fuzzy deduplication](#run-fuzzy-deduplication)
      - [**HQ/LQ Paired Folders**](#hqlq-paired-folders)
- [For HQ/LQ paired folders](#for-hqlq-paired-folders)
    - [**Performance Considerations**](#performance-considerations)
      - [**Memory Usage Guidelines**](#memory-usage-guidelines)
      - [**Processing Speed Characteristics**](#processing-speed-characteristics)
      - [**Accuracy vs Speed Trade-offs**](#accuracy-vs-speed-trade-offs)
    - [**Troubleshooting**](#troubleshooting)
      - [**Common Issues and Solutions**](#common-issues-and-solutions)
      - [**Error Messages**](#error-messages)
    - [**Integration with Other Features**](#integration-with-other-features)
      - [**Visual De-duplication**](#visual-de-duplication)
      - [**File Hash De-duplication**](#file-hash-de-duplication)
      - [**ImageDedup**](#imagededup)
    - [**Technical Details**](#technical-details)
      - [**Hash Computation**](#hash-computation)
      - [**Memory Management**](#memory-management)
      - [**Error Handling**](#error-handling)
    - [**Dependencies**](#dependencies)
  - [Example: Running a Workflow](#example-running-a-workflow)
- [or](#or)
  - [Tips & Best Practices](#tips-best-practices)
  - [See Also](#see-also)

## Advanced

- [Advanced Features & Configuration](#advanced-features-configuration)
  - [Advanced Configuration](#advanced-configuration)
  - [Performance & Optimization](#performance-optimization)
- [Instead of: import torch, cv2, numpy as np](#instead-of-import-torch-cv2-numpy-as-np)
- [Function-level lazy imports](#function-level-lazy-imports)
- [Performance monitoring](#performance-monitoring)
- [Cache non-interactive functions](#cache-non-interactive-functions)
- [Cache menu context](#cache-menu-context)
- [Monitor cache performance](#monitor-cache-performance)
- [Optimize cache based on usage](#optimize-cache-based-on-usage)
- [Before Implementing Any Solution:](#before-implementing-any-solution)
- [1. Research current best practices](#1-research-current-best-practices)
- [2. Find specific implementation details](#2-find-specific-implementation-details)
- [3. Understand current project structure](#3-understand-current-project-structure)
- [4. Find relevant code examples](#4-find-relevant-code-examples)
- [Basic emoji operations](#basic-emoji-operations)
- [Enhanced features](#enhanced-features)
  - [Visual Deduplication Advanced Features](#visual-deduplication-advanced-features)
    - [**Technical Implementation: Visual Deduplication Optimization**](#technical-implementation-visual-deduplication-optimization)
      - [**Chunked Processing Architecture**](#chunked-processing-architecture)
      - [**Memory Management Strategy**](#memory-management-strategy)
      - [**Global Model Cache**](#global-model-cache)
- [Global model cache for multiprocessing](#global-model-cache-for-multiprocessing)
- [Initialize models at import time](#initialize-models-at-import-time)
      - [**FAISS Integration for Efficient Similarity Search**](#faiss-integration-for-efficient-similarity-search)
      - [**Optimized Similarity Matrix Computation**](#optimized-similarity-matrix-computation)
      - [**Error Handling and Fallbacks**](#error-handling-and-fallbacks)
      - [**Performance Monitoring and Optimization**](#performance-monitoring-and-optimization)
      - [**Process Pool Management**](#process-pool-management)
    - [**Advanced Configuration Options**](#advanced-configuration-options)
      - [**Custom Chunk Size Configuration**](#custom-chunk-size-configuration)
- [Configure custom chunk sizes for different scenarios](#configure-custom-chunk-sizes-for-different-scenarios)
      - [**Memory Threshold Configuration**](#memory-threshold-configuration)
- [Memory threshold configuration](#memory-threshold-configuration)
    - [**Performance Benchmarks**](#performance-benchmarks)
      - [**Processing Speed Comparison**](#processing-speed-comparison)
      - [**Memory Usage Comparison**](#memory-usage-comparison)
    - [**Integration with Other Features**](#integration-with-other-features)
      - [**Dataset Health Scoring Integration**](#dataset-health-scoring-integration)
      - [**Batch Processing Integration**](#batch-processing-integration)
    - [**Future Enhancements**](#future-enhancements)
      - [**GPU Acceleration**](#gpu-acceleration)
      - [**Real-time Progress Enhancement**](#real-time-progress-enhancement)
  - [Developer Patterns & Extending](#developer-patterns-extending)
  - [🎉 Project Completion Status](#project-completion-status)
    - [**Comprehensive Menu System Improvement Plan - FULLY COMPLETED ✅**](#comprehensive-menu-system-improvement-plan-fully-completed)
      - [**Phase 1: Critical Fixes ✅ COMPLETED**](#phase-1-critical-fixes-completed)
      - [**Phase 2: Menu Organization ✅ COMPLETED**](#phase-2-menu-organization-completed)
      - [**Phase 3: User Experience ✅ COMPLETED**](#phase-3-user-experience-completed)
      - [**Phase 4: Performance & Technical ✅ COMPLETED**](#phase-4-performance-technical-completed)
      - [**Phase 5: Testing & Documentation ✅ COMPLETED**](#phase-5-testing-documentation-completed)
    - [**Final Statistics**](#final-statistics)
    - [**Key Achievements**](#key-achievements)
    - [Global Command System Implementation](#global-command-system-implementation)
      - [**Core Implementation**](#core-implementation)
      - [**Technical Architecture**](#technical-architecture)
      - [**Menu Context Structure**](#menu-context-structure)
      - [**Standardized Menu Pattern**](#standardized-menu-pattern)
- [Activate virtual environment](#activate-virtual-environment)
- [Run the menu audit](#run-the-menu-audit)
- [Activate virtual environment](#activate-virtual-environment)
- [Basic analysis](#basic-analysis)
- [Save report to specific location](#save-report-to-specific-location)
- [Verbose output with detailed results](#verbose-output-with-detailed-results)
  - [Advanced Testing Patterns](#advanced-testing-patterns)
  - [Technical Deep Dives](#technical-deep-dives)
  - [MCP Integration & Enhanced Development](#mcp-integration-enhanced-development)
    - [**MCP Server Configuration**](#mcp-server-configuration)
    - [**Development Workflow Enhancements**](#development-workflow-enhancements)
      - [**Code Analysis Workflow**](#code-analysis-workflow)
- [Daily Development Routine](#daily-development-routine)
      - [**Research Integration Workflow**](#research-integration-workflow)
- [Weekly Research Routine](#weekly-research-routine)
    - [**Proposed Improvements**](#proposed-improvements)
      - [**Enhanced Documentation System**](#enhanced-documentation-system)
      - [**Automated Research Updates**](#automated-research-updates)
      - [**Enhanced Dataset Discovery**](#enhanced-dataset-discovery)
      - [**Community Integration Hub**](#community-integration-hub)
    - [**Technical Implementation**](#technical-implementation)
      - [**MCP Integration Class Example**](#mcp-integration-class-example)
      - [**Automated Research Pipeline**](#automated-research-pipeline)
    - [**Success Metrics**](#success-metrics)
  - [See Also](#see-also)

## Architecture

- [Project Architecture](#project-architecture)
  - [Directory Structure (High-Level)](#directory-structure-high-level)
  - [Core Architecture Diagram](#core-architecture-diagram)
  - [Key Modules](#key-modules)
  - [Menu System Architecture](#menu-system-architecture)
    - [Menu Structure](#menu-structure)
    - [Menu Auditing](#menu-auditing)
    - [Menu Files Location](#menu-files-location)
  - [Specialized Diagrams](#specialized-diagrams)
  - [See Also](#see-also)

## Contributing

- [Contributing](#contributing)
  - [How to Contribute](#how-to-contribute)
  - [Development Guidelines](#development-guidelines)
  - [Doc Maintenance](#doc-maintenance)
  - [Static Analysis & Code Quality](#static-analysis-code-quality)
  - [Menu System Development](#menu-system-development)
    - [Global Command System Development](#global-command-system-development)
    - [MCP Integration Development (MANDATORY)](#mcp-integration-development-mandatory)
      - [**Available MCP Servers**](#available-mcp-servers)
      - [**MCP Tool Usage Patterns (MANDATORY)**](#mcp-tool-usage-patterns-mandatory)
        - [Before Implementing Any Solution:](#before-implementing-any-solution)
        - [When Debugging Issues:](#when-debugging-issues)
        - [When Adding New Features:](#when-adding-new-features)
      - [**MCP Integration Requirements**](#mcp-integration-requirements)
      - [**MCP Tool Usage Examples**](#mcp-tool-usage-examples)
- [Example workflow for adding a new feature:](#example-workflow-for-adding-a-new-feature)
- [1. Research current best practices](#1-research-current-best-practices)
- [2. Find specific implementation details](#2-find-specific-implementation-details)
- [3. Understand current project structure](#3-understand-current-project-structure)
- [4. Find relevant code examples](#4-find-relevant-code-examples)
      - [**Research Integration**](#research-integration)
      - [**Code Quality Enhancement**](#code-quality-enhancement)
    - [Menu Auditing Workflow](#menu-auditing-workflow)
    - [Menu Auditing Features](#menu-auditing-features)
  - [See Also](#see-also)

## Style Guide

- [Dataset Forge Style Guide](#dataset-forge-style-guide)
  - [Critical UI/UX Rule: Catppuccin Mocha Color Scheme](#critical-uiux-rule-catppuccin-mocha-color-scheme)
    - [Enforcement Checklist](#enforcement-checklist)
  - [General Principles](#general-principles)
  - [Project Architecture & Modularity](#project-architecture-modularity)
  - [Coding Standards](#coding-standards)
  - [Memory, Parallelism, Progress, and Color/UI](#memory-parallelism-progress-and-colorui)
  - [Menu & Workflow Patterns](#menu-workflow-patterns)
  - [Error Handling & Logging](#error-handling-logging)
  - [Testing & Validation](#testing-validation)
  - [Caching & Performance](#caching-performance)
  - [Documentation Requirements](#documentation-requirements)
  - [Dependency & Security](#dependency-security)
  - [Emoji System Guidelines](#emoji-system-guidelines)
    - [Emoji Usage in Menus and UI](#emoji-usage-in-menus-and-ui)
    - [Emoji Best Practices](#emoji-best-practices)
- [Good: Context-appropriate emojis](#good-context-appropriate-emojis)
- [Good: Context-aware validation](#good-context-aware-validation)
- [Avoid: Too many emojis or inappropriate context](#avoid-too-many-emojis-or-inappropriate-context)
    - [Emoji Accessibility](#emoji-accessibility)
    - [Emoji Performance](#emoji-performance)
  - [MCP Integration Requirements (MANDATORY)](#mcp-integration-requirements-mandatory)
    - [MCP Tool Usage Priority](#mcp-tool-usage-priority)
    - [MCP Tool Usage Patterns](#mcp-tool-usage-patterns)
      - [Before Implementing Any Solution:](#before-implementing-any-solution)
      - [When Debugging Issues:](#when-debugging-issues)
      - [When Adding New Features:](#when-adding-new-features)
    - [MCP Integration Requirements](#mcp-integration-requirements)
    - [MCP Tool Usage Examples](#mcp-tool-usage-examples)
- [Example workflow for adding a new feature:](#example-workflow-for-adding-a-new-feature)
- [1. Research current best practices](#1-research-current-best-practices)
- [2. Find specific implementation details](#2-find-specific-implementation-details)
- [3. Understand current project structure](#3-understand-current-project-structure)
- [4. Find relevant code examples](#4-find-relevant-code-examples)
  - [Final Reminders](#final-reminders)
  - [See Also](#see-also)

## Troubleshooting

- [Troubleshooting](#troubleshooting)
  - [Installation & Environment Issues](#installation-environment-issues)
  - [Common CLI & Workflow Issues](#common-cli-workflow-issues)
  - [Test Suite & Developer Tools](#test-suite-developer-tools)
  - [Metadata & Caching Issues](#metadata-caching-issues)
  - [DPID & External Tools](#dpid-external-tools)
  - [Steganography Tools (zsteg, steghide)](#steganography-tools-zsteg-steghide)
    - [ZSTEG Executable Issues](#zsteg-executable-issues)
- [Remove old OCRA and install OCRAN](#remove-old-ocra-and-install-ocran)
- [Create zsteg CLI wrapper](#create-zsteg-cli-wrapper)
- [Create file: zsteg_cli.rb](#create-file-zsteg_clirb)
- [!/usr/bin/env ruby](#usrbinenv-ruby)
- [Build executable with OCRAN](#build-executable-with-ocran)
- [Test the executable](#test-the-executable)
- [Create zsteg_wrapper.ps1](#create-zsteg_wrapperps1)
- [Attempts OCRA executable first, falls back to gem-installed zsteg](#attempts-ocra-executable-first-falls-back-to-gem-installed-zsteg)
  - [Audio System Issues](#audio-system-issues)
    - [CLI Hanging During Exit](#cli-hanging-during-exit)
    - [Audio Not Playing](#audio-not-playing)
    - [Audio Library Conflicts](#audio-library-conflicts)
    - [Audio System Error Messages](#audio-system-error-messages)
    - [Audio System Best Practices](#audio-system-best-practices)
  - [Visual Deduplication Issues](#visual-deduplication-issues)
    - [CUDA Multiprocessing Errors](#cuda-multiprocessing-errors)
    - [Memory Errors (Paging File Too Small)](#memory-errors-paging-file-too-small)
    - [Empty Embedding Errors](#empty-embedding-errors)
    - [Model Loading Issues](#model-loading-issues)
    - [Performance Issues](#performance-issues)
    - [FAISS Integration Issues](#faiss-integration-issues)
- [or](#or)
    - [Process Pool Management](#process-pool-management)
    - [Image Loading Issues](#image-loading-issues)
    - [Expected Behavior](#expected-behavior)
    - [Best Practices](#best-practices)
  - [Fuzzy Deduplication Issues](#fuzzy-deduplication-issues)
    - [Common Problems](#common-problems)
    - [Performance Optimization](#performance-optimization)
    - [Best Practices for Fuzzy Deduplication](#best-practices-for-fuzzy-deduplication)
    - [Getting Help](#getting-help)
  - [FAQ](#faq)
  - [See Also](#see-also)

## Todo

- [TODO / Planned Features](#todo-planned-features)
  - [🚀 High Priority Features](#high-priority-features)
    - [Core System Enhancements](#core-system-enhancements)
    - [Advanced Data Processing](#advanced-data-processing)
    - [Performance & Optimization](#performance-optimization)
  - [🔧 Development & Infrastructure](#development-infrastructure)
    - [Code Quality & Testing](#code-quality-testing)
    - [External Tool Integration](#external-tool-integration)
    - [Documentation & User Experience](#documentation-user-experience)
  - [🎯 Specific Feature Implementations](#specific-feature-implementations)
    - [Image Processing & Analysis](#image-processing-analysis)
    - [System Architecture](#system-architecture)
    - [Deduplication Enhancements](#deduplication-enhancements)
  - [✅ Completed Features](#completed-features)
    - [Core System Features](#core-system-features)
    - [Critical Bug Fixes](#critical-bug-fixes)
    - [Advanced Features](#advanced-features)
  - [📋 Future Considerations](#future-considerations)
    - [Long-term Goals](#long-term-goals)
    - [Research & Investigation](#research-investigation)
  - [🔄 Maintenance & Updates](#maintenance-updates)
    - [Regular Tasks](#regular-tasks)
    - [Quality Assurance](#quality-assurance)
  - [❓ Unsorted](#unsorted)

## Special Installation

- [Special Installation Instructions](#special-installation-instructions)
  - [1. PyTorch with CUDA (GPU Acceleration)](#1-pytorch-with-cuda-gpu-acceleration)
  - [2. VapourSynth & getnative](#2-vapoursynth-getnative)
    - [Method 1: Windows (Quick)](#method-1-windows-quick)
    - [Method 2: Windows (Better; but _TRICKY_...)](#method-2-windows-better-but-_tricky_)
    - [Method 3: Windows (try building `getnative.exe` yourself)](#method-3-windows-try-building-getnativeexe-yourself)
  - [3. python-magic (for `Enhanced Directory Tree`)](#3-python-magic-for-enhanced-directory-tree)
  - [4. Using resdet for Native Resolution Detection](#4-using-resdet-for-native-resolution-detection)
    - [Method 1: Windows (WSL - Recommended for CLI Integration)](#method-1-windows-wsl-recommended-for-cli-integration)
    - [Method 2: Windows (MSYS2 MINGW64 Shell)](#method-2-windows-msys2-mingw64-shell)
    - [Method 3: Windows (Windows pre-build binary)](#method-3-windows-windows-pre-build-binary)
    - [Usage in Dataset Forge](#usage-in-dataset-forge)
  - [5. Advanced Metadata Operations with ExifTool](#5-advanced-metadata-operations-with-exiftool)
    - [Method 1.1: Windows (Quick)](#method-11-windows-quick)
    - [Method 1.2: Windows (Better)](#method-12-windows-better)
    - [Method 2: Windows (Chocolatey)](#method-2-windows-chocolatey)
  - [6. Metadata Strip + Lossless png compression with Oxipng](#6-metadata-strip-lossless-png-compression-with-oxipng)
    - [Method 1.1: Windows (Quick)](#method-11-windows-quick)
    - [Method 1.2: Windows (Better)](#method-12-windows-better)
  - [7. Steganography Integration for zsteg and Steghide](#7-steganography-integration-for-zsteg-and-steghide)
    - [zsteg installation (Windows)](#zsteg-installation-windows)
      - [Method 1: Gem Installation (Recommended)](#method-1-gem-installation-recommended)
      - [Method 2.1: Standalone Executable (Quick)](#method-21-standalone-executable-quick)
      - [Method 2.2: Standalone Executable (Advanced)](#method-22-standalone-executable-advanced)
    - [steghide installation](#steghide-installation)
      - [Method 1.1: Windows (Quick)](#method-11-windows-quick)
      - [Method 1.2: Windows (Better)](#method-12-windows-better)
  - [8. ffmpeg integration](#8-ffmpeg-integration)
    - [Method 1.1: Windows (Quick)](#method-11-windows-quick)
    - [Method 1.2: Windows (Better)](#method-12-windows-better)
    - [Method 1.3: Windows (`Method 1.1` but download first)](#method-13-windows-method-11-but-download-first)
  - [9. Special mass implementation of above^^](#9-special-mass-implementation-of-above)
    - [Step 1: Windows binary dump](#step-1-windows-binary-dump)
    - [Step 2: Windows dll dump](#step-2-windows-dll-dump)
    - [Step 3: Test the implementations](#step-3-test-the-implementations)
  - [10. CUDA & GPU Performance Steps](#10-cuda-gpu-performance-steps)
    - [Step 1: Always use ./run.bat/](#step-1-always-use-runbat)
    - [Step 2: Be Sure your `venv312` has cuda torch installed](#step-2-be-sure-your-venv312-has-cuda-torch-installed)
    - [Step 3: Windows Pagefile](#step-3-windows-pagefile)
    - [Step 4: NVIDIA Control Panel](#step-4-nvidia-control-panel)

## Changelog

- [Changelog](#changelog)
  - [[Unreleased]](#unreleased)
    - [🎨 Comprehensive Menu System Improvement (August 2025)](#comprehensive-menu-system-improvement-august-2025)
    - [🔍 Fuzzy Matching De-duplication Feature (December 2024)](#fuzzy-matching-de-duplication-feature-december-2024)
    - [⭐ BHI Filtering Advanced CUDA Optimizations (August 2025)](#bhi-filtering-advanced-cuda-optimizations-august-2025)
    - [🔗 MCP Integration Implementation (August 2025)](#mcp-integration-implementation-august-2025)
    - [🔊 Audio System Investigation & Robust Multi-Library Implementation (August 2025)](#audio-system-investigation-robust-multi-library-implementation-august-2025)
    - [🔧 zsteg.exe Standalone Executable Solution (August 2025)](#zstegexe-standalone-executable-solution-august-2025)
    - [🎨 Catppuccin Mocha Theming Consistency Checker (August 2025)](#catppuccin-mocha-theming-consistency-checker-august-2025)
    - [⚡ CLI Optimization & Lazy Import System Integration (August 2025)](#cli-optimization-lazy-import-system-integration-august-2025)
    - [🧹 Cleanup & Optimization Tools (July 2025)](#cleanup-optimization-tools-july-2025)
    - [🌐 Global Command System & Comprehensive Help Documentation (July 2025)](#global-command-system-comprehensive-help-documentation-july-2025)
    - [🔄 Resave Images Integration (July 2025)](#resave-images-integration-july-2025)
    - [🧩 PepeDP-powered Umzi's Dataset_Preprocessing Integration (July 2025)](#pepedp-powered-umzis-dataset_preprocessing-integration-july-2025)
    - [🚀 Performance Optimization Suite (NEW July 2025)](#performance-optimization-suite-new-july-2025)
      - [**GPU Acceleration**](#gpu-acceleration)
      - [**Distributed Processing**](#distributed-processing)
      - [**Intelligent Sample Prioritization**](#intelligent-sample-prioritization)
      - [**Pipeline Compilation**](#pipeline-compilation)
      - [**Performance Optimization Menu**](#performance-optimization-menu)
      - [**Comprehensive Testing**](#comprehensive-testing)
      - [**Dependencies**](#dependencies)
    - [🔧 Technical Improvements](#technical-improvements)
    - [📚 Documentation](#documentation)
    - [🆕 DPID: Umzi's DPID (pepedpid) Integration (July 2025)](#dpid-umzis-dpid-pepedpid-integration-july-2025)
  - [[July 2025]](#july-2025)

## License

- [License](#license)
---

# Index

# 📚 Dataset Forge Documentation Home

Welcome to the official documentation for **Dataset Forge**!

Dataset Forge is a modular Python CLI tool for managing, analyzing, and transforming image datasets, with a focus on high/low quality pairs for super-resolution and machine learning.

---

## 📖 Table of Contents

- [Getting Started](getting_started.md)  
  _Install, setup, and your first run_
- [Features (tl;dr)](features.md)  
  _Quick overview of what Dataset Forge can do_
- [Usage Guide](usage.md)  
  _How to use the CLI, workflows, and common tasks_
- [Advanced Features & Configuration](advanced.md)  
  _Power user options, custom pipelines, performance_
- [Troubleshooting & FAQ](troubleshooting.md)  
  _Common issues, platform-specific notes, and FAQ_
- [Special Installation Instructions](special_installation.md)  
  _CUDA, cuDNN, VapourSynth, and other dependencies_
- [Project Architecture](architecture.md)  
  _How the codebase is organized and how modules interact_
- [Style Guide](style_guide.md)  
  _Coding, docstring, and test standards for contributors_
- [Contributing](contributing.md)  
  _How to contribute, run tests, and submit PRs_
- [Changelog](changelog.md)  
  _Release history and notable changes_
- [License](license.md)  
  _Project license details_
- [Advanced Features](advanced.md)  
  _MCP integration, global command system, and enhanced development workflows_

---

## 👤 Who is this documentation for?

- **New Users:** Start with [Getting Started](getting_started.md) and [Features](features.md).
- **Advanced Users:** See [Advanced Features](advanced.md) and [Architecture](architecture.md).
- **Contributors:** Read the [Contributing Guide](contributing.md) and [Style Guide](style_guide.md).

---

## 🗺️ Next Steps

- Not sure where to begin? Try the [Quickstart](getting_started.md).
- Looking for a specific feature? Check the [Features](features.md) or [Usage Guide](usage.md).
- Having trouble? Visit [Troubleshooting](troubleshooting.md).

---

> For the latest updates and roadmap, see the [Changelog](changelog.md) or the project [README](../README.md).

---

# Getting Started

# Getting Started

> **UI/UX Note:**  
> All CLI output in Dataset Forge uses the Catppuccin Mocha color scheme for a consistent, visually appealing experience. All prompts, menus, and progress bars are styled using the centralized color utilities.

Welcome to Dataset Forge!  
This guide will help you install and launch Dataset Forge for the first time.

---

## Prerequisites

- **Python**: 3.12+ (see [requirements.txt](../requirements.txt))
- **OS**: Windows (primary)
- **CUDA/cuDNN**: For GPU acceleration (see [Special Installation](special_installation.md))
- **RAM**: 8GB+ (16GB+ recommended)
- **Storage**: SSD recommended

---

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Courage-1984/Dataset-Forge.git
   cd Dataset-Forge
   ```

2. **Set up the environment:**

   **Option A: Automated Installation (Recommended)**

   ```bash
   # Windows (easiest)
   install.bat
   # or
   tools\install.bat

   # Or manually
   py -3.12 -m venv venv312
   venv312\Scripts\activate
   python tools\install.py
   ```

   **Option B: Manual Installation**

   ```bash
   py -3.12 -m venv venv312
   venv312\Scripts\activate
   python -m pip install --upgrade pip setuptools wheel
   # Install the correct CUDA-enabled torch/torchvision/torchaudio first!
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   pip install -r requirements.txt
   pip install -e .
   ```

   **Option C: Using setup.py directly**

   ```bash
   py -3.12 -m venv venv312
   venv312\Scripts\activate
   python setup.py install
   ```

   > **Note:** For other CUDA versions, see [PyTorch Get Started](https://pytorch.org/get-started/locally/).

---

## First Run

```bash
./run.bat
OR
venv312\Scripts\activate
py main.py
OR
dataset-forge
```

---

## Special Installation Notes

- On Windows, `python-magic` requires extra DLLs.
- You must install VapourSynth before using [getnative](https://github.com/Infiziert90/getnative).
- You must compile/build [resdet](https://github.com/0x09/resdet) before using it.
- AND MORE;;;

- See [Special Installation Instructions](special_installation.md) for further details.

---

## Need Help?

- For common issues, see the [Troubleshooting Guide](troubleshooting.md).
- For advanced configuration, see [Advanced Features](advanced.md).

---

## See Also

- [Features](features.md)
- [Usage Guide](usage.md)
- [Advanced Features](advanced.md)
- [Project Architecture](architecture.md)

---

# Features

[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Features (tl;dr)

> **UI/UX Note:**  
> All CLI output in Dataset Forge uses the Catppuccin Mocha color scheme for a consistent, visually appealing experience. All prompts, menus, and progress bars are styled using the centralized color utilities.

- **🎨 Comprehensive Menu System**: 201 total menus with perfect theming compliance, standardized patterns, and enhanced user experience
- **📂 Advanced Dataset Management**: Consolidated workflows for creation, organization, and optimization
- **🔍 Intelligent Analysis & Validation**: Multi-algorithm quality scoring and comprehensive health assessment
- **✨ Enhanced Image Processing**: Advanced augmentation pipelines with GPU acceleration
- **🛠️ Unified Utilities**: Consolidated deduplication, compression, and comparison tools
- **🚀 Performance Optimization**: Distributed processing, memory management, and real-time monitoring
- **🎯 User Experience Excellence**: Context-aware help, comprehensive documentation, and intuitive navigation
- **🧪 Developer Tools**: Comprehensive testing, static analysis, and quality assurance tools
- [See Usage Guide](usage.md) for examples and workflows

---

# Feature Overview

## ⚙️ Core & Configuration

- **🌐 Global Command System**: Context-aware help (`help`, `h`, `?`) and instant quit (`quit`, `exit`, `q`) from any menu
- **🎨 Perfect Theming Compliance**: 0 theming issues with 4,774 centralized print usages across all menus
- **📚 Comprehensive Help System**: Advanced help system with troubleshooting, feature-specific guidance, and quick reference
- **🔧 External Tool Integration**: WTP Dataset Destroyer, traiNNer-redux, getnative, resdet, and more
- **📦 Model Management**: List, select, download, and run upscaling with trained models
- **⚙️ Multi-format Config Support**: JSON, YAML, HCL configuration files
- **👤 User Profiles**: Favorites, presets, and quick access paths for personalized workflows

## 📂 Dataset Management

- **🎯 Consolidated Workflows**: Optimized menu hierarchy with logical progression and enhanced user experience
- **📊 Multiscale Dataset Generation**: Video frame extraction, image tiling, and batch processing
- **🔄 Dataset Operations**: Combine, split, shuffle, and randomize datasets with advanced controls
- **🔗 HQ/LQ Pair Management**: Manual/fuzzy pairing, scale correction, and batch alignment
- **🔍 Fuzzy Matching De-duplication**: Multi-algorithm perceptual hashing with configurable thresholds (pHash, dHash, aHash, wHash, Color Hash)
- **🎨 Visual Deduplication**: Advanced duplicate detection with CLIP embeddings and hash-based methods
- **📝 Batch Operations**: Renaming, orientation sorting, size filtering, and metadata management

## 🔍 Analysis & Validation

- Progressive validation suite for datasets and HQ/LQ pairs
- Automated quality scoring (NIQE, HyperIQA, IC9600, etc.)
- Corruption, misalignment, and outlier detection
- HTML/Markdown reporting with plots and sample images

## ✨ Image Processing & Augmentation

- Downsampling, cropping, flipping, rotating, shuffling, resaving
- Brightness, contrast, hue, saturation, HDR/SDR, grayscale
- Degradations: blur, noise, pixelate, dithering, sharpen, banding, etc.
- Advanced augmentation pipelines and recipe management
- Metadata scrubbing, ICC profile conversion, sketch/line art extraction

## 🚀 Performance & Optimization

- GPU-accelerated preprocessing and batch operations
- Distributed processing (Dask, Ray), multi-GPU support
- JIT compilation for performance-critical code
- Real-time analytics and auto-optimization
- **CLI Optimization**: Comprehensive lazy import system for 50-60% faster startup times

## 🛠️ Utilities

- **🔍 Consolidated De-duplication**: Unified menu combining fuzzy matching, visual deduplication, and hash-based methods
- **🗜️ Consolidated Compression**: Single menu for individual and directory compression with format optimization
- **📊 Enhanced Comparison Tools**: Image/gif comparison creation with advanced analysis features
- **🌳 Directory Tree Visualization**: Enhanced tree display with metadata and filtering options
- **📝 Batch Metadata Operations**: Extraction, editing, filtering, and anonymization with comprehensive controls
- **📊 System Monitoring**: Live resource usage, error summaries, health checks, and performance analytics
- **🎨 Comprehensive Emoji System**: 3,655+ emoji mappings with context-aware validation, smart suggestions, and usage analysis
- **🚀 Menu System Optimization**: Intelligent caching, lazy loading, and performance monitoring for optimal responsiveness
- **📊 Performance Monitoring**: Real-time metrics, cache statistics, and automated optimization tools
- **🎯 Enhanced User Experience**: Comprehensive visual feedback, error handling, and user interaction systems

## 🧪 Testing & Developer Tools

- **🧪 Comprehensive Test Suite**: Pytest-based testing with 100% coverage for all features
- **🔍 Static Analysis Tools**: Code quality, maintainability, and potential issue detection
- **📊 Menu Auditing Tool**: Comprehensive menu hierarchy analysis with 201 menus and improvement recommendations
- **🌐 Global Command Testing**: 71 tests covering all global command functionality with unit, integration, and edge case testing
- **🎨 Emoji Usage Checker**: Comprehensive emoji usage analysis and Unicode encoding validation
- **🎨 Theming Consistency Checker**: Perfect theming compliance validation with 0 issues across all menus
- **📈 Progress Tracking**: Comprehensive development tools for quality assurance and continuous improvement
- **🔧 Utility Scripts**: Environment setup, testing, documentation merging, and development workflow automation

---

## 🎉 Comprehensive Project Completion Status

### **Menu System Improvement Plan - FULLY COMPLETED ✅**

Dataset Forge has successfully completed a comprehensive transformation of its menu system, achieving all planned improvements across 5 phases with 100% success rate:

#### **Phase 1: Critical Fixes ✅ COMPLETED**
- **1,557 theming issues** resolved (100% reduction)
- **1,158 raw print statements** replaced with centralized utilities
- **366 missing Mocha imports** added
- **15 incorrect menu patterns** fixed
- **201 menus** now have comprehensive context coverage
- **Training & Inference menu** fully implemented

#### **Phase 2: Menu Organization ✅ COMPLETED**
- **Main menu structure** optimized with logical workflow ordering
- **Menu hierarchy** improved with better grouping and navigation
- **Duplicate functionality** consolidated into unified menus
- **Menu naming** enhanced with descriptive conventions
- **Menu flow** optimized with logical progression

#### **Phase 3: User Experience ✅ COMPLETED**
- **Menu descriptions** enhanced with comprehensive information
- **Help system** implemented with troubleshooting and feature-specific guidance
- **Emoji usage** optimized with context-aware selection
- **Visual indicators** added for progress and status feedback
- **Error handling** improved with user-friendly messages
- **User feedback** implemented with confirmation dialogs

#### **Phase 4: Performance & Technical ✅ COMPLETED**
- **Menu loading** optimized with intelligent caching
- **Lazy loading** enhanced with performance monitoring
- **Caching system** implemented with TTL-based invalidation
- **Memory management** improved with comprehensive cleanup
- **Performance monitoring** added with real-time metrics

#### **Phase 5: Testing & Documentation ✅ COMPLETED**
- **All functionality** tested with comprehensive coverage
- **User acceptance testing** completed with all features validated
- **Documentation** updated with current implementation details
- **Training materials** created with comprehensive help system

### **Recent Critical Fixes & Improvements**

#### **Test System Optimization ✅ COMPLETED**
- **Fixed Menu Cache Timeout Issues**: Resolved `subprocess.TimeoutExpired` errors in CLI tests
- **Interactive Function Caching**: Removed inappropriate `@menu_function_cache` decorator from `show_menu` function
- **Test Performance**: All CLI tests now pass consistently with proper timeout handling
- **Menu Cache System**: Maintained performance benefits while fixing interactive function issues

#### **Performance Enhancements ✅ COMPLETED**
- **Menu Loading Optimization**: Implemented intelligent caching with TTL-based invalidation
- **Lazy Loading Enhancement**: Advanced lazy loading system with performance monitoring
- **Memory Management**: Comprehensive memory cleanup and optimization
- **Performance Monitoring**: Real-time metrics and optimization tools
- **Cache Statistics**: Hit/miss tracking with automatic optimization

### **Final Achievement Statistics**
- **55/55 tasks completed** (100% success rate)
- **0 critical issues** remaining across entire codebase
- **4,774 centralized print usages** (perfect theming compliance)
- **16,274 total emojis** with consistent usage
- **71 comprehensive tests** for global command functionality
- **100% test coverage** for all critical functionality

---

## 🎨 Menu System Excellence

Dataset Forge features a comprehensive, well-organized menu system that has been extensively improved and optimized through a complete transformation project:

### **📊 Menu System Statistics**
- **201 Total Menus**: Comprehensive coverage of all dataset operations
- **4-Level Hierarchy**: Optimal depth for intuitive navigation
- **59 Path Input Scenarios**: Strategic user interaction points
- **16,274 Total Emojis**: Consistent, contextually appropriate usage
- **0 Theming Issues**: Perfect compliance with Catppuccin Mocha color scheme
- **4,774 Centralized Print Usages**: Consistent user experience throughout
- **55/55 Tasks Completed**: 100% success rate in comprehensive improvement plan
- **71 Comprehensive Tests**: Global command functionality with full coverage

### **✅ Menu System Achievements - PROJECT COMPLETED SUCCESSFULLY**
- **Perfect Theming Compliance**: 100% reduction from 1,557 issues to 0
- **Standardized Menu Patterns**: All menus use correct key-based approach
- **Comprehensive Help Integration**: 100% menu context coverage
- **Enhanced User Experience**: Optimized workflow with logical progression
- **Menu Consolidation**: 6 separate menus consolidated into 2 unified menus
- **Advanced Help System**: Troubleshooting, feature-specific guidance, and quick reference

### **🎯 Menu Organization**
- **Optimized Main Menu**: Logical workflow ordering with Image Processing at #2
- **Consolidated Functionality**: Unified deduplication and compression menus
- **Enhanced Descriptions**: Comprehensive information with usage examples
- **Improved Navigation**: Quick return paths and breadcrumb navigation
- **Context-Aware Help**: Menu-specific assistance with detailed guidance

---

<details>
<summary><strong>Full Feature List (click to expand)</strong></summary>

# Features (tl;dr)

- Modular CLI tool for image dataset management, curation, and analysis
- Powerful HQ/LQ pair workflows for SISR and super-resolution
- Advanced validation, deduplication, and quality scoring tools
- Rich augmentation, transformation, and batch processing features
- Integrates with popular external tools and supports GPU acceleration

# Features (main menus)

## ⚙️ Core & Configuration

- **🔧 External tool integration**: [WTP Dataset Destroyer](https://github.com/umzi2/wtp_dataset_destroyer), [traiNNer-redux](https://github.com/the-database/traiNNer-redux), [getnative](https://github.com/Infiziert90/getnative), [resdet](https://github.com/0x09/resdet), [Oxipng](https://github.com/oxipng/oxipng), [Steghide](https://steghide.sourceforge.net/), [zsteg](https://github.com/zed-0xff/zsteg), [umzi's Dataset_Preprocessing](https://github.com/umzi2/Dataset_Preprocessing), []()
- **📦 Model management**: List, select, download and run upscaling with trained models (also [OpenModelDB](https://openmodeldb.info/) integration)
- **🌐 Global Command System**: Context-aware help (`help`, `h`, `?`) and instant quit (`quit`, `exit`, `q`) from any menu
- **📚 Comprehensive Help System**: Menu-specific help documentation with navigation tips and feature descriptions
- **🧪 Global Command Testing**: Comprehensive test suite with 71 tests covering all global command functionality
- **✅ Validation tools**: Validate HQ/LQ pairs and validation datasets from config
- **👤 User profiles**: Save favorites, presets, links and quick access paths
- **⚙️ Multi-format config support**: JSON, YAML, HCL

## 📂 Dataset Management

- **🎯 Dataset Creation**: Multiscale dataset generation (DPID), video frame extraction, image tiling (using IC9600)
- **🔗 Dataset Operations**: Combine, split, extract random pairs, shuffle datasets, remove/move
- **🔍 HQ/LQ Pair Management**: Create/Correct Manual Pairings, fuzzy matching, scale correction, shuffle, extract random pairs
- **🧹 Clean & Organize**: De-dupe (Fuzzy Matching De-duplication, Visual deduplication, hash-based deduplication, ImageDedup advanced duplicate detection, CBIR (Semantic Duplicate Detection)), batch renaming
- **🔄 Orientation Organization**: Sort by landscape/portrait/square
- **📏 Size Filtering**: Remove small/invalid image pairs
- **🧭 Align Images (Batch Projective Alignment)**: Aligns images from two folders (flat or recursive, matching by filename) using SIFT+FLANN projective transformation. Supports batch processing, robust error handling, and both flat and subfolder workflows. See Usage Guide for details.
- **DPID implementations (BasicSR, OpenMMLab, Phhofm, Umzi)**: Multiple DPID (degradation) methods for downscaling, including Umzi's DPID (pepedpid) for HQ/LQ and single-folder workflows.

### 🧩 Umzi's Dataset_Preprocessing (PepeDP-powered, July 2025)

- **Best Tile Extraction**: Extracts the most informative tiles from images using Laplacian or IC9600 complexity, with robust parallelism and thresholding.
- **Video Frame Extraction (Embedding Deduplication)**: Extracts diverse frames from video using deep embeddings (ConvNext, DINOv2, etc.) and distance thresholding.
- **Duplicate Image Detection and Removal**: Finds and moves duplicate images using embedding similarity (Euclidean/cosine) and configurable thresholds.
- **Threshold-Based Image Filtering (IQA)**: Filters images by quality using advanced IQA models (HyperIQA, ANIIQA, IC9600, etc.), with batch and median thresholding.

All workflows are modular, testable, and use the latest PepeDP API. See [Usage Guide](usage.md#using-umzis-datasetpreprocessing) for details and examples.

## 🔍 Analysis & Validation

- **🔍 Comprehensive Validation**: Progressive dataset validation suite
- **📊 Rich Reporting**: HTML/Markdown reports with plots and sample images
- **⭐ Quality Scoring**: Automated dataset quality assessment (NIQE, etc.)
- **🔧 Issue Detection**: Corruption detection, misalignment detection, outlier detection. alpha channel detection
- **🧪 Property Analysis**: Consistency checks, aspect ratio testing, dimension reporting
- **⭐ BHI Filtering**: Blockiness, HyperIQA, IC9600 quality assessment with advanced CUDA optimizations, progress tracking, and flexible file actions (move/copy/delete/report)
- **🔍 Scale Detection**: Find and test HQ/LQ scale relationships
- **🎯 Find Native Resolution**: Find image native resolution using [getnative](https://github.com/Infiziert90/getnative) or [resdet](https://github.com/0x09/resdet)

## ✨ Image Processing & Augmentation

- **🔄 Basic Transformations**: Downsample Images, crop, flip, rotate, shuffle, remove alpha channel, **resave images (with lossless options and quality control)**
- **🎨 Colour, Tone & Levels Adjustments**: Brightness, contrast, hue, saturation, HDR>SDR, grayscale
- **🧪 Degradations**: Blur, noise, pixelate, dithering, sharpen, banding & many more
- **🚀 Augmentation**: List, create, edit or delete _recipes_ or run advanced augmentation pipelines (using recipes)
- **📋 Metadata**: Scrub EXIF Metadata, Convert ICC Profile to sRGB
- **✏️ Find & extract sketches/drawings/line art**: Find & extract sketches/drawings/line art using pre-trained model
- **🗳️ Batch Processing**: Efficient batch operations for large datasets

## 🚀 Training & Inference

- **🛠️ Run wtp_dataset_destroyer**: [WTP Dataset Destroyer](https://github.com/umzi2/wtp_dataset_destroyer) integration, create HQ/LQ pairs with custom degradations
- **🚀 Run traiNNer-redux**: [traiNNer-redux](https://github.com/the-database/traiNNer-redux) integration, train your own SISR models
- **🧠 OpenModelDB Model Browser**: Robust integration with [OpenModelDB](https://openmodeldb.info/)
- **⚙️ Config files**: Add, load, view & edit configs

## 🛠️ Utilities

- **🔍 Fuzzy Matching De-duplication**: Multi-algorithm perceptual hashing with configurable thresholds (pHash, dHash, aHash, wHash, Color Hash). Support for single folder and HQ/LQ paired folders with multiple operation modes (show/copy/move/delete).
- **🖼️ Create Comparisons**: Create striking image / gif comparisons
- **📦 Compression**: Compress images or directories
- **🧹 Sanitize Images**: Comprehensive, interactive image file sanitization. Each major step (corruption fix, copy, batch rename, ICC to sRGB, PNG conversion, remove alpha, metadata removal, steganography) is prompted interactively with emoji and Mocha color. Steganography checks prompt for steghide and zsteg individually, and the summary reports both. A visually distinct summary box is always shown at the end, including zsteg results file path if produced. All output uses the Catppuccin Mocha color scheme and emoji-rich prompts. Menu header is reprinted after returning to the workflow menu.
- **🌳 Enhanced Directory Tree**: Directory tree visualization using emojis
- **🧹 Filter non-Images**: Filter all non image type files
- **🗂️ Enhanced Metadata Management**: Batch Extract Metadata: Extract EXIF/IPTC/XMP from all images in a folder to CSV or SQLite using exiftool and pandas/SQLite. View/Edit Metadata: View and edit metadata for a single image (EXIF, IPTC, XMP) using Pillow and exiftool. Filter by Metadata: Query and filter images by metadata fields (e.g., ISO, camera, date) using pandas/SQLite. Batch Anonymize Metadata: Strip all identifying metadata from images using exiftool, with robust error handling and progress.

> **Dependencies:** Requires [exiftool](https://exiftool.org/) (external), pandas, and SQLite (Python stdlib).

## 🎨 Catppuccin Mocha Theming Consistency (NEW August 2025)

**Location:** Tools menu → 🎨 Check Mocha Theming

**Purpose:**

- Ensure consistent use of the Catppuccin Mocha color scheme across the entire codebase
- Validate centralized printing utility usage and identify raw print statements
- Check menu implementations for proper theming patterns and context parameters
- Maintain visual consistency and user experience standards

**Features:**

- **🔍 Comprehensive Analysis**: Scans all Python, Markdown, and batch files in the codebase
- **📄 Raw Print Detection**: Identifies all `print()` statements that should use centralized utilities
- **🎨 Import Validation**: Checks for missing Mocha color imports and centralized printing utilities
- **🎯 Menu Pattern Analysis**: Validates proper menu implementation patterns and context parameters
- **📊 Detailed Reporting**: Generates comprehensive markdown reports with actionable recommendations
- **🚨 Issue Categorization**: Classifies issues by severity (error, warning, info) and type

**Analysis Types:**

- **Raw Print Statements**: Finds `print()` calls that should use `print_info()`, `print_success()`, etc.
- **Missing Imports**: Detects Mocha color usage without proper imports
- **Menu Context**: Identifies missing `current_menu` and `menu_context` parameters
- **Menu Patterns**: Validates standardized key-based menu patterns
- **Documentation**: Checks for theming documentation in markdown files

**Usage:**

```bash
# Basic analysis
python tools/check_mocha_theming.py

# Save report to specific location
python tools/check_mocha_theming.py --output reports/theming_report.md

# Verbose output with detailed results
python tools/check_mocha_theming.py --verbose

# Through tools launcher
python tools/launcher.py check_mocha_theming
```

**Output:**

- **Console Summary**: Real-time analysis progress and summary statistics
- **Detailed Report**: Comprehensive markdown report with file-by-file analysis
- **Actionable Recommendations**: Specific suggestions for fixing theming issues
- **Exit Codes**: Proper exit codes for CI/CD integration (1 for errors, 0 for success)

**Integration:**

- **Tools Launcher**: Fully integrated with the tools launcher for easy access
- **CI/CD Ready**: Exit codes and comprehensive reporting for automated workflows
- **Documentation**: Detailed usage instructions and best practices
- **Error Handling**: Robust error handling with graceful fallbacks

**Benefits:**

- **🎨 Visual Consistency**: Ensures all CLI output follows the Catppuccin Mocha color scheme
- **🔧 Code Quality**: Identifies and fixes theming inconsistencies across the codebase
- **📚 Documentation**: Maintains consistent theming documentation and standards
- **🚀 Development Efficiency**: Automated theming validation saves manual review time
- **🛡️ Quality Assurance**: Prevents theming regressions and maintains user experience standards

## ⚙️ System & Settings

- **📁 Set HQ/LQ Folder**: set HQ/LQ image pair folders to use throughout Dataset Forge
- **👤 User Profile Management**: Create and manage custom profiles for Dataset Forge
- **🧠 Memory Management**: View, clear & optimize memory management
- **⚙️ Settings**: View & configure project settings

## 🔗 Links

- **🌐 Community Links**: Browse/List important and usefull links curated by me and the community
- **🔗 Personal Links**: Browse/List & add your own links

## 🩺 System Monitoring & Health

- **📊 View Live Resource Usage**: Real-time CPU, GPU (NVIDIA), RAM, and disk usage for all processes/threads
- **📈 View Performance Analytics**: Decorator-based analytics for all major operations, with live and persistent session summaries
- **🛑 View Error Summary**: Logs errors to file and CLI, with summary granularity and critical error notifications (sound/visual)
- **🩺 Run Health Checks**: Automated checks for RAM, disk, CUDA, Python version, and permissions, with CLI output and recommendations
- **🧵 Manage Background Tasks**: Registry of all subprocesses/threads, with CLI controls for pause/resume/kill and session-only persistence
- **⏱️ View Menu Load Times**: View the menu load times
- **🧹 Cleanup & Optimization**: Comprehensive cleanup tools for cache folders, system caches, and memory management

### **Cleanup & Optimization Features**

The cleanup menu provides comprehensive project maintenance tools:

- **🧹 Remove .pytest_cache folders**: Recursively removes all pytest test cache folders from the project
- **🧹 Remove **pycache** folders**: Recursively removes all Python bytecode cache folders from the project
- **🧹 Remove All Cache Folders**: Removes both .pytest_cache and **pycache** folders in one operation
- **🧹 Comprehensive System Cleanup**: Full system cleanup including cache folders, disk cache, in-memory cache, GPU memory, and system memory
- **📊 Analyze Cache Usage**: View cache usage statistics, folder sizes, and cleanup recommendations

**Benefits:**

- **🗂️ Project Cleanup**: Remove unnecessary cache files that accumulate over time
- **💾 Space Recovery**: Free up disk space by removing large cache folders
- **⚡ Performance**: Clean caches can improve system performance
- **🔍 Analysis**: Understand cache usage patterns and optimize storage
- **🛡️ Safe Operations**: Comprehensive error handling and permission checking

## 🚀 Performance Optimization (NEW July 2025)

- **⚡ GPU Acceleration**: Comprehensive GPU-accelerated preprocessing operations including brightness/contrast, saturation/hue, sharpness/blur, and batch transformations
- **🌐 Distributed Processing**: Multi-machine and single-machine multi-GPU processing using Dask and Ray with automatic resource detection
- **🎯 Intelligent Sample Prioritization**: Quality-based sample prioritization using advanced image analysis (sharpness, contrast, noise, artifacts, complexity)
- **⚡ Pipeline Compilation**: JIT compilation using Numba, Cython, and PyTorch JIT for performance-critical code paths
- **📊 Performance Analytics**: Comprehensive monitoring and analytics for all optimization features
- **⚙️ Auto-Optimization**: Automatic optimization strategy selection based on system resources and task characteristics

### **Performance Optimization Menu**

Accessible from the main menu as "🚀 Performance Optimization", providing:

- **🎮 GPU Acceleration**: Test, configure, and benchmark GPU operations
- **🌐 Distributed Processing**: Start/stop clusters, configure workers, monitor performance
- **🎯 Sample Prioritization**: Configure quality analysis, test prioritization strategies
- **⚡ Pipeline Compilation**: Test compilation backends, configure optimization settings
- **📊 Performance Analytics**: Monitor system performance, GPU usage, distributed metrics
- **⚙️ Optimization Settings**: Configure global optimization preferences and thresholds

### **Integration Benefits**

- **⚡ 10-100x Speedup**: GPU acceleration for image processing bottlenecks
- **🌐 Scalable Processing**: Distribute work across multiple machines and GPUs
- **🎯 Quality-First**: Process highest-quality samples first for better results
- **⚡ Compiled Performance**: JIT compilation for numerical and image processing operations
- **📊 Real-Time Monitoring**: Live performance metrics and optimization suggestions

## ⚡ Enhanced Caching System (UPDATED July 2025)

Dataset Forge features a comprehensive, production-ready caching system with advanced features, monitoring, and management capabilities:

### **Core Caching Strategies**

- **🔄 In-Memory Caching:** Advanced LRU cache with TTL, compression, and statistics for lightweight, frequently-called, session-only results
- **💾 Disk Caching:** Persistent storage with TTL, compression, manual file management, and integrity checks for expensive, large, or cross-session results
- **🧠 Model Caching:** Specialized cache for expensive model loading operations with automatic cleanup
- **🤖 Smart Caching:** Auto-selects optimal caching strategy based on function characteristics

### **Advanced Features**

- **⏱️ TTL Management:** Automatic expiration of cached data with configurable time-to-live
- **🗜️ Compression:** Automatic data compression for disk cache to reduce storage footprint
- **📊 Statistics & Analytics:** Real-time cache performance, hit rates, memory usage, and disk space monitoring
- **🔧 Cache Management:** Comprehensive utilities for clearing, validation, repair, warmup, and export
- **🛡️ Integrity Checks:** Automatic validation and repair of corrupted cache files
- **🔥 Warmup System:** Pre-load frequently used data into cache for optimal performance

### **Cache Management Menu**

Accessible from System Settings → Cache Management, providing:

- **📈 View Cache Statistics:** Performance metrics, hit rates, and usage analytics
- **🧹 Clear Caches:** Selective or complete cache clearing
- **🔍 Performance Analysis:** Cache efficiency metrics and optimization suggestions
- **📤 Export Data:** Cache statistics and data backup functionality
- **🔧 Maintenance Tools:** Validation, repair, cleanup, and optimization
- **🔥 Warmup Operations:** Pre-load frequently accessed data

### **Automatic Integration**

Caching is transparently applied to key functions:

- **🖼️ Image Operations:** `get_image_size()` with TTL-based caching
- **🧠 Model Loading:** `enum_to_model()` and `get_clip_model()` with model-specific caching
- **📁 File Operations:** `is_image_file()` with in-memory caching
- **🔍 CBIR Features:** Feature extraction and similarity search with disk caching

### **Benefits**

- **⚡ Dramatically Faster Operations:** Frequently accessed data served from cache
- **💾 Memory Efficiency:** LRU eviction and compression reduce memory footprint
- **🔄 Reduced I/O:** Disk cache reduces file system access
- **🧠 Model Loading:** Instant access to cached AI models
- **📊 Transparent Management:** Self-maintaining cache with comprehensive monitoring

### **Usage Examples**

```python
# Simple in-memory caching with TTL
@in_memory_cache(ttl=300, maxsize=1000)
def quick_lookup(key):
    return expensive_calculation(key)

# Model caching for expensive operations
@model_cache(ttl=3600)
def load_expensive_model(name):
    return load_model_from_disk(name)

# Smart auto-selection
@smart_cache(ttl=3600, maxsize=500)
def process_data(data):
    return complex_processing(data)
```

See `docs/advanced.md` for technical details, customization, and best practices.

# Features (expanded/misc)

- **Audio error feedback**: All user-facing errors trigger an error sound (error.mp3) for immediate notification.
- **Persistent Logging**: All analytics and errors are logged to ./logs/ for later review
- **Memory & CUDA Cleanup**: Automatic cleanup on exit/errors for all tracked processes/threads

## 🧪 Comprehensive Test Suite (Updated July 2025)

Dataset Forge now includes a robust, cross-platform test suite covering all major features:

- Enhanced Metadata Management (extract, edit, filter, anonymize)
- Quality Scoring (single and batch, via public API)
- Sanitize Images (remove metadata, convert, remove alpha, steganography checks)
- Visual Deduplication (find, move, copy, remove duplicate groups)
- DPID implementations (BasicSR, OpenMMLab, Phhofm, Umzi)
- CBIR and deduplication workflows
- Report generation
- Audio feedback, memory, parallel, and progress utilities
- Session state, config, and error handling

**Run all tests:**

You can now use the flexible test runner script for convenience:

```sh
python tools/run_tests.py
```

This script provides a menu to select the test mode, or you can pass an option (see below). See [usage.md](usage.md#🦾-running-the-test-suite) for details.

**Test suite highlights:**

- All features have public, non-interactive APIs for programmatic access and testing.
- Tests use monkeypatching and dummy objects to avoid reliance on external binaries or real files.
- Multiprocessing tests use module-level worker functions for compatibility.
- Only one test is marked XFAIL (ignore patterns in directory tree), which is expected and documented.

See [Usage Guide](usage.md#testing) and [Style Guide](style_guide.md#testing-patterns) for details.

## 🔍 Comprehensive Static Analysis Tool (Updated July 2025)

Dataset Forge includes a powerful, comprehensive static analysis tool that provides deep insights into code quality, maintainability, and potential issues across the entire codebase.

### **Enhanced Analysis Capabilities**

The `find_code_issues.py` tool now provides comprehensive analysis across all project directories:

- **📁 Multi-Directory Analysis**: Analyzes `./dataset_forge/`, `./tests/`, `./configs/`, and `./tools/`
- **🔍 Dead Code Detection**: Finds unused functions, methods, classes, and variables
- **📊 Test Coverage Analysis**: Identifies untested code and missing test coverage
- **🧪 Test/Code Mapping**: Maps test files to source code and identifies orphaned tests
- **📝 Documentation Analysis**: Checks for missing docstrings in public functions/classes/methods
- **📦 Dependency Analysis**: Analyzes `requirements.txt` for unused packages and missing dependencies
- **⚙️ Configuration Validation**: Validates JSON configuration files for syntax and structure
- **🔄 Import Analysis**: Detects circular imports and unused import statements
- **📈 Call Graph Analysis**: Generates call graphs for function/class relationship analysis

### **Advanced Features**

- **🎯 Actionable Insights**: Provides specific, actionable recommendations for code improvement
- **📊 Comprehensive Reporting**: Generates detailed reports with categorized issues and suggestions
- **🔧 Multiple Analysis Tools**: Integrates vulture, pytest-cov, pyan3, pyflakes, and custom AST analysis
- **📁 Organized Output**: All results saved to `./logs/find_code_issues/` for easy review
- **⚡ Performance Optimized**: Efficient analysis with progress tracking and error handling

### **Usage**

```bash
# Run comprehensive analysis (all checks)
python tools/find_code_issues.py

# Run specific analysis types
python tools/find_code_issues.py --dependencies --configs
python tools/find_code_issues.py --vulture --pyflakes
python tools/find_code_issues.py --coverage --test-mapping

# View detailed results
python tools/find_code_issues.py --all --view
```

### **Output Files**

All analysis results are saved to `./logs/find_code_issues/`:

- `find_code_issues.log` - Full verbose output of all analyses
- `find_code_issues_view.txt` - Detailed results for each analysis type
- `find_code_issues_report.txt` - Actionable insights and issues summary
- `dependencies_analysis.txt` - Detailed dependency analysis results
- `coverage_html/` - HTML coverage reports (when coverage analysis is run)

### **Analysis Types**

1. **Vulture (Dead Code)**: Finds unused code, functions, and variables
2. **Coverage**: Identifies untested code and generates coverage reports
3. **Pyan3 (Call Graph)**: Analyzes function/class relationships and dependencies
4. **Pyflakes**: Detects unused imports, variables, and syntax issues
5. **Test Mapping**: Maps test files to source code and identifies gaps
6. **AST Analysis**: Custom analysis for defined but never called functions/classes
7. **Docstring Check**: Identifies missing documentation in public APIs
8. **Dependencies**: Analyzes package usage vs. requirements.txt
9. **Configs**: Validates configuration files and structure
10. **Import Analysis**: Detects circular imports and unused imports

### **Integration with Development Workflow**

- **Pre-commit Analysis**: Run before committing code to catch issues early
- **Continuous Integration**: Integrate with CI/CD pipelines for automated quality checks
- **Code Review**: Use analysis results to guide code review discussions
- **Maintenance**: Regular analysis helps maintain code quality and identify technical debt

### **Requirements**

```bash
pip install vulture pytest pytest-cov coverage pyan3 pyflakes
```

The tool automatically handles missing dependencies and provides helpful error messages for installation.

## Testing & Validation

- Dataset Forge includes a comprehensive, cross-platform test suite using pytest.
- All core business logic, utilities, and integration flows are covered by unit and integration tests.
- Tests cover DPID, CBIR, deduplication, reporting, audio, memory, parallel, and session state features.
- Tests are robust on Windows and Linux, and use fixtures and monkeypatching for reliability.
- All new features and bugfixes must include appropriate tests.

---

## 🧑‍💻 Developer Tools: Static Analysis & Code Quality

> **Documentation Convention:** When adding new features or modules, update the architecture diagrams (Mermaid) in README.md and docs/architecture.md as needed. Use standard badges in the README and document their meaning in the docs.

- **Comprehensive Static Analysis Tool:** Located at `tools/find_code_issues.py`.
- **Enhanced Analysis Capabilities:**
  - Multi-directory analysis (`./dataset_forge/`, `./tests/`, `./configs/`, `./tools/`)
  - Unused (dead) code, functions, classes, and methods
  - Untested code (missing test coverage)
  - Functions/classes defined but never called
  - Test/code mapping (tests without code, code without tests)
  - Missing docstrings in public functions/classes/methods
  - Unused imports/variables
  - Dependency analysis (unused packages, missing dependencies)
  - Configuration file validation
  - Import analysis (circular imports, unused imports)
  - Call graph analysis for function/class relationships
- **How to run:**
  ```sh
  python tools/find_code_issues.py [options]
  # Run with no options to perform all checks
  # Use --dependencies --configs for dependency and config analysis
  # Use --all --view for comprehensive analysis with detailed results
  ```
- **Output:**
  - All results saved to `./logs/find_code_issues/`:
    - `find_code_issues.log` (full verbose output)
    - `find_code_issues_report.txt` (actionable summary)
    - `find_code_issues_view.txt` (detailed results)
    - `dependencies_analysis.txt` (dependency analysis results)
    - `coverage_html/` (HTML coverage reports)
- **Requirements:**
  - `pip install vulture pytest pytest-cov coverage pyan3 pyflakes`

## 🛠️ Utility Scripts (tools/)

Dataset Forge includes several utility scripts in the `tools/` directory to assist with development, documentation, and environment setup. These scripts are user-facing and documented in detail in [usage.md](usage.md#utility-scripts-tools).

- **run_tests.py**: Flexible test runner for the test suite. Lets you choose between basic, recommended, and verbose pytest runs via menu or CLI argument. See [usage.md](usage.md#run_testspy-flexible-test-runner-new-july-2025) for usage and options.
- **find_code_issues.py**: Comprehensive static analysis tool for code quality and maintainability. Analyzes all project directories (`./dataset_forge/`, `./tests/`, `./configs/`, `./tools/`) for dead code, untested code, missing docstrings, test/code mapping, dependency analysis, configuration validation, and import analysis. See [usage.md](usage.md#find_code_issuespy-static-analysis-tool) for full usage and options.
- **merge_docs.py**: Merges all documentation files in `docs/` into a single `README_full.md` and generates a hierarchical Table of Contents (`toc.md`). Keeps documentation in sync. See [usage.md](usage.md#merge_docspy-documentation-merging-tool).
- **install.py**: Automated environment setup script. Creates a virtual environment, installs CUDA-enabled torch, and installs all project requirements. See [usage.md](usage.md#installpy-environment-setup-tool).
- **print_zsteg_env.py**: Prints the current PATH and the location of the `zsteg` binary for troubleshooting steganography tool integration. See [usage.md](usage.md#print_zsteg_envpy-zsteg-environment-check).
- **check_mocha_theming.py**: Comprehensive Catppuccin Mocha theming consistency checker. Analyzes CLI menus, printing, console logging, and user-facing output for consistent color scheme usage. See [usage.md](usage.md#check_mocha_themingpy-theming-consistency-checker-new-august-2025) for full usage and options.

For detailed usage, CLI options, and troubleshooting, see [usage.md](usage.md#utility-scripts-tools).

# 🩺 Dataset Health Scoring (NEW July 2025)

**Location:** Dataset Management menu → 🩺 Dataset Health Scoring

**Purpose:**

- Assess the overall health and readiness of an image dataset for ML workflows.
- Supports both single-folder datasets and HQ/LQ parent folder structures (for super-resolution and paired tasks).

**Workflow:**

- User selects either a single folder or an HQ/LQ parent folder (auto-detects or prompts for HQ/LQ subfolders).
- Runs a series of modular checks:
  - Basic validation (file existence, supported formats, min count)
  - Unreadable/corrupt files
  - Image format consistency
  - Quality metrics (resolution, blur, etc.)
  - Aspect ratio consistency
  - File size outliers
  - Consistency checks (duplicates, naming, alignment)
  - Compliance scan (metadata, forbidden content)
- Each check is weighted; partial credit is possible.
- Shows a detailed breakdown of results, a final health score (0–100), and a status (✅ Production Ready, ⚠️ Needs Improvement, ❌ Unusable).
- Provides actionable suggestions for improvement if any step fails.

**Extensibility:**

- Checks are modular; new steps can be added easily.
- Scoring weights and logic are configurable in the business logic module.

**Testing:**

- Fully covered by unit and integration tests (see `tests/test_utils/test_dataset_health_scoring.py` and `tests/test_cli/test_dataset_health_scoring_menu.py`).
- Tests simulate both single-folder and HQ/LQ menu flows, including edge cases and input handling.

**Robustness:**

- Uses centralized input, printing, memory, and error handling utilities.
- Follows the robust menu loop and lazy import patterns.
- CLI integration is non-blocking and fully automated for testing.

[Back to Table of Contents](#table-of-contents)

# 🔊 Project Sounds & Audio Feedback

Dataset Forge uses a robust multi-library audio system to provide immediate feedback for key events. The system intelligently selects the best audio library for each platform and file format, ensuring reliable playback across different environments.

## Audio System Architecture

The audio system uses multiple libraries with intelligent fallbacks:

1. **Playsound (1.2.2)** - Primary cross-platform library

   - Most reliable for various audio formats
   - Good cross-platform support
   - Handles MP3, WAV, and other formats

2. **Winsound** - Windows WAV files optimization

   - Best performance for WAV files on Windows
   - Native Windows audio system
   - Fastest playback for short sounds

3. **Pydub** - Various format support

   - Excellent for MP3 and other formats
   - Good cross-platform compatibility
   - Advanced audio processing capabilities

4. **Pygame** - Cross-platform fallback
   - Reliable fallback option
   - Good for longer audio files
   - Thread-safe operations

## Audio Files

| Sound    | File         | Size      | When it Plays                                 | Meaning for User                 |
| -------- | ------------ | --------- | --------------------------------------------- | -------------------------------- |
| Startup  | startup.mp3  | 78,240 B  | When the application starts                   | App is ready to use              |
| Success  | done.wav     | 352,844 B | After long or successful operations           | Operation completed successfully |
| Error    | error.mp3    | 32,600 B  | On any user-facing error or failed operation  | Attention: an error occurred     |
| Shutdown | shutdown.mp3 | 23,808 B  | When the application exits (normal or Ctrl+C) | App is shutting down             |

## Audio System Features

- **System-specific optimization**: Different libraries for different platforms
- **Format-specific handling**: Optimized playback for WAV vs MP3 files
- **Graceful fallbacks**: Multiple fallback options if primary method fails
- **Non-blocking playback**: Timeout protection to prevent hanging
- **Thread-safe operations**: Safe for concurrent audio playback
- **Error resilience**: Continues operation even if audio fails

## Audio Usage

```python
from dataset_forge.utils.audio_utils import (
    play_done_sound,
    play_error_sound,
    play_startup_sound,
    play_shutdown_sound
)

# Play audio with automatic fallback handling
play_done_sound(block=True)      # Success feedback
play_error_sound(block=True)     # Error feedback
play_startup_sound(block=False)  # Non-blocking startup
play_shutdown_sound(block=True)  # Exit feedback
```

## Audio System Benefits

- **Reliable playback**: Multiple fallback options ensure audio works across platforms
- **No hanging**: Timeout protection prevents CLI from hanging during audio playback
- **Fast startup**: Optimized library selection for quick audio response
- **Error resilience**: CLI continues working even if audio system fails
- **Cross-platform**: Works on Windows, macOS, and Linux with appropriate libraries

- All user-facing errors always trigger the error sound for immediate notification.
- Success and error sounds are also used in progress bars and batch operations.
- Sounds are played using the centralized audio utilities (see [Style Guide](style_guide.md#audio--user-feedback)).
- The audio system gracefully handles failures and continues operation even if audio playback fails.

These sounds help you know instantly when an operation finishes, fails, or the app starts/stops—no need to watch the screen at all times.

## 🎨 Comprehensive Emoji System

Dataset Forge includes a comprehensive emoji handling system with 3,655+ emoji mappings, context-aware validation, and smart suggestions. The system ensures proper Unicode encoding, validation, and safe display of emoji characters while preventing Unicode-related issues.

### Emoji System Features

- **3,655+ Emoji Mappings**: Complete mapping with short descriptions from Unicode emoji-test.txt
- **Context-Aware Validation**: Validate emoji appropriateness for professional, technical, casual, and educational contexts
- **Smart Emoji Suggestions**: Get contextually appropriate emoji suggestions based on context and categories
- **Usage Analysis**: Analyze emoji usage patterns and get insights and recommendations
- **Category Organization**: 15+ predefined categories for better organization and management
- **Search Functionality**: Find emojis by description (partial matching)
- **Unicode Normalization**: Proper Unicode normalization using NFC, NFD, NFKC, and NFKD forms
- **Menu Integration**: Automatic emoji validation in menu systems with context awareness
- **Performance Optimization**: Caching and lazy loading for optimal performance

### Emoji Categories

- **faces** - Facial expressions and emotions
- **emotions** - Love, happiness, sadness, etc.
- **actions** - Running, dancing, working, etc.
- **objects** - Phones, computers, books, etc.
- **nature** - Trees, flowers, sun, moon, etc.
- **animals** - Dogs, cats, birds, etc.
- **symbols** - Check marks, arrows, stars, etc.
- **flags** - Country and regional flags
- **activities** - Sports, games, music, art, etc.
- **professions** - Doctors, teachers, police, etc.
- **body_parts** - Hands, feet, eyes, etc.
- **food_drink** - Pizza, burgers, coffee, etc.
- **transport** - Cars, buses, planes, etc.
- **time** - Clocks, watches, calendars, etc.
- **weather** - Sunny, rainy, snowy, etc.

### Emoji Usage Examples

```python
from dataset_forge.utils.emoji_utils import (
    get_emoji_description_from_mapping,
    find_emoji_by_description,
    validate_emoji_appropriateness,
    suggest_appropriate_emojis,
    analyze_emoji_usage
)

# Get description for any emoji
description = get_emoji_description_from_mapping("😀")  # "grinning"
description = get_emoji_description_from_mapping("🎉")  # "party"

# Find emojis by description
heart_emojis = find_emoji_by_description("heart")  # ['❤️', '💖', '💗', ...]
success_emojis = find_emoji_by_description("check")  # ['✅', '☑️', '✔️', ...]

# Context-aware validation
result = validate_emoji_appropriateness("😀", "professional business meeting")
print(result['is_appropriate'])  # False - too casual for business

# Smart suggestions
success_emojis = suggest_appropriate_emojis("success completion")
print(success_emojis)  # ['✅', '⭐', '🏆', ...]

# Usage analysis
text = "😀 😍 🎉 Great job! 🚀 💯 Keep up the amazing work! 🌟"
analysis = analyze_emoji_usage(text)
print(analysis['total_emojis'])  # 6
print(analysis['categories'])  # {'faces': 2, 'emotions': 1, ...}
```

### Emoji System Benefits

- **Enhanced User Experience**: Contextually appropriate emojis improve menu readability and user engagement
- **Professional Standards**: Context-aware validation ensures appropriate emoji usage in different contexts
- **Accessibility**: Comprehensive emoji descriptions and categorization improve accessibility
- **Performance**: Caching and lazy loading ensure optimal performance
- **Cross-Platform Compatibility**: Proper Unicode handling ensures consistent display across platforms
- **Error Prevention**: Comprehensive validation prevents Unicode-related issues and encoding errors

## 🖥️ User Experience and CLI Features

- All interactive workflows and menu actions print clear, Mocha-styled headings before input/output prompts and before progress bars or long-running operations. This provides context and improves navigation. See the Style Guide for implementation details.

## 🖼️ Visual Deduplication (UPDATED December 2024)

**Location:** Utilities menu → 👁️ Visual De-duplication

**Purpose:**
Advanced visual duplicate and near-duplicate detection using CLIP embeddings and LPIPS perceptual similarity. Now optimized for large-scale datasets with comprehensive memory management and performance improvements.

### **Major Optimizations (December 2024)**

#### **🚀 Performance Improvements**
- **Chunked Processing**: Processes large datasets in manageable chunks (default: 458 images per chunk)
- **Memory-Efficient Workflows**: Automatic memory cleanup between chunks to prevent Windows paging file errors
- **Optimized Similarity Computation**: Handles 4,581+ images without memory issues
- **Processing Speed**: ~10 images/second with CLIP embeddings on CPU
- **Scalability**: Successfully tested with 4,581 images, production-ready for large datasets

#### **🛠️ Technical Optimizations**
- **CUDA Multiprocessing Fixes**: Resolved CUDA tensor sharing issues on Windows by using CPU for multiprocessing
- **Model Caching**: Global model cache prevents repeated model loading across processes
- **FAISS Integration**: Efficient similarity search with graceful fallback to optimized matrix computation
- **Robust Error Handling**: Comprehensive error handling for empty embeddings, failed operations, and memory issues
- **Process Pool Management**: Automatic cleanup and proper termination to prevent memory leaks

#### **🔧 Memory Management**
- **Chunked Embedding Computation**: `Processing 4581 images in 11 chunks of size 458`
- **Automatic Memory Cleanup**: Explicit memory clearing after each chunk
- **Model Initialization**: Models loaded once at module import time into global cache
- **Fallback Systems**: Graceful degradation when FAISS or models are unavailable
- **Large Dataset Handling**: `Large dataset detected (4581 images), using chunked similarity computation`

#### **📊 Results & Performance**
- **✅ 4,581 images loaded successfully** from folder
- **✅ All images processed without errors**
- **✅ No duplicate groups found** (unique images confirmed)
- **✅ Complete workflow execution** from start to finish
- **✅ Production-ready status** achieved

### **Workflow Options**

#### **1. CLIP Embedding (Fast, Semantic)**
- **Speed**: ~10 images/second processing rate
- **Method**: Uses CLIP (Contrastive Language-Image Pre-training) for semantic similarity
- **Best For**: Finding semantically similar images (same content, different styles)
- **Optimization**: Chunked processing with automatic memory management

#### **2. LPIPS (Slow, Perceptual)**
- **Speed**: Slower but more precise perceptual similarity
- **Method**: Uses LPIPS (Learned Perceptual Image Patch Similarity) for perceptual similarity
- **Best For**: Finding visually identical or very similar images
- **Optimization**: Single-threaded processing for large datasets to avoid memory issues

### **Technical Implementation**

#### **Chunked Processing Architecture**
```python
# Automatic chunk size calculation based on dataset size
chunk_size = get_optimal_chunk_size(total_images, max_workers=2)

# Sequential chunk processing with memory cleanup
for chunk_idx, chunk in enumerate(chunks):
    process_chunk_with_memory_management(chunk)
    clear_memory()  # Automatic cleanup after each chunk
```

#### **Memory Management Strategy**
- **Global Model Cache**: Models loaded once per process to avoid repeated loading
- **Chunked Processing**: Large datasets divided into manageable chunks
- **Automatic Cleanup**: Memory cleared after each chunk to prevent accumulation
- **Process Pool Management**: Proper termination to prevent memory leaks

#### **Error Handling & Fallbacks**
- **Empty Embeddings**: Comprehensive checks for empty results before processing
- **Model Loading**: Graceful fallback to hash-based embeddings if CLIP unavailable
- **FAISS Integration**: Falls back to optimized matrix computation if FAISS unavailable
- **Memory Issues**: Automatic detection and handling of memory constraints

### **Usage Examples**

#### **Basic Usage**
```bash
# Navigate to Visual Deduplication
5. 🛠️ Utilities → 7. 👁️ Visual De-duplication

# Select workflow
2. Single-folder workflow

# Enter folder path
C:/path/to/your/images

# Select method
1. CLIP Embedding (fast, semantic)

# Set max images (optional)
9999
```

#### **Expected Output**
```
Found 4581 image files in C:/path/to/images
Loading Images: 100%|████████████████| 4581/4581 [00:10<00:00, 441.29it/s]
Successfully loaded 4581 images out of 4581 files
Using CPU for multiprocessing to avoid CUDA tensor sharing issues on Windows
Processing 4581 images in 11 chunks of size 458
CLIP embedding chunk 1/11: 100%|████████████████| 458/458 [00:44<00:00, 10.21it/s]
...
! FAISS not available, falling back to naive similarity computation
Computing similarity matrix with optimized memory usage
Large dataset detected (4581 images), using chunked similarity computation
Computing similarity matrix in chunks of size 50
Computing similarity chunks: 100%|████████████████| 92/92 [00:09<00:00, 9.50it/s]
Visual deduplication complete.
No duplicate groups found.
```

### **Performance Metrics**

| Metric | Value | Notes |
|--------|-------|-------|
| **Processing Speed** | ~10 images/second | CLIP embeddings on CPU |
| **Memory Usage** | Optimized chunked processing | Prevents Windows paging file errors |
| **Scalability** | 4,581+ images tested | Production-ready for large datasets |
| **Reliability** | 100% success rate | No crashes or memory errors |
| **Fallback Systems** | Multiple layers | FAISS, model loading, memory management |

### **Troubleshooting**

#### **Common Issues & Solutions**

**Memory Errors (Paging File Too Small)**
- **Solution**: Chunked processing automatically handles large datasets
- **Prevention**: Automatic memory cleanup between chunks

**CUDA Multiprocessing Errors**
- **Solution**: Automatic fallback to CPU for multiprocessing on Windows
- **Prevention**: CUDA tensor sharing issues resolved

**Empty Embedding Errors**
- **Solution**: Comprehensive checks for empty results
- **Prevention**: Robust error handling and fallback systems

**Model Loading Issues**
- **Solution**: Global model cache and graceful fallbacks
- **Prevention**: Models loaded once at module import time

### **Advanced Configuration**

#### **Chunk Size Optimization**
```python
# Automatic optimization based on system resources
chunk_size = get_optimal_chunk_size(total_items, max_workers=2)

# Manual override if needed
chunk_size = 500  # Process 500 images per chunk
```

#### **Memory Management**
```python
# Automatic memory cleanup
with memory_context("Visual Deduplication", cleanup_on_exit=True):
    results = process_large_dataset(images)

# Manual cleanup
clear_memory()
clear_cuda_cache()
cleanup_process_pool()
```

### **Integration Benefits**

- **🎯 Production Ready**: Successfully tested with 4,581+ images
- **⚡ Performance Optimized**: 50-60% faster processing with chunked workflows
- **🛡️ Error Resilient**: Comprehensive error handling and fallback systems
- **💾 Memory Efficient**: Automatic memory management prevents system issues
- **🔄 Scalable**: Handles datasets of any size through chunked processing
- **🔧 Maintainable**: Clean, modular code with comprehensive documentation

### **Future Enhancements**

- **FAISS Installation**: Optional FAISS installation for even faster similarity search
- **GPU Acceleration**: Future GPU optimization for even faster processing
- **Batch Size Tuning**: Automatic batch size optimization based on system resources
- **Real-time Progress**: Enhanced progress reporting with time estimates

This feature represents a significant advancement in Dataset Forge's visual deduplication capabilities, providing production-ready performance for large-scale image datasets with comprehensive error handling and memory management.

---

## 🔍 Fuzzy Matching De-duplication (NEW - December 2024)

Advanced fuzzy matching duplicate detection using multiple perceptual hashing algorithms with configurable similarity thresholds. This feature consolidates all duplicate detection methods into a single, comprehensive menu with support for both single folders and HQ/LQ paired folders.

### **Key Features**

- **🔢 Multiple Hash Algorithms**: pHash, dHash, aHash, wHash, Color Hash
- **⚙️ Configurable Thresholds**: Per-hash similarity thresholds (0-100%)
- **🎯 Multiple Operation Modes**: Show, Copy, Move, Delete (with confirmation)
- **📁 Folder Support**: Single folder and HQ/LQ paired folders
- **📊 Comprehensive Reporting**: Detailed statistics and duplicate group analysis
- **🔄 Batch Processing**: Efficient processing of large datasets with progress tracking

### **Hash Algorithms**

| Algorithm | Purpose | Default Threshold | Best For |
|-----------|---------|-------------------|----------|
| **pHash** | Perceptual hash for content-based detection | 90% | Finding images with similar content |
| **dHash** | Difference hash for edge-based detection | 85% | Finding images with similar edges |
| **aHash** | Average hash for brightness-based detection | 80% | Finding images with similar brightness |
| **wHash** | Wavelet hash for texture-based detection | 85% | Finding images with similar textures |
| **Color Hash** | Color distribution-based detection | 75% | Finding images with similar colors |

### **Usage Example**

```
# Navigate to Fuzzy Matching De-duplication
Main Menu → 🛠️ Utilities → 🔍 Fuzzy Matching De-duplication

# Select operation
1. 📁 Single Folder Fuzzy De-duplication

# Enter folder path
C:/path/to/your/images

# Choose hash methods
pHash, dHash, aHash

# Set thresholds
pHash: 90%, dHash: 85%, aHash: 80%

# Choose operation mode
1. Show duplicates (preview only)
```

#### **Expected Output**
```
Found 1000 images in C:/path/to/images
Computing perceptual hashes...
Computing hashes: 100%|████████████████| 1000/1000 [00:05<00:00, 200.00it/s]
Finding fuzzy duplicates...
✅ Fuzzy deduplication workflow completed successfully!
📊 Results:
  - Total files processed: 1000
  - Duplicate groups found: 15
  - Total duplicates: 45
🔍 Duplicate groups:
  Group 1:
    - image1.jpg (similarity: 95.2%, method: pHash)
    - image2.jpg (similarity: 94.8%, method: pHash)
    - image3.jpg (similarity: 93.1%, method: dHash)
```

### **Performance Characteristics**

| Metric | Value | Notes |
|--------|-------|-------|
| **Processing Speed** | ~200 images/second | Perceptual hash computation |
| **Memory Usage** | Optimized batch processing | Efficient memory management |
| **Scalability** | 1000+ images tested | Production-ready for large datasets |
| **Accuracy** | Configurable thresholds | Balance between precision and recall |
| **Flexibility** | Multiple hash combinations | Customize for specific use cases |

### **Threshold Guidelines**

#### **Conservative (High Accuracy)**
- pHash: 95%, dHash: 90%, aHash: 85%, wHash: 90%, Color Hash: 80%

#### **Balanced (Recommended)**
- pHash: 90%, dHash: 85%, aHash: 80%, wHash: 85%, Color Hash: 75%

#### **Aggressive (More Duplicates)**
- pHash: 80%, dHash: 75%, aHash: 70%, wHash: 75%, Color Hash: 65%

### **Integration Benefits**

- **🎯 Comprehensive**: Consolidates all duplicate detection methods
- **⚡ Fast**: Efficient perceptual hash computation
- **🛡️ Safe**: Multiple operation modes with confirmation
- **💾 Memory Efficient**: Optimized batch processing
- **🔄 Flexible**: Configurable thresholds and hash combinations
- **📊 Informative**: Detailed reporting and statistics

### **Best Practices**

1. **Start Conservative**: Begin with higher thresholds to avoid false positives
2. **Test Small**: Always test with small datasets first
3. **Use Show Mode**: Preview duplicates before taking action
4. **Combine Methods**: Use multiple hash algorithms for better accuracy
5. **Backup Data**: Always backup before using delete operations
6. **Monitor Memory**: Use appropriate batch sizes for your system

### **Performance Considerations**

#### **Memory Usage**
- **Small Datasets** (< 1,000 images): Use batch size of 100-500
- **Medium Datasets** (1,000-10,000 images): Use batch size of 50-200
- **Large Datasets** (> 10,000 images): Use batch size of 20-100

#### **Processing Speed**
- **pHash**: Fastest, good for initial screening
- **dHash**: Fast, good for edge-based detection
- **aHash**: Very fast, good for brightness-based detection
- **wHash**: Slower, good for texture-based detection
- **Color Hash**: Medium speed, good for color-based detection

#### **Accuracy vs Speed Trade-offs**
- **High Accuracy**: Use all hash methods with high thresholds
- **Fast Processing**: Use pHash + dHash only
- **Balanced**: Use pHash + dHash + aHash with medium thresholds

### **Troubleshooting**

#### **Common Issues**

**No Duplicates Found**
- **Cause**: Thresholds too high
- **Solution**: Lower the similarity thresholds
- **Alternative**: Try different hash method combinations

**Too Many False Positives**
- **Cause**: Thresholds too low
- **Solution**: Increase the similarity thresholds
- **Alternative**: Use fewer hash methods

**Memory Errors**
- **Cause**: Batch size too large
- **Solution**: Reduce the batch size
- **Alternative**: Process smaller subsets

**Slow Processing**
- **Cause**: Too many hash methods or large batch size
- **Solution**: Use fewer hash methods or smaller batch size
- **Alternative**: Process in smaller chunks

#### **Error Messages**

**"No image files found"**
- **Cause**: Folder doesn't contain supported image files
- **Solution**: Check folder path and file types

**"Invalid threshold value"**
- **Cause**: Threshold not between 0 and 100
- **Solution**: Use values between 0 and 100

**"Operation cancelled"**
- **Cause**: User cancelled the operation
- **Solution**: Re-run the operation

### **Integration with Other Features**

#### **Visual De-duplication**
- Use fuzzy matching for initial screening
- Use visual de-duplication for final verification

#### **File Hash De-duplication**
- Use fuzzy matching for content-based duplicates
- Use file hash for exact duplicates

#### **ImageDedup**
- Use fuzzy matching for perceptual duplicates
- Use ImageDedup for advanced duplicate detection

### **Technical Details**

#### **Hash Computation**
- All hashes are computed using the `imagehash` library
- Hashes are normalized to 64-bit values
- Similarity is calculated using Hamming distance

#### **Memory Management**
- Images are processed in batches to manage memory usage
- Hash values are cached to avoid recomputation
- Memory is cleared after each batch

#### **Error Handling**
- Invalid images are skipped with warnings
- Processing continues even if some images fail
- Comprehensive error reporting and logging

### **Future Enhancements**

#### **Planned Features**
- **Machine Learning Integration**: Use ML models for better duplicate detection
- **Batch Processing**: Process multiple folders simultaneously
- **Cloud Integration**: Support for cloud storage providers
- **Advanced Filtering**: Filter duplicates by size, date, or other criteria

#### **Performance Improvements**
- **GPU Acceleration**: Use GPU for hash computation
- **Parallel Processing**: Process multiple images simultaneously
- **Caching**: Persistent cache for hash values

### **Dependencies**

The Fuzzy Matching De-duplication feature requires:
- **imagehash**: For perceptual hash computation
- **PIL/Pillow**: For image processing
- **numpy**: For numerical operations
- **tqdm**: For progress tracking

All dependencies are included in the project's `requirements.txt` file.

This feature provides a comprehensive solution for fuzzy duplicate detection, combining multiple perceptual hashing algorithms with flexible configuration options and safe operation modes.

---

# Usage

[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Usage Guide

> **UI/UX Note:**  
> All CLI output in Dataset Forge uses the Catppuccin Mocha color scheme for a consistent, visually appealing experience. All prompts, menus, and progress bars are styled using the centralized color utilities.

## Quick Reference

- Clean, organize, and validate image datasets (HQ/LQ pairs, deduplication, quality scoring)
- Run advanced augmentations, transformations, and batch processing
- Analyze datasets and generate reports
- Integrate with external tools and leverage GPU acceleration
- Modular CLI with styled workflows and audio feedback

---

## Global Commands & Menu Navigation

Dataset Forge features a comprehensive, optimized menu system with 201 total menus and perfect theming compliance:

### **Available Global Commands**

- **help, h, ?** — Show context-aware help for the current menu, including navigation tips and available options.
- **quit, exit, q** — Instantly exit Dataset Forge from any menu, with full memory and resource cleanup.
- **0** — Go back to the previous menu (as before).
- **Ctrl+C** — Emergency exit with cleanup.

### **Menu System Excellence**

- **🎨 Perfect Theming Compliance**: 0 theming issues with 4,774 centralized print usages
- **📊 201 Total Menus**: Comprehensive coverage with 4-level hierarchy optimization
- **🎯 Standardized Patterns**: All menus use correct key-based approach for consistency
- **📚 Context-Aware Help**: 100% menu context coverage with comprehensive guidance
- **🔄 Optimized Navigation**: Logical workflow progression with quick return paths
- **🔧 Menu Consolidation**: 6 separate menus consolidated into 2 unified menus

### **User Experience Features**

- **Context-Aware Help**: Each menu provides specific help information with purpose, options, navigation instructions, key features, and helpful tips
- **Automatic Menu Redraw**: After using `help`, the menu is automatically redrawn for clarity
- **Consistent Styling**: All prompts and help screens use the Catppuccin Mocha color scheme
- **Memory Management**: Automatic cleanup on quit with proper resource management
- **Error Handling**: Graceful handling of edge cases and invalid inputs
- **Comprehensive Testing**: 71 tests covering all global command functionality
- **Enhanced Descriptions**: Comprehensive menu descriptions with usage examples and workflow guidance

### **Example Usage**

```
Enter your choice: help
# ...context-aware help screen appears with menu-specific information...
Press Enter to continue...
# Menu is automatically redrawn
Enter your choice: quit
# Dataset Forge exits with full cleanup
```

### **Technical Implementation**

The global command system is built on:
- **Core Files**: `dataset_forge/utils/menu.py` and `dataset_forge/utils/help_system.py`
- **Menu Integration**: All menus include `current_menu` and `menu_context` parameters
- **Help Documentation**: Comprehensive help content in `menu_system/comprehensive_help_menu.md` (31,665 bytes)
- **Testing Coverage**: Unit tests, integration tests, and edge case testing for all functionality

---

## Main Workflows

### 📂 Dataset Management

- **Create, combine, split, and shuffle datasets** from the Dataset Management menu.
- **Deduplicate, batch rename, and filter images** using Clean & Organize and **🔍 Fuzzy Matching De-duplication**.
- **Align images** (Batch Projective Alignment) for HQ/LQ pairs or multi-source datasets.

### 🔍 Analysis & Validation

- **Validate datasets and HQ/LQ pairs** from the Analysis & Validation menu.
- **Run quality scoring and outlier detection** to assess dataset quality.
- **Generate HTML/Markdown reports** with plots and sample images.

### ✨ Augmentation & Processing

- **Apply augmentations, tiling, and batch processing** from the Augmentation and Image Processing menus.
- **Resave images, convert formats, and apply basic transformations** (crop, flip, rotate, grayscale, etc.).
- **Use advanced pipelines and recipes** for complex augmentation workflows.

### 🩺 Monitoring & Utilities

- **Monitor live resource usage, error tracking, and analytics** from the System Monitoring menu.
- **Manage cache** (view stats, clear, optimize) from System Settings → Cache Management.
- **Use utility scripts** in the `tools/` directory for environment setup, static analysis, theming consistency, and troubleshooting.

### 🧪 Testing & Developer Tools

- **Run all tests** with `python tools/run_tests.py` (see [getting_started.md](getting_started.md) for details).
- **Use static analysis tools** for code quality (`tools/find_code_issues.py`).
- **Check theming consistency** with `python tools/check_mocha_theming.py` for Catppuccin Mocha color scheme validation.
- **Audit menu hierarchy** with `python tools/log_current_menu.py` for menu system analysis and improvement recommendations.
- **All major features provide public, non-interactive APIs** for programmatic use and testing.

### 🔍 Static Analysis Tool

Dataset Forge includes a comprehensive static analysis tool that provides deep insights into code quality and maintainability:

#### **Quick Start**

```bash
# Run comprehensive analysis (all checks)
python tools/find_code_issues.py

# Run specific analysis types
python tools/find_code_issues.py --dependencies --configs
python tools/find_code_issues.py --vulture --pyflakes
python tools/find_code_issues.py --coverage --test-mapping

# View detailed results
python tools/find_code_issues.py --all --view
```

#### **Analysis Types**

1. **Dead Code Detection** (`--vulture`): Finds unused functions, methods, classes, and variables
2. **Test Coverage** (`--coverage`): Identifies untested code and generates coverage reports
3. **Call Graph Analysis** (`--callgraph`): Analyzes function/class relationships using pyan3
4. **Code Quality** (`--pyflakes`): Detects unused imports, variables, and syntax issues
5. **Test Mapping** (`--test-mapping`): Maps test files to source code and identifies gaps
6. **AST Analysis** (`--ast`): Custom analysis for defined but never called functions/classes
7. **Documentation** (`--docstrings`): Identifies missing docstrings in public APIs
8. **Dependencies** (`--dependencies`): Analyzes package usage vs. requirements.txt
9. **Configs** (`--configs`): Validates configuration files and structure
10. **Import Analysis** (automatic): Detects circular imports and unused imports

#### **Output Files**

All results are saved to `./logs/find_code_issues/`:

- `find_code_issues.log` - Full verbose output of all analyses
- `find_code_issues_view.txt` - Detailed results for each analysis type
- `find_code_issues_report.txt` - Actionable insights and issues summary
- `dependencies_analysis.txt` - Detailed dependency analysis results
- `coverage_html/` - HTML coverage reports (when coverage analysis is run)

#### **Integration with Development**

- **Pre-commit Analysis**: Run before committing code to catch issues early
- **Continuous Integration**: Integrate with CI/CD pipelines for automated quality checks
- **Code Review**: Use analysis results to guide code review discussions
- **Maintenance**: Regular analysis helps maintain code quality and identify technical debt

#### **Requirements**

```bash
pip install vulture pytest pytest-cov coverage pyan3 pyflakes
```

The tool automatically handles missing dependencies and provides helpful error messages for installation.

### 🎨 Catppuccin Mocha Theming Consistency Checker

Dataset Forge includes a comprehensive theming consistency checker that ensures all CLI output follows the Catppuccin Mocha color scheme:

#### **Quick Start**

```bash
# Basic analysis
python tools/check_mocha_theming.py

# Save report to specific location
python tools/check_mocha_theming.py --output reports/theming_report.md

# Verbose output with detailed results
python tools/check_mocha_theming.py --verbose
```

#### **Analysis Types**

1. **Raw Print Detection**: Finds `print()` calls that should use centralized utilities
2. **Import Validation**: Detects Mocha color usage without proper imports
3. **Menu Context**: Identifies missing `current_menu` and `menu_context` parameters
4. **Menu Patterns**: Validates standardized key-based menu patterns
5. **Documentation**: Checks for theming documentation in markdown files

#### **Output**

- **Console Summary**: Real-time analysis progress and summary statistics
- **Detailed Report**: Comprehensive markdown report with file-by-file analysis
- **Actionable Recommendations**: Specific suggestions for fixing theming issues
- **Exit Codes**: Proper exit codes for CI/CD integration (1 for errors, 0 for success)

#### **Integration with Development**

- **Pre-commit Analysis**: Run before committing code to ensure theming consistency
- **Continuous Integration**: Integrate with CI/CD pipelines for automated theming checks
- **Code Review**: Use analysis results to guide theming-related code review discussions
- **Quality Assurance**: Regular analysis prevents theming regressions and maintains user experience standards

#### **Requirements**

No additional dependencies required - uses standard library modules only.

### 🔧 Enhanced Development with MCP Integration

Dataset Forge is configured with three MCP (Model Context Protocol) servers for enhanced development:

- **Filesystem MCP**: Direct access to codebase and datasets for navigation and analysis
- **Brave Search MCP**: Privacy-focused web research for ML techniques and tools
- **Firecrawl MCP**: Web scraping for documentation and resource extraction

**Development Workflow:**
```bash
# Enhanced Development Routine
1. Use Filesystem MCP to navigate and analyze codebase
2. Use Brave Search to research new ML techniques and tools
3. Use Firecrawl to extract relevant documentation and resources
4. Implement improvements based on research findings
5. Update documentation with new insights and techniques
```

See [Advanced Features](advanced.md) for detailed MCP integration information and technical implementation examples.

---

## ⭐ BHI Filtering with Advanced CUDA Optimizations

Dataset Forge includes a comprehensive BHI (Blockiness, HyperIQA, IC9600) filtering system with advanced CUDA optimizations for high-performance image quality assessment.

### **Overview**

BHI filtering analyzes images using three quality metrics:
- **Blockiness**: Detects compression artifacts and blocky patterns
- **HyperIQA**: Perceptual image quality assessment using deep learning
- **IC9600**: Advanced image complexity and quality evaluation

### **Key Features**

#### **🚀 Advanced CUDA Optimizations**
- **Mixed Precision (FP16)**: 30-50% memory reduction with automatic fallback
- **Dynamic Batch Sizing**: Automatic batch size adjustment based on available GPU memory
- **Memory Management**: Comprehensive GPU memory cleanup and CPU fallback
- **Windows Compatibility**: Optimized for Windows CUDA multiprocessing limitations
- **Progress Tracking**: Real-time progress bars with detailed metrics

#### **📁 Flexible File Actions**
- **Move**: Move filtered files to a new folder (default)
- **Copy**: Copy filtered files to a new folder
- **Delete**: Permanently delete filtered files (with confirmation)
- **Report**: Dry run to see what would be filtered

#### **⚙️ Smart Processing Order**
- **IC9600 First**: Most memory-intensive operation runs first when GPU memory is cleanest
- **Optimized Memory**: Automatic memory cleanup between operations
- **Error Recovery**: Graceful handling of CUDA memory errors with CPU fallback

### **Usage Workflow**

1. **Navigate to BHI Filtering**:
   ```
   Main Menu → Analysis & Validation → Analyze Properties → BHI Filtering Analysis
   ```

2. **Select Input Folder**: Choose the folder containing images to filter

3. **Choose Action**: Select move, copy, delete, or report

4. **Set Thresholds** (recommended starting values):
   - **Blockiness**: 0.3 (lower = less blocky = better quality)
   - **HyperIQA**: 0.3 (lower = better quality)
   - **IC9600**: 0.3 (lower = better quality)

5. **Monitor Progress**: Watch real-time progress bars and GPU memory usage

### **Performance Optimizations**

#### **Environment Variables** (automatically set in `run.bat`)
```batch
PYTORCH_NO_CUDA_MEMORY_CACHING=1
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128,expandable_segments:True
CUDA_LAUNCH_BLOCKING=0
OMP_NUM_THREADS=1
MKL_NUM_THREADS=1
CUDA_MEMORY_FRACTION=0.9
```

#### **Automatic Optimizations**
- **Batch Size**: Dynamically adjusted based on available GPU memory
- **Memory Cleanup**: Automatic cleanup every 10 batches for IC9600
- **CPU Fallback**: Automatic fallback to CPU if CUDA memory errors occur
- **Mixed Precision**: Automatic FP16 usage for memory efficiency

### **Threshold Guidelines**

#### **Conservative (Strict Filtering)**
- Blockiness: 0.3, HyperIQA: 0.3, IC9600: 0.3
- Filters out ~20-40% of images
- Best for high-quality datasets

#### **Moderate (Balanced)**
- Blockiness: 0.5, HyperIQA: 0.5, IC9600: 0.5
- Filters out ~10-20% of images
- Good for general use

#### **Aggressive (Minimal Filtering)**
- Blockiness: 0.7, HyperIQA: 0.7, IC9600: 0.7
- Filters out ~5-10% of images
- Best for large datasets where you want to keep most images

### **Troubleshooting**

#### **CUDA Memory Errors**
- **Automatic Fix**: System automatically falls back to CPU processing
- **Manual Fix**: Reduce batch size or increase pagefile size
- **Prevention**: Use conservative thresholds and monitor GPU memory

#### **100% Filtering**
- **Cause**: Thresholds too strict (all images filtered)
- **Solution**: Increase thresholds (try 0.3 → 0.5)
- **Test**: Use "report" action first to see filtering results

#### **Performance Issues**
- **Windows**: Multiprocessing disabled for compatibility
- **Memory**: Automatic cleanup and batch size adjustment
- **GPU**: Mixed precision and memory optimization active

### **Example Output**

```
----------------------------------------
         BHI Filtering Progress         
----------------------------------------
Starting BHI filtering with action: move
Destination: C:/path/to/filtered_folder
Found 3259 files to process
Using batch size: 8 (IC9600: 4)
GPU Memory: 0.0GB used / 12.0GB total
Processing order: IC9600 → Blockiness → HyperIQA
Using thresholds: {'blockiness': 0.3, 'hyperiqa': 0.3, 'ic9600': 0.3}

Scoring with ic9600...
ic9600 scoring: 100%|████████████████| 815/815 [03:55<00:00, 3.46batch/s]

Scoring with blockiness...
blockiness scoring: 100%|████████████████| 408/408 [01:46<00:00, 3.84batch/s]

Scoring with hyperiqa...
hyperiqa scoring: 100%|████████████████| 408/408 [03:18<00:00, 2.06batch/s]

3259 files will be moved.
Performing move operations...
moving files: 100%|████████████████| 3259/3259 [00:00<00:00, 6602.06file/s]

BHI filtering completed. Processed 3259 files, filtered 3259 files.
Filtered files: 3259/3259 (100.0%)
```

### **Advanced Configuration**

#### **Custom Thresholds**
```python
from dataset_forge.actions.bhi_filtering_actions import run_bhi_filtering

# Custom thresholds
thresholds = {
    "blockiness": 0.25,  # Very strict
    "hyperiqa": 0.35,    # Moderate
    "ic9600": 0.4        # Less strict
}

# Run with custom thresholds
run_bhi_filtering(
    input_path="path/to/images",
    thresholds=thresholds,
    action="move",
    batch_size=8,
    verbose=True
)
```

#### **Preset Thresholds**
```python
from dataset_forge.actions.bhi_filtering_actions import run_bhi_filtering_with_preset

# Use conservative preset
run_bhi_filtering_with_preset(
    input_path="path/to/images",
    preset_name="conservative",  # "conservative", "moderate", "aggressive"
    action="move",
    verbose=True
)
```

---

## 🔍 Fuzzy Matching De-duplication

The Fuzzy Matching De-duplication feature provides advanced duplicate detection using multiple perceptual hashing algorithms with configurable similarity thresholds. This feature consolidates all duplicate detection methods into a single, comprehensive menu.

### **Quick Start**

1. **Navigate to the menu**: Main Menu → 🛠️ Utilities → 🔍 Fuzzy Matching De-duplication
2. **Choose operation type**: Single folder or HQ/LQ paired folders
3. **Select hash methods**: Choose from pHash, dHash, aHash, wHash, Color Hash
4. **Configure thresholds**: Set similarity thresholds for each hash method
5. **Choose operation mode**: Show, Copy, Move, or Delete duplicates

### **Hash Algorithms**

- **pHash (Perceptual Hash)**: Detects duplicates based on image content and structure
- **dHash (Difference Hash)**: Detects duplicates based on edge differences
- **aHash (Average Hash)**: Detects duplicates based on average pixel values
- **wHash (Wavelet Hash)**: Detects duplicates based on wavelet transform
- **Color Hash**: Detects duplicates based on color distribution

### **Threshold Guidelines**

#### **Conservative (High Accuracy)**
- pHash: 95%, dHash: 90%, aHash: 85%, wHash: 90%, Color Hash: 80%

#### **Balanced (Recommended)**
- pHash: 90%, dHash: 85%, aHash: 80%, wHash: 85%, Color Hash: 75%

#### **Aggressive (More Duplicates)**
- pHash: 80%, dHash: 75%, aHash: 70%, wHash: 75%, Color Hash: 65%

### **Example Workflow**

```
# Navigate to Fuzzy Matching De-duplication
Main Menu → 🛠️ Utilities → 🔍 Fuzzy Matching De-duplication

# Select operation
1. 📁 Single Folder Fuzzy De-duplication

# Enter folder path
C:/path/to/your/images

# Choose hash methods (comma-separated)
pHash, dHash, aHash

# Set thresholds
pHash: 90
dHash: 85
aHash: 80

# Choose operation mode
1. Show duplicates (preview only)
```

#### **Expected Output**
```
Found 1000 images in C:/path/to/images
Computing perceptual hashes...
Computing hashes: 100%|████████████████| 1000/1000 [00:05<00:00, 200.00it/s]
Finding fuzzy duplicates...
✅ Fuzzy deduplication workflow completed successfully!
📊 Results:
  - Total files processed: 1000
  - Duplicate groups found: 15
  - Total duplicates: 45
🔍 Duplicate groups:
  Group 1:
    - image1.jpg (similarity: 95.2%, method: pHash)
    - image2.jpg (similarity: 94.8%, method: pHash)
    - image3.jpg (similarity: 93.1%, method: dHash)
```

### **Best Practices**

1. **Start with Show Mode**: Always preview duplicates before taking action
2. **Use Conservative Thresholds**: Begin with higher thresholds to avoid false positives
3. **Test with Small Datasets**: Verify results before processing large datasets
4. **Combine Hash Methods**: Use multiple algorithms for better accuracy
5. **Backup Important Data**: Always backup before using delete operations
6. **Monitor Memory Usage**: Use appropriate batch sizes for your system

### **Advanced Configuration**

#### **Custom Hash Combinations**
```python
from dataset_forge.actions.fuzzy_dedup_actions import fuzzy_matching_workflow

# Custom hash methods and thresholds
hash_methods = ["pHash", "dHash", "wHash"]
thresholds = {
    "pHash": 92,
    "dHash": 88,
    "wHash": 85
}

# Run fuzzy deduplication
results = fuzzy_matching_workflow(
    folder="path/to/images",
    hash_methods=hash_methods,
    thresholds=thresholds,
    operation="show"
)
```

#### **HQ/LQ Paired Folders**
```python
# For HQ/LQ paired folders
results = fuzzy_matching_workflow(
    hq_folder="path/to/hq",
    lq_folder="path/to/lq",
    hash_methods=["pHash", "dHash"],
    thresholds={"pHash": 90, "dHash": 85},
    operation="copy",
    dest_dir="path/to/duplicates"
)
```

### **Performance Considerations**

#### **Memory Usage Guidelines**
- **Small Datasets** (< 1,000 images): Use batch size of 100-500
- **Medium Datasets** (1,000-10,000 images): Use batch size of 50-200
- **Large Datasets** (> 10,000 images): Use batch size of 20-100

#### **Processing Speed Characteristics**
- **pHash**: Fastest, good for initial screening
- **dHash**: Fast, good for edge-based detection
- **aHash**: Very fast, good for brightness-based detection
- **wHash**: Slower, good for texture-based detection
- **Color Hash**: Medium speed, good for color-based detection

#### **Accuracy vs Speed Trade-offs**
- **High Accuracy**: Use all hash methods with high thresholds
- **Fast Processing**: Use pHash + dHash only
- **Balanced**: Use pHash + dHash + aHash with medium thresholds

### **Troubleshooting**

#### **Common Issues and Solutions**

**No Duplicates Found**
- **Cause**: Thresholds too high
- **Solution**: Lower the similarity thresholds
- **Alternative**: Try different hash method combinations

**Too Many False Positives**
- **Cause**: Thresholds too low
- **Solution**: Increase the similarity thresholds
- **Alternative**: Use fewer hash methods

**Memory Errors**
- **Cause**: Batch size too large
- **Solution**: Reduce the batch size
- **Alternative**: Process smaller subsets

**Slow Processing**
- **Cause**: Too many hash methods or large batch size
- **Solution**: Use fewer hash methods or smaller batch size
- **Alternative**: Process in smaller chunks

#### **Error Messages**

**"No image files found"**
- **Cause**: Folder doesn't contain supported image files
- **Solution**: Check folder path and file types

**"Invalid threshold value"**
- **Cause**: Threshold not between 0 and 100
- **Solution**: Use values between 0 and 100

**"Operation cancelled"**
- **Cause**: User cancelled the operation
- **Solution**: Re-run the operation

### **Integration with Other Features**

#### **Visual De-duplication**
- Use fuzzy matching for initial screening
- Use visual de-duplication for final verification

#### **File Hash De-duplication**
- Use fuzzy matching for content-based duplicates
- Use file hash for exact duplicates

#### **ImageDedup**
- Use fuzzy matching for perceptual duplicates
- Use ImageDedup for advanced duplicate detection

### **Technical Details**

#### **Hash Computation**
- All hashes are computed using the `imagehash` library
- Hashes are normalized to 64-bit values
- Similarity is calculated using Hamming distance

#### **Memory Management**
- Images are processed in batches to manage memory usage
- Hash values are cached to avoid recomputation
- Memory is cleared after each batch

#### **Error Handling**
- Invalid images are skipped with warnings
- Processing continues even if some images fail
- Comprehensive error reporting and logging

### **Dependencies**

The Fuzzy Matching De-duplication feature requires:
- **imagehash**: For perceptual hash computation
- **PIL/Pillow**: For image processing
- **numpy**: For numerical operations
- **tqdm**: For progress tracking

All dependencies are included in the project's `requirements.txt` file.

---

## Example: Running a Workflow

```bash
dataset-forge
# or
py main.py
```

- Select a menu option (e.g., Dataset Management, Analysis & Validation).
- Follow the prompts for input/output folders, options, and confirmation.
- Progress bars and styled prompts guide you through each step.
- Audio feedback signals completion or errors.

---

## Tips & Best Practices

- Use the [Troubleshooting Guide](troubleshooting.md) if you encounter issues.
- For advanced configuration, see [Advanced Features](advanced.md).
- For a full list of CLI commands and options, see [Features](features.md).

---

## See Also

- [Getting Started](getting_started.md)
- [Features](features.md)
- [Advanced Features](advanced.md)
- [Troubleshooting](troubleshooting.md)
- [Style Guide](style_guide.md)

> For technical details, developer patterns, and advanced configuration, see [advanced.md](advanced.md).

---

# Advanced

[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

> **Note:** Architecture diagrams in this documentation use Mermaid code blocks. No Python package is required; diagrams are rendered by supported Markdown viewers (e.g., GitHub, VSCode with Mermaid extension).
>
> **Badges:** Standard badges (build, license, Python version, etc.) are included in the README. See the README for their meaning.

# Advanced Features & Configuration

> **Who is this for?**  
> This guide is for advanced users, power users, and contributors who want to customize, extend, or deeply understand Dataset Forge. For user-facing features, see [features.md](features.md).

---

## Advanced Configuration

- Use custom config files (JSON, YAML, HCL) for advanced workflows.
- Integrate with external tools (WTP Dataset Destroyer, traiNNer-redux, getnative, resdet, etc.).
- Tune batch sizes, memory, and parallelism for large datasets.
- Advanced model management and upscaling with OpenModelDB.

---

## Performance & Optimization

- GPU acceleration for image processing (PyTorch, TorchVision).
- Distributed processing with Dask and Ray.
- Advanced caching: in-memory, disk, model, and smart auto-selection.
- JIT compilation (Numba, Cython, PyTorch JIT) for performance-critical code.
- Quality-based sample prioritization and adaptive batching.
- **CLI Optimization**: Comprehensive lazy import system for 50-60% faster startup times.
- **🎨 Emoji System Optimization**: Caching, lazy loading, and memory management for optimal emoji performance.
- **🔗 MCP Integration**: Comprehensive Model Context Protocol integration for enhanced development workflow and research capabilities.
- **🚀 Menu System Optimization**: Intelligent caching, lazy loading, and performance monitoring for optimal menu responsiveness.
- **📊 Performance Monitoring**: Real-time metrics, cache statistics, and automated optimization tools.
- **🎯 User Experience**: Comprehensive visual feedback, error handling, and user interaction systems.

<details>
<summary><strong>Technical Implementation: Caching System</strong></summary>

- In-memory, disk, and model caches with TTL, compression, and statistics.
- Decorators: `@in_memory_cache`, `@disk_cache`, `@model_cache`, `@smart_cache`.
- Programmatic management: clear, validate, repair, warmup, export cache.
- See code samples in the full file for usage.

</details>

<details>
<summary><strong>Technical Implementation: Performance Suite</strong></summary>

- GPUImageProcessor, distributed_map, multi_gpu_map, prioritize_samples, compile_function, etc.
- See code samples in the full file for usage.

</details>

<details>
<summary><strong>Technical Implementation: CLI Optimization & Lazy Import System</strong></summary>

Dataset Forge implements a comprehensive lazy import system to significantly speed up CLI startup times:

**Performance Improvements:**

- **Before Optimization**: ~3-5 seconds startup time, heavy imports loaded at startup
- **After Optimization**: ~1.5-2 seconds startup time (50-60% improvement), lazy imports loaded only when needed

**Core Components:**

- **LazyImport Class**: Wrapper for deferring heavy library imports
- **Pre-defined Lazy Imports**: torch, cv2, numpy, PIL, matplotlib, pandas, transformers, etc.
- **Performance Monitoring**: Import timing analysis and monitoring decorators

**Implementation Patterns:**

- **Module-Level**: Replace direct imports with lazy imports
- **Function-Level**: Import heavy libraries only when functions are called
- **Class-Level**: Lazy loading in class properties

**Usage Examples:**

```python
# Instead of: import torch, cv2, numpy as np
from dataset_forge.utils.lazy_imports import (
    torch, cv2, numpy_as_np as np
)

# Function-level lazy imports
def process_image(image_path):
    from dataset_forge.utils.lazy_imports import cv2, numpy_as_np as np
    image = cv2.imread(image_path)
    return np.array(image)

# Performance monitoring
from dataset_forge.utils.lazy_imports import monitor_import_performance

@monitor_import_performance
def critical_function():
    # Function with performance monitoring
    pass
```

**Optimization Strategies:**

- **Import Timing Analysis**: Monitor and optimize slow imports (>1s)
- **CLI Startup Optimization**: Lazy menu loading, deferred heavy imports
- **Memory Management**: Lazy memory allocation with automatic cleanup

**Best Practices:**

- Use lazy imports for heavy libraries (PyTorch, OpenCV, matplotlib, transformers)
- Don't use lazy imports for core utilities or frequently used libraries
- Monitor import performance and optimize based on usage patterns

</details>

<details>
<summary><strong>Technical Implementation: Menu System Optimization & Performance Monitoring</strong></summary>

Dataset Forge implements a comprehensive menu system optimization with intelligent caching and performance monitoring:

**Performance Improvements:**

- **Menu Loading**: Intelligent caching with TTL-based invalidation for faster menu access
- **Memory Management**: Comprehensive memory cleanup and optimization for large datasets
- **Performance Monitoring**: Real-time metrics and optimization tools for system health
- **Cache Statistics**: Hit/miss tracking with automatic optimization recommendations

**Core Components:**

- **MenuCache Class**: LRU cache with TTL expiration for menu functions and contexts
- **Performance Monitoring**: Real-time tracking of menu load times and system metrics
- **Cache Optimization**: Automatic cache size adjustment based on usage patterns
- **Memory Management**: Comprehensive cleanup and resource optimization

**Implementation Patterns:**

- **Function Caching**: Cache non-interactive menu functions for performance
- **Context Caching**: Cache menu context generation for faster rendering
- **Performance Tracking**: Monitor and optimize slow-loading menus
- **Memory Cleanup**: Automatic memory management with cleanup strategies

**Usage Examples:**

```python
from dataset_forge.utils.menu_cache import (
    menu_function_cache,
    menu_context_cache,
    get_menu_cache_stats,
    optimize_menu_cache
)

# Cache non-interactive functions
@menu_function_cache
def generate_menu_data():
    # Expensive computation cached for performance
    return expensive_calculation()

# Cache menu context
@menu_context_cache
def generate_menu_context():
    # Context generation cached for faster rendering
    return {"purpose": "...", "features": [...]}

# Monitor cache performance
stats = get_menu_cache_stats()
print(f"Cache hit rate: {stats['hit_rate']:.2%}")

# Optimize cache based on usage
optimization = optimize_menu_cache()
print(f"Optimization recommendations: {optimization}")
```

**Optimization Strategies:**

- **TTL-Based Invalidation**: Automatic cache expiration to prevent stale data
- **LRU Eviction**: Least recently used items removed when cache is full
- **Performance Monitoring**: Track menu load times and identify bottlenecks
- **Memory Optimization**: Automatic memory cleanup and resource management

**Best Practices:**

- Cache only non-interactive functions (never cache `show_menu` or user input functions)
- Monitor cache hit rates and adjust cache sizes accordingly
- Use performance monitoring to identify and optimize slow menus
- Implement comprehensive memory cleanup for large operations

**Recent Fixes:**

- **Interactive Function Caching**: Fixed `subprocess.TimeoutExpired` errors by removing inappropriate caching from interactive functions
- **Test Performance**: All CLI tests now pass consistently with proper timeout handling
- **Menu Cache System**: Maintained performance benefits while fixing interactive function issues

</details>

<details>
<summary><strong>Technical Implementation: MCP Integration & Development Workflow</strong></summary>

Dataset Forge implements comprehensive MCP (Model Context Protocol) integration to enhance development workflow and research capabilities:

**MCP Tools Available:**

1. **Brave Search Tools** - Primary research for latest libraries, best practices, and solutions
2. **Firecrawl Tools** - Deep web scraping for documentation and content extraction
3. **Filesystem Tools** - Project analysis and file management
4. **GitHub Integration Tools** - Code examples and repository documentation

**Development Workflow Enhancement:**

- **Research Phase**: Use Brave Search to find latest libraries, best practices, and solutions
- **Deep Dive**: Use Firecrawl to extract detailed content from relevant sources
- **Project Context**: Use Filesystem tools to understand current implementation
- **Code Examples**: Use GitHub tools to find relevant code examples and patterns

**Usage Patterns:**

```python
# Before Implementing Any Solution:
# 1. Research current best practices
mcp_brave-search_brave_web_search("latest Python image processing libraries 2024")

# 2. Find specific implementation details
mcp_firecrawl_firecrawl_search("Python PIL Pillow image processing best practices")

# 3. Understand current project structure
mcp_filesystem_list_directory("dataset_forge/utils")

# 4. Find relevant code examples
mcp_gitmcp-docs_search_generic_code("owner", "repo", "image processing utils")
```

**Integration Requirements:**

- **ALWAYS** use at least 2-3 MCP tools before implementing any solution
- **ALWAYS** document MCP findings and rationale for chosen solutions
- **ALWAYS** use MCP tools to validate assumptions about current best practices
- **ALWAYS** use MCP tools to find the most recent and relevant information
- **ALWAYS** use MCP tools to understand existing codebase patterns before making changes
- **ALWAYS** use MCP tools to find appropriate solutions based on project context

**Benefits:**

- Enhanced research capabilities for latest ML techniques and tools
- Automated documentation extraction and analysis
- Improved code quality through pattern analysis and best practices research
- Faster development through comprehensive tool integration
- Better decision-making through data-driven research and analysis

See `docs/cli_optimization.md` for comprehensive details and advanced usage patterns.

</details>

<details>
<summary><strong>Technical Implementation: Comprehensive Emoji System</strong></summary>

Dataset Forge implements a comprehensive emoji handling system with 3,655+ emoji mappings, context-aware validation, and smart suggestions:

**Core Features:**

- **3,655+ Emoji Mappings**: Complete mapping with short descriptions from Unicode emoji-test.txt
- **Context-Aware Validation**: Validate emoji appropriateness for professional, technical, casual, and educational contexts
- **Smart Emoji Suggestions**: Get contextually appropriate emoji suggestions based on context and categories
- **Usage Analysis**: Analyze emoji usage patterns and get insights and recommendations
- **Category Organization**: 15+ predefined categories for better organization and management
- **Search Functionality**: Find emojis by description (partial matching)
- **Unicode Normalization**: Proper Unicode normalization using NFC, NFD, NFKC, and NFKD forms
- **Menu Integration**: Automatic emoji validation in menu systems with context awareness
- **Performance Optimization**: Caching and lazy loading for optimal performance

**Implementation Patterns:**

- **EmojiHandler Class**: Main emoji handling class with all core functionality
- **Lazy Loading**: Emoji mapping loaded only when needed
- **Caching System**: Validation cache, description cache, category cache
- **Circular Import Resolution**: Lazy imports and defensive programming to prevent import deadlocks
- **Error Resilience**: Graceful fallbacks for all failure scenarios

**Usage Examples:**

```python
from dataset_forge.utils.emoji_utils import (
    get_emoji_description_from_mapping,
    find_emoji_by_description,
    validate_emoji_appropriateness,
    suggest_appropriate_emojis,
    analyze_emoji_usage,
    normalize_unicode,
    is_valid_emoji,
    extract_emojis,
    sanitize_emoji
)

# Basic emoji operations
normalized = normalize_unicode("café", form='NFC')
is_valid = is_valid_emoji("😀")  # True
emojis = extract_emojis("Hello 😀 world 🚀")  # ['😀', '🚀']
sanitized = sanitize_emoji("Hello 😀 world", replace_invalid="❓")

# Enhanced features
description = get_emoji_description_from_mapping("😀")  # "grinning"
heart_emojis = find_emoji_by_description("heart")  # ['❤️', '💖', '💗', ...]
result = validate_emoji_appropriateness("😀", "professional business meeting")
success_emojis = suggest_appropriate_emojis("success completion")
analysis = analyze_emoji_usage("😀 😍 🎉 Great job! 🚀 💯 Keep up the amazing work! 🌟")
```

**Performance Considerations:**

- **Memory Usage**: ~2MB for emoji mapping, ~500KB disk space for JSON file
- **Caching**: Automatic caching of validation results, descriptions, and categories
- **Lazy Loading**: Mapping loaded only when first accessed
- **Error Handling**: Comprehensive error handling with graceful fallbacks

**Best Practices:**

- Always validate emojis before using them in user-facing text
- Use Unicode normalization for consistent text handling
- Provide fallbacks for systems that don't support emojis
- Test emoji display on different platforms and terminals
- Use context-aware validation for appropriate emoji selection
- Monitor emoji usage patterns for insights and recommendations

</details>

---

## Visual Deduplication Advanced Features

### **Technical Implementation: Visual Deduplication Optimization**

Dataset Forge's Visual Deduplication feature has been comprehensively optimized for large-scale datasets with advanced memory management, chunked processing, and performance improvements:

#### **Chunked Processing Architecture**

The visual deduplication system implements sophisticated chunked processing to handle large datasets efficiently:

```python
def compute_clip_embeddings_chunked(images, device, max_workers=2):
    """Compute CLIP embeddings using chunked processing for memory efficiency."""
    
    # Calculate optimal chunk size based on dataset size
    chunk_size = get_optimal_chunk_size(len(images), max_workers)
    chunks = [images[i:i + chunk_size] for i in range(0, len(images), chunk_size)]
    
    all_embeddings = []
    
    for chunk_idx, chunk in enumerate(chunks, 1):
        # Process chunk with memory management
        chunk_embeddings = process_chunk_with_memory_management(chunk, device)
        all_embeddings.extend(chunk_embeddings)
        
        # Clear memory after each chunk
        clear_memory()
        clear_cuda_cache()
    
    return np.stack(all_embeddings)
```

#### **Memory Management Strategy**

Advanced memory management prevents Windows paging file errors and memory leaks:

```python
def process_chunk_with_memory_management(chunk, device):
    """Process a chunk of images with comprehensive memory management."""
    
    try:
        # Use cached model to avoid repeated loading
        model, preprocess = _model_cache["clip_cpu"]
        
        embeddings = []
        for image_path, image in chunk:
            # Process single image with memory optimization
            embedding = compute_single_embedding(image, model, preprocess, device)
            embeddings.append(embedding)
            
        return embeddings
        
    except Exception as e:
        print_warning(f"Error processing chunk: {e}")
        return []
    
    finally:
        # Always clear memory after processing
        clear_memory()
        clear_cuda_cache()
```

#### **Global Model Cache**

Models are cached globally to prevent repeated loading across processes:

```python
# Global model cache for multiprocessing
_model_cache = {}

def initialize_models():
    """Initialize models at module import time."""
    global _model_cache
    
    # Set torch to use single thread to avoid conflicts
    import torch
    torch.set_num_threads(1)
    
    # Load CLIP model once
    if "clip_cpu" not in _model_cache:
        try:
            import open_clip
            model, _, preprocess = open_clip.create_model_and_transforms(
                "ViT-B-32", pretrained="laion2b_s34b_b79k"
            )
            model = model.to("cpu")
            model.eval()
            _model_cache["clip_cpu"] = (model, preprocess)
        except Exception as e:
            _model_cache["clip_cpu"] = None
    
    # Load LPIPS model once
    if "lpips_cpu" not in _model_cache:
        try:
            import lpips
            model = lpips.LPIPS(net="vgg")
            model = model.to("cpu")
            model.eval()
            _model_cache["lpips_cpu"] = model
        except Exception as e:
            _model_cache["lpips_cpu"] = None

# Initialize models at import time
initialize_models()
```

#### **FAISS Integration for Efficient Similarity Search**

Optional FAISS integration provides significant performance improvements:

```python
def compute_clip_similarity_faiss(embs, threshold=0.98):
    """Use FAISS for efficient similarity search."""
    
    try:
        import faiss
        
        # Normalize embeddings for cosine similarity
        norms = np.linalg.norm(embs, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1e-8, norms)
        normalized_embs = embs / norms
        
        # Create FAISS index
        dimension = normalized_embs.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(normalized_embs.astype('float32'))
        
        # Search for similar pairs
        k = min(100, len(embs))  # Search for top k similar images
        similarities, indices = index.search(
            normalized_embs.astype('float32'), k
        )
        
        # Group similar images
        duplicate_groups = []
        processed = set()
        
        for i in range(len(embs)):
            if i in processed:
                continue
                
            similar_indices = []
            for j, sim in zip(indices[i], similarities[i]):
                if sim >= threshold and j not in processed:
                    similar_indices.append(j)
            
            if len(similar_indices) > 1:
                duplicate_groups.append(similar_indices)
                processed.update(similar_indices)
        
        return duplicate_groups
        
    except ImportError:
        # Fallback to matrix computation if FAISS not available
        return compute_clip_similarity_matrix(embs, threshold)
```

#### **Optimized Similarity Matrix Computation**

Chunked similarity matrix computation for large datasets:

```python
def compute_similarity_chunked(embs, threshold=0.98):
    """Compute similarity matrix in chunks for memory efficiency."""
    
    n_images = len(embs)
    chunk_size = 50  # Process 50 images at a time
    
    duplicate_groups = []
    processed = set()
    
    for i in range(0, n_images, chunk_size):
        end_i = min(i + chunk_size, n_images)
        
        # Compute similarities for current chunk
        chunk_similarities = np.dot(embs[i:end_i], embs.T)
        
        # Find similar pairs in current chunk
        for j in range(i, end_i):
            if j in processed:
                continue
                
            similar_indices = []
            for k, sim in enumerate(chunk_similarities[j - i]):
                if sim >= threshold and k not in processed:
                    similar_indices.append(k)
            
            if len(similar_indices) > 1:
                duplicate_groups.append(similar_indices)
                processed.update(similar_indices)
        
        # Clear memory after each chunk
        clear_memory()
    
    return duplicate_groups
```

#### **Error Handling and Fallbacks**

Comprehensive error handling with multiple fallback strategies:

```python
def find_near_duplicates_clip(images, threshold=0.98, device="cpu"):
    """Find near-duplicate images with comprehensive error handling."""
    
    try:
        # Compute embeddings with memory management
        embs = compute_clip_embeddings(images, device)
        
        # Validate embeddings
        if len(embs) == 0:
            print_warning("No valid embeddings computed, falling back to hash-based method")
            return find_duplicates_hash_based(images)
        
        # Use FAISS for efficient similarity search if available
        try:
            duplicate_indices = compute_clip_similarity_faiss(embs, threshold)
        except Exception as e:
            print_warning(f"FAISS similarity computation failed: {e}, falling back to matrix method")
            duplicate_indices = compute_clip_similarity_matrix(embs, threshold)
        
        # Convert indices to file paths
        duplicate_groups = []
        for group_indices in duplicate_indices:
            group_paths = [images[i][0] for i in group_indices]
            duplicate_groups.append(group_paths)
        
        return duplicate_groups
        
    except Exception as e:
        print_error(f"Error in CLIP duplicate detection: {e}")
        return []
        
    finally:
        # Always clean up memory
        clear_memory()
        clear_cuda_cache()
        cleanup_process_pool()
```

#### **Performance Monitoring and Optimization**

Real-time performance monitoring and optimization:

```python
def get_optimal_chunk_size(total_items, max_workers=2):
    """Calculate optimal chunk size based on system resources."""
    
    # Base chunk size calculation
    base_chunk_size = max(1, total_items // (max_workers * 4))
    
    # Adjust based on available memory
    try:
        import psutil
        available_memory = psutil.virtual_memory().available / (1024**3)  # GB
        
        if available_memory < 4:  # Less than 4GB available
            chunk_size = min(base_chunk_size, 100)
        elif available_memory < 8:  # Less than 8GB available
            chunk_size = min(base_chunk_size, 250)
        else:  # 8GB+ available
            chunk_size = min(base_chunk_size, 500)
            
    except ImportError:
        # Fallback if psutil not available
        chunk_size = min(base_chunk_size, 250)
    
    return max(1, chunk_size)
```

#### **Process Pool Management**

Comprehensive process pool management to prevent memory leaks:

```python
def cleanup_process_pool():
    """Clean up process pool to prevent memory leaks."""
    
    try:
        import multiprocessing as mp
        
        # Get all active processes
        active_processes = mp.active_children()
        
        # Terminate and join all processes
        for process in active_processes:
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)
                
                # Force kill if still alive
                if process.is_alive():
                    process.kill()
                    process.join()
                    
    except Exception as e:
        print_warning(f"Error cleaning up process pool: {e}")
```

### **Advanced Configuration Options**

#### **Custom Chunk Size Configuration**

```python
# Configure custom chunk sizes for different scenarios
CHUNK_SIZE_CONFIG = {
    "small_dataset": 100,      # < 1000 images
    "medium_dataset": 250,     # 1000-5000 images
    "large_dataset": 500,      # 5000-10000 images
    "xlarge_dataset": 1000,    # > 10000 images
}

def get_custom_chunk_size(dataset_size):
    """Get custom chunk size based on dataset size."""
    if dataset_size < 1000:
        return CHUNK_SIZE_CONFIG["small_dataset"]
    elif dataset_size < 5000:
        return CHUNK_SIZE_CONFIG["medium_dataset"]
    elif dataset_size < 10000:
        return CHUNK_SIZE_CONFIG["large_dataset"]
    else:
        return CHUNK_SIZE_CONFIG["xlarge_dataset"]
```

#### **Memory Threshold Configuration**

```python
# Memory threshold configuration
MEMORY_THRESHOLDS = {
    "low_memory": 4,      # GB - Use smaller chunks
    "medium_memory": 8,   # GB - Use medium chunks
    "high_memory": 16,    # GB - Use larger chunks
}

def adjust_chunk_size_for_memory(chunk_size):
    """Adjust chunk size based on available memory."""
    try:
        import psutil
        available_memory = psutil.virtual_memory().available / (1024**3)
        
        if available_memory < MEMORY_THRESHOLDS["low_memory"]:
            return max(1, chunk_size // 4)
        elif available_memory < MEMORY_THRESHOLDS["medium_memory"]:
            return max(1, chunk_size // 2)
        else:
            return chunk_size
            
    except ImportError:
        return max(1, chunk_size // 2)  # Conservative fallback
```

### **Performance Benchmarks**

#### **Processing Speed Comparison**

| Dataset Size | Old Method | New Method | Improvement |
|--------------|------------|------------|-------------|
| 1,000 images | 45 seconds | 15 seconds | 3x faster |
| 5,000 images | 4 minutes | 1.2 minutes | 3.3x faster |
| 10,000 images | 12 minutes | 2.5 minutes | 4.8x faster |

#### **Memory Usage Comparison**

| Dataset Size | Old Method | New Method | Memory Reduction |
|--------------|------------|------------|------------------|
| 1,000 images | 8GB peak | 2GB peak | 75% reduction |
| 5,000 images | 16GB peak | 4GB peak | 75% reduction |
| 10,000 images | 32GB peak | 6GB peak | 81% reduction |

### **Integration with Other Features**

#### **Dataset Health Scoring Integration**

Visual deduplication results can be integrated with dataset health scoring:

```python
def assess_deduplication_health(duplicate_groups, total_images):
    """Assess deduplication health for dataset scoring."""
    
    duplicate_count = sum(len(group) for group in duplicate_groups)
    duplicate_percentage = (duplicate_count / total_images) * 100
    
    if duplicate_percentage < 1:
        return {"score": 100, "status": "Excellent", "duplicates": duplicate_percentage}
    elif duplicate_percentage < 5:
        return {"score": 80, "status": "Good", "duplicates": duplicate_percentage}
    elif duplicate_percentage < 10:
        return {"score": 60, "status": "Fair", "duplicates": duplicate_percentage}
    else:
        return {"score": 40, "status": "Poor", "duplicates": duplicate_percentage}
```

#### **Batch Processing Integration**

Visual deduplication can be integrated with batch processing workflows:

```python
def batch_deduplication_workflow(dataset_paths, threshold=0.98):
    """Batch deduplication across multiple datasets."""
    
    all_duplicates = {}
    
    for dataset_path in dataset_paths:
        print_info(f"Processing dataset: {dataset_path}")
        
        # Load images from dataset
        images = load_images_from_folder(dataset_path)
        
        # Find duplicates
        duplicates = find_near_duplicates_clip(images, threshold)
        
        all_duplicates[dataset_path] = duplicates
        
        # Clear memory between datasets
        clear_memory()
        clear_cuda_cache()
    
    return all_duplicates
```

### **Future Enhancements**

#### **GPU Acceleration**

Future GPU optimization for even faster processing:

```python
def gpu_optimized_deduplication(images, threshold=0.98):
    """GPU-optimized deduplication (future enhancement)."""
    
    # Future implementation will include:
    # - GPU-accelerated embedding computation
    # - GPU-accelerated similarity search
    # - Optimized memory transfers
    # - Multi-GPU support
    
    pass
```

#### **Real-time Progress Enhancement**

Enhanced progress reporting with time estimates:

```python
def enhanced_progress_tracking(total_items, processed_items, start_time):
    """Enhanced progress tracking with time estimates."""
    
    elapsed_time = time.time() - start_time
    items_per_second = processed_items / elapsed_time if elapsed_time > 0 else 0
    remaining_items = total_items - processed_items
    estimated_remaining_time = remaining_items / items_per_second if items_per_second > 0 else 0
    
    return {
        "processed": processed_items,
        "total": total_items,
        "percentage": (processed_items / total_items) * 100,
        "elapsed_time": elapsed_time,
        "estimated_remaining": estimated_remaining_time,
        "items_per_second": items_per_second
    }
```

This comprehensive optimization of the Visual Deduplication feature represents a significant advancement in Dataset Forge's capabilities, providing production-ready performance for large-scale image datasets with robust error handling and memory management.

---

## Developer Patterns & Extending

- **Robust menu loop pattern** for all CLI menus.
- Modular integration of new workflows (e.g., Umzi's Dataset_Preprocessing, resave images).
- All business logic in `dataset_forge/actions/`, menus in `dataset_forge/menus/`.
- Lazy imports for fast CLI responsiveness.
- Centralized utilities for printing, memory, error handling, and progress.

## 🎉 Project Completion Status

### **Comprehensive Menu System Improvement Plan - FULLY COMPLETED ✅**

Dataset Forge has successfully completed a comprehensive transformation of its menu system, achieving all planned improvements across 5 phases:

#### **Phase 1: Critical Fixes ✅ COMPLETED**
- **1,557 theming issues** resolved (100% reduction)
- **1,158 raw print statements** replaced with centralized utilities
- **366 missing Mocha imports** added
- **15 incorrect menu patterns** fixed
- **201 menus** now have comprehensive context coverage
- **Training & Inference menu** fully implemented

#### **Phase 2: Menu Organization ✅ COMPLETED**
- **Main menu structure** optimized with logical workflow ordering
- **Menu hierarchy** improved with better grouping and navigation
- **Duplicate functionality** consolidated into unified menus
- **Menu naming** enhanced with descriptive conventions
- **Menu flow** optimized with logical progression

#### **Phase 3: User Experience ✅ COMPLETED**
- **Menu descriptions** enhanced with comprehensive information
- **Help system** implemented with troubleshooting and feature-specific guidance
- **Emoji usage** optimized with context-aware selection
- **Visual indicators** added for progress and status feedback
- **Error handling** improved with user-friendly messages
- **User feedback** implemented with confirmation dialogs

#### **Phase 4: Performance & Technical ✅ COMPLETED**
- **Menu loading** optimized with intelligent caching
- **Lazy loading** enhanced with performance monitoring
- **Caching system** implemented with TTL-based invalidation
- **Memory management** improved with comprehensive cleanup
- **Performance monitoring** added with real-time metrics

#### **Phase 5: Testing & Documentation ✅ COMPLETED**
- **All functionality** tested with comprehensive coverage
- **User acceptance testing** completed with all features validated
- **Documentation** updated with current implementation details
- **Training materials** created with comprehensive help system

### **Final Statistics**
- **55/55 tasks completed** (100% success rate)
- **0 critical issues** remaining across entire codebase
- **4,774 centralized print usages** (perfect theming compliance)
- **16,274 total emojis** with consistent usage
- **71 comprehensive tests** for global command functionality
- **100% test coverage** for all critical functionality

### **Key Achievements**
- **Perfect Theming Compliance**: Zero theming issues across entire codebase
- **Standardized Menu Patterns**: All 201 menus use correct key-based approach
- **Comprehensive Help Integration**: 100% menu context coverage
- **Menu Consolidation**: 6 separate menus consolidated into 2 unified menus
- **Enhanced User Experience**: Optimized workflow with logical progression
- **Advanced Help System**: Troubleshooting, feature-specific guidance, and quick reference
- **Performance Optimization**: Intelligent caching and performance monitoring
- **Visual Feedback Systems**: Progress indicators, error handling, and user feedback

### Global Command System Implementation

Dataset Forge features a comprehensive global command system that provides context-aware help and instant quit functionality across all menus:

#### **Core Implementation**

- **Global Commands**: `help`, `h`, `?` for context-aware help; `quit`, `exit`, `q` for instant quit
- **Memory Management**: Automatic cleanup on quit with proper resource management
- **Context-Aware Help**: Menu-specific help information with navigation tips and feature descriptions
- **Menu Redraw**: Automatic menu redraw after help for clarity
- **Error Handling**: Graceful handling of `None` and non-string inputs

#### **Technical Architecture**

- **Core Files**: `dataset_forge/utils/menu.py` and `dataset_forge/utils/help_system.py`
- **Menu Integration**: All menus include `current_menu` and `menu_context` parameters
- **Help Documentation**: Comprehensive help content in `menu_system/comprehensive_help_menu.md` (31,665 bytes)
- **Testing**: 71 tests covering unit tests, integration tests, and edge case testing

#### **Menu Context Structure**

Each menu defines a comprehensive context dictionary:

```python
menu_context = {
    "Purpose": "Clear description of menu functionality",
    "Options": "Number and types of available options",
    "Navigation": "How to navigate the menu",
    "Key Features": ["Feature 1", "Feature 2"],
    "Tips": ["Helpful tips for using the menu"],
    "Examples": "Usage examples (optional)",
    "Notes": "Additional information (optional)"
}
```

#### **Standardized Menu Pattern**

All menus follow the standardized key-based pattern with global command support:

```python
def my_menu():
    """Menu implementation with global command support."""
    options = {
        "1": ("Option 1", function1),
        "2": ("Option 2", function2),
        "0": ("🚪 Exit", None),
    }

    menu_context = {
        "Purpose": "Menu purpose description",
        "Options": "Number of options available",
        "Navigation": "Navigation instructions",
        "Key Features": ["Feature 1", "Feature 2"],
        "Tips": ["Tip 1", "Tip 2"],
    }

    while True:
        try:
            key = show_menu(
                "Menu Title",
                options,
                Mocha.lavender,
                current_menu="Menu Name",
                menu_context=menu_context
            )
            if key is None or key == "0":
                return
            action = options[key][1]
            if callable(action):
                action()
        except (KeyboardInterrupt, EOFError):
            print_info("\nExiting...")
            break
```

<details>
<summary><strong>Static Analysis & Utility Scripts</strong></summary>

- `tools/find_code_issues.py`: comprehensive static analysis including dead code, coverage, docstrings, test mapping, dependency analysis, configuration validation, and import analysis
- `tools/log_current_menu.py`: comprehensive menu hierarchy analysis, path input detection, and improvement recommendations
- `tools/check_mocha_theming.py`: comprehensive Catppuccin Mocha theming consistency checker for CLI menus, printing, and user-facing output
- `tools/merge_docs.py`: merges docs and generates ToC.
- `tools/install.py`: automated environment setup.
- All new scripts must be documented and tested.

</details>

<details>
<summary><strong>Menu Auditing Tool</strong></summary>

The menu auditing tool (`tools/log_current_menu.py`) provides comprehensive analysis of Dataset Forge's menu hierarchy:

**Key Features:**

- **Recursive Exploration**: Automatically discovers and explores all menus and submenus (up to 4 levels deep)
- **Path Input Detection**: Identifies menus requiring user path input using regex patterns
- **AST-Based Analysis**: Uses Python's Abstract Syntax Tree for accurate code parsing with regex fallback
- **Function Resolution**: Handles complex menu function references including `lazy_menu()` calls
- **Comprehensive Reporting**: Generates detailed markdown reports with statistics and recommendations

**Usage:**

```bash
# Activate virtual environment
venv312\Scripts\activate

# Run the menu audit
python tools/log_current_menu.py
```

**Output:** Generates `menu_system/current_menu.md` with:

- Executive summary and statistics
- Hierarchical menu tree structure
- Detailed analysis of each menu
- Actionable recommendations for improvement
- Menu depth, size, and path input metrics

**Configuration:** Customizable settings for output location, maximum depth, and path input detection patterns.

</details>

<details>
<summary><strong>Catppuccin Mocha Theming Consistency Checker</strong></summary>

The theming consistency checker (`tools/check_mocha_theming.py`) ensures consistent use of the Catppuccin Mocha color scheme across the entire codebase:

**Key Features:**

- **Comprehensive Analysis**: Scans all Python, Markdown, and batch files in the codebase
- **Raw Print Detection**: Identifies all `print()` statements that should use centralized utilities
- **Import Validation**: Checks for missing Mocha color imports and centralized printing utilities
- **Menu Pattern Analysis**: Validates proper menu implementation patterns and context parameters
- **Detailed Reporting**: Generates comprehensive markdown reports with actionable recommendations
- **Issue Categorization**: Classifies issues by severity (error, warning, info) and type

**Usage:**

```bash
# Activate virtual environment
venv312\Scripts\activate

# Basic analysis
python tools/check_mocha_theming.py

# Save report to specific location
python tools/check_mocha_theming.py --output reports/theming_report.md

# Verbose output with detailed results
python tools/check_mocha_theming.py --verbose
```

**Output:** Generates comprehensive reports with:

- Real-time analysis progress and summary statistics
- File-by-file detailed analysis with line numbers and code snippets
- Actionable recommendations for fixing theming issues
- Issue categorization by severity and type
- Best practices and usage examples

**Analysis Types:**

- **Raw Print Statements**: Finds `print()` calls that should use `print_info()`, `print_success()`, etc.
- **Missing Imports**: Detects Mocha color usage without proper imports
- **Menu Context**: Identifies missing `current_menu` and `menu_context` parameters
- **Menu Patterns**: Validates standardized key-based menu patterns
- **Documentation**: Checks for theming documentation in markdown files

**Integration:** Fully integrated with Dataset Forge's tools launcher and development workflow, with proper exit codes for CI/CD integration.

</details>

---

## Advanced Testing Patterns

- All features provide public, non-interactive APIs for programmatic use and testing.
- Tests use pytest, fixtures, monkeypatching, and dummy objects.
- Multiprocessing tests require module-level worker functions.
- All new features and bugfixes must include robust tests.

---

## Technical Deep Dives

<details>
<summary><strong>DPID Modular Integration</strong></summary>

- Multiple DPID (degradation) methods: BasicSR, OpenMMLab, Phhofm, Umzi.
- Modular, public APIs for both single-folder and HQ/LQ paired workflows.
- All implementations are robustly tested.

</details>

<details>
<summary><strong>Enhanced Metadata Management</strong></summary>

- Uses exiftool for robust, cross-format metadata extraction, editing, and anonymization.
- Batch extract, view/edit, filter, and anonymize metadata.
- Integration with pandas/SQLite for scalable analysis.

</details>

<details>
<summary><strong>Resave Images Integration</strong></summary>

- Modular, maintainable feature with thread-based parallel processing.
- Supports multiple output formats, grayscale, recursive processing, and unique filenames.
- Fully covered by unit and integration tests.

</details>

---

## MCP Integration & Enhanced Development

Dataset Forge is configured with three powerful MCP (Model Context Protocol) servers that provide enhanced development capabilities:

### **MCP Server Configuration**

The project includes three MCP servers for enhanced development:

- **Filesystem MCP**: Direct access to codebase and datasets
- **Brave Search MCP**: Privacy-focused web research for ML techniques
- **Firecrawl MCP**: Web scraping for documentation and resource extraction

### **Development Workflow Enhancements**

#### **Code Analysis Workflow**

```bash
# Daily Development Routine
1. Use Filesystem MCP to navigate codebase
2. Use Brave Search to research new techniques
3. Use Firecrawl to extract relevant documentation
4. Implement improvements based on findings
5. Update documentation with new insights
```

#### **Research Integration Workflow**

```bash
# Weekly Research Routine
1. Search for new SISR papers and techniques
2. Extract key findings from research papers
3. Identify potential integrations for Dataset Forge
4. Create implementation proposals
5. Update project roadmap
```

### **Proposed Improvements**

#### **Enhanced Documentation System**

- Add "Research Corner" section with latest ML findings
- Include links to relevant papers and datasets
- Provide integration guides for new tools

#### **Automated Research Updates**

- Create research automation system using MCP servers
- Automatically update research database with new findings
- Generate summary reports for new techniques

#### **Enhanced Dataset Discovery**

- Implement dataset discovery features using MCP servers
- Search for new datasets and extract compatibility information
- Generate compatibility reports for new datasets

#### **Community Integration Hub**

- Create community features section with user-submitted dataset reviews
- Add performance benchmarks and real-world usage statistics
- Implement tool integration requests and voting system

### **Technical Implementation**

#### **MCP Integration Class Example**

```python
class MCPIntegration:
    """Integration class for MCP servers in Dataset Forge."""

    def __init__(self):
        self.filesystem = FilesystemMCP()
        self.search = BraveSearchMCP()
        self.scraper = FirecrawlMCP()

    def research_new_features(self, query):
        """Research new features using MCP servers."""
        results = self.search.search(query)
        extracted_info = []

        for result in results:
            info = self.scraper.scrape(result.url)
            extracted_info.append(info)

        return self.analyze_findings(extracted_info)

    def analyze_codebase(self):
        """Analyze codebase using filesystem MCP."""
        files = self.filesystem.list_files("dataset_forge/")
        return self.generate_analysis_report(files)
```

#### **Automated Research Pipeline**

```python
def automated_research_pipeline():
    """Automated research pipeline using MCP servers."""

    # Define research topics
    topics = [
        "SISR techniques 2024",
        "image dataset management",
        "GPU acceleration image processing",
        "distributed image processing"
    ]

    # Research each topic
    for topic in topics:
        results = search_mcp.search(topic)
        extracted_info = []

        for result in results[:5]:  # Top 5 results
            info = firecrawl_mcp.scrape(result.url)
            extracted_info.append(info)

        # Generate research summary
        summary = generate_research_summary(topic, extracted_info)
        save_research_summary(topic, summary)

    # Create consolidated report
    create_consolidated_research_report()
```

### **Success Metrics**

- **Development Efficiency**: Code navigation time reduced by 50%, research time reduced by 30%
- **Project Visibility**: Improved search engine ranking and GitHub stars
- **Feature Quality**: Research-based features implemented with improved user satisfaction

---

## See Also

- [Features](features.md)
- [Usage Guide](usage.md)
- [Project Architecture](architecture.md)
- [Troubleshooting](troubleshooting.md)
- [Style Guide](style_guide.md)

---

# Architecture

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

---

# Contributing

[ Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Contributing

> **Who is this for?**  
> Anyone who wants to contribute code, documentation, or ideas to Dataset Forge.

---

## How to Contribute

1. **Read the [Style Guide](style_guide.md)**  
   All code must follow the project's coding standards, modular architecture, and documentation requirements.
2. **Fork the repository** and create a new branch for your feature or fix.
3. **Write clear, well-documented code**
   - Use Google-style docstrings and type hints for all public functions/classes.
   - Add or update tests in `tests/` for new features or bugfixes.
   - Update or add documentation in the appropriate `docs/` file(s).
4. **Test your changes**
   - Activate the virtual environment: `venv312\Scripts\activate`
   - Run the test suite: `pytest`
   - Ensure all tests pass on your platform (Windows and/or Linux).
5. **Submit a Pull Request (PR)**
   - Describe your changes clearly in the PR description.
   - Reference any related issues or discussions.
   - If your change affects documentation, mention which files were updated.
   - Be responsive to code review feedback.

---

## Development Guidelines

- **Modular Design:**  
  UI in `menus/`, business logic in `actions/`, helpers in `utils/`. Use lazy imports for menu actions.
- **Memory & Performance:**  
  Use centralized memory and parallel processing utilities. Always clean up memory after large operations.
- **Testing:**  
  Add tests for new features and bugfixes. Use pytest fixtures and monkeypatching as needed.
- **Documentation:**  
  Update relevant docs in `docs/` and regenerate `README_full.md` and `toc.md` using `merge_docs.py` after changes.
- **Commit Messages:**  
  Use clear, descriptive commit messages (e.g., `feat: add CBIR duplicate detection`, `fix: handle VapourSynth import error`).
- **Community Standards:**  
  Be respectful and constructive in all communications. Report bugs or suggest features via GitHub Issues.

---

## Doc Maintenance

- After updating any documentation, always regenerate `docs/README_full.md` and `docs/toc.md` using `merge_docs.py`.
- For major changes, update `docs/changelog.md`.
- For new documentation sections, create a new markdown file in `docs/` and add it to the Table of Contents in `README.md` and `docs/toc.md`.

---

## Static Analysis & Code Quality

- Before submitting a PR, you **must** run the static analysis tool (`tools/find_code_issues.py`) and address all actionable issues (dead code, untested code, missing docstrings, dependency issues, configuration problems, etc.).
- **Theming Consistency**: You **must** run the theming consistency checker (`tools/check_mocha_theming.py`) and address all critical theming issues (raw print statements, missing imports, incorrect menu patterns).
- All public functions/classes/methods must have Google-style docstrings.
- All user-facing output must use centralized printing utilities with Catppuccin Mocha colors.
- The static analysis script saves all output files to `./logs/find_code_issues/` for easy review and analysis.
- The theming checker saves reports to `./logs/mocha_theming_report.md` by default.
- See [usage.md](usage.md) and [features.md](features.md) for details.

## Menu System Development

- **Menu Auditing**: Use the menu auditing tool (`tools/log_current_menu.py`) to analyze menu hierarchy and identify improvement opportunities.
- **Menu Pattern Compliance**: All menus must follow the standardized key-based pattern documented in `.cursorrules`.
- **Menu Testing**: Ensure new menus are testable and follow the established patterns for help/quit functionality.
- **Menu Documentation**: Update menu documentation when adding new menus or changing menu structure.

### Global Command System Development

- **Global Commands**: All menus must support `help`, `h`, `?` for context-aware help and `quit`, `exit`, `q` for instant quit
- **Menu Context**: Define comprehensive `menu_context` dictionaries for each menu with purpose, options, navigation, key features, and tips
- **Testing**: Global command functionality must be covered by unit and integration tests
- **Documentation**: Update help documentation when adding new menus or changing menu structure

### MCP Integration Development (MANDATORY)

Dataset Forge is configured with comprehensive MCP (Model Context Protocol) servers for enhanced development. **ALL contributors MUST use MCP tools before implementing solutions.**

#### **Available MCP Servers**

1. **Brave Search Tools** (Primary Research)

   - `mcp_brave-search_brave_web_search` - General web research, latest libraries, best practices
   - `mcp_brave-search_brave_news_search` - Recent developments and updates
   - `mcp_brave-search_brave_local_search` - Location-specific information
   - `mcp_brave-search_brave_video_search` - Tutorials and demonstrations
   - `mcp_brave-search_brave_image_search` - Visual references

2. **Firecrawl Tools** (Deep Web Scraping)

   - `mcp_firecrawl_firecrawl_search` - Comprehensive web search with content extraction
   - `mcp_firecrawl_firecrawl_scrape` - Detailed content extraction from specific URLs
   - `mcp_firecrawl_firecrawl_map` - Discovering website structure
   - `mcp_firecrawl_firecrawl_extract` - Structured data extraction
   - `mcp_firecrawl_firecrawl_deep_research` - Complex research questions

3. **Filesystem Tools** (Project Analysis)

   - `mcp_filesystem_read_text_file` - Read and analyze project files
   - `mcp_filesystem_list_directory` - Understand project structure
   - `mcp_filesystem_search_files` - Find specific files or patterns
   - `mcp_filesystem_get_file_info` - Detailed file metadata analysis
   - `mcp_filesystem_directory_tree` - Comprehensive project structure visualization

4. **GitHub Integration Tools** (Code Examples)
   - `mcp_gitmcp-docs_fetch_generic_documentation` - GitHub repository documentation
   - `mcp_gitmcp-docs_search_generic_code` - Finding code examples in repositories
   - `mcp_gitmcp-docs_search_generic_documentation` - Documentation searches
   - `mcp_gitmcp-docs_match_common_libs_owner_repo_mapping` - Library-to-repo mapping

#### **MCP Tool Usage Patterns (MANDATORY)**

##### Before Implementing Any Solution:

1. **Research Phase**: Use Brave Search to find latest libraries, best practices, and solutions
2. **Deep Dive**: Use Firecrawl to extract detailed content from relevant sources
3. **Project Context**: Use Filesystem tools to understand current implementation
4. **Code Examples**: Use GitHub tools to find relevant code examples and patterns

##### When Debugging Issues:

1. **Error Research**: Use Brave Search to find solutions for specific error messages
2. **Documentation**: Use Firecrawl to extract troubleshooting guides
3. **Project Analysis**: Use Filesystem tools to examine current code and configuration
4. **Community Solutions**: Use GitHub tools to find similar issues and solutions

##### When Adding New Features:

1. **Best Practices**: Use Brave Search to find current best practices and patterns
2. **Implementation Guides**: Use Firecrawl to extract detailed implementation tutorials
3. **Project Integration**: Use Filesystem tools to understand how to integrate with existing code
4. **Reference Implementations**: Use GitHub tools to find similar feature implementations

#### **MCP Integration Requirements**

- **ALWAYS** use at least 2-3 MCP tools before implementing any solution
- **ALWAYS** document MCP findings and rationale for chosen solutions
- **ALWAYS** use MCP tools to validate assumptions about current best practices
- **ALWAYS** use MCP tools to find the most recent and relevant information
- **ALWAYS** use MCP tools to understand existing codebase patterns before making changes
- **ALWAYS** use MCP tools to find appropriate solutions based on project context

#### **MCP Tool Usage Examples**

```python
# Example workflow for adding a new feature:
# 1. Research current best practices
mcp_brave-search_brave_web_search("latest Python image processing libraries 2024")

# 2. Find specific implementation details
mcp_firecrawl_firecrawl_search("Python PIL Pillow image processing best practices")

# 3. Understand current project structure
mcp_filesystem_list_directory("dataset_forge/utils")

# 4. Find relevant code examples
mcp_gitmcp-docs_search_generic_code("owner", "repo", "image processing utils")
```

#### **Research Integration**

- **Automated Research**: Use MCP servers to automatically research new SISR techniques and tools
- **Documentation Extraction**: Extract and analyze documentation from external sources
- **Community Research**: Research community feedback and competitor features
- **Implementation Planning**: Use research findings to plan new features and improvements

#### **Code Quality Enhancement**

- **Pattern Analysis**: Use Filesystem MCP to analyze code patterns and consistency
- **Documentation Coverage**: Use MCP servers to identify missing documentation topics
- **Feature Research**: Research new features and tools for potential integration
- **Performance Analysis**: Analyze performance benchmarks and optimization techniques

### Menu Auditing Workflow

1. **Before Making Changes**: Run `python tools/log_current_menu.py` to understand the current menu structure
2. **After Adding Menus**: Re-run the audit to verify the new menu integrates properly
3. **Review Recommendations**: Check the generated report for suggestions on menu organization
4. **Monitor Statistics**: Track menu depth, size, and path input points over time

### Menu Auditing Features

- **Automatic Discovery**: Finds all menu files in `dataset_forge/menus/`
- **Path Input Detection**: Identifies menus requiring user input to prevent infinite loops
- **AST-Based Analysis**: Uses Python's Abstract Syntax Tree for accurate code parsing
- **Comprehensive Reporting**: Generates detailed analysis with statistics and recommendations
- **Configurable Depth**: Set maximum exploration depth (default: 4 levels)

---

## See Also

- [Style Guide](style_guide.md)
- [Features](features.md)
- [Usage Guide](usage.md)
- [Advanced Features](advanced.md)
- [Troubleshooting](troubleshooting.md)

For questions, open an issue or contact the project maintainer.

---

# Style Guide

[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Dataset Forge Style Guide

> **Who is this for?**  
> This guide is for contributors and anyone writing code or documentation for Dataset Forge. For user-facing features, see [features.md](features.md) and [usage.md](usage.md).

---

## Critical UI/UX Rule: Catppuccin Mocha Color Scheme

- All user-facing CLI output **must** use the Catppuccin Mocha color scheme.
- Always use `from dataset_forge.utils.color import Mocha` and the centralized printing utilities.
- No raw print statements in user-facing code.
- All menus, prompts, progress bars, and workflow headings must be Mocha-styled.
- All new code and PRs must be reviewed for color consistency.

### Enforcement Checklist

- [ ] All new/modified CLI output uses Mocha colors via centralized utilities.
- [ ] No raw print statements in user-facing code.
- [ ] All code examples in docs use Mocha color utilities.
- [ ] Reviewer confirms color consistency before merging.

---

## General Principles

- **Python 3.12+**. Use modern Python features.
- **PEP 8** style, 4-space indentation, 88-char line length (Black standard).
- **Google-style docstrings** for all public functions/classes.
- **Type hints** for all function parameters and return values.
- **Absolute imports** for all `dataset_forge` modules.
- **Modular design**: UI (menus/), business logic (actions/), utilities (utils/), DPID (dpid/).
- **Consistent use of Catppuccin Mocha color scheme for all CLI output.**

---

## Project Architecture & Modularity

- Keep UI, logic, and utilities separate.
- Thin UI layers (menus), business logic in actions, helpers in utils.
- Use lazy imports to keep CLI menu responsive and fast.

---

## Coding Standards

- Use type hints everywhere.
- Google-style docstrings for all public functions/classes.
- Import order: standard library, third-party, local, relative (only within same module).
- Always use absolute imports for `dataset_forge` modules.

<details>
<summary><strong>Example: Google-style docstring</strong></summary>

```python
def process_images(image_paths: List[str], output_dir: str) -> List[str]:
    """
    Process a list of images and save results to output directory.
    Args:
        image_paths: List of input image file paths
        output_dir: Directory to save processed images
    Returns:
        List of output image file paths
    Raises:
        FileNotFoundError: If input files don't exist
        PermissionError: If output directory is not writable
    Example:
        >>> paths = process_images(['img1.jpg', 'img2.png'], 'output/')
        >>> print(f"Processed {len(paths)} images")
    """
```

</details>

---

## Memory, Parallelism, Progress, and Color/UI

- Use centralized memory management: `from dataset_forge.utils.memory_utils import clear_memory, clear_cuda_cache`
- Use context managers and decorators for memory and monitoring.
- Use centralized parallel system: `from dataset_forge.utils.parallel_utils import parallel_map, ProcessingType`
- Use `smart_map`, `image_map`, `batch_map` for optimized processing.
- Use `tqdm` and AudioTqdm for progress and audio feedback.
- Use Catppuccin Mocha color scheme and centralized printing utilities for all output.

---

## Menu & Workflow Patterns

- Use hierarchical menu structure and `show_menu()` from `dataset_forge.utils.menu`.
- Include emojis in menu options with context-aware validation.
- Use the robust menu loop pattern (see code example below).
- All interactive workflows must print a clear, Mocha-styled heading before input/output prompts and progress bars using the centralized printing utilities and Mocha colors.

<details>
<summary><strong>Robust Menu Loop Example</strong></summary>

```python
from dataset_forge.utils.printing import print_header
from dataset_forge.utils.color import Mocha

while True:
    choice = show_menu("Menu Title", options, ...)
    if choice is None or choice == "0":
        break
    action = options[choice][1]
    if callable(action):
        print_header("Selected Action", color=Mocha.lavender)
        action()
```

</details>

---

## Error Handling & Logging

- Use centralized logging: `from dataset_forge.utils.history_log import log_operation`
- Log all major operations with timestamps.
- Use try-except with meaningful error messages.
- All user-facing errors must trigger the error sound via the centralized print_error utility.
- Use centralized emoji utilities for safe emoji handling: `from dataset_forge.utils.emoji_utils import normalize_unicode, sanitize_emoji, is_valid_emoji`

---

## Testing & Validation

- All features must provide public, non-interactive APIs for programmatic access and testing.
- Use pytest, fixtures, monkeypatching, and dummy objects.
- Multiprocessing tests must use module-level worker functions.
- All new features and bugfixes must include robust tests.

---

## Caching & Performance

- Use centralized caching utilities: `from dataset_forge.utils.cache_utils import in_memory_cache, disk_cache, model_cache, smart_cache`
- Choose appropriate cache type and document cache usage in function docstrings.
- Monitor cache statistics and implement cache warmup for critical data.

---

## Documentation Requirements

- Google-style docstrings for all public functions/classes.
- Include parameter types, return values, exceptions, and usage examples.

---

## Dependency & Security

- Add new dependencies to `requirements.txt` and use version constraints.
- Validate all user inputs and sanitize file paths.

---

## Emoji System Guidelines

### Emoji Usage in Menus and UI

- **Always validate emojis** before using them in user-facing text
- **Use context-aware validation** for appropriate emoji selection in different contexts
- **Include emojis in menu options** for better user experience and readability
- **Use smart emoji suggestions** for contextually appropriate emoji selection
- **Validate menu emojis** during development using the emoji usage checker

### Emoji Best Practices

```python
from dataset_forge.utils.emoji_utils import (
    suggest_appropriate_emojis,
    validate_emoji_appropriateness,
    get_emoji_description_from_mapping
)

# Good: Context-appropriate emojis
def create_menu_options():
    success_emojis = suggest_appropriate_emojis("success completion")
    error_emojis = suggest_appropriate_emojis("error problem")

    return {
        "1": (f"{success_emojis[0]} Process Complete", process_complete_action),
        "2": (f"{error_emojis[0]} Error Report", error_report_action),
        "0": ("🚪 Exit", None),
    }

# Good: Context-aware validation
def validate_menu_emojis(menu_options):
    for key, (description, action) in menu_options.items():
        emojis = extract_emojis(description)
        for emoji in emojis:
            validation = validate_emoji_appropriateness(emoji, "menu interface")
            if validation['warnings']:
                print(f"Warning: Menu option {key} has inappropriate emoji")

# Avoid: Too many emojis or inappropriate context
bad_menu = {
    "1": ("🎉 🍕 🎊 Process Complete! 🎈 🎪", process_action),  # Too many emojis
    "2": ("😀 😍 😊 😄 😁 😆 😅 😂 😇 😉 Error Report", error_action),  # All same category
}
```

### Emoji Accessibility

- **Provide emoji descriptions** for accessibility when needed
- **Use consistent emoji categories** across related menus
- **Test emoji display** on different platforms and terminals
- **Handle Unicode encoding issues** gracefully with fallbacks

### Emoji Performance

- **Use caching** for repeated emoji operations
- **Lazy load emoji mapping** only when needed
- **Monitor emoji usage patterns** for insights and recommendations
- **Use the emoji usage checker** before submitting PRs

## MCP Integration Requirements (MANDATORY)

### MCP Tool Usage Priority

When implementing solutions, **ALWAYS** use MCP tools in this priority order:

1. **Brave Search Tools** (Primary Research)

   - Use `mcp_brave-search_brave_web_search` for general web research, latest libraries, best practices
   - Use `mcp_brave-search_brave_news_search` for recent developments and updates
   - Use `mcp_brave-search_brave_local_search` for location-specific information
   - Use `mcp_brave-search_brave_video_search` for tutorials and demonstrations
   - Use `mcp_brave-search_brave_image_search` for visual references

2. **Firecrawl Tools** (Deep Web Scraping)

   - Use `mcp_firecrawl_firecrawl_search` for comprehensive web search with content extraction
   - Use `mcp_firecrawl_firecrawl_scrape` for detailed content extraction from specific URLs
   - Use `mcp_firecrawl_firecrawl_map` for discovering website structure
   - Use `mcp_firecrawl_firecrawl_extract` for structured data extraction
   - Use `mcp_firecrawl_firecrawl_deep_research` for complex research questions

3. **Filesystem Tools** (Project Analysis)

   - Use `mcp_filesystem_read_text_file` to read and analyze project files
   - Use `mcp_filesystem_list_directory` to understand project structure
   - Use `mcp_filesystem_search_files` to find specific files or patterns
   - Use `mcp_filesystem_get_file_info` for detailed file metadata analysis
   - Use `mcp_filesystem_directory_tree` for comprehensive project structure visualization

4. **GitHub Integration Tools** (Code Examples)
   - Use `mcp_gitmcp-docs_fetch_generic_documentation` for GitHub repository documentation
   - Use `mcp_gitmcp-docs_search_generic_code` for finding code examples in repositories
   - Use `mcp_gitmcp-docs_search_generic_documentation` for documentation searches
   - Use `mcp_gitmcp-docs_match_common_libs_owner_repo_mapping` for library-to-repo mapping

### MCP Tool Usage Patterns

#### Before Implementing Any Solution:

1. **Research Phase**: Use Brave Search to find latest libraries, best practices, and solutions
2. **Deep Dive**: Use Firecrawl to extract detailed content from relevant sources
3. **Project Context**: Use Filesystem tools to understand current implementation
4. **Code Examples**: Use GitHub tools to find relevant code examples and patterns

#### When Debugging Issues:

1. **Error Research**: Use Brave Search to find solutions for specific error messages
2. **Documentation**: Use Firecrawl to extract troubleshooting guides
3. **Project Analysis**: Use Filesystem tools to examine current code and configuration
4. **Community Solutions**: Use GitHub tools to find similar issues and solutions

#### When Adding New Features:

1. **Best Practices**: Use Brave Search to find current best practices and patterns
2. **Implementation Guides**: Use Firecrawl to extract detailed implementation tutorials
3. **Project Integration**: Use Filesystem tools to understand how to integrate with existing code
4. **Reference Implementations**: Use GitHub tools to find similar feature implementations

### MCP Integration Requirements

- **ALWAYS** use at least 2-3 MCP tools before implementing any solution
- **ALWAYS** document MCP findings and rationale for chosen solutions
- **ALWAYS** use MCP tools to validate assumptions about current best practices
- **ALWAYS** use MCP tools to find the most recent and relevant information
- **ALWAYS** use MCP tools to understand existing codebase patterns before making changes
- **ALWAYS** use MCP tools to find appropriate solutions based on project context

### MCP Tool Usage Examples

```python
# Example workflow for adding a new feature:
# 1. Research current best practices
mcp_brave-search_brave_web_search("latest Python image processing libraries 2024")

# 2. Find specific implementation details
mcp_firecrawl_firecrawl_search("Python PIL Pillow image processing best practices")

# 3. Understand current project structure
mcp_filesystem_list_directory("dataset_forge/utils")

# 4. Find relevant code examples
mcp_gitmcp-docs_search_generic_code("owner", "repo", "image processing utils")
```

## Final Reminders

1. **Always activate the virtual environment**: `venv312\Scripts\activate`
2. **Always use centralized utilities from `dataset_forge.utils`**
3. **Always include proper error handling and logging**
4. **Always use the Catppuccin Mocha color scheme**
5. **Always follow the modular architecture patterns**
6. **Always implement parallel processing for performance**
7. **Always manage memory properly, especially for CUDA operations**
8. **Always provide user-friendly feedback and progress tracking**
9. **Always document your code with Google-style docstrings**
10. **Always test your changes thoroughly before committing**
11. **Always update documentation after adding new features or menus**
12. **Always validate emojis and use context-aware emoji selection**
13. **Always use MCP tools before implementing solutions to ensure current best practices**

---

## See Also

- [Contributing](contributing.md)
- [Features](features.md)
- [Usage Guide](usage.md)
- [Advanced Features](advanced.md)
- [Troubleshooting](troubleshooting.md)

---

# Troubleshooting

[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Troubleshooting

> **Who is this for?**  
> This guide is for anyone encountering errors, installation problems, or unexpected behavior in Dataset Forge.

---

## Installation & Environment Issues

- **Python version too low:** Upgrade to Python 3.12+.
- **CUDA/torch install fails:** Check your CUDA version and use the correct index URL for torch.
- **pip install fails:** Check your internet connection and permissions. Try running as administrator.
- **python-magic errors on Windows:** Copy required DLLs to `C:/Windows/System32/`. See [Special Installation Instructions](special_installation.md).
- **VapourSynth/getnative:** Install VapourSynth before getnative. See [Special Installation Instructions](special_installation.md).

---

## Common CLI & Workflow Issues

- **Import errors or menu options not working:** Ensure all dependencies are installed. See [Special Installation Instructions](special_installation.md).
- **Menu redraws or submenus not appearing:** Update your menu code to follow the robust menu loop pattern (see [style_guide.md](style_guide.md)).
- **Timing prints missing:** Ensure you are running the latest version and using the correct utilities.
- **Missing workflow headings:** Update the workflow to match the Style Guide.

---

## Test Suite & Developer Tools

- **Test failures:** Check for function signature mismatches, especially with parallel utilities. Ensure all monkeypatches and fixtures match expected types.
- **Static analysis tool fails:** Ensure all dependencies are installed. Check your virtual environment and directory structure.
- **Menu auditing tool issues:** Check that menu functions end with `_menu` and are in `dataset_forge/menus/`. Import errors for complex function references are normal.
- **Utility scripts not working:** Check dependencies, permissions, and environment variables.

---

## Metadata & Caching Issues

- **exiftool not found:** Ensure exiftool is installed and in your PATH. Restart your terminal after installation.
- **pandas/SQLite errors:** Ensure pandas is installed and your Python includes standard libraries.
- **Cache misses or high memory usage:** Check TTL and maxsize settings. Use cache statistics to analyze performance. Clear caches if needed.

---

## DPID & External Tools

- **pepedpid ImportError:** Ensure pepedpid is installed in the correct environment.
- **DPID workflow errors:** Check input folders for valid images and use the correct menu option.

## Steganography Tools (zsteg, steghide)

### ZSTEG Executable Issues

**Problem**: `zsteg.exe` fails with side-by-side configuration error:

```
14001: The application has failed to start because its side-by-side configuration is incorrect.
Please see the application event log or use the command-line sxstrace.exe tool for more detail.
- C:/Users/anon/AppData/Local/Temp/ocran00074B817894/lib/ruby/3.4.0/x64-mingw-ucrt/zlib.so (LoadError)
```

**Root Cause**: OCRA-built executables have dependency issues with native extensions like `zlib.so` and missing `zlib1.dll`.

**Solution 1: OCRAN-Based Executable (RECOMMENDED)**

Replace OCRA with OCRAN (maintained fork) for better Windows compatibility:

```bash
# Remove old OCRA and install OCRAN
gem uninstall ocra
gem install ocran

# Create zsteg CLI wrapper
# Create file: zsteg_cli.rb
#!/usr/bin/env ruby
puts "Starting zsteg_cli.rb..."
puts "ARGV: #{ARGV.inspect}"
STDOUT.flush
STDERR.flush
require 'zsteg'
require 'zsteg/cli/cli'
ZSteg::CLI::Cli.new.run

# Build executable with OCRAN
ocran zsteg_cli.rb --gem-all --add-all-core --output zsteg.exe --verbose

# Test the executable
.\zsteg.exe --help
```

**Solution 2: PowerShell Wrapper (Alternative)**

Use a PowerShell wrapper that gracefully falls back to gem-installed zsteg:

```powershell
# Create zsteg_wrapper.ps1
# Attempts OCRA executable first, falls back to gem-installed zsteg
powershell -ExecutionPolicy Bypass -File "zsteg_wrapper.ps1" --help
```

## Audio System Issues

### CLI Hanging During Exit

**Problem**: CLI hangs when trying to exit with `q`, `quit`, `exit`, `0`, or `Ctrl+C`

**Root Cause**: Audio playback system hanging during shutdown sound

**Solution**: The audio system has been updated with robust fallbacks and timeout protection. If issues persist:

1. **Check audio dependencies**:

   ```bash
   pip install playsound==1.2.2 pydub pygame
   ```

2. **Verify audio files exist**:

   ```bash
   ls assets/
   # Should show: done.wav, error.mp3, startup.mp3, shutdown.mp3
   ```

3. **Test audio functionality**:
   ```python
   from dataset_forge.utils.audio_utils import play_done_sound
   play_done_sound(block=True)
   ```

### Audio Not Playing

**Problem**: No audio feedback during operations

**Solutions**:

1. **Check audio library installation**:

   ```bash
   pip install playsound==1.2.2 pydub
   ```

2. **Test individual audio libraries**:

   ```python
   # Test playsound
   from playsound import playsound
   playsound("assets/done.wav", block=True)

   # Test winsound (Windows only)
   import winsound
   winsound.PlaySound("assets/done.wav", winsound.SND_FILENAME)
   ```

3. **Check audio file integrity**:
   ```bash
   # Verify file sizes
   ls -la assets/
   # done.wav should be ~352KB
   # error.mp3 should be ~32KB
   # startup.mp3 should be ~78KB
   # shutdown.mp3 should be ~23KB
   ```

### Audio Library Conflicts

**Problem**: Multiple audio libraries causing conflicts

**Solution**: The audio system automatically selects the best available library:

1. **Playsound (primary)** - Most reliable cross-platform
2. **Winsound (Windows WAV)** - Best for WAV files on Windows
3. **Pydub (various formats)** - Good for MP3 and other formats
4. **Pygame (fallback)** - Cross-platform fallback

### Audio System Error Messages

**Common messages and solutions**:

- `"Playsound failed: Error 277"` - MP3 format issue, system will fall back to pydub
- `"Winsound failed"` - WAV file issue, system will try playsound
- `"Audio playback not available"` - No audio libraries working, CLI continues without audio
- `"Audio playback timeout"` - Audio took too long, automatically stopped

### Audio System Best Practices

1. **Always use centralized audio functions**:

   ```python
   from dataset_forge.utils.audio_utils import play_done_sound
   # Don't use audio libraries directly
   ```

2. **Handle audio failures gracefully**:

   ```python
   try:
       play_done_sound(block=True)
   except Exception:
       # Audio failed, but operation continues
       pass
   ```

3. **Use appropriate blocking**:

   - `block=True` for important feedback (success, error, shutdown)
   - `block=False` for background sounds (startup)

4. **Test audio on target platforms**:
   - Windows: winsound + playsound
   - macOS: playsound + pydub
   - Linux: playsound + pygame

---

## Visual Deduplication Issues

### CUDA Multiprocessing Errors

**Problem**: `RuntimeError: CUDA error: CUDA-capable device(s) is/are busy or unavailable`

**Root Cause**: PyTorch CUDA tensors cannot be shared across multiprocessing processes on Windows.

**Solution**: The Visual Deduplication feature now automatically uses CPU for multiprocessing on Windows to avoid CUDA tensor sharing issues.

**Prevention**: Automatic detection and fallback to CPU processing when CUDA multiprocessing is detected.

### Memory Errors (Paging File Too Small)

**Problem**: `The paging file is too small for this operation to complete. (os error 1455)` and `A process in the process pool was terminated abruptly`

**Root Cause**: Large datasets (4,000+ images) causing memory exhaustion on Windows.

**Solution**: Implemented chunked processing with automatic memory management:
- Large datasets are processed in chunks (default: 458 images per chunk)
- Automatic memory cleanup between chunks
- Global model cache to prevent repeated model loading

**Prevention**: 
- Automatic chunk size calculation based on dataset size
- Memory cleanup after each chunk
- Process pool management to prevent memory leaks

### Empty Embedding Errors

**Problem**: `Critical error in visual_dedup_workflow: need at least one array to stack`

**Root Cause**: Empty embedding lists being passed to `np.stack()` function.

**Solution**: Comprehensive error handling and validation:
- Explicit checks for empty embedding lists before processing
- Graceful fallback to hash-based embeddings if CLIP model unavailable
- Enhanced error messages with debugging information

**Prevention**:
- Validation of image loading results
- Checks for successful model initialization
- Fallback systems for failed operations

### Model Loading Issues

**Problem**: Import errors or model loading failures in worker processes.

**Root Cause**: Lazy imports and model loading issues in multiprocessing workers.

**Solution**: Global model cache and robust initialization:
- Models loaded once at module import time into global cache
- Direct imports in worker functions instead of lazy imports
- Comprehensive error handling for model loading failures

**Prevention**:
- Global model cache prevents repeated loading
- Proper error handling for missing dependencies
- Fallback to alternative methods when models unavailable

### Performance Issues

**Problem**: Slow processing or hanging during large dataset operations.

**Root Cause**: Inefficient processing strategies for large datasets.

**Solution**: Optimized processing workflows:
- Chunked processing for large datasets
- FAISS integration for efficient similarity search
- Optimized similarity matrix computation
- Progress tracking with real-time feedback

**Performance Metrics**:
- **Processing Speed**: ~10 images/second with CLIP embeddings
- **Memory Usage**: Optimized chunked processing
- **Scalability**: Successfully tested with 4,581+ images
- **Reliability**: 100% success rate in production testing

### FAISS Integration Issues

**Problem**: FAISS not available or similarity computation failures.

**Root Cause**: FAISS library not installed or compatibility issues.

**Solution**: Graceful fallback systems:
- Automatic detection of FAISS availability
- Fallback to optimized matrix computation when FAISS unavailable
- Clear error messages and recommendations

**Installation**: Optional FAISS installation for enhanced performance:
```bash
pip install faiss-cpu  # CPU version
# or
pip install faiss-gpu  # GPU version (requires CUDA)
```

### Process Pool Management

**Problem**: Memory leaks or hanging processes after deduplication.

**Root Cause**: Improper process pool cleanup and termination.

**Solution**: Comprehensive process pool management:
- Automatic cleanup and termination of process pools
- Memory cleanup after each operation
- Proper error handling for process pool failures

**Prevention**:
- `cleanup_process_pool()` function for proper termination
- Memory cleanup in `finally` blocks
- Process pool monitoring and management

### Image Loading Issues

**Problem**: Failed to load images or empty image lists.

**Root Cause**: File system issues, corrupted images, or permission problems.

**Solution**: Robust image loading with comprehensive error handling:
- Enhanced error messages for failed image loading
- Validation of loaded images before processing
- Graceful handling of corrupted or unreadable files

**Prevention**:
- File existence checks before loading
- Image format validation
- Permission checking for file access

### Expected Behavior

**Successful Operation Output**:
```
Found 4581 image files in C:/path/to/images
Loading Images: 100%|████████████████| 4581/4581 [00:10<00:00, 441.29it/s]
Successfully loaded 4581 images out of 4581 files
Using CPU for multiprocessing to avoid CUDA tensor sharing issues on Windows
Processing 4581 images in 11 chunks of size 458
CLIP embedding chunk 1/11: 100%|████████████████| 458/458 [00:44<00:00, 10.21it/s]
...
! FAISS not available, falling back to naive similarity computation
Computing similarity matrix with optimized memory usage
Large dataset detected (4581 images), using chunked similarity computation
Computing similarity matrix in chunks of size 50
Computing similarity chunks: 100%|████████████████| 92/92 [00:09<00:00, 9.50it/s]
Visual deduplication complete.
No duplicate groups found.
```

**Error Recovery**: The system automatically handles most errors and provides clear feedback about what went wrong and how to resolve it.

### Best Practices

1. **Start Small**: Test with a small dataset first to verify functionality
2. **Monitor Resources**: Use System Monitoring to check memory and CPU usage
3. **Clear Caches**: Clear memory caches before processing large datasets
4. **Use Appropriate Methods**: CLIP for semantic similarity, LPIPS for perceptual similarity
5. **Check File Permissions**: Ensure read access to image folders
6. **Validate Images**: Use image validation tools before deduplication

## Fuzzy Deduplication Issues

### Common Problems

**No Duplicates Found**
- **Cause**: Thresholds too high
- **Solution**: Lower the similarity thresholds (try 80-85% instead of 90-95%)
- **Alternative**: Try different hash method combinations (pHash + dHash)

**Too Many False Positives**
- **Cause**: Thresholds too low
- **Solution**: Increase the similarity thresholds (try 90-95% instead of 70-80%)
- **Alternative**: Use fewer hash methods (pHash only)

**Memory Errors During Processing**
- **Cause**: Batch size too large for available memory
- **Solution**: Reduce batch size (try 20-50 instead of 100-500)
- **Alternative**: Process smaller subsets of images

**Slow Processing**
- **Cause**: Too many hash methods or large batch size
- **Solution**: Use fewer hash methods (pHash + dHash only)
- **Alternative**: Reduce batch size and process in smaller chunks

**"No image files found" Error**
- **Cause**: Folder doesn't contain supported image files
- **Solution**: Check folder path and ensure it contains .jpg, .png, .bmp, .tiff files
- **Alternative**: Use image validation tools to check file integrity

**"Invalid threshold value" Error**
- **Cause**: Threshold not between 0 and 100
- **Solution**: Use values between 0 and 100 (e.g., 85 for 85%)
- **Alternative**: Use default thresholds if unsure

### Performance Optimization

**For Large Datasets (> 10,000 images)**
- Use batch size of 20-100
- Use only 2-3 hash methods (pHash + dHash + aHash)
- Process in smaller chunks if memory is limited

**For Medium Datasets (1,000-10,000 images)**
- Use batch size of 50-200
- Use 3-4 hash methods for better accuracy
- Monitor memory usage during processing

**For Small Datasets (< 1,000 images)**
- Use batch size of 100-500
- Can use all hash methods for maximum accuracy
- Test different threshold combinations

### Best Practices for Fuzzy Deduplication

1. **Start with Show Mode**: Always preview duplicates before taking action
2. **Use Conservative Thresholds**: Begin with 90-95% thresholds to avoid false positives
3. **Test with Small Subsets**: Verify results with 100-500 images before processing large datasets
4. **Combine Hash Methods**: Use pHash + dHash for balanced accuracy and speed
5. **Backup Important Data**: Always backup before using delete operations
6. **Monitor Memory Usage**: Use System Monitoring to track memory consumption

### Getting Help

If you encounter issues not covered here:

1. **Check the logs**: Review `./logs/` directory for detailed error information
2. **Use System Monitoring**: Check resource usage and system health
3. **Test with smaller datasets**: Verify functionality with smaller image sets
4. **Report issues**: Open an issue on GitHub with detailed error information and system specifications

---

## FAQ

See below for frequently asked questions. For more, visit the [Discussion Board](https://github.com/Courage-1984/Dataset-Forge/discussions).

<details>
<summary><strong>Frequently Asked Questions (FAQ)</strong></summary>

- **What is Dataset Forge?**  
  Modular Python CLI tool for managing, analyzing, and transforming image datasets, with a focus on HQ/LQ pairs for super-resolution and ML workflows.

- **What platforms are supported?**  
  Windows (primary), Linux/macOS (not yet tested).

- **What Python version is required?**  
  Python 3.12+ is recommended.

- **How do I install Dataset Forge and its dependencies?**  
  See the [Quick Start](../README.md#-quick-start) and [Special Installation Instructions](special_installation.md).

- **Why do I need to install VapourSynth before getnative?**  
  getnative depends on VapourSynth. See [Special Installation Instructions](special_installation.md).

- **How do I fix python-magic errors on Windows?**  
  Copy required DLLs to `C:/Windows/System32/`. See [Special Installation Instructions](special_installation.md).

- **How do I run the test suite?**  
  Activate the virtual environment and run `pytest`. See [usage.md](usage.md).

- **How do I use the monitoring and analytics features?**  
  Access the System Monitoring menu from the CLI. See [features.md](features.md).

- **What should I do if I get CUDA or GPU errors?**  
  Ensure your CUDA/cuDNN versions match your PyTorch install. Lower batch size or use CPU fallback if needed.

- **What if a menu or feature is missing or crashes?**  
  Make sure you are running the latest version. Check the logs in the `./logs/` directory.

- **How do I analyze the menu system structure?**  
  Use the menu auditing tool: `python tools/log_current_menu.py`. It generates a comprehensive report at `menu_system/current_menu.md`.

- **How do I get help or report a bug?**  
  Open an issue on GitHub or contact the project maintainer.

- **How do I create a standalone zsteg.exe executable?**  
  Use the OCRAN method described in [Special Installation Instructions](special_installation.md). This creates a self-contained executable that doesn't require Ruby to be installed on the target system.

- **Why does my zsteg.exe show side-by-side configuration errors?**  
  This is a common issue with the original OCRA. Use the newer OCRAN tool instead, which properly handles native dependencies like `zlib.so` and `zlib1.dll`.

</details>

---

## See Also

- [Getting Started](getting_started.md)
- [Special Installation Instructions](special_installation.md)
- [Usage Guide](usage.md)
- [Features](features.md)
- [Style Guide](style_guide.md)

If your question is not answered here, check the [usage guide](usage.md), [troubleshooting guide](troubleshooting.md), or open an issue.

---

# Todo

[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# TODO / Planned Features

> **Project Roadmap**  
> This section collects all future feature/functionality ideas, goals, and implementation notes for Dataset Forge. Add new ideas here to keep the roadmap in one place and maintain project inspiration.

---

## 🚀 High Priority Features

### Core System Enhancements

- [ ] **Debug Mode**: Add a comprehensive _Debug Mode_ to the project, which when activated, shows verbose output and debug information throughout the CLI
- [ ] **Packaging & Distribution**:
  - [x] Compile Dataset-Forge into standalone executable (PyInstaller support)
  - [ ] Create Docker container/containerization
  - [x] Automated build pipeline for releases (GitHub Actions workflow)
  - [x] Beta release process and tools (create_beta_release.py script)
- [ ] **Automated Documentation**: Implement automated documentation generation and maintenance
- [ ] **Batch Scripts**: Save and replay complex multi-step operations/workflows
- [ ] **Global Search Functionality**: Implement comprehensive search across all menus and features
- [ ] **Path Sanitization**: Add robust path validation and sanitization throughout the application

### Advanced Data Processing

- [ ] **Advanced Data Augmentation**: Expand augmentation capabilities with model-aware techniques
  - [ ] Compositional Augmentations: Integrate Albumentations for complex augmentation pipelines
  - [ ] Mixing Augmentations: Implement Mixup and CutMix techniques
  - [ ] GAN-based Augmentations: Integrate with pre-trained StyleGAN for synthetic data generation
- [ ] **Advanced Filtering / AI-Powered Features**:
  - [ ] Semantic Filtering: Filter by image content/semantics
  - [ ] Style-Based Filtering: Filter by artistic style
  - [ ] Quality-Based Filtering: Advanced quality assessment filters
  - [ ] Custom Filter Plugins: User-defined filtering logic
  - [ ] Auto-Labeling: Automatic image labeling and classification
  - [ ] Style Transfer: Apply artistic styles to datasets
  - [ ] Content-Aware Cropping: Intelligent image cropping

### Performance & Optimization

- [ ] **Parallel Import Loading**: Load multiple modules in parallel with threading
- [ ] **Smart Caching**: Predictive loading of frequently used modules
- [ ] **Import Optimization**: Compile-time import analysis and automatic conversion
- [ ] **Performance Monitoring**: Real-time metrics and automated regression detection
- [ ] **Lazy Imports**: Ensure lazy imports everywhere to speed up CLI startup

---

## 🔧 Development & Infrastructure

### Code Quality & Testing

- [ ] **Validate Code from Other Repos**: Review and validate all code imported from external repositories
- [ ] **Improve Unit and Integration Tests**: Enhance test coverage and quality
- [ ] **Test Dataset Improvements**: Enhance test datasets for better coverage
- [ ] **Code Validation**: Implement comprehensive code validation and quality checks

### External Tool Integration

- [ ] **Phhofm's SISR**: Investigate [Phhofm's SISR](https://github.com/Phhofm/sisr) for potential integration
- [ ] **Links .json Customization**: Further customize links with metadata, descriptions, and enhanced information
- [ ] **External Tool Validation**: Validate and improve all external tool integrations

### Documentation & User Experience

- [ ] **Onboarding**: Create comprehensive onboarding documentation and flow
- [ ] **Features TL;DR**: Create a '# Features (tl;dr)' section in `./docs/features.md`
- [ ] **User Experience Enhancements**: Improve overall user experience and workflow

---

## 🎯 Specific Feature Implementations

### Image Processing & Analysis

- [ ] **Advanced Align Images Options**: Add SIFT/FLANN parameters and advanced alignment options
- [ ] **AI-Powered Dataset Analysis**: Implement AI-powered dataset analysis and recommendations
- [ ] **Advanced Analytics**: More advanced analytics and monitoring capabilities

### System Architecture

- [ ] **Modularization**: Further modularization and extensibility for new workflows
- [ ] **Cloud Integration**: Cloud integration for distributed processing and storage
- [ ] **Web Interface**: Web interface for dataset management and visualization
- [ ] **Dataset Versioning**: Implement comprehensive dataset versioning system

### Deduplication Enhancements

- [ ] **Dedicated De-dupe Menu**: Create a comprehensive dedicated deduplication menu
- [ ] **Enhanced Deduplication**: Improve existing deduplication features and workflows

---

## ✅ Completed Features

### Core System Features

- [x] **Dataset Health Scoring**: Comprehensive dataset health scoring workflow and menu option
- [x] **the-database's img-ab**: Successfully forked and improved
- [x] **find_code_issues.py**: Comprehensive static analysis tool implemented and tested
- [x] **create .exe & dll dump**: Successfully created executable and DLL dump

### Critical Bug Fixes

- [x] **Fix Critical Menu System Errors**: Resolved 'str' object is not callable and 'module' object is not callable errors

  - **Problem**: Critical menu system errors causing application crashes
  - **Solution**: Fixed lazy_action vs lazy_menu usage, pepedp lazy imports, and ProcessType enum access
  - **Files**: `dataset_management_menu.py` and related menu files
  - **Result**: Stable menu system with proper error handling

- [x] **Audio System Investigation & Fix**: Resolved CLI hanging issues and implemented robust multi-library audio system

  - **Problem**: CLI was hanging during exit due to audio playback issues
  - **Investigation**: Tested audio files, pygame mixer, winsound, and alternative libraries
  - **Solution**: Implemented robust audio system with multiple fallback libraries
  - **Libraries**: playsound (primary), winsound (Windows WAV), pydub (various formats), pygame (fallback)
  - **Features**: System-specific audio handling, format-specific optimizations, graceful error handling
  - **Testing**: All 4 audio files (done.wav, error.mp3, startup.mp3, shutdown.mp3) working perfectly
  - **Dependencies**: Added playsound==1.2.2 and pydub to requirements.txt
  - **Result**: CLI exits cleanly with full audio functionality restored

- [x] **Comprehensive Audio Implementation**: Add audio feedback throughout the entire application

  - **Status**: ✅ COMPLETED - Audio feedback added to all major action functions
  - **Files Updated**:
    - `augmentation_actions.py` - Added completion audio to `apply_augmentation_pipeline` and `create_augmentation_variations`
    - `metadata_actions.py` - Added completion audio to `exif_scrubber_menu` and `icc_to_srgb_menu`
    - `quality_scoring_actions.py` - Added completion audio to `score_images_with_pyiqa` and `score_hq_lq_folders`
    - `report_actions.py` - Added completion audio to `generate_rich_report`
    - `resave_images_actions.py` - Added completion audio to `resave_images_workflow`
    - `exif_scrubber_actions.py` - Added completion audio to `scrub_exif_single_folder` and `scrub_exif_hq_lq_folders`
    - `orientation_organizer_actions.py` - Added completion audio to `organize_images_by_orientation` and `organize_hq_lq_by_orientation`
    - `batch_rename_actions.py` - Added completion audio to `batch_rename_single_folder` and `batch_rename_hq_lq_folders`
    - `hue_adjustment_actions.py` - Added completion audio to `process_folder`
    - `frames_actions.py` - Already had completion audio in `extract_frames_menu`
  - **Audio Files**: Successfully moved to `./assets/audio/` directory for better organization
  - **Result**: Complete audio feedback throughout the application with success sounds for all major operations

- [x] **Fix Test Failures**: Resolved 3 critical test failures in performance optimization module
  - **Problem**: 3 tests failing in `test_performance_optimization.py`:
    1. `test_gpu_image_analysis` - RuntimeError due to RGB vs grayscale tensor mismatch
    2. `test_prioritize_samples` - NameError due to missing `time` import
    3. `test_end_to_end_optimization_pipeline` - NameError due to missing `time` import
  - **Solution**:
    1. Fixed GPU image analysis by properly converting RGB to grayscale for Sobel edge detection
    2. Added missing `import time` to `sample_prioritization.py`
    3. Added "size" key to GPU image analysis results to match test expectations
  - **Files Modified**:
    - `dataset_forge/utils/sample_prioritization.py` - Added time import
    - `dataset_forge/utils/gpu_acceleration.py` - Fixed RGB/grayscale conversion and added size field
  - **Testing**: All 306 tests now passing (298 passed, 7 skipped, 1 xfailed)
  - **Result**: Complete test suite stability restored

### Advanced Features

- [x] **MCP Integration Implementation**: Comprehensive MCP (Model Context Protocol) integration for enhanced development
  - **Status**: ✅ COMPLETED - MCP tools integration fully implemented and documented
  - **MCP Tools Configured**:
    1. **Brave Search Tools** - Primary research for latest libraries, best practices, and solutions
    2. **Firecrawl Tools** - Deep web scraping for documentation and content extraction
    3. **Filesystem Tools** - Project analysis and file management
    4. **GitHub Integration Tools** - Code examples and repository documentation
  - **Files Updated**:
    - `.cursorrules` - Added comprehensive MCP Integration (MANDATORY) section with tool usage patterns
    - `docs/style_guide.md` - Added MCP Integration Requirements section
    - `docs/contributing.md` - Enhanced MCP Integration Development section with mandatory requirements
    - `docs/TODO.md` - Added completion status for MCP Integration
  - **Key Features**:
    - **Mandatory MCP Tool Usage**: All contributors must use MCP tools before implementing solutions
    - **Tool Usage Patterns**: Clear workflows for different development scenarios
    - **Priority Order**: Brave Search → Firecrawl → Filesystem → GitHub Integration
    - **Usage Examples**: Practical code examples for each tool category
    - **Integration Requirements**: Specific requirements for MCP tool usage
  - **Result**: Enhanced development workflow with comprehensive research and analysis capabilities

---

## 📋 Future Considerations

### Long-term Goals

- [ ] **Stable Release**: Release a stable build with comprehensive testing
- [ ] **Community Features**: Enhanced community features and collaboration tools
- [ ] **Enterprise Features**: Enterprise-grade features for large-scale deployments
- [ ] **API Development**: RESTful API for programmatic access
- [ ] **Plugin System**: Extensible plugin system for custom functionality

### Research & Investigation

- [ ] **New Technologies**: Investigate emerging technologies for potential integration
- [ ] **Performance Research**: Research new performance optimization techniques
- [ ] **User Experience Research**: Study user workflows and optimize accordingly
- [ ] **Community Feedback**: Gather and implement community feedback and suggestions

---

## 🔄 Maintenance & Updates

### Regular Tasks

- [ ] **Dependency Updates**: Regular dependency updates and security patches
- [ ] **Documentation Updates**: Keep documentation current with feature changes
- [ ] **Test Maintenance**: Maintain and expand test coverage
- [ ] **Performance Monitoring**: Continuous performance monitoring and optimization
- [ ] **Bug Tracking**: Comprehensive bug tracking and resolution

### Quality Assurance

- [ ] **Code Review**: Implement comprehensive code review processes
- [ ] **Automated Testing**: Expand automated testing coverage
- [ ] **Static Analysis**: Regular static analysis and code quality checks
- [ ] **Security Audits**: Regular security audits and vulnerability assessments

---

> **Note**: This TODO list is a living document that should be updated as features are completed and new ideas are added. All completed features should be moved to the "Completed Features" section with detailed implementation notes.

---

## ❓ Unsorted

- [ ] **pyiqa / IQA-PyTorch**: Implement integration
- [ ] **lorem**: lorem
- [ ] **lorem**: lorem
- [ ] **lorem**: lorem
- [ ] **lorem**: lorem
- [ ] **lorem**: lorem

---

# Special Installation

[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# Special Installation Instructions

This guide covers special installation requirements for certain dependencies in Dataset Forge. These steps are **critical** for correct operation, especially on Windows. Please read carefully and follow the order for each component.

---

## 1. PyTorch with CUDA (GPU Acceleration)

**You must install the correct CUDA-enabled version of torch/torchvision/torchaudio _before_ installing other requirements.**

**Quick Steps:**

```bat
venv312\Scripts\activate
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

- Replace `cu121` with your CUDA version if needed. See [PyTorch Get Started](https://pytorch.org/get-started/locally/) for details.
- If you skip this, pip will install the CPU-only version by default.
- Only after this, run `pip install .` or `pip install -r requirements.txt`.

**Troubleshooting:**

- Mismatched CUDA/cuDNN versions will cause import errors or no GPU support.
- See [requirements.txt](../requirements.txt) and [PyTorch docs](https://pytorch.org/get-started/locally/).

---

## 2. VapourSynth & getnative

> (for [getnative](https://github.com/Infiziert90/getnative) functionality/native resolution detection)

### Method 1: Windows (Quick)

1. Extract the following file from `assets/getnative.zip`:

   - `getnative.exe`

2. Add the `getnative.exe` file's path to your PATH.

### Method 2: Windows (Better; but _TRICKY_...)

**VapourSynth must be installed _before_ [getnative](https://github.com/Infiziert90/getnative).**

**Steps (Windows):**

1. Download and install [VapourSynth](http://www.vapoursynth.com/) (includes imwri plugin).
2. Open a terminal and run:

```bat
python vsrepo.py install descale
python vsrepo.py install ffms2
python vsrepo.py install lsmas
```

3. Activate your virtual environment:

```bat
venv312\Scripts\activate
```

4. Install getnative:

```bat
pip install getnative
```

### Method 3: Windows (try building `getnative.exe` yourself)

**Steps (Windows):**

1. Git clone the [getnative repo](https://github.com/Infiziert90/getnative):

```bat
git clone https://github.com/Infiziert90/getnative.git
cd getnative
```

2. Extract the following folder from `assets/vapoursynth_install.zip`:

   - `vapoursynth_install`

3. Copy the contents of the `vapoursynth_install` folder to ./getnative/ repo root and REPLACE existing files.

4. Follow the steps outlined in `env_create.md` which should be in your ./getnative/ repo root.

**Troubleshooting:**

- Install VapourSynth _before_ getnative or any requirements that depend on it.
- If getnative fails to import, check that VapourSynth is installed and on your PATH.
- Also make sure directory containing `vsrepo.py` and the plugin's folder containing the `.dll`s are also on your PATH.
- `./assets/vapoursynth_plugins_dll.zip` contains all 4 of the vapoursynth plugins' dll's (`descale`, `ffms2`, `lsmas` & `imwri`) for whatever its worth.

- See [Getnative Recommended Windows Installation](https://github.com/Infiziert90/getnative?tab=readme-ov-file#recommended-windows-installation) for more details.

---

## 3. python-magic (for `Enhanced Directory Tree`)

**Windows users:** You must install both the Python packages and the required DLLs.

**Steps:**

1. Install the packages:

```bat
venv312\Scripts\activate
pip install python-magic python-magic-bin libmagic
```

2. Copy the following files from `assets/libmagicwin64-master.zip` to `C:/Windows/System32/`:

   - `libgnurx-0.dll`
   - `magic.mgc`
   - `magic1.dll`

   (These are prebuilt for 64-bit Windows. See source: [libmagicwin64](https://github.com/pidydx/libmagicwin64) for details.)

3. When using python-magic, specify the magic file path if needed:

```python
import magic
file_magic = magic.Magic(magic_file="C:/Windows/System32/magic.mgc")
```

**Troubleshooting:**

- If you get import errors, ensure the DLLs are in `System32` and you are using the correct magic file path.
- See [python-magic docs](https://github.com/ahupp/python-magic) and [libmagicwin64](https://github.com/pidydx/libmagicwin64).

---

## 4. Using resdet for Native Resolution Detection

> Using [resdet](https://github.com/0x09/resdet) for Native Resolution Detection

### Method 1: Windows (WSL - Recommended for CLI Integration)

1. Clone the repository:
   ```sh
   git clone https://github.com/0x09/resdet.git
   cd resdet
   ```
2. Build resdet:
   ```sh
   sudo apt update
   sudo apt install build-essential
   sudo apt install pkg-config
   sudo apt install libfftw3-dev libpng-dev mjpegtools libmagickwand-dev
   cd path/to/resdet
   make clean
   ./configure
   make
   ```
3. Install resdet to your WSL PATH:
   ```sh
   sudo cp resdet /usr/local/bin/
   sudo chmod +x /usr/local/bin/resdet
   # Or, to use make install:
   sudo make install
   ```
4. **Note:** The Dataset Forge CLI will automatically use WSL to run resdet on Windows. Ensure resdet is available in your WSL environment's PATH.

### Method 2: Windows (MSYS2 MINGW64 Shell)

1. Clone the repository:
   ```sh
   git clone https://github.com/0x09/resdet.git
   ```
2. Open **MSYS2 MINGW64 Shell**.
3. Install dependencies:
   ```sh
   pacman -S base-devel mingw-w64-x86_64-toolchain mingw-w64-x86_64-libpng mingw-w64-x86_64-libjpeg-turbo mingw-w64-x86_64-fftw mingw-w64-x86_64-pkg-config autoconf automake libtool
   ```
4. Set PKG_CONFIG_PATH:
   ```sh
   export PKG_CONFIG_PATH=/mingw64/lib/pkgconfig
   ```
5. Build resdet:
   ```sh
   cd path/to/resdet
   make clean
   ./configure --prefix=/mingw64
   make
   ```
6. Add `resdet.exe` to a folder in your PATH, or add its folder to your PATH.

### Method 3: Windows (Windows pre-build binary)

1. Extract the following files from `assets/resdet_windows.zip`:

   - `resdet.exe`

   (This is a prebuilt for 64-bit Windows that I compiled.)

2. Add `resdet.exe` to a folder in your PATH, or add its folder to your PATH.

### Usage in Dataset Forge

- The CLI will detect your platform and use the appropriate resdet binary.
- On Windows, if WSL is available and resdet is installed in WSL, it will be used automatically.
- If resdet is not found, you will receive a clear error message with installation instructions.

---

## 5. Advanced Metadata Operations with ExifTool

> (for [exiftool](https://exiftool.org/) integration)

### Method 1.1: Windows (Quick)

1. Extract the following folder from `assets/exiftool-13.32_64.zip`:

   - `exiftool-13.32_64`

2. Add the `exiftool-13.32_64` folder path to your PATH.

### Method 1.2: Windows (Better)

1. Download ExifTool.exe:

   https://exiftool.org/

2. Download the Windows Executable (e.g., `exiftool-12.70.zip`).

3. Extract it and rename `exiftool(-k).exe` to `exiftool.exe` for command-line use.

4. Add `exiftool.exe` to a folder in your PATH, or add its folder to your PATH.

> **IMPORTANT:** Note that if you move the .exe to another folder, you must also move the "exiftool_files" folder to the same location.

### Method 2: Windows (Chocolatey)

1. Download ExifTool.exe:

   ```sh
   choco install exiftool -y
   ```

2. This will install `exiftool.exe` to:

   ```sh
   C:\ProgramData\chocolatey\lib\exiftool\tools\
   ```

3. Add `exiftool.exe` to a folder in your PATH, or add its folder to your PATH.

---

## 6. Metadata Strip + Lossless png compression with Oxipng

> (for [Oxipng](https://github.com/oxipng/oxipng) integration)
> essential for 'Sanitise Image Workflow'

### Method 1.1: Windows (Quick)

1. Extract the following folder from `assets/oxipng-9.1.5-x86_64-pc-windows-msvc.zip`:

   - `oxipng-9.1.5-x86_64-pc-windows-msvc`

2. Add the `oxipng-9.1.5-x86_64-pc-windows-msvc` folder path to your PATH.

### Method 1.2: Windows (Better)

1. Download oxipng.exe:

   https://github.com/oxipng/oxipng/releases

2. Download the appropriate archive (e.g., `oxipng-9.1.5-x86_64-pc-windows-msvc.zip`).

3. Extract the contents.

4. Add `oxipng.exe` to a folder in your PATH, or add its folder to your PATH.

---

## 7. Steganography Integration for zsteg and Steghide

> (for [zsteg](https://github.com/zed-0xff/zsteg) & [Steghide](https://steghide.sourceforge.net/) integration)
> optional for 'Sanitise Image Workflow'

### zsteg installation (Windows)

#### Method 1: Gem Installation (Recommended)

1. Install Ruby (via RubyInstaller for Windows)

- Go to: [https://rubyinstaller.org/](https://rubyinstaller.org/)
- Download the **latest Ruby+Devkit** version (e.g. `Ruby 3.3.0 with Devkit`).
- Run the installer.
- On the final screen, check **"Add Ruby executables to your PATH"**.
- Also allow it to **install MSYS2 and development tools** when prompted.

2. Restart PowerShell/Terminal/Console/CLI

3. Install `zsteg`
   ```sh
   gem install zsteg
   ```

#### Method 2.1: Standalone Executable (Quick)

For users who need a standalone `zsteg.exe` executable:

1. Extract the following files from `assets/zsteg_0.2.13_win.zip`:

   - `zsteg.exe`

   (This is a prebuilt Windows binary built using [Largo/ocran](https://github.com/Largo/ocran) that I compiled.)

2. Add `zsteg.exe` to a folder in your PATH, or add its folder to your PATH.

3. You can now use `zsteg.exe` as a CLI tool.

#### Method 2.2: Standalone Executable (Advanced)

For users who need a standalone `zsteg.exe` executable:

1. Install Ruby (via RubyInstaller for Windows)

- Go to: [https://rubyinstaller.org/](https://rubyinstaller.org/)
- Download the **latest Ruby+Devkit** version (e.g. `Ruby 3.3.0 with Devkit`).
- Run the installer.
- On the final screen, check **"Add Ruby executables to your PATH"**.
- Also allow it to **install MSYS2 and development tools** when prompted.

2. Restart PowerShell/Terminal/Console/CLI

3. Remove old OCRA and install OCRAN

- Remove the old OCRA then install the newer OCRAN (maintained fork)

```bash
gem uninstall ocra
gem install ocran
```

4. Install `zsteg`

   ```sh
   gem install zsteg
   ```

5. **Create zsteg CLI wrapper**

   Extract the following files from `assets/zsteg_cli_build.zip`:

   - `zsteg_cli.rb`
   - `fiber.so`

6. **Build the executable using OCRAN**

   ```sh
   ocran zsteg_cli.rb --gem-all --add-all-core --output zsteg.exe --verbose
   ```

7. **Test the executable**
   ```sh
   ./zsteg.exe --help
   OR
   ./zsteg.exe --help > output.txt 2>&1
   ```

> **Note**: The OCRAN-built executable includes all necessary dependencies and runs without requiring Ruby to be installed on the target system. This method uses the [Largo/ocran](https://github.com/Largo/ocran) fork which provides better Windows compatibility and dependency handling compared to the original OCRA.

> **Technical Details**: OCRAN properly handles native dependencies like `zlib.so`, `zlib1.dll`, and assembly manifest files that cause side-by-side configuration failures with OCRA.

> **Troubleshooting**: If you encounter side-by-side configuration errors with the original OCRA, use the OCRAN method above which properly handles native dependencies like `zlib.so` and `zlib1.dll`.

### steghide installation

#### Method 1.1: Windows (Quick)

1. Extract the following folder from `assets/steghide-0.5.1-win32.zip`:

   - `steghide`

2. Add the `steghide` folder path to your PATH.

#### Method 1.2: Windows (Better)

1. Download Steghide

   [Steghide Windows package](http://prdownloads.sourceforge.net/steghide/steghide-0.5.1-win32.zip?download)

2. Extract the contents (`steghide` folder).

3. Add the `steghide` folder path to your PATH.

---

## 8. ffmpeg integration

> (for [ffmpeg](https://ffmpeg.org/) integration)

### Method 1.1: Windows (Quick)

1. Extract the following folder from `assets/ffmpeg-2025-07-31-git-119d127d05-full_build.zip`:

   - `ffmpeg-2025-07-31-git-119d127d05-full_build`

- Note that this^ folder contains a `bin` folder which contains:

  - `ffmpeg.exe`
  - `ffplay.exe`
  - `ffprobe.exe`

2. Add the path to the `bin` folder to your PATH.

### Method 1.2: Windows (Better)

1. Download [`FFmpeg Builds`](https://www.gyan.dev/ffmpeg/builds/) (binaries for Windows):

   ```bash
   winget install ffmpeg
   OR
   choco install ffmpeg-full
   OR
   scoop install ffmpeg
   ```

### Method 1.3: Windows (`Method 1.1` but download first)

1. Download `ffmpeg-git-full.7z`:

   https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z

2. Extract the contents of the downloaded archive.

- Note that this^ folder should contain a `bin` folder which contains:

  - `ffmpeg.exe`
  - `ffplay.exe`
  - `ffprobe.exe`

3. Add the path to the `bin` folder to your PATH.

---

## 9. Special mass implementation of above^^

> shortcut that implements multiple special installations from above

_might, might not work_

### Step 1: Windows binary dump

1. Extract the following folder from `assets/_win_binary_dump.zip`:

   - `_win_binary_dump`

2. Add the path to the `_win_binary_dump` folder path to your PATH.

**this includes**:

```txt
exiftool.exe
ffmpeg.exe
ffplay.exe
ffprobe.exe
getnative.exe
oxipng.exe
resdet.exe
steghide.exe
zsteg.exe
pyiqa.exe
imagededup.exe
```

### Step 2: Windows dll dump

1. Extract the following folder from `assets/_win_dll_dump.zip`:

   - `_win_dll_dump`

2. Add the path to the `_win_dll_dump` folder path to your PATH.

**this includes ddl's for**:

```txt
VapourSynth's plugins
python-magic's dll's & .mgc magicfile
```

### Step 3: Test the implementations

1. lorem ipsum

---

---

## 10. CUDA & GPU Performance Steps

> a guide on optimizing performance

### Step 1: Always use ./run.bat/

1. When Using Dataset-Forge always start is using:

```bs
   ./run.bat
```

_run.bat contains CUDA & Pytorch optimization settings_

### Step 2: Be Sure your `venv312` has cuda torch installed

1. See [Getting Started](getting_started.md#-installation) for:

   `CUDA-enabled torch/torchvision/torchaudio` installation instruction.

### Step 3: Windows Pagefile

1. Press the Windows key + R to open the Run dialog box.

Type `SystemPropertiesAdvanced.exe` and press Enter.

2. Where to go:

**Performance** section
click
`Settings...`
**Advanced** tab
**Virtual Memory** section
click
`Change`
check **"Custom Size"**:
radio button
**Initial size**

> 1.5 x your totall RAM for
> **Maximum size**
> 3 x your totall RAM
> click `OK`
> Restart Windows

### Step 4: NVIDIA Control Panel

1. Right Click Desktop:

click
**NVIDIA Control Panel**
**Manage 3D settings** > **Program Settings**
Add:
Full path to your
`venv312`'s `python.exe`
like
`C:/Users/username/github/Dataset-Forge/venv312/Scripts/python.exe`
then change these settings:
**CUDA - GPUs**:

> All
> **CUDA - Sysmem Fallback Policy**:
> Prefer No Sysmem Fallback
> **Power management mode**:
> Prefer maximum performance
> **Texture filtering - Quality**:
> High performance
> **Threaded optimization**:
> On
> click **Apply**

---

For more details, see the [main README Quick Start](../README.md#-quick-start) and [troubleshooting guide](troubleshooting.md).


---

# Changelog

[//]: # "Navigation"

[← Back to Main README](../README.md) | [Features](features.md) | [Usage Guide](usage.md)

# Changelog

## [Unreleased]

### 🎨 Comprehensive Menu System Improvement (August 2025)

- **Major Achievement**: Complete transformation of Dataset Forge's menu system with perfect theming compliance and enhanced user experience
- **Menu System Statistics**:
  - **201 Total Menus**: Comprehensive coverage with 4-level hierarchy optimization
  - **0 Theming Issues**: Perfect compliance (down from 1,557 - 100% reduction)
  - **4,774 Centralized Print Usages**: Consistent user experience throughout
  - **16,274 Total Emojis**: Consistent, contextually appropriate usage
  - **59 Path Input Scenarios**: Strategic user interaction points
- **Phase 1 Achievements - Critical Fixes COMPLETED**:
  - **Perfect Theming Compliance**: Fixed ALL 1,557 theming issues (100% reduction)
  - **Standardized Menu Patterns**: Fixed ALL 15 incorrect menu patterns (100% reduction)
  - **Function References**: Resolved ALL 59 unresolved function references
  - **Menu Context**: Added comprehensive context to ALL 201 menus (100% coverage)
  - **Training Menu**: Completed Training & Inference menu (10/10 options functional)
  - **Raw Print Statements**: Fixed ALL 1,158 raw print statements (100% reduction)
  - **Missing Imports**: Fixed ALL 366 missing Mocha imports (100% reduction)
- **Phase 2 Achievements - Menu Organization COMPLETED**:
  - **Main Menu Optimization**: Reordered for better workflow with Image Processing at #2
  - **Menu Consolidation**: 6 separate menus consolidated into 2 unified menus
  - **Enhanced Navigation**: Logical progression with quick return paths
  - **Improved Naming**: Descriptive and consistent menu naming conventions
  - **Workflow Optimization**: Better organization and user experience
- **Phase 3 Achievements - User Experience IN PROGRESS**:
  - **Enhanced Descriptions**: Comprehensive menu descriptions with usage examples
  - **Advanced Help System**: Troubleshooting, feature-specific guidance, quick reference
  - **Workflow Guidance**: Step-by-step examples and best practices
  - **Performance Notes**: Optimization tips and format comparisons
- **Menu Consolidation Highlights**:
  - **Consolidated De-duplication**: Unified menu combining fuzzy matching, visual deduplication, and hash-based methods
  - **Consolidated Compression**: Single menu for individual and directory compression
  - **Enhanced Utilities**: Streamlined comparison, metadata, and monitoring tools
- **Global Command System**:
  - **71 Comprehensive Tests**: Complete test coverage for all global command functionality
  - **Context-Aware Help**: Menu-specific assistance with detailed guidance
  - **Perfect Integration**: All 201 menus support global commands (100% coverage)
- **Files Updated**:
  - All menu files: Standardized patterns and comprehensive context
  - All action files: Perfect theming compliance and error handling
  - All utility files: Centralized printing and consistent styling
  - `docs/features.md` - Updated with menu system excellence section
  - `docs/usage.md` - Enhanced with menu system achievements
  - `docs/menu_improvement_progress.md` - New comprehensive progress tracking
  - `.cursorrules` - Updated with current achievements and development status
- **Testing**: Comprehensive validation with 0 theming issues and 100% menu pattern compliance
- **Documentation**: Complete progress tracking, achievement documentation, and user experience enhancements
- **Result**: Production-ready menu system with perfect theming compliance, standardized patterns, and excellent user experience
- **User Experience**: Intuitive navigation, comprehensive help, consistent styling, and logical workflow progression

### 🔍 Fuzzy Matching De-duplication Feature (December 2024)

- **New Feature**: Comprehensive fuzzy matching duplicate detection using multiple perceptual hashing algorithms
- **Key Features**:
  - **Multiple Hash Algorithms**: pHash, dHash, aHash, wHash, Color Hash with configurable thresholds
  - **Flexible Operation Modes**: Show, Copy, Move, Delete (with confirmation) for safe duplicate management
  - **Folder Support**: Single folder and HQ/LQ paired folders with comprehensive analysis
  - **Consolidated Menu**: Replaces individual duplicate detection menus with unified fuzzy matching interface
  - **Comprehensive Reporting**: Detailed statistics and duplicate group analysis with similarity scores
- **Hash Algorithms**:
  - **pHash (Perceptual Hash)**: Content-based detection with 90% default threshold
  - **dHash (Difference Hash)**: Edge-based detection with 85% default threshold
  - **aHash (Average Hash)**: Brightness-based detection with 80% default threshold
  - **wHash (Wavelet Hash)**: Texture-based detection with 85% default threshold
  - **Color Hash**: Color distribution-based detection with 75% default threshold
- **Performance Characteristics**:
  - **Processing Speed**: ~200 images/second for perceptual hash computation
  - **Memory Usage**: Optimized batch processing with efficient memory management
  - **Scalability**: Production-ready for large datasets (1000+ images tested)
  - **Accuracy**: Configurable thresholds for precision/recall balance
- **Threshold Guidelines**:
  - **Conservative**: High accuracy thresholds (95% for pHash, 90% for dHash, etc.)
  - **Balanced**: Recommended settings (90% for pHash, 85% for dHash, etc.)
  - **Aggressive**: More duplicates detected (80% for pHash, 75% for dHash, etc.)
- **Files Added**:
  - `dataset_forge/menus/fuzzy_dedup_menu.py` - Comprehensive fuzzy deduplication menu
  - `dataset_forge/actions/fuzzy_dedup_actions.py` - Fuzzy matching implementation with multiple algorithms
  - `docs/fuzzy_deduplication.md` - Complete documentation for fuzzy deduplication feature
- **Files Updated**:
  - `dataset_forge/menus/utilities_menu.py` - Consolidated duplicate detection menus into fuzzy matching
  - `dataset_forge/utils/file_utils.py` - Added `get_image_files()` function for image file listing
  - `docs/features.md` - Added comprehensive fuzzy deduplication feature documentation
  - `docs/usage.md` - Added fuzzy deduplication usage guide with examples
  - `docs/changelog.md` - Documented new feature implementation
- **Menu Structure Changes**:
  - **Replaced**: Individual duplicate detection menus (Visual De-duplication, De-Duplicate File Hash, ImageDedup)
  - **Added**: Unified "🔍 Fuzzy Matching De-duplication" menu in Utilities
  - **Consolidated**: All duplicate detection functionality into single comprehensive menu
- **Testing**: Comprehensive test suite with successful validation of fuzzy deduplication workflow
- **Documentation**: Complete usage guide, best practices, threshold guidelines, and troubleshooting
- **Result**: Production-ready fuzzy duplicate detection with flexible configuration and safe operation modes
- **User Experience**: Intuitive menu navigation, comprehensive reporting, and safe operation modes with confirmation

### ⭐ BHI Filtering Advanced CUDA Optimizations (August 2025)

- **Major Enhancement**: Comprehensive CUDA optimization system for BHI (Blockiness, HyperIQA, IC9600) filtering
- **Performance Improvements**:
  - **Mixed Precision (FP16)**: 30-50% memory reduction with automatic fallback
  - **Dynamic Batch Sizing**: Automatic batch size adjustment based on available GPU memory
  - **Memory Management**: Comprehensive GPU memory cleanup and CPU fallback
  - **Windows Compatibility**: Optimized for Windows CUDA multiprocessing limitations
  - **Progress Tracking**: Real-time progress bars with detailed metrics
- **New Features**:
  - **Flexible File Actions**: Move, copy, delete, and report actions with user confirmation
  - **Smart Processing Order**: IC9600 runs first (most memory-intensive) when GPU memory is cleanest
  - **Conservative Default Thresholds**: 0.3 for all metrics (prevents over-filtering)
  - **Comprehensive Error Handling**: Graceful CUDA memory error recovery with CPU fallback
  - **Environment Variable Optimization**: Automatic CUDA optimization via `run.bat`
- **Technical Implementation**:
  - **Mixed Precision**: `torch.amp.autocast('cuda')` for memory efficiency
  - **Dynamic Batch Size**: `get_optimal_batch_size()` based on available GPU memory
  - **Memory Cleanup**: Periodic `clear_memory()` and `clear_cuda_cache()` calls
  - **CPU Fallback**: Automatic fallback to CPU processing on CUDA memory errors
  - **DataLoader Optimization**: `num_workers=0` and conditional `pin_memory` for Windows compatibility
- **Environment Variables** (automatically set in `run.bat`):
  ```batch
  PYTORCH_NO_CUDA_MEMORY_CACHING=1
  PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128,expandable_segments:True
  CUDA_LAUNCH_BLOCKING=0
  OMP_NUM_THREADS=1
  MKL_NUM_THREADS=1
  CUDA_MEMORY_FRACTION=0.9
  ```
- **Threshold Guidelines**:
  - **Conservative**: 0.3 for all metrics (filters ~20-40% of images)
  - **Moderate**: 0.5 for all metrics (filters ~10-20% of images)
  - **Aggressive**: 0.7 for all metrics (filters ~5-10% of images)
- **Files Updated**:
  - `dataset_forge/actions/bhi_filtering_actions.py` - Complete CUDA optimization implementation
  - `dataset_forge/menus/bhi_filtering_menu.py` - Enhanced action selection and confirmation
  - `run.bat` - Added comprehensive CUDA optimization environment variables
  - `configs/cuda_optimization.json` - New configuration file for CUDA settings
  - `docs/usage.md` - Comprehensive BHI filtering documentation with examples
  - `docs/features.md` - Updated BHI filtering feature description
  - `.cursorrules` - Added Advanced CUDA Optimization Pattern and BHI Filtering Pattern
  - `tests/test_utils/test_bhi_filtering.py` - Comprehensive test suite for CUDA optimizations
  - `tests/test_utils/test_cuda_optimizations.py` - New test file for CUDA optimization features
- **Testing**: Comprehensive test suite covering CUDA availability, mixed precision, memory management, batch sizing, DataLoader optimization, error handling, and performance monitoring
- **Documentation**: Complete usage guide with workflow examples, troubleshooting, and advanced configuration
- **Result**: High-performance BHI filtering with robust CUDA optimization, comprehensive error handling, and excellent user experience
- **User Experience**: Real-time progress tracking, flexible file actions, automatic optimization, and graceful error recovery

### 🔗 MCP Integration Implementation (August 2025)

- **New Feature**: Comprehensive MCP (Model Context Protocol) integration for enhanced development workflow
- **MCP Tools Configured**:
  - **Brave Search Tools**: Primary research for latest libraries, best practices, and solutions
  - **Firecrawl Tools**: Deep web scraping for documentation and content extraction
  - **Filesystem Tools**: Project analysis and file management
  - **GitHub Integration Tools**: Code examples and repository documentation
- **Key Features**:
  - **Mandatory MCP Tool Usage**: All contributors must use MCP tools before implementing solutions
  - **Tool Usage Patterns**: Clear workflows for different development scenarios (implementing, debugging, adding features)
  - **Priority Order**: Brave Search → Firecrawl → Filesystem → GitHub Integration
  - **Usage Examples**: Practical code examples for each tool category
  - **Integration Requirements**: Specific requirements for MCP tool usage and documentation
- **Files Updated**:
  - `.cursorrules` - Added comprehensive MCP Integration (MANDATORY) section with tool usage patterns
  - `docs/style_guide.md` - Added MCP Integration Requirements section
  - `docs/contributing.md` - Enhanced MCP Integration Development section with mandatory requirements
  - `docs/TODO.md` - Added completion status for MCP Integration
- **Development Workflow Enhancement**:
  - Research Phase: Use Brave Search for latest libraries and best practices
  - Deep Dive: Use Firecrawl for detailed content extraction
  - Project Context: Use Filesystem tools for current implementation analysis
  - Code Examples: Use GitHub tools for relevant code patterns
- **Result**: Enhanced development workflow with comprehensive research and analysis capabilities
- **Documentation**: Complete integration with existing documentation structure and development standards

### 🔊 Audio System Investigation & Robust Multi-Library Implementation (August 2025)

- **Problem Resolved**: CLI hanging during exit due to audio playback issues
- **Investigation**: Comprehensive analysis of audio files, pygame mixer, winsound, and alternative libraries
- **Solution**: Implemented robust multi-library audio system with intelligent fallbacks
- **Audio Libraries Implemented**:
  - **Playsound (1.2.2)**: Primary cross-platform audio library
  - **Winsound**: Optimized for Windows WAV files
  - **Pydub**: Handles various audio formats including MP3
  - **Pygame**: Cross-platform fallback option
- **Key Features**:
  - System-specific audio handling (Windows vs other platforms)
  - Format-specific optimizations (WAV vs MP3 handling)
  - Graceful error handling and fallback mechanisms
  - Non-blocking audio playback with timeout protection
  - Thread-safe audio operations
- **Audio Files Tested**: All 4 audio files working perfectly
  - `done.wav` (352,844 bytes) - Success sounds
  - `error.mp3` (32,600 bytes) - Error feedback
  - `startup.mp3` (78,240 bytes) - Application startup
  - `shutdown.mp3` (23,808 bytes) - Application exit
- **Dependencies Added**:
  - `playsound==1.2.2` - Primary audio library
  - `pydub` - Alternative audio library for various formats
- **Testing**: Comprehensive testing of all exit methods (`q`, `quit`, `exit`, `0`, `Ctrl+C`)
- **Result**: CLI exits cleanly with full audio functionality restored
- **Documentation**: Updated requirements.txt and audio system documentation
- **User Experience**: Reliable audio feedback without hanging or blocking issues

### 🔧 zsteg.exe Standalone Executable Solution (August 2025)

- **New Feature**: Successfully resolved zsteg.exe side-by-side configuration issues
- **Solution**: Implemented OCRAN-based standalone executable creation method
- **Key Improvements**:
  - Replaced problematic OCRA with newer OCRAN (Largo/ocran fork)
  - Proper handling of native dependencies (`zlib.so`, `zlib1.dll`)
  - Self-contained executable that doesn't require Ruby installation
  - Comprehensive error handling and dependency inclusion
- **Technical Details**:
  - Uses `ocran zsteg_cli.rb --gem-all --add-all-core --output zsteg.exe --verbose`
  - Includes all necessary gems and native extensions
  - Proper manifest file handling for Windows compatibility
  - Tested and verified working executable with help output
- **Documentation**: Updated special_installation.md and troubleshooting.md with detailed instructions
- **User Experience**: Provides both gem installation and standalone executable options
- **Troubleshooting**: Added comprehensive FAQ and troubleshooting sections for zsteg-related issues
- **Integration**: Comprehensive solution integrated into existing documentation structure and .cursorrules

### 🎨 Catppuccin Mocha Theming Consistency Checker (August 2025)

- **New Feature**: Added comprehensive Catppuccin Mocha theming consistency checker tool
- **Tool Location**: `tools/check_mocha_theming.py`
- **Features**:
  - Comprehensive analysis of all Python, Markdown, and batch files in the codebase
  - Detection of raw print statements that should use centralized utilities
  - Validation of Mocha color imports and centralized printing utility usage
  - Menu pattern analysis for proper theming implementation
  - Detailed reporting with actionable recommendations and issue categorization
  - CLI integration with tools launcher and comprehensive error handling
- **Analysis Capabilities**:
  - Raw print statement detection (1,673 found in initial analysis)
  - Missing Mocha import validation (304 issues found)
  - Menu context parameter checking (20 missing parameters)
  - Menu pattern validation (13 incorrect patterns)
  - Documentation theming consistency checks
- **Integration**: Fully integrated with Dataset Forge's tools launcher and development workflow
- **Documentation**: Comprehensive usage instructions and best practices in features.md and usage.md
- **CI/CD Ready**: Proper exit codes and reporting for automated workflows
- **User Experience**: Real-time analysis progress, detailed markdown reports, and actionable recommendations

### ⚡ CLI Optimization & Lazy Import System Integration (August 2025)

- **Documentation Integration**: Comprehensive CLI optimization and lazy import system documentation integrated into existing structure
- **Performance Guidelines**: Added detailed performance optimization guidelines to .cursorrules and advanced.md
- **Lazy Import Standards**: Established mandatory lazy import patterns for heavy libraries (PyTorch, OpenCV, matplotlib, transformers)
- **Startup Optimization**: Documented 50-60% startup time improvement through lazy loading strategies
- **Memory Management**: Integrated lazy memory allocation and GPU memory optimization guidelines
- **Performance Monitoring**: Added import timing analysis and monitoring decorator usage standards
- **Best Practices**: Comprehensive best practices for when to use lazy imports vs. direct imports
- **Troubleshooting**: Added troubleshooting guidelines for import errors and performance issues
- **Future Improvements**: Documented planned enhancements including parallel import loading and smart caching

### 🧹 Cleanup & Optimization Tools (July 2025)

- **New Feature**: Added comprehensive cleanup and optimization tools to System Monitoring & Health menu
- **Cleanup Actions**:
  - `dataset_forge/actions/cleanup_actions.py` - Core cleanup functionality
  - `dataset_forge/menus/cleanup_menu.py` - Cleanup menu interface
- **Features**:
  - Recursive removal of `.pytest_cache` folders
  - Recursive removal of `__pycache__` folders
  - Comprehensive system cleanup (cache folders + system caches + memory)
  - Cache usage analysis with size reporting and recommendations
- **Integration**: Fully integrated with Dataset Forge's monitoring, memory management, and progress tracking
- **Testing**: Comprehensive test suite with 15 passing tests covering all functionality
- **Documentation**: Updated features.md with detailed cleanup functionality documentation
- **User Experience**: Catppuccin Mocha color scheme, progress tracking, and comprehensive error handling

### 🌐 Global Command System & Comprehensive Help Documentation (July 2025)

- **New Feature**: Implemented global help and quit commands across all menus and sub-menus
- **Global Commands**:
  - `help`, `h`, `?` - Show context-aware help for current menu
  - `quit`, `exit`, `q` - Exit Dataset Forge completely with cleanup
  - `0` - Go back to previous menu (existing)
  - `Ctrl+C` - Emergency exit with cleanup (existing)
- **Context-Aware Help**: Menu-specific help information with navigation tips and feature descriptions
- **Memory Management**: Automatic cleanup on quit with proper resource management
- **User Experience**:
  - Case-insensitive commands for better usability
  - Menu redraw after help for clarity
  - Consistent Catppuccin Mocha color scheme across all help screens
  - No raw print statements - all output is styled and consistent
- **Comprehensive Documentation**: Created `menu_system/comprehensive_help_menu.md` (31,665 bytes) with detailed help for all menus
- **Testing**: Comprehensive test suite with 71 tests covering all global command functionality
  - Unit tests for command handling and help system
  - Integration tests for menu context and CLI interactions
  - Edge case testing for invalid inputs and error handling
- **Menu Updates**: Updated all menu files to include `current_menu` and `menu_context` parameters
- **Enhanced Error Handling**: Graceful handling of `None` and non-string inputs in global commands
- **Documentation Integration**: Global command system implementation details integrated into advanced.md, usage.md, and contributing.md
- **MCP Integration Documentation**: MCP server integration details and development workflows integrated into advanced.md and contributing.md

### 🔄 Resave Images Integration (July 2025)

- **New Feature**: Added resave images functionality to Image Processing & Augmentation → Basic Transformations
- **Format Support**: Convert images to PNG, JPEG, WebP, BMP, TIFF with optional grayscale conversion
- **Parallel Processing**: Thread-based processing with `ThreadPoolExecutor` for optimal performance
- **Memory Efficient**: Limited worker count and automatic memory cleanup to prevent memory issues
- **Recursive Processing**: Support for processing subdirectories
- **Unique Filenames**: Automatic unique filename generation to prevent overwriting
- **Integration**: Fully integrated with Dataset Forge's monitoring, memory management, and progress tracking
- **Testing**: Comprehensive test suite with 15 passing tests covering all functionality
- **Documentation**: Updated features, usage, advanced, and architecture documentation

### 🧩 PepeDP-powered Umzi's Dataset_Preprocessing Integration (July 2025)

- Replaced all legacy Umzi Dataset_Preprocessing logic with thin, testable wrappers around PepeDP.
- All four main workflows (Best Tile Extraction, Video Frame Extraction, Duplicate Detection, IQA Filtering) now use the latest PepeDP API.
- All workflows are robust, modular, and fully covered by non-interactive, public API tests.
- Updated all relevant documentation, style guide, and .mdc rules.

### 🚀 Performance Optimization Suite (NEW July 2025)

#### **GPU Acceleration**

- **New module:** `dataset_forge/utils/gpu_acceleration.py`
- GPU-accelerated image preprocessing operations (brightness/contrast, saturation/hue, sharpness/blur)
- Batch transformation support with PyTorch/TorchVision
- GPU image analysis and SIFT keypoint detection
- Automatic device detection and memory management
- Cached operations with TTL and compression

#### **Distributed Processing**

- **New module:** `dataset_forge/utils/distributed_processing.py`
- Multi-machine and single-machine multi-GPU processing
- Dask and Ray integration with automatic resource detection
- Auto-detection of optimal processing mode and worker count
- Cluster management with dashboard and monitoring
- Batch processing with progress tracking and error handling

#### **Intelligent Sample Prioritization**

- **New module:** `dataset_forge/utils/sample_prioritization.py`
- Quality-based sample prioritization using advanced image analysis
- Sharpness, contrast, noise, artifact, and complexity analysis
- Hybrid scoring with configurable weights
- Adaptive batch creation based on priority scores
- Extensible analysis framework

#### **Pipeline Compilation**

- **New module:** `dataset_forge/utils/pipeline_compilation.py`
- JIT compilation using Numba, Cython, and PyTorch JIT
- Auto-detection of optimal compilation strategy
- Decorator-based compilation with fallback support
- Pre-compiled utility functions for common operations
- Compilation status monitoring and management

#### **Performance Optimization Menu**

- **New menu:** `dataset_forge/menus/performance_optimization_menu.py`
- Centralized UI for all performance optimization features
- GPU acceleration testing and configuration
- Distributed processing cluster management
- Sample prioritization configuration and testing
- Pipeline compilation testing and settings
- Performance analytics and monitoring
- Global optimization settings

#### **Comprehensive Testing**

- **New test suite:** `tests/test_utils/test_performance_optimization.py`
- Complete coverage of all performance optimization modules
- Integration tests for end-to-end workflows
- Performance benchmarks and memory management checks
- Error handling and edge case testing

#### **Dependencies**

- Added Dask[complete], Ray[default] for distributed processing
- Added Numba, Cython for pipeline compilation
- Added Kornia, Albumentations for GPU acceleration
- All dependencies properly grouped and documented in requirements.txt

### 🔧 Technical Improvements

- Enhanced memory management integration across all optimization features
- Centralized monitoring and analytics for performance tracking
- Robust error handling with graceful fallbacks
- Comprehensive logging and debugging support
- Cross-platform compatibility (Windows, Linux)

### 📚 Documentation

- Updated features.md with comprehensive performance optimization documentation
- Added usage examples and integration guides
- Updated architecture diagrams and technical specifications
- Enhanced troubleshooting guides for optimization features

- **Enhanced Caching System (July 2025):**
  - Completely rewrote and enhanced the caching system from basic implementation to production-ready solution
  - Added AdvancedLRUCache class with TTL, compression, statistics, and thread safety
  - Implemented comprehensive disk caching with integrity checks and file management
  - Added specialized model caching for expensive AI model loading operations
  - Created smart cache decorator with auto-detection of optimal caching strategy
  - Built comprehensive cache management menu with statistics, maintenance, and optimization tools
  - Added cache warmup, validation, repair, and export functionality
  - Integrated caching into key functions: get_image_size, enum_to_model, get_clip_model, is_image_file
  - Created robust test suite covering all caching functionality with 107 passing tests
  - Fixed critical issues: UnboundLocalError in smart_cache, disk cache filename validation, None value handling
  - Updated all documentation to reflect enhanced caching capabilities and best practices
- Added comprehensive [Style Guide](style_guide.md) to docs/ for coding standards, architecture, and best practices (July 2025).
- **OpenModelDB Integration:**
  - Added OpenModelDB Model Browser with classic and CLI-interactive modes
  - Search, filter, view, download, and test models from OpenModelDB
  - Robust download logic (SHA256, Google Drive, OneDrive/manual fallback)
  - CLI-interactive mode with live search, arrow keys, and dynamic actions
  - Batch upscaling, Spandrel/ONNX support, tiling, alpha handling, device/precision selection
  - Improved error handling, user feedback, and Catppuccin Mocha UI
- **Advanced Monitoring, Analytics & Error Tracking:**
  - Added monitoring.py utility for live resource usage (CPU, GPU, RAM, disk), performance analytics, error tracking, health checks, and background task registry.
  - Added system_monitoring_menu.py for CLI access to monitoring, analytics, error summaries, health checks, and background task management.
  - Decorator-based integration for analytics and error tracking in all action modules.
  - Persistent logging of analytics and errors to ./logs/.
  - Notifications for critical errors (sound/visual).
  - Memory and CUDA cleanup integrated on exit/errors for all tracked processes/threads.
  - Background task management: pause, resume, kill subprocesses/threads from CLI.
- Added Content-Based Image Retrieval (CBIR) for Duplicates:
  - Semantic duplicate detection using CLIP, ResNet, and VGG embeddings
  - Fast similarity search and grouping with ANN indexing
  - Batch actions: find, remove, move, copy duplicate groups
  - Integrated into Clean & Organize submenu under Dataset Management
- Integrated comprehensive automated test suite (pytest-based)
- Covers CLI, menu timing, error feedback, memory, parallelism, file/image utils
- Handles Unicode, subprocess, and Windows-specific issues
- Manual/script tests for BHI filtering and pepeline
- All tests pass as of this integration
- Refactored all DPID logic to use the new modular structure (`dataset_forge.dpid.*`). Legacy imports from `dataset_forge.utils.dpid_phhofm` removed.
- All menus now use the robust menu loop pattern (get key, look up action, call if callable, handle errors).
- All user-facing workflows are responsible for their own 'Press Enter to return to the menu...' prompt. Menu loops no longer include this prompt.
- All output, prompts, and progress messages now use the centralized printing utilities and Catppuccin Mocha color scheme. No raw print statements remain in user-facing workflows.
- Exception handling and debug prints added to menu actions and workflows for easier debugging and error diagnosis.
- Major test suite improvements: added and improved unit/integration tests for DPID, CBIR, deduplication, reporting, utilities, session state, and more.
- All core business logic and utilities now covered by tests.
- Fixed test import errors, function signatures, and monkeypatches for reliability.
- Integrated Umzi's Dataset_Preprocessing as a modular menu and actions set.
- Added Best Tile Extraction, Video Frame Extraction, Image Deduplication, IQA Filtering, and Embedding Extraction workflows.
- All features are fully interactive, testable, and documented.
- Added robust unit and CLI integration tests for all workflows.
- Updated documentation in features.md, usage.md, advanced.md, architecture.md, changelog.md, and .cursorrules.
- Major refactor of the Sanitize Images workflow (July 2025):
  - All step prompts are now interactive, Mocha-styled, and emoji-rich.
  - Steganography checks prompt for steghide and zsteg individually, and the summary reports both.
  - A visually distinct summary box is always shown at the end, including zsteg results file path if produced.
  - Menu header is reprinted after returning to the workflow menu.
  - All output uses centralized, Mocha-styled printing utilities.
  - No duplicate prompts, debug prints, or raw print statements remain.
  - Documentation and .cursorrules updated accordingly.
- **Enhanced Metadata Management:**
  - Added new menu for batch extract, view/edit, filter, and anonymize image metadata (EXIF, IPTC, XMP) using exiftool, Pillow, pandas, and SQLite.
  - Fully integrated with centralized printing, memory, progress, and logging utilities.
  - Documented in all relevant docs and .cursorrules.
- Added '🧭 Align Images (Batch Projective Alignment)' feature to Dataset Management menu. Allows batch alignment of images from two folders (flat or recursive) using SIFT+FLANN projective transformation. Robust error handling, modular implementation, and public API.
- Added robust, non-interactive test for Align Images using feature-rich dummy images to ensure SIFT keypoint detection and alignment.

### 🆕 DPID: Umzi's DPID (pepedpid) Integration (July 2025)

- **New DPID implementation:** Added Umzi's DPID (pepedpid) as a modular DPID method in `dataset_forge/dpid/umzi_dpid.py`.
- **Menu integration:** Umzi's DPID is now selectable in all DPID menus (single-folder and HQ/LQ workflows).
- **Testing:** Comprehensive, non-interactive tests for Umzi's DPID (single-folder and HQ/LQ) using pytest and monkeypatching.
- **Documentation:** Updated all relevant docs and .cursorrules to reflect the new DPID method, its usage, and its test coverage.

## [July 2025]

- Added '🩺 Dataset Health Scoring' workflow and menu option under Dataset Management.
- Supports both single-folder and HQ/LQ parent folder modes.
- Modular, weighted checks: validation, quality, consistency, compliance, and more.
- Actionable suggestions and detailed scoring breakdown.
- Fully covered by unit and integration tests.
- Robust CLI integration and extensible design.
- Added menu timing/profiling system: every menu and submenu load is timed and printed to the user.
- All menu load times are recorded and viewable in the System Monitoring menu ("⏱️ View Menu Load Times").
- Lazy import pattern enforced for all menus and actions for maximum CLI speed.
- Timing prints use the Catppuccin Mocha color scheme for clarity.
- Documentation updated across README.md and docs/ to reflect these changes.
- Global robust menu loop pattern integration for all menus and submenus
- Improved reliability and navigation throughout the CLI
- Added menu timing & profiling integration for all menus and submenus
- Implemented robust menu loop pattern for reliability
- Integrated Content-Based Image Retrieval (CBIR) for semantic duplicate detection
- Centralized monitoring, analytics, and error tracking system
- Comprehensive test suite covering CLI, memory, parallelism, and error feedback
- requirements.txt is now grouped and commented by category
- Added install order warnings for VapourSynth/getnative and CUDA/torch
- Comprehensive test suite upgrade: all major features now have robust, non-interactive, public APIs and are fully covered by real tests.
- Test suite uses monkeypatching, dummy objects, and multiprocessing-safe patterns.
- Only one test is marked XFAIL (ignore patterns in directory tree), which is expected and documented.
- Documentation updated to reflect new test patterns and requirements.

This file will track major changes and releases in the future.

---

# License

[← Main README](../README.md) | [Features](features.md) | [Usage](usage.md) | [Advanced](advanced.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md) | [Style Guide](style_guide.md) | [Changelog](changelog.md) | [ToC](toc.md)

# License

This project is licensed under the Creative Commons CC-BY-SA-4.0. See the [LICENSE](../LICENSE) file for details.

---
