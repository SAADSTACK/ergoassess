# ErgoAssess - RULA & REBA Calculator

<div align="center">

![ErgoAssess Logo](static/images/logo.svg)

**Professional Ergonomic Posture Assessment Tool**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-green.svg)](https://python.org)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)]()

*100% Offline | ISO 11226 Compliant | AI-Powered*

[Download](#download) • [Features](#features) • [Installation](#installation) • [Usage](#usage) • [Documentation](#documentation)

</div>

---

## Overview

ErgoAssess is a desktop application that automatically calculates **RULA (Rapid Upper Limb Assessment)** and **REBA (Rapid Entire Body Assessment)** scores from images. Using AI-powered pose detection, it analyzes working postures and provides detailed ergonomic recommendations aligned with international standards.

## Features

### 🎯 Core Capabilities

- **AI-Powered Pose Detection** - Automatically detects 33 body landmarks using MediaPipe
- **RULA Scoring** - Complete upper limb assessment with action levels 1-4
- **REBA Scoring** - Full body assessment with risk levels (Negligible to Very High)
- **Joint Angle Analysis** - Precise angle calculations for all major joints
- **Smart Recommendations** - Prioritized ergonomic improvements based on ISO/HSE guidelines

### 📊 Reporting

- **Interactive Dashboard** - Visual scores with color-coded risk indicators
- **Annotated Visualization** - See detected pose with joint angles overlaid
- **PDF Reports** - Professional, audit-ready documentation
- **Score Justifications** - Detailed reasoning matching official RULA/REBA diagrams

### 🔒 Privacy & Security

- **100% Offline** - All processing happens locally on your device
- **No Data Collection** - Images never leave your computer
- **No Internet Required** - Works completely without network access

### 🎨 User Experience

- **Modern Interface** - Clean, intuitive design
- **Dark/Light Themes** - Choose your preferred appearance
- **Drag & Drop** - Easy image upload
- **Real-time Feedback** - Loading animations and status updates

## Installation

### Quick Install (Windows)

1. **Download** `ErgoAssess_Setup.exe` from the [Releases](releases) page
2. **Run** the installer and follow the setup wizard
3. **Launch** ErgoAssess from your Desktop or Start Menu

### Requirements

- Windows 10/11
- Python 3.9 or higher
- 500 MB free disk space

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ergoassess.git
cd ergoassess

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## Usage

1. **Upload Image** - Drag & drop or click to select a posture image (JPEG/PNG)
2. **Configure Options** - Set load weight, coupling quality, and task type
3. **Analyze** - Click "Analyze Posture" to run the assessment
4. **Review Results** - View scores, joint angles, and recommendations
5. **Export** - Download a PDF report for documentation

## Standards Compliance

ErgoAssess follows official RULA and REBA methodologies and aligns with:

- **ISO 11226** - Evaluation of static working postures
- **ISO 11228** - Manual handling guidelines
- **HSE Guidelines** - Health and Safety Executive recommendations
- **EN 1005-4** - Machinery safety ergonomic principles

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Python, Flask |
| AI/ML | MediaPipe Pose |
| Frontend | HTML5, CSS3, JavaScript |
| PDF Generation | ReportLab |
| Image Processing | OpenCV, Pillow |

## Project Structure

```
ergoassess/
├── app.py              # Flask application entry point
├── config.py           # Configuration settings
├── core/               # Pose detection and angle calculation
├── scoring/            # RULA and REBA scoring engines
├── recommendations/    # Standards-aligned recommendations
├── reports/            # PDF report generation
├── templates/          # HTML templates
├── static/             # CSS, JS, and assets
└── tests/              # Test suite
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [MediaPipe](https://mediapipe.dev/) for pose estimation
- RULA methodology by McAtamney & Corlett (1993)
- REBA methodology by Hignett & McAtamney (2000)

---

<div align="center">

**Made with ❤️ for Workplace Safety**

[Report Bug](issues) • [Request Feature](issues) • [Documentation](docs)

</div>
