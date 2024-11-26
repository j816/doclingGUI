import sys
import os
import logging
import shutil
from pathlib import Path
import tempfile
from typing import Optional, List, Set
from dataclasses import dataclass
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QComboBox, 
                            QFileDialog, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('docling_gui.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ProcessingConfig:
    """Configuration for document processing."""
    input_path: str
    output_path: str
    export_format: str
    table_mode: str
    force_ocr: bool
    ocr_bitmaps: bool
    temp_dir: str

class FileProcessor:
    """Handles file processing operations."""
    
    VALID_EXTENSIONS: Set[str] = {
        '.pdf', '.docx', '.pptx', '.html', '.xlsx', '.md', '.txt'
    }

    @staticmethod
    def is_valid_file(file_path: Path) -> bool:
        """Check if file is valid for processing."""
        return (
            not file_path.name.startswith('.') and 
            file_path.suffix.lower() in FileProcessor.VALID_EXTENSIONS
        )

    @staticmethod
    def get_files_to_process(directory: Path) -> List[Path]:
        """Get list of valid files to process from directory."""
        files = []
        try:
            for file_path in directory.rglob('*'):
                if file_path.is_file() and FileProcessor.is_valid_file(file_path):
                    files.append(file_path)
                    logger.debug(f"Found valid file: {file_path}")
        except Exception as e:
            logger.error(f"Error scanning directory: {str(e)}")
        return files

class DoclingWorker(QThread):
    """Worker thread for processing documents."""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, config: ProcessingConfig):
        super().__init__()
        self.config = config
        self.is_cancelled = False

    def run(self) -> None:
        """Main processing loop."""
        try:
            self._process_files()
        except Exception as e:
            logger.error(f"Error in worker thread: {str(e)}")
            self.error.emit(str(e))
        finally:
            self.finished.emit()

    def _process_files(self) -> None:
        """Process all valid files in the input directory."""
        input_dir = Path(self.config.input_path)
        files_to_process = FileProcessor.get_files_to_process(input_dir)
        
        for file_path in files_to_process:
            if self.is_cancelled:
                logger.info("Processing cancelled by user")
                break

            self.progress.emit(f"Processing {file_path}")
            try:
                self._process_single_file(file_path)
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
                self.error.emit(f"Failed to process {file_path.name}: {str(e)}")

    def _process_single_file(self, file_path: Path) -> None:
        """Process a single file using docling."""
        cmd = self._build_docling_command(file_path)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            logger.debug(f"Docling output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Docling failed: {e.stderr}")

    def _build_docling_command(self, file_path: Path) -> List[str]:
        """Build docling command with appropriate options."""
        cmd = [
            'docling',
            str(file_path),
            '--to', self.config.export_format,
            '--output', self.config.output_path,
            '--table-mode', self.config.table_mode,
            '--ocr-engine', 'easyocr',
            '--verbose'
        ]

        if self.config.force_ocr:
            cmd.append('--force-ocr')
        if self.config.ocr_bitmaps:
            cmd.append('--ocr')

        logger.debug(f"Docling command: {' '.join(cmd)}")
        return cmd

    def cancel(self) -> None:
        """Cancel processing."""
        self.is_cancelled = True

class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.temp_dir: Optional[str] = None
        self.worker: Optional[DoclingWorker] = None
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle('Docling GUI')
        self.setMinimumWidth(600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add UI components
        self._setup_folder_selection(layout)
        self._setup_processing_options(layout)
        self._setup_progress_section(layout)
        self._setup_control_buttons(layout)

    def _setup_folder_selection(self, layout: QVBoxLayout) -> None:
        """Setup input/output folder selection."""
        self.input_path = QLabel('No folder selected')
        self.output_path = QLabel('No folder selected')

        for label, path_label, button_text in [
            ('Input:', self.input_path, 'Select Input Folder'),
            ('Output:', self.output_path, 'Select Output Folder')
        ]:
            h_layout = QHBoxLayout()
            h_layout.addWidget(QLabel(label))
            h_layout.addWidget(path_label)
            btn = QPushButton(button_text)
            btn.clicked.connect(
                self.select_input_folder if 'Input' in button_text 
                else self.select_output_folder
            )
            h_layout.addWidget(btn)
            layout.addLayout(h_layout)

    def _setup_processing_options(self, layout: QVBoxLayout) -> None:
        """Setup processing options."""
        self.format_combo = QComboBox()
        self.format_combo.addItems(['md', 'json', 'text', 'doctags'])

        self.table_mode = QComboBox()
        self.table_mode.addItems(['fast', 'accurate'])

        for label, combo in [
            ('Export Format:', self.format_combo),
            ('Table Mode:', self.table_mode)
        ]:
            h_layout = QHBoxLayout()
            h_layout.addWidget(QLabel(label))
            h_layout.addWidget(combo)
            layout.addLayout(h_layout)

        self.force_ocr = QCheckBox('Force OCR')
        self.ocr_bitmaps = QCheckBox('OCR for Bitmaps')
        layout.addWidget(self.force_ocr)
        layout.addWidget(self.ocr_bitmaps)

    def _setup_progress_section(self, layout: QVBoxLayout) -> None:
        """Setup progress display section."""
        self.progress_label = QLabel()
        layout.addWidget(self.progress_label)

    def _setup_control_buttons(self, layout: QVBoxLayout) -> None:
        """Setup control buttons."""
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton('Start Processing')
        self.start_btn.clicked.connect(self.start_processing)
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.clicked.connect(self.cancel_processing)
        self.cancel_btn.setEnabled(False)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

    def select_input_folder(self) -> None:
        """Handle input folder selection."""
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder:
            self.input_path.setText(folder)
            logger.info(f"Input directory selected: {folder}")

    def select_output_folder(self) -> None:
        """Handle output folder selection."""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_path.setText(folder)
            logger.info(f"Output directory selected: {folder}")

    def start_processing(self) -> None:
        """Start document processing."""
        if not self._validate_paths():
            return

        self.temp_dir = tempfile.mkdtemp()
        logger.info(f"Created temporary directory: {self.temp_dir}")

        config = ProcessingConfig(
            input_path=self.input_path.text(),
            output_path=self.output_path.text(),
            export_format=self.format_combo.currentText(),
            table_mode=self.table_mode.currentText(),
            force_ocr=self.force_ocr.isChecked(),
            ocr_bitmaps=self.ocr_bitmaps.isChecked(),
            temp_dir=self.temp_dir
        )

        self.worker = DoclingWorker(config)
        self.worker.progress.connect(self._update_progress)
        self.worker.error.connect(self._handle_error)
        self.worker.finished.connect(self._processing_finished)

        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.worker.start()

    def _validate_paths(self) -> bool:
        """Validate input and output paths."""
        if self.input_path.text() == 'No folder selected':
            self.progress_label.setText('Please select an input folder')
            return False
        if self.output_path.text() == 'No folder selected':
            self.progress_label.setText('Please select an output folder')
            return False
        return True

    def cancel_processing(self) -> None:
        """Cancel ongoing processing."""
        if self.worker:
            self.worker.cancel()
            self.progress_label.setText("Cancelling...")
            self.cancel_btn.setEnabled(False)

    def _update_progress(self, message: str) -> None:
        """Update progress display."""
        self.progress_label.setText(message)

    def _handle_error(self, error_message: str) -> None:
        """Handle processing errors."""
        self.progress_label.setText(f"Error: {error_message}")

    def _processing_finished(self) -> None:
        """Clean up after processing is finished."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            logger.info(f"Removed temporary directory: {self.temp_dir}")

        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_label.setText("Processing completed")

def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 