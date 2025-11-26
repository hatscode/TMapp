# filepath: /home/wh1t3h4t/Desktop/TMapp/src/ui/main_window.py
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QSplitter, QStatusBar, QToolBar, QLabel, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence, QIcon
import logging

from src.core.config import AppConfig
from src.core.encryption import EncryptionService
from src.controllers.note_controller import NoteController
from src.controllers.notebook_controller import NotebookController

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window with three-panel layout."""
    
    locked = pyqtSignal()
    unlocked = pyqtSignal()
    
    def __init__(self, config: AppConfig, encryption_service: EncryptionService,
                 note_controller: NoteController, notebook_controller: NotebookController):
        super().__init__()
        
        self.config = config
        self.encryption_service = encryption_service
        self.note_controller = note_controller
        self.notebook_controller = notebook_controller
        self.is_locked = False
        
        self._setup_ui()
        self._setup_toolbar()
        self._setup_statusbar()
        self._setup_shortcuts()
        self._setup_auto_lock()
        self._load_data()
        
        logger.info("Main window initialized")
    
    def _setup_ui(self):
        """Setup the main UI layout."""
        self.setWindowTitle("TMapp - Secure Notes")
        self.setMinimumSize(1000, 600)
        
        # Central widget with three-panel layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create main splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sidebar (250px default)
        self.sidebar = QWidget()
        self.sidebar.setMinimumWidth(200)
        self.sidebar.setMaximumWidth(400)
        sidebar_layout = QVBoxLayout(self.sidebar)
        
        # Sidebar header
        sidebar_header = QLabel("📚 Navigation")
        sidebar_header.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        sidebar_layout.addWidget(sidebar_header)
        
        # Quick access section
        quick_access_label = QLabel("Quick Access")
        quick_access_label.setStyleSheet("padding: 5px 10px; color: #888;")
        sidebar_layout.addWidget(quick_access_label)
        
        # Placeholder for quick access buttons
        for item in ["📝 All Notes", "⭐ Favorites", "🕐 Recent", "🗑️ Trash"]:
            btn_label = QLabel(item)
            btn_label.setStyleSheet("padding: 8px 15px; border-radius: 4px;")
            sidebar_layout.addWidget(btn_label)
        
        # Notebooks section
        notebooks_label = QLabel("Notebooks")
        notebooks_label.setStyleSheet("padding: 5px 10px; margin-top: 10px; color: #888;")
        sidebar_layout.addWidget(notebooks_label)
        
        # Placeholder for notebooks
        self.notebooks_container = QWidget()
        self.notebooks_layout = QVBoxLayout(self.notebooks_container)
        sidebar_layout.addWidget(self.notebooks_container)
        
        sidebar_layout.addStretch()
        
        # Notes list panel (300px default)
        self.notes_panel = QWidget()
        self.notes_panel.setMinimumWidth(250)
        self.notes_panel.setMaximumWidth(500)
        notes_layout = QVBoxLayout(self.notes_panel)
        
        notes_header = QLabel("📝 All Notes")
        notes_header.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        notes_layout.addWidget(notes_header)
        
        notes_placeholder = QLabel("No notes yet.\nClick '📝 New Note' to create one.")
        notes_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        notes_placeholder.setStyleSheet("color: #888; padding: 40px;")
        notes_layout.addWidget(notes_placeholder)
        notes_layout.addStretch()
        
        # Editor panel (flexible width)
        self.editor_panel = QWidget()
        editor_layout = QVBoxLayout(self.editor_panel)
        
        editor_placeholder = QLabel("✏️ Editor\n\nSelect or create a note to start writing.")
        editor_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        editor_placeholder.setStyleSheet("color: #888; font-size: 13px;")
        editor_layout.addWidget(editor_placeholder)
        
        # Add panels to splitter
        self.main_splitter.addWidget(self.sidebar)
        self.main_splitter.addWidget(self.notes_panel)
        self.main_splitter.addWidget(self.editor_panel)
        
        # Set initial sizes
        sidebar_width = self.config.get("sidebar_width", 250)
        notes_width = self.config.get("notes_panel_width", 300)
        self.main_splitter.setSizes([sidebar_width, notes_width, 450])
        
        main_layout.addWidget(self.main_splitter)
        
        # Apply dark theme
        self._apply_theme()
    
    def _setup_toolbar(self):
        """Setup main toolbar."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # New note action
        new_note_action = QAction("📝 New Note", self)
        new_note_action.setShortcut(QKeySequence("Ctrl+N"))
        new_note_action.triggered.connect(self._new_note)
        toolbar.addAction(new_note_action)
        
        toolbar.addSeparator()
        
        # Search action
        search_action = QAction("🔍 Search", self)
        search_action.setShortcut(QKeySequence("Ctrl+K"))
        search_action.triggered.connect(self._open_search)
        toolbar.addAction(search_action)
        
        toolbar.addSeparator()
        
        # Lock action
        self.lock_action = QAction("🔒 Lock", self)
        self.lock_action.setShortcut(QKeySequence("Ctrl+L"))
        self.lock_action.triggered.connect(self._lock_application)
        toolbar.addAction(self.lock_action)
        
        toolbar.addSeparator()
        
        # Settings action
        settings_action = QAction("⚙️ Settings", self)
        settings_action.triggered.connect(self._open_settings)
        toolbar.addAction(settings_action)
    
    def _setup_statusbar(self):
        """Setup status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Encryption status
        self.encryption_label = QLabel("🔐 Encrypted")
        self.statusbar.addPermanentWidget(self.encryption_label)
        
        # Auto-save status
        self.autosave_label = QLabel("💾 Auto-save: ON")
        self.statusbar.addPermanentWidget(self.autosave_label)
        
        self.statusbar.showMessage("Ready")
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        logger.info("Keyboard shortcuts configured")
    
    def _setup_auto_lock(self):
        """Setup auto-lock timer."""
        timeout = self.config.get("auto_lock_timeout", 300) * 1000  # Convert to ms
        self.auto_lock_timer = QTimer()
        self.auto_lock_timer.timeout.connect(self._lock_application)
        self.auto_lock_timer.start(timeout)
        
        logger.info(f"Auto-lock configured: {timeout/1000}s")
    
    def _load_data(self):
        """Load initial data."""
        try:
            # Load notebooks
            notebooks = self.notebook_controller.get_all_notebooks()
            for notebook in notebooks:
                notebook_label = QLabel(f"{notebook.icon} {notebook.name}")
                notebook_label.setStyleSheet("padding: 8px 15px; border-radius: 4px;")
                self.notebooks_layout.addWidget(notebook_label)
            
            # Load notes count
            notes = self.note_controller.get_all_notes()
            self.statusbar.showMessage(f"Loaded {len(notes)} notes, {len(notebooks)} notebooks")
            
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
    
    def _apply_theme(self):
        """Apply dark theme."""
        theme = self.config.get("theme", "dark")
        
        if theme == "dark":
            stylesheet = """
                QMainWindow {
                    background-color: #1a1a1a;
                    color: #e4e4e4;
                }
                QWidget {
                    background-color: #1a1a1a;
                    color: #e4e4e4;
                }
                QToolBar {
                    background-color: #2d2d2d;
                    border: none;
                    spacing: 5px;
                    padding: 5px;
                }
                QStatusBar {
                    background-color: #2d2d2d;
                    color: #e4e4e4;
                }
                QLabel {
                    color: #e4e4e4;
                }
            """
            self.setStyleSheet(stylesheet)
    
    def _new_note(self):
        """Create a new note."""
        try:
            default_notebook = self.notebook_controller.get_default_notebook()
            note = self.note_controller.create_note(
                title="Untitled Note",
                content="",
                notebook_id=default_notebook.id if default_notebook else None
            )
            if note:
                self.statusbar.showMessage(f"Created new note: {note.title}", 3000)
                logger.info(f"Created note: {note.id}")
            else:
                self.statusbar.showMessage("Failed to create note", 3000)
        except Exception as e:
            logger.error(f"Failed to create note: {e}")
            QMessageBox.warning(self, "Error", f"Failed to create note:\n{str(e)}")
    
    def _open_search(self):
        """Open search dialog."""
        logger.info("Search action triggered")
        self.statusbar.showMessage("Search feature coming soon...", 2000)
    
    def _lock_application(self):
        """Lock the application."""
        if not self.is_locked:
            self.is_locked = True
            self.encryption_service.clear_cached_key()
            self.lock_action.setText("🔓 Unlock")
            self.statusbar.showMessage("Application locked")
            self.locked.emit()
            logger.info("Application locked")
    
    def _unlock_application(self):
        """Unlock the application."""
        self.is_locked = False
        self.lock_action.setText("🔒 Lock")
        self.statusbar.showMessage("Application unlocked")
        self.unlocked.emit()
        logger.info("Application unlocked")
    
    def _open_settings(self):
        """Open settings dialog."""
        logger.info("Settings action triggered")
        self.statusbar.showMessage("Settings feature coming soon...", 2000)
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save window state
        splitter_sizes = self.main_splitter.sizes()
        if len(splitter_sizes) >= 2:
            self.config.set("sidebar_width", splitter_sizes[0])
            self.config.set("notes_panel_width", splitter_sizes[1])
        self.config.save()
        
        # Clear encryption keys
        self.encryption_service.clear_cached_key()
        
        logger.info("Application closing")
        event.accept()