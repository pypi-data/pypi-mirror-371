# 🛠️ sidetool

**sidetool** is a command-line utility and helper module that simplifies execution and building [PySide6](https://doc.qt.io/qtforpython/) Python 3.7+ applications into executables using **PyInstaller 5.8.0**.

It's especially useful for GUI projects that need embedded resources (e.g., `.ui`, `.qrc`) and aim to produce portable `.exe` builds with minimal setup.

---

## ❤️ Why Use sidetool?

If you build windows desktop apps using PySide6 or PyQt, `sidetool`:

- Saves time when converting `.ui` and `.qrc` files
- Simplifies PyInstaller builds
- Packages your application with minimal commands
- Automates repetitive tasks like building and cleanup
- Integrates easily with `.bat` scripts or shell commands
- Is great for both beginners and advanced developers using PySide6

---

## 🔧 Commands

### 1. `run`

Executes the Python program after recursively builds all `.ui` and `.qrc` files in the current directory and subdirectories using `pyside6-uic.exe` and `pyside6-rcc.exe`.  Then run python source code.

Note: it will ONLY rebuild pyside components that are out of date, so that execution is fast as possible, yet always includes any changes.
FYI: python program is run with pythonw.exe so that the terminal window does not appear.

```cli
usage: sidetool-run [-h] file

Build ui and qrc files, then run python source

positional parameters:
  file        python file to run

parameters:
  -h, --help  show this help message and exit
```

### 2. `clean`

Removes temporary files and build artifacts, including:

- `__pycache__` folders  
- `*_ui.py`, `*_rc.py`, `*.pyc`, `*.pyo`  
- PyInstaller `build/` and `dist/` folders  
- `.spec` files in the current directory

Run it like this:

```cli
sidetool-clean
```

### 3. `compile`

Builds your python app into an executable using PyInstaller.

- Compiles `.ui` and `.qrc` and image resources  
- Generates a PyInstaller `.spec` file  
- Runs PyInstaller with the provided options

```cli
usage: sidetool-compile [-h] --file FILE --type {onefile,onedir,console} [--icon="myicon.ico"] [--embed="sqlite3.dll"]

parameters:
  -h, --help            show this help message and exit
  --file FILE           python file to compile to exe
  --type {onefile,onedir,console}
                        type of exe to build
  --icon ICON           ico file
  --embed EMBED         comma delimited list of files to embed
```

---

## ✨ Features

- 💡 Simple command-line interface for `.bat` or `.sh` workflows 
- 🔄 Converts all `.ui` and `.qrc` files recursively
- 🧹 Cleans up Python build artifacts
- 📦 Packages PySide6 apps using PyInstaller 
- Supports custom `.ico` icons  
- Supports optional resource embedding

---

## 📦 Requirements

- Python 3.7+
- [PySide6](https://pypi.org/project/PySide6/)
- [PyInstaller 5.8](https://pypi.org/project/pyinstaller/)

Install using:

```bash
pip install sidetool
```

---

## 📥 Installation

Install from PyPI:

```bash
pip install sidetool
```

---

## 📝 License

MIT License  
© 2025 Alan Lilly  
