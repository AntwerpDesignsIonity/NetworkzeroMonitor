# Core Module

The core module contains the platform-agnostic network monitoring engine that is shared across all platform implementations.

## Components

- **Monitor Engine**: Central monitoring logic
- **Data Structures**: Common data structures for network metrics
- **Interfaces**: Abstract interfaces for platform-specific implementations
- **Utilities**: Helper functions and utilities

## Architecture

The core module provides the foundation for:
- Network packet capture and analysis
- Metric collection and aggregation
- Event handling and notifications
- Data storage and retrieval

## Usage

This module is imported by platform-specific implementations and should not contain any platform-dependent code.
