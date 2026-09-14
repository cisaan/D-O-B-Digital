# Daily Occurrence Report

A Python desktop application for recording daily occurrence reports and generating a non-editable PDF report with supporting images.

> **Portfolio project:** built by Zeeshan Nasir to streamline the capture, storage, and export of incident information.

## What it does

- Captures report details including date, time, reporting officer, incident description, and actions taken
- Supports image attachments for visual evidence
- Stores reports locally in SQLite
- Generates a formatted, non-editable PDF report
- Includes basic trial and licence-flow logic

## Built with

- Python
- Tkinter for the desktop interface
- SQLite for local data storage
- ReportLab for PDF generation
- Pillow for image handling

## Run locally

1. Clone this repository.
2. Create and activate a virtual environment.
3. Install the required dependencies:

```bash
pip install pillow reportlab
```

4. Run the application:

```bash
python main.py
```

## Project structure

- `main.py` — application interface and report-generation workflow
- `images/` — application image assets
- `occurrence_reports.db` — local SQLite database used by the app

## Roadmap

- Add a requirements file and automated tests
- Package a downloadable desktop release
- Add screenshots and a short product demo
- Move licence validation to a secure server-side approach before production use

## Notes

This is an evolving portfolio project. Please do not use real confidential incident data in a public copy of the application.
