# Excel Plot App

A desktop tool for turning measurement data from Excel files into clean, publication-ready PDF charts — no manual plotting required.

## Features

- **Excel import** — load `.xlsx` / `.xls` files and pick any column as the X-axis
- **Dual Y-axes** — plot multiple series on independent left and right Y-axes (up to 10 lines per axis)
- **Custom colors & labels** — assign a color and label to each series
- **Date/time support** — automatically detects and formats datetime columns on the X-axis
- **Adjustable grid density** — fine-tune the tick spacing to your needs
- **Optional Y-axis start at data minimum** — instead of always starting at 0
- **Logo overlay** — add your company logo (built-in default logo or a custom image)
- **Optional date stamp** — display a date above the chart
- **Adjustable chart size** — scale the plot area (as a %) independently of the page/legend layout
- **PDF export** — saves a ready-to-share PDF next to the source Excel file

## Requirements

- Python 3.9+
- Dependencies:
```bash
  pip install pandas matplotlib pillow openpyxl
```

## Usage

1. Run the app:
```bash
   python main.py
```
2. Load an Excel file via **"Excel-Datei öffnen"**.
3. Select the column to use for the X-axis.
4. Add one or more series to the left and/or right Y-axis using the **+** button, and assign a column, label, and color to each.
5. (Optional) Adjust the chart title, axis labels, date stamp, grid fineness, chart size, and logo.
6. Click **"Diagramm erstellen & als PDF speichern"** to generate and save the chart as a PDF.

The output PDF is saved in the same folder as the source Excel file, with `_Diagramm` appended to the filename.

## Project Structure in app/
├── main.py # Application entry point
├── gui.py # Tkinter UI and user interaction logic
├── plotting.py # Chart generation (matplotlib) and PDF export
├── utils.py # Helper functions (date parsing, tick intervals, resource paths)
├── ToolTip.py # Reusable tooltip widget for the UI
└── resources/ # Icons and logo images

## Building a Standalone Executable

The app can be packaged into a single Windows `.exe` using [PyInstaller](https://pyinstaller.org/):

```bash
pip install pyinstaller
pyinstaller --clean --noconfirm main.spec
```

The resulting executable will be located in the `dist/` folder.

> **Note:** If you rebuild after changing resource paths, delete the old `build/`, `dist/`, and `.spec` files first to avoid stale configuration being reused.
