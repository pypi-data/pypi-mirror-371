# GNSS-IR Real-Time Water Level Processing

[![License: BSD 3-Clause](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

A Python package for real-time processing of low-cost GNSS-IR (Global Navigation Satellite System Interferometric Reflectometry) water level data. This software provides tools for flood monitoring and water level estimation using GNSS signals.

## About

This software accompanies the research article ["Real-time water levels using GNSS-IR: a potential tool for flood monitoring"](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2023GL105039) by Purnell et al., published in Geophysical Research Letters (2024).

GNSS-IR is a technique that uses reflected GNSS signals to estimate surface height changes, making it particularly useful for monitoring water levels in coastal and inland environments.

## Features

- Real-time water level processing from GNSS-IR data
- Support for low-cost GNSS receivers
- Configurable site-specific processing parameters
- Built-in visualization tools
- Multiple processing tasks: `snr2arcs`, `arcsplot`, `arcs2splines`
- Test data and examples included

## Prerequisites

- Python 3.7 or higher
- pip package manager
- Git (for cloning the repository)

## Installation

### From PyPI (recommended)

```bash
pip install gnssir-rt
```

### From Source

```bash
git clone https://github.com/purnelldj/gnssir-rt.git
cd gnssir-rt
pip install -e .
```

## Quick Start

Here's a complete example using the included test data from Saint-Joseph-de-la-Rive:

### Step 1: Prepare Test Data

Create a data directory and extract the test dataset:
```bash
mkdir data
unzip tests/testdata/sjdlr.zip -d data/sjdlr
```

### Step 2: Process the Data

Run the processing command:
```bash
gnssir site=sjdlr task=arcs2splines
```

This command will generate a plot showing the processed water level data:

![Spline Output](./images/sjdlr_oneday.png)

## Usage

### General Command Structure

```bash
gnssir site=[site] task=[task]
```

**Parameters:**
- `[site]`: Site identifier corresponding to a config file in `gnssir/configs/site/[site].yaml`
  - Available sites: `sjdlr`, `rv3s`
- `[task]`: Processing task to perform
  - `snr2arcs`: Convert SNR data to reflection arcs
  - `arcsplot`: Generate plots of reflection arcs
  - `arcs2splines`: Process arcs and generate spline-fitted water levels

### Configuration

Site-specific parameters are stored in YAML configuration files located in `gnssir/configs/site/`. You can:
- Edit existing configuration files
- Create new configuration files for additional sites
- Customize processing parameters for your specific requirements

## Data

### Research Dataset

The complete SNR dataset used in the accompanying research paper is available on Zenodo: [10.5281/zenodo.10114719](https://doi.org/10.5281/zenodo.10114719)

To download the dataset:
```bash
pip install zenodo_get
zenodo_get 10.5281/zenodo.10114719
```

**Note:** The download is approximately 1GB and may take several minutes.

### SNR Data Format

The software expects SNR data in a specific format similar to the [gnssrefl format](https://gnssrefl.readthedocs.io/en/latest/pages/file_structure.html#the-snr-data-format), with the following modifications:

| Column | Description |
|--------|-------------|
| 1 | Satellite number |
| 2 | Elevation angle (degrees) |
| 3 | Azimuth angle (degrees) |
| 4 | [GPS time](https://docs.astropy.org/en/stable/api/astropy.time.TimeGPS.html) (instead of seconds of day) |
| 5 | L1 SNR values |

## Contributing

We welcome contributions from the community! Whether you're fixing bugs, adding features, improving documentation, or sharing new site configurations, your help is appreciated.

### How to Contribute

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/gnssir-rt.git
   cd gnssir-rt
   ```
3. **Create a new branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes** and test them thoroughly
5. **Commit your changes** with clear, descriptive messages:
   ```bash
   git commit -m "Add feature: description of your changes"
   ```
6. **Push to your fork** and submit a pull request

### Types of Contributions

- **Bug Reports**: Use GitHub Issues to report bugs with detailed reproduction steps
- **Feature Requests**: Suggest new features or improvements via GitHub Issues
- **Code Contributions**: Submit pull requests for bug fixes or new features
- **Documentation**: Improve README, docstrings, or add examples
- **Site Configurations**: Share configuration files for new GNSS sites
- **Test Data**: Contribute test datasets from different locations/conditions

### Development Setup

For development work:
```bash
pip install -e ".[dev]"  # Install with development dependencies
python -m pytest         # Run tests
```

### Code Style

- Follow PEP 8 style guidelines
- Write clear, descriptive commit messages
- Add tests for new functionality
- Update documentation as needed

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this software in your research, please cite:

```
Purnell, D., et al. (2024). Real-time water levels using GNSS-IR: a potential tool 
for flood monitoring. Geophysical Research Letters. 
https://doi.org/10.1029/2023GL105039
```

## Acknowledgments

- The script [make_gpt.py](./gnssir/make_gpt.py) was adapted from the [gnssrefl](https://github.com/kristinemlarson/gnssrefl) repository
- This work builds upon the broader GNSS-IR research community's contributions

## Support

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/purnelldj/gnssir-rt/issues)
- **Discussions**: Join community discussions in [GitHub Discussions](https://github.com/purnelldj/gnssir-rt/discussions)
- **Email**: For direct inquiries, contact the maintainers

---

**Keywords:** GNSS-IR, water level monitoring, flood detection, interferometric reflectometry, remote sensing
