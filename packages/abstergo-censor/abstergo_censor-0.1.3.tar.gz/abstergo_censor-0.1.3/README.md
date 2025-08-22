# Abstergo Censor

[![PyPI](https://img.shields.io/pypi/v/abstergo-censor.svg)](https://pypi.org/project/abstergo-censor/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)

A **privacy-first command-line tool** to automatically blur **faces** and **license plates** in images and videos.  
Built with [OpenCV](https://opencv.org/), works fully offline, no cloud services required.

---

## ✨ Features
- 🔒 **Privacy-first**: anonymize images & videos locally, nothing leaves your computer  
- 👥 **Face detection**: blur human faces using Haar cascades  
- 🚘 **License plates**: optional plate blurring for videos & street images  
- ⚡ **Fast & simple**: single command to process whole files  
- 🖥️ **Cross-platform**: works on Windows, Linux, macOS with Python 3.9+  

---

## 📦 Installation

```bash
pip install abstergo-censor
```

---

## 🚀 Usage

### Blur an image
```bash
abstergo-censor input.jpg --out output.jpg --plates
```

### Blur a video
```bash
abstergo-censor input.mp4 --out output.mp4 --plates
```

### Options
| Flag           | Description                               | Default   |
|----------------|-------------------------------------------|-----------|
| `--out PATH`   | Output file (required)                    | –         |
| `--plates`     | Also detect and blur license plates        | disabled  |
| `--strength N` | Blur kernel size (odd integer)             | 25        |
| `--scale N`    | Detection scale factor                     | 1.2       |
| `--show`       | Show a preview window while processing     | disabled  |

---

## 📜 License
Released under the [MIT License](LICENSE).  
Copyright © 2025 Abstergo LLC
