import sys
import logging
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from src.core.config import AppConfig
from src.core.encryption import EncryptionService
from src.core.database import Database
from src.controllers.note_controller import NoteController
from src.controllers.notebook_controller import NotebookController
from src.ui.first_run_wizard import FirstRunWizard
from src.ui.main_window import MainWindow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TMApp:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application."""
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("TMapp")
        self.app.setOrganizationName("TMapp")
        
        # Enable high DPI scaling
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        # Initialize core services
        self.config = AppConfig()
        self.encryption_service = EncryptionService()
        self.database = Database(self.config.db_file)
        
        # Initialize controllers
        self.note_controller = NoteController(self.database, self.encryption_service)
        self.notebook_controller = NotebookController(self.database)
        
        self.main_window = None
        
        logger.info("TMapp initialized")
    
    def run(self):
        """Run the application."""
        try:
            if self.config.is_first_run():
                logger.info("First run detected, showing setup wizard")
                self._show_first_run_wizard()
            else:
                logger.info("Showing main window")
                self._show_main_window()
            
            return self.app.exec()
        
        except Exception as e:
            logger.error(f"Application error: {e}", exc_info=True)
            QMessageBox.critical(
                None,
                "Application Error",
                f"An unexpected error occurred:\n{str(e)}"
            )
            return 1
    
    def _show_first_run_wizard(self):
        """Show the first-run setup wizard."""
        wizard = FirstRunWizard()
        wizard.wizard_completed.connect(self._on_wizard_completed)
        
        if wizard.exec() == wizard.DialogCode.Accepted:
            logger.info("First-run wizard completed")
        else:
            logger.info("First-run wizard cancelled, exiting")
            sys.exit(0)
    
    def _on_wizard_completed(self, password: str):
        """Handle wizard completion."""
        try:
            # Cache the master password
            salt = self.encryption_service.cache_key(password)
            
            # Store salt in config (salt is not sensitive)
            self.config.set("password_salt", salt.hex())
            self.config.mark_initialized()
            
            logger.info("Master password configured")
            
            # Show success message
            QMessageBox.information(
                None,
                "Setup Complete",
                "Your master password has been created successfully!\n\n"
                "⚠️ IMPORTANT: Store your password in a safe place. "
                "If you forget it, your notes cannot be recovered."
            )
            
            # Show main window
            self._show_main_window()
        
        except Exception as e:
            logger.error(f"Failed to complete setup: {e}")
            QMessageBox.critical(
                None,
                "Setup Error",
                f"Failed to complete setup:\n{str(e)}"
            )
            sys.exit(1)
    
    def _show_main_window(self):
        """Show the main application window."""
        self.main_window = MainWindow(
            self.config,
            self.encryption_service,
            self.note_controller,
            self.notebook_controller
        )
        self.main_window.show()
        logger.info("Main window displayed")


def main():
    """Application entry point."""
    app = TMApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()