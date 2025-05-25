# PDFPayslips

A collection of Python scripts for batch-processing payslips in PDF format.  
This toolset is designed for extracting structured data from payslips, enriching it with additional metadata, and generating summaries for HR or accounting purposes.

## Overview

The project helps to:

- 📂 Scan a folder with payslip PDFs
- 🧾 Extract structured data from each file (name, date, amount, NIN, etc.)
- 📊 Generate summary reports (monthly totals, per-employee stats)
- 💾 Export data to CSV or Excel for further analysis

## Scripts

### `read_payslips.py`

- Extracts basic fields (employee name, date, amount) from PDFs
- Outputs raw data table

### `info_extra.py`

- Parses additional fields such as:
  - National Insurance Number (NIN)
  - Tax code
  - Pay period
  - Employer name

- Uses pattern matching and text heuristics
- Works as a second pass over `read_payslips.py` results

### `pay_summary.py`

- Aggregates payslip data into summary tables
- Useful for payroll overview, export to `.csv` or `.xlsx`
- Can group by month, employee, or employer

## Requirements

- Python 3.8+
- Dependencies:
  - `pdfplumber` or `PyPDF2`
  - `pandas`
  - `openpyxl`
  - `re` (built-in)

If your PDFs are scanned images, you may need:
- `pytesseract`
- `Tesseract OCR` installed

## Installation

```bash
git clone https://github.com/loglux-dev/PDFPayslips.git
cd PDFPayslips
pip install -r requirements.txt
```

## Usage

Example flow:

```bash
# Step 1 – read and extract base fields
python read_payslips.py --input-dir ./pdfs/

# Step 2 – extract extra info like NIN, tax code
python info_extra.py --source data_raw.csv --output data_extended.csv

# Step 3 – generate summary
python pay_summary.py --input data_extended.csv --output summary.xlsx
```

## Output

- `data_raw.csv` — parsed fields (name, date, amount)
- `data_extended.csv` — enriched with tax details
- `summary.xlsx` — grouped by month or employee

## License

MIT License — see [LICENSE](LICENSE) for details.
