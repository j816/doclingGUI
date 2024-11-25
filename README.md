# Docling PDF to Markdown GUI

A graphical user interface for the Docling PDF to Markdown converter, designed to make batch PDF conversion easier and more user-friendly.

## Features

- Convert PDF files to Markdown format
- Recursive folder scanning for PDF files
- OCR support for images and text
- Multiple OCR engine options
- Configurable table processing modes
- Progress tracking with visual feedback
- Settings persistence between sessions
- PDF deletion after conversion (optional)
- Detailed logging and error reporting

## Requirements

- Python 3.9 or higher
- PyQt5
- Docling library
- Operating System: Windows, macOS, or Linux

## Installation

1. First, ensure you have Python 3.9+ installed on your system:
   ```bash
   python --version
   ```

2. Install the required dependencies:
   ```bash
   pip install PyQt5 docling
   ```

3. Clone this repository or download the `doclingGUI.py` file:
   ```bash
   git clone https://github.com/j816/doclingGUI.git
   cd doclinggui
   ```

4. Make sure the Docling command-line tool is properly installed and accessible from the command line:
   ```bash
   docling --version
   ```

## Usage

1. Run the application:
   ```bash
   python doclingGUI.py
   ```

2. The GUI will appear with the following options:

   ### Input/Output Settings
   - **Input Folder**: Select the folder containing your PDF files
   - **Output Folder**: Choose where to save the converted Markdown files

   ### OCR Settings
   - **Enable OCR**: Process images in PDFs
   - **Force OCR**: Process all text (not just images)
   - **Delete PDFs**: Option to remove original PDFs after conversion
   - **OCR Engine**: Choose between easyocr, tesseract, tesseract_cli, or ocrmac

   ### Processing Options
   - **Table Mode**: 
     - Accurate (better quality, slower)
     - Fast (lower quality, faster)
   
   ### Verbosity Level
   - 0: Silent (errors only)
   - 1: Info (processing updates)
   - 2: Debug (detailed technical info)

3. Click "Run Conversion" to start the process
4. Use "Reset" to clear the current state and start a new conversion

## Features in Detail

### Recursive Folder Processing
- The application automatically scans all subfolders in the input directory
- Maintains folder structure in the output directory
- Processes all PDF files found in the folder hierarchy

### Progress Tracking
- Visual progress bar
- Current file display
- File count tracking
- Status updates

### Settings Persistence
- All settings are automatically saved
- Settings are restored when the application restarts
- Saved in `~/.docling_gui_settings.json`

### Error Handling
- Detailed error messages
- Logging to console
- User-friendly error notifications
- Graceful failure recovery

## Common Issues and Solutions

1. **OCR Engine Not Found**
   - Ensure the selected OCR engine is installed
   - For Tesseract: Install tesseract-ocr on your system
   - For EasyOCR: `pip install easyocr`

2. **Permission Errors**
   - Ensure you have write permissions for the output folder
   - Run the application with appropriate permissions

3. **Docling Command Not Found**
   - Ensure Docling is properly installed: `pip install docling`
   - Verify installation: `docling --version`

## Best Practices

1. **Before Converting**
   - Backup your PDF files
   - Ensure sufficient disk space
   - Test with a small batch first

2. **OCR Settings**
   - Use Force OCR for scanned documents
   - Use regular OCR for documents with mixed content
   - Choose accurate table mode for complex tables

3. **Performance**
   - Process smaller batches for better control
   - Monitor system resources during conversion
   - Use appropriate verbosity level for your needs

## Logging

The application creates detailed logs with timestamps. Log levels:
- INFO: Normal operation information
- WARNING: Non-critical issues
- ERROR: Critical issues that need attention
- DEBUG: Detailed technical information (verbosity level 2)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built on top of the Docling library
- Uses PyQt5 for the graphical interface
- Special thanks to the Docling development team

## Support

For issues, questions, or contributions, please:
1. Check the existing issues on GitHub
2. Create a new issue if needed
3. Provide detailed information about your problem

---

Created by Juan
