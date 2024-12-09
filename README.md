# Docling GUI

A graphical user interface for the Docling document processing tool, built with PyQt6. This application provides a user-friendly way to process various document formats using Docling.


![blah](https://github.com/user-attachments/assets/bce0b1dd-2d24-4113-ab7b-bde7515c5d8a)

## Features

- Process multiple document types (PDF, DOCX, PPTX, HTML, XLSX, MD, TXT)
- Batch processing support
- Multiple export formats (Markdown, JSON, Text, Doctags)
- OCR capabilities with EasyOCR
- Progress tracking
- Configurable table processing modes
- Error handling and logging

## Requirements

- Python 3.6+
- PyQt6
- Docling CLI tool
- EasyOCR (for OCR functionality)

## Installation

1. Install Python dependencies: 
pip install PyQt6 docling easyocr

git clone <doclingGUI>
cd doclingGUI

## Usage

1. Run the application:
python main.py


2. Using the GUI:
   - Select an input folder containing your documents
   - Choose an output folder for processed files
   - Configure processing options:
     - Export Format: Choose between md, json, text, or doctags
     - Table Mode: Select 'fast' or 'accurate' processing
     - OCR Options: Enable/disable force OCR or bitmap OCR
   - Click "Start Processing" to begin
   - Use "Cancel" to stop processing at any time

## Processing Options

### Export Formats
- `md`: Markdown format
- `json`: JSON format
- `text`: Plain text
- `doctags`: Document tags format

### Table Processing Modes
- `fast`: Quicker processing with potentially lower accuracy
- `accurate`: More precise table extraction with longer processing time

### OCR Options
- **Force OCR**: Forces OCR on all content
- **OCR for Bitmaps**: Applies OCR only to bitmap images

## File Support

Supported input formats:
- PDF (.pdf)
- Microsoft Word (.docx)
- Microsoft PowerPoint (.pptx)
- Microsoft Excel (.xlsx)
- HTML (.html)
- Markdown (.md)
- Text files (.txt)

## Logging

The application maintains logs in `docling_gui.log`, recording:
- Processing operations
- Errors and exceptions
- File operations
- Configuration changes

## Error Handling

The application includes comprehensive error handling for:
- Invalid file types
- Processing failures
- Directory access issues
- OCR processing errors

## Development

The application is structured with the following main components:
- `ProcessingConfig`: Configuration dataclass
- `FileProcessor`: Handles file operations
- `DoclingWorker`: Background processing thread
- `MainWindow`: Main GUI interface

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
MIT
