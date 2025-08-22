<p align="center">
  <img src="https://sandyie.in/images/Logo.svg" width="140" alt="Sandyie Logo">
</p>

<h1 align="center">📚 Sandyie Read</h1>

<p align="center">
  <a href="https://pypi.org/project/sandyie-read/"><img src="https://img.shields.io/pypi/v/sandyie_read?color=blue" alt="PyPI version"></a>
  <a href="https://pypi.org/project/sandyie-read/"><img src="https://img.shields.io/pypi/dm/sandyie_read" alt="Downloads"></a>
  <a href="https://github.com/sandyie/sandyie-read/blob/main/LICENSE"><img src="https://img.shields.io/github/license/sandyie/sandyie-read" alt="License"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.7%2B-blue.svg" alt="Python Version"></a>
</p>

<p align="center"><strong>Effortlessly read files of almost any type — PDFs, images, YAML, CSV, Excel, and more — with built-in logging and custom exceptions.</strong></p>

---

## ⚠️ Python Compatibility

> 🐍 **Requires Python 3.7 or higher**

---

## 🔧 Features

- ✅ Read and extract content from:
  - **Documents** → PDF, DOCX, TXT, HTML, Markdown
  - **Data files** → CSV, TSV, Excel, Parquet
  - **Serialized files** → Pickle, Models
  - **Configs** → JSON, YAML, JS
  - **Archives** → ZIP
  - **Images** → JPG, PNG, SVG (OCR-enabled)
- 🧠 OCR support via **Tesseract**
- 📋 Human-friendly **logging**
- 🛡️ Consistent error handling with `SandyieException`

---

## 📦 Installation

```bash
# Upgrade pip and setuptools first
python -m pip install --upgrade pip setuptools

# Clear old caches (optional)
pip cache purge

# Install sandyie_read
pip install sandyie_read
````

-----

## 🚀 Quick Start

```python
from sandyie_read import read

# Example: Reading a PDF
data = read("example.pdf", pages = [0])
print(data)
```

-----

## 📁 Supported File Types & Examples

### 1\. 📄 Pickle / Model Files

```python
data = read("model.pkl")
print(data)
```

🟢 **Returns:** A Python object / model container.

-----

### 2\. 🖼️ Images (PNG, JPG, SVG)

```python
data = read("photo.jpg")
print(data)
```

🟢 **Returns:** OCR-extracted text as a string or NumPy array.

-----

### 3\. 📊 Parquet

```python
data = read("data.parquet")
print(data)
```

🟢 **Returns:** `pandas.DataFrame`.

-----

### 4\. 📊 CSV / Excel

```python
data = read("data.csv")
print(data)
```

🟢 **Returns:** `pandas.DataFrame`.

-----

## ⚠️ Error Handling

All exceptions are wrapped in a custom `SandyieException`, making debugging **simple and consistent**.

-----

## 🧪 Logging

Logs include:

  * File type detection
  * Success/failure reports
  * Processing details

-----

## 📚 Documentation

📖 Full documentation (with API reference and usage notebooks) will be available soon at 👉 [sandyie.in/docs](https://sandyie.in/docs)

-----

## 🗺️ Roadmap

  - **Cloud Storage Support:** Read files directly from S3, Azure Blob, and Google Cloud Storage.
  - **Streaming Files:** Process large files without loading the entire content into memory.
  - **Improved Performance:** Optimize parsing for various file formats.

-----

## 🤝 Contributing

Got an idea or found a bug?

  * Open an [Issue](mailto:business@sandyie.in)
  * Or submit a Pull Request 🚀

-----

## 📄 License

Licensed under the **MIT License**.
See [LICENSE](https://www.google.com/url?sa=E&source=gmail&q=https://github.com/sandyie/sandyie-read/blob/main/LICENSE) for details.

-----

## 👤 Author

**Sanju (aka Sandyie)**
 * 🌐 Website: [www.sandyie.in](https://www.sandyie.in)
 * 📧 Email: [business@sandyie.in](mailto:business@sandyie.in)
 * 🐍 PyPI: [sandyie-read](https://pypi.org/project/sandyie-read)

```
```