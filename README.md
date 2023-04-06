# python-nvda

This project provides embedded python distributions with all requirements to build NVDA. In Addition the source of the current release is copied to site-packages, so code-completion works with NVDA-API. This is useful for plugin-developers.

# Usage
Pull the repository:

---
python download.py
---

This will download the latest NVDA with all dependencies to python32 and python64. YOu can use python32\python.exe and python64\python.exe for development.

You can clean NVDA-sources and dependencies with .\clean.bat
