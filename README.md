# GDB to Excel Converter

## Problem I Faced: 

When working with geospatial data, I faced the challenge of extracting layers from **.gdb (File Geodatabase)** files and converting them into **Excel sheets** for analysis. Most solutions I found were either **premium software**, or **heavy GIS tools**, making the process **expensive, slow, and hard to automate**.

To solve this, I built a **simple, free, and automated GDB to Excel converter** using Python and FastAPI, with a **user-friendly web interface**.

---

## Features

- Upload `.zip` files containing `.gdb` folders.
- Automatically extract all layers from the GDB.
- Convert each layer into a separate Excel (`.xlsx`) file.
- Download all Excel files bundled in a single `.zip`.

---

## Tech Stack

**Backend:**
- Python 
- FastAPI
- GeoPandas
- Fiona
- Pandas
- OpenPyXL

**Frontend:**
- HTML, CSS, JavaScript


---


## Installation and Local Setup

1. Clone the repository:

```bash
git clone https://github.com/tousifinity/Geo-Database-to-Excel-Converter.git
cd Geo-Database-to-Excel-Converter
```

2. Create a virtual environment and activate it:

```bash
# Windows
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the FastAPI backend:

```bash
uvicorn app:app --reload
```

5. Open `public/index.html` in a browser and start using the converter.


## How It Works

1. Upload a `.zip` containing a `.gdb` folder.
2. Click `Convert`.
3. Watch the progress bar update in real-time.
4. Once complete, the `Exports.zip` file will download automatically.

---