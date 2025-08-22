![Coords-NSGA2](logo.drawio.svg)
# Welcome to Coords-NSGA2

> **⚠️ Important Notice**: This document is AI-generated based on source-code analysis. Although we strive for accuracy, inconsistencies or issues may still exist. We are actively improving and validating all content. If you encounter any problems, please report them promptly.

Coords-NSGA2 is a Python library for multi-objective optimization of coordinate layouts, built upon an enhanced version of the NSGA-II algorithm.

## Overview

Coords-NSGA2 is a Python library specifically designed for optimizing the layout of coordinate points, based on an improved implementation of the classic NSGA-II (Non-Dominated Sorting Genetic Algorithm II).

## Key Features

- **Coordinate-focused optimization**: Purpose-built for optimizing point layouts
- **Variable point count support**: Supports both fixed number of points and dynamic point count within a specified range
- **Specialized constraints**: Built-in support for inter-point spacing, boundary limits, and custom constraints  
- **Customized genetic operators**: Crossover and mutation operators tailored to coordinate data  
- **Multi-objective optimization**: Leveraging the proven NSGA-II algorithm  
- **Parallel computation**: Accelerate optimization with parallel processing for computationally intensive problems  
- **Flexible region definitions**: Supports both polygonal and rectangular regions  
- **Lightweight and extensible**: Easy to add custom operators and constraints  
- **Progress tracking**: Built-in progress bar and optimization history  
- **Save/Load capability**: Persist and restore optimization state  

## Quick Start

- **Installation**: See the [Installation Guide](install.md)  
- **Usage**: Detailed tutorial in the [User Guide](usage.md)  
- **API Reference**: Refer to the [API Documentation](api.md)  
- **Examples**: Browse the [Example Code](examples.md)  

## Use Cases

- Wind turbine layout optimization  
- Sensor network deployment  
- Facility location problems  
- Robot path planning  
- Any scenario requiring optimized coordinate layouts  

## System Requirements

- Python 3.8+
- NumPy >= 1.23
- tqdm >= 4.64
- Shapely >= 2
- matplotlib >= 3.6
- joblib >= 1.4
- SciPy (optional, for distance computations)