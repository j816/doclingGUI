import sys
import os
import json
from typing import List, Optional, Dict
from dataclasses import dataclass
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QCheckBox,
    QComboBox, QLineEdit, QFileDialog, QSpinBox, QHBoxLayout, QMessageBox,
    QProgressBar
)
from PyQt5.QtCore import Qt
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class AppSettings:
    """Immutable settings configuration."""
    input_path: str
    output_path: str
    ocr_enabled: bool = False
    force_ocr: bool = False
    ocr_engine: str = "easyocr"
    table_mode: str = "accurate"
    verbosity: int = 0
    delete_pdfs: bool = False

class SettingsManager:
    """Manages persistent storage of application settings."""
    def __init__(self):
        self.config_file = os.path.expanduser("~/.docling_gui_settings.json")
        self.default_settings = AppSettings(
            input_path=os.path.expanduser("~/Documents"),
            output_path=os.path.expanduser("~/Documents")
        )

    def load_settings(self) -> AppSettings:
        """Load saved settings or return defaults if not available."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    saved_settings = json.load(f)
                return AppSettings(
                    input_path=saved_settings.get("input_path", self.default_settings.input_path),
                    output_path=saved_settings.get("output_path", self.default_settings.output_path),
                    ocr_enabled=saved_settings.get("ocr_enabled", self.default_settings.ocr_enabled),
                    force_ocr=saved_settings.get("force_ocr", self.default_settings.force_ocr),
                    ocr_engine=saved_settings.get("ocr_engine", self.default_settings.ocr_engine),
                    table_mode=saved_settings.get("table_mode", self.default_settings.table_mode),
                    verbosity=saved_settings.get("verbosity", self.default_settings.verbosity),
                    delete_pdfs=saved_settings.get("delete_pdfs", self.default_settings.delete_pdfs)
                )
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load settings: {e}")
        return self.default_settings

    def save_settings(self, settings: AppSettings) -> None:
        """Safely save settings to configuration file."""
        try:
            settings_dict = {
                "input_path": settings.input_path,
                "output_path": settings.output_path,
                "ocr_enabled": settings.ocr_enabled,
                "force_ocr": settings.force_ocr,
                "ocr_engine": settings.ocr_engine,
                "table_mode": settings.table_mode,
                "verbosity": settings.verbosity,
                "delete_pdfs": settings.delete_pdfs
            }
            with open(self.config_file, 'w') as f:
                json.dump(settings_dict, f)
        except OSError as e:
            logger.error(f"Failed to save settings: {e}")

class DoclingGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()
        self.current_settings = self.settings_manager.load_settings()
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize the user interface components."""
        self.setWindowTitle("Docling PDF to Markdown Converter")
        self.setGeometry(200, 200, 500, 400)

        layout = QVBoxLayout()
        self._setup_folder_selection(layout)
        self._setup_options(layout)
        self._setup_progress_section(layout)
        self.setLayout(layout)

    def _setup_folder_selection(self, layout: QVBoxLayout) -> None:
        """Set up the folder selection widgets."""
        # Input folder
        input_layout = QHBoxLayout()
        self.input_label = QLabel("Input Folder:")
        self.input_path = QLineEdit()
        self.input_path.setText(self.current_settings.input_path)
        self.input_browse = QPushButton("Browse")
        self.input_browse.clicked.connect(self.browse_input_folder)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_path)
        input_layout.addWidget(self.input_browse)
        layout.addLayout(input_layout)

        # Output folder
        output_layout = QHBoxLayout()
        self.output_label = QLabel("Output Folder:")
        self.output_path = QLineEdit()
        self.output_path.setText(self.current_settings.output_path)
        self.output_browse = QPushButton("Browse")
        self.output_browse.clicked.connect(self.browse_output_folder)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(self.output_browse)
        layout.addLayout(output_layout)

    def browse_input_folder(self) -> None:
        """Handle input folder selection."""
        start_dir = self.input_path.text() or self.current_settings.input_path
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder", start_dir)
        if folder:
            self.input_path.setText(folder)
            self.current_settings.input_path = folder

    def browse_output_folder(self) -> None:
        """Handle output folder selection."""
        start_dir = self.output_path.text() or self.current_settings.output_path
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", start_dir)
        if folder:
            self.output_path.setText(folder)
            self.current_settings.output_path = folder

    def _find_pdf_files(self, folder: str) -> List[str]:
        """Find all PDF files in the folder and subfolders."""
        pdf_files = []
        try:
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(root, file))
        except OSError as e:
            logger.error(f"Error scanning for PDF files: {e}")
            raise RuntimeError(f"Failed to scan for PDF files: {e}")
        return pdf_files

    def _setup_options(self, layout: QVBoxLayout) -> None:
        """Set up the conversion options widgets."""
        # OCR Options
        ocr_group = QVBoxLayout()
        ocr_label = QLabel("OCR Settings:")
        ocr_label.setStyleSheet("font-weight: bold;")
        self.ocr_checkbox = QCheckBox("Enable OCR (process images)")
        self.force_ocr_checkbox = QCheckBox("Force OCR (process all text)")
        self.delete_pdfs_checkbox = QCheckBox("Delete PDFs after conversion")
        
        ocr_group.addWidget(ocr_label)
        ocr_group.addWidget(self.ocr_checkbox)
        ocr_group.addWidget(self.force_ocr_checkbox)
        ocr_group.addWidget(self.delete_pdfs_checkbox)
        layout.addLayout(ocr_group)

        # OCR Engine Selection
        engine_group = QVBoxLayout()
        self.ocr_engine_label = QLabel("OCR Engine:")
        self.ocr_engine_combo = QComboBox()
        self.ocr_engine_combo.addItems(["easyocr", "tesseract", "tesseract_cli", "ocrmac"])
        engine_group.addWidget(self.ocr_engine_label)
        engine_group.addWidget(self.ocr_engine_combo)
        layout.addLayout(engine_group)

        # Table Mode
        table_group = QVBoxLayout()
        self.table_mode_label = QLabel("Table Mode:")
        self.table_mode_combo = QComboBox()
        self.table_mode_combo.addItems(["accurate", "fast"])
        self.table_mode_combo.setCurrentText("accurate")  # Set accurate as default
        table_desc = QLabel("accurate = better quality but slower\nfast = lower quality but faster")
        table_desc.setStyleSheet("color: gray; font-size: 10px;")
        table_group.addWidget(self.table_mode_label)
        table_group.addWidget(self.table_mode_combo)
        table_group.addWidget(table_desc)
        layout.addLayout(table_group)

        # Verbosity Level
        verbosity_group = QVBoxLayout()
        self.verbosity_label = QLabel("Verbosity Level:")
        self.verbosity_spinbox = QSpinBox()
        self.verbosity_spinbox.setRange(0, 2)
        verbosity_desc = QLabel(
            "0 = Silent (errors only)\n"
            "1 = Info (processing updates)\n"
            "2 = Debug (detailed technical info)"
        )
        verbosity_desc.setStyleSheet("color: gray; font-size: 10px;")
        verbosity_group.addWidget(self.verbosity_label)
        verbosity_group.addWidget(self.verbosity_spinbox)
        verbosity_group.addWidget(verbosity_desc)
        layout.addLayout(verbosity_group)

    def _setup_progress_section(self, layout: QVBoxLayout) -> None:
        """Set up the progress section widgets."""
        progress_group = QVBoxLayout()
        
        # Status label for current file
        self.status_label = QLabel("Ready to start conversion...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666;
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
                background: #f9f9f9;
            }
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        progress_group.addWidget(self.status_label)
        
        # Progress information
        self.progress_info = QLabel("0/0 files processed")
        self.progress_info.setAlignment(Qt.AlignCenter)
        progress_group.addWidget(self.progress_info)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bbb;
                border-radius: 3px;
                text-align: center;
                padding: 1px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
            }
        """)
        progress_group.addWidget(self.progress_bar)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Run button
        self.run_button = QPushButton("Run Conversion")
        self.run_button.clicked.connect(self.run_conversion)
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                font-weight: bold;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        # Reset button
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_conversion)
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px;
                font-weight: bold;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        buttons_layout.addWidget(self.run_button)
        buttons_layout.addWidget(self.reset_button)
        progress_group.addLayout(buttons_layout)
        
        layout.addLayout(progress_group)

    def run_conversion(self) -> None:
        """Run the conversion process."""
        error_message = self.validate_paths()
        if error_message:
            QMessageBox.critical(self, "Error", error_message)
            return

        config = self.get_config()
        
        try:
            self._process_conversion(config)
            QMessageBox.information(self, "Success", "Conversion completed successfully!")
        except Exception as e:
            logger.error(f"Conversion failed: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Conversion failed:\n{str(e)}")

    def validate_paths(self) -> Optional[str]:
        """Validate input and output paths."""
        input_folder = self.input_path.text().strip()
        output_folder = self.output_path.text().strip()

        if not input_folder or not output_folder:
            return "Please specify both input and output folders."
        
        if not os.path.exists(input_folder):
            return "Input folder does not exist."
        
        if not os.path.exists(output_folder):
            try:
                os.makedirs(output_folder)
            except OSError as e:
                return f"Failed to create output folder: {e}"

        return None

    def get_config(self) -> AppSettings:
        """Get the current configuration from UI elements."""
        verbosity_level = self.verbosity_spinbox.value()
        verbosity = "-v" * verbosity_level if verbosity_level > 0 else ""
        
        return AppSettings(
            input_path=self.input_path.text().strip(),
            output_path=self.output_path.text().strip(),
            ocr_enabled=self.ocr_checkbox.isChecked(),
            force_ocr=self.force_ocr_checkbox.isChecked(),
            ocr_engine=self.ocr_engine_combo.currentText(),
            table_mode=self.table_mode_combo.currentText(),
            verbosity=verbosity,
            delete_pdfs=self.delete_pdfs_checkbox.isChecked()
        )

    def _process_conversion(self, config: AppSettings) -> None:
        """Process the conversion with the given configuration."""
        try:
            # Disable run button during conversion
            self.run_button.setEnabled(False)
            self.run_button.setText("Converting...")
            
            pdf_files = self._find_pdf_files(config.input_path)
            if not pdf_files:
                raise RuntimeError("No PDF files found in the input folder")

            total_files = len(pdf_files)
            self.progress_bar.setMaximum(total_files)
            self.progress_bar.setValue(0)
            
            for index, pdf_file in enumerate(pdf_files, 1):
                # Update status displays
                filename = os.path.basename(pdf_file)
                self.status_label.setText(f"Processing: {filename}")
                self.progress_info.setText(f"{index}/{total_files} files processed")
                
                relative_path = os.path.relpath(pdf_file, config.input_path)
                output_dir = os.path.join(config.output_path, os.path.dirname(relative_path))
                
                os.makedirs(output_dir, exist_ok=True)
                
                # Build command with proper structure
                command = ["docling"]
                command.append(pdf_file)
                command.extend(["--from", "pdf", "--to", "md"])
                
                if config.ocr_enabled:
                    command.append("--ocr")
                else:
                    command.append("--no-ocr")
                    
                if config.force_ocr:
                    command.append("--force-ocr")
                else:
                    command.append("--no-force-ocr")
                    
                command.extend(["--ocr-engine", config.ocr_engine])
                command.extend(["--table-mode", config.table_mode])
                command.extend(["--output", output_dir])
                
                if config.verbosity:
                    command.append(config.verbosity)

                logger.info(f"Processing file {index}/{total_files}: {pdf_file}")
                logger.info(f"Running command: {' '.join(command)}")
                
                try:
                    result = subprocess.run(
                        command,
                        check=True,
                        text=True,
                        capture_output=True
                    )
                    
                    if result.stderr:
                        logger.warning(f"Command stderr output:\n{result.stderr}")
                    if result.stdout:
                        logger.info(f"Command stdout output:\n{result.stdout}")
                        
                except subprocess.CalledProcessError as e:
                    error_message = (
                        f"Error processing {filename}\n"
                        f"Command failed with exit status {e.returncode}\n"
                        f"Error output:\n{e.stderr if e.stderr else 'No error output'}\n"
                        f"Standard output:\n{e.stdout if e.stdout else 'No standard output'}"
                    )
                    logger.error(error_message)
                    raise RuntimeError(error_message)

                self.progress_bar.setValue(index)
                QApplication.processEvents()  # Update UI

            if config.delete_pdfs:
                self.status_label.setText("Deleting processed PDF files...")
                self._delete_processed_pdfs(config.input_path)
                
            self.status_label.setText("Conversion completed successfully!")
            self.progress_info.setText(f"Processed {total_files} files")
            
        finally:
            # Re-enable run button
            self.run_button.setEnabled(True)
            self.run_button.setText("Run Conversion")

    def _delete_processed_pdfs(self, folder: str) -> None:
        """Delete PDF files after successful conversion."""
        for root, _, files in os.walk(folder):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_path = os.path.join(root, file)
                    try:
                        os.remove(pdf_path)
                        logger.info(f"Deleted PDF: {pdf_path}")
                    except OSError as e:
                        logger.error(f"Failed to delete PDF {pdf_path}: {e}")

    def reset_conversion(self) -> None:
        """Reset the conversion state and refresh file lists."""
        try:
            # Reset progress indicators
            self.progress_bar.setValue(0)
            self.progress_info.setText("0/0 files processed")
            self.status_label.setText("Ready to start conversion...")
            
            # Re-enable buttons
            self.run_button.setEnabled(True)
            self.run_button.setText("Run Conversion")
            
            # Save current settings
            self.save_current_settings()
            
            # Refresh the UI
            QMessageBox.information(self, "Reset Complete", 
                "Conversion state has been reset.\nYou can now start a new conversion.")
            
        except Exception as e:
            logger.error(f"Failed to reset conversion: {e}")
            QMessageBox.critical(self, "Error", f"Failed to reset conversion: {str(e)}")

    def save_current_settings(self) -> None:
        """Save current UI state to settings."""
        try:
            current_settings = AppSettings(
                input_path=self.input_path.text().strip(),
                output_path=self.output_path.text().strip(),
                ocr_enabled=self.ocr_checkbox.isChecked(),
                force_ocr=self.force_ocr_checkbox.isChecked(),
                ocr_engine=self.ocr_engine_combo.currentText(),
                table_mode=self.table_mode_combo.currentText(),
                verbosity=self.verbosity_spinbox.value(),
                delete_pdfs=self.delete_pdfs_checkbox.isChecked()
            )
            self.settings_manager.save_settings(current_settings)
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")

    def closeEvent(self, event) -> None:
        """Handle application closure."""
        try:
            self.save_current_settings()
            event.accept()
        except Exception as e:
            logger.error(f"Failed to save settings on close: {e}")
            event.accept()

def main():
    """Main entry point of the application."""
    try:
        app = QApplication(sys.argv)
        gui = DoclingGUI()
        gui.show()
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical("Application failed to start", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
