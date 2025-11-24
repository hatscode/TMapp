from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QSplitter, QTreeWidget, QTreeWidgetItem,
                             QLineEdit, QFrame, QLabel, QPushButton, QToolBar,
                             QStatusBar, QTabWidget, QMessageBox, QInputDialog,
                             QMenu, QAction, QShortcut)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap, QKeyEvent, QKeySequence
import qtawesome as qta
from core.encryption import EncryptionService
from core.auth import AuthenticationManager
from core.note_manager import NoteManager
from .auth_dialog import AuthDialog
from .sidebar_widget import SidebarWidget
from .editor_widget import EditorWidget
from .settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    """
    Professional main window for TMapp with modern UI design.
    Security Controls: Authentication, Secure UI patterns
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize security components first
        self.auth_manager = AuthenticationManager()
        self.encryption_service = None
        self.note_manager = None
        self.master_password = None
        self.current_note_id = None
        
        # Setup window properties
        self.setWindowTitle("TMapp - Secure Notes")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Authenticate user before proceeding
        if not self.authenticate():
            self.close()
            return
            
        # Initialize core services
        self.init_services()
        
        # Setup UI
        self.init_ui()
        self.create_toolbar()
        self.create_status_bar()
        self.setup_shortcuts()
        
        # Load initial notes
        self.load_initial_notes()
    
    def authenticate(self) -> bool:
        """Handle authentication flow with modern dialog."""
        auth_dialog = AuthDialog(self.auth_manager, self)
        
        if auth_dialog.exec_() != auth_dialog.Accepted:
            return False
            
        self.master_password = auth_dialog.get_password()
        return True
    
    def init_services(self):
        """Initialize encryption and note management services."""
        salt = self.auth_manager.get_salt()
        self.encryption_service = EncryptionService(self.master_password, salt)
        self.note_manager = NoteManager(self.encryption_service)
    
    def init_ui(self):
        """Setup the main UI layout."""
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create splitter for resizable layout
        splitter = QSplitter(Qt.Horizontal)
        
        # Left sidebar with note list
        self.sidebar = SidebarWidget(self.note_manager)
        self.sidebar.setFixedWidth(280)
        self.sidebar.note_selected.connect(self.load_note)
        self.sidebar.new_note_requested.connect(self.create_new_note)
        self.sidebar.delete_note_requested.connect(self.delete_note)
        
        # Right editor area with enhanced widget
        self.editor_widget = EditorWidget()
        self.editor_widget.content_changed.connect(self.on_content_changed)
        
        # Add to splitter
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.editor_widget)
        splitter.setStretchFactor(0, 0)  # Sidebar fixed
        splitter.setStretchFactor(1, 1)  # Editor expandable
        
        main_layout.addWidget(splitter)
    
    def create_toolbar(self):
        """Create modern toolbar with essential actions."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(20, 20))
        
        # File actions
        try:
            new_action = toolbar.addAction(qta.icon('fa.plus', color='#cdd6f4'), "New Note")
        except:
            new_action = toolbar.addAction("+ New Note")
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.create_new_note)
        new_action.setToolTip("Create new note (Ctrl+N)")
        
        try:
            save_action = toolbar.addAction(qta.icon('fa.save', color='#cdd6f4'), "Save")
        except:
            save_action = toolbar.addAction("💾 Save")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_current_note)
        save_action.setToolTip("Save note (Ctrl+S)")
        
        toolbar.addSeparator()
        
        # Edit actions
        try:
            bold_action = toolbar.addAction(qta.icon('fa.bold', color='#cdd6f4'), "Bold")
        except:
            bold_action = toolbar.addAction("B")
        bold_action.setShortcut("Ctrl+B")
        bold_action.triggered.connect(lambda: self.editor_widget.insert_markdown("**", "**"))
        bold_action.setToolTip("Bold text (Ctrl+B)")
        
        try:
            italic_action = toolbar.addAction(qta.icon('fa.italic', color='#cdd6f4'), "Italic")
        except:
            italic_action = toolbar.addAction("I")
        italic_action.setShortcut("Ctrl+I")
        italic_action.triggered.connect(lambda: self.editor_widget.insert_markdown("*", "*"))
        italic_action.setToolTip("Italic text (Ctrl+I)")
        
        try:
            code_action = toolbar.addAction(qta.icon('fa.code', color='#cdd6f4'), "Code")
        except:
            code_action = toolbar.addAction("</>")
        code_action.setShortcut("Ctrl+K")
        code_action.triggered.connect(lambda: self.editor_widget.insert_markdown("`", "`"))
        code_action.setToolTip("Inline code (Ctrl+K)")
        
        toolbar.addSeparator()
        
        # View actions
        try:
            preview_action = toolbar.addAction(qta.icon('fa.eye', color='#cdd6f4'), "Preview")
        except:
            preview_action = toolbar.addAction("👁️")
        preview_action.triggered.connect(lambda: self.editor_widget.set_view_mode("preview"))
        preview_action.setToolTip("Toggle preview mode")
        
        toolbar.addSeparator()
        
        # Export action
        try:
            export_action = toolbar.addAction(qta.icon('fa.download', color='#cdd6f4'), "Export")
        except:
            export_action = toolbar.addAction("📤")
        export_action.triggered.connect(self.export_note)
        export_action.setToolTip("Export note as Markdown")
        
        toolbar.addSeparator()
        
        # Settings action
        try:
            settings_action = toolbar.addAction(qta.icon('fa.cog', color='#cdd6f4'), "Settings")
        except:
            settings_action = toolbar.addAction("⚙️")
        settings_action.triggered.connect(self.show_settings)
        settings_action.setToolTip("Open settings")
        
        # Security indicator
        self.security_indicator = QLabel("🔒 AES-256-GCM")
        self.security_indicator.setStyleSheet("""
            QLabel {
                color: #4ade80;
                font-weight: bold;
                padding: 4px 8px;
                background-color: #1e293b;
                border-radius: 4px;
            }
        """)
        toolbar.addWidget(self.security_indicator)
        
        self.addToolBar(toolbar)
    
    def create_status_bar(self):
        """Create status bar with useful information."""
        status_bar = QStatusBar()
        
        # Encryption status
        self.encryption_status = QLabel("PBKDF2 • AES-256-GCM")
        status_bar.addPermanentWidget(self.encryption_status)
        
        # Last saved time
        self.last_saved_label = QLabel("Not saved")
        status_bar.addPermanentWidget(self.last_saved_label)
        
        self.setStatusBar(status_bar)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # New note
        QShortcut(QKeySequence("Ctrl+N"), self, self.create_new_note)
        
        # Save
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_current_note)
        
        # Delete note
        QShortcut(QKeySequence("Delete"), self, self.delete_current_note)
        
        # Search
        QShortcut(QKeySequence("Ctrl+F"), self, self.focus_search)
        
        # Bold
        QShortcut(QKeySequence("Ctrl+B"), self, lambda: self.editor_widget.insert_markdown("**", "**"))
        
        # Italic
        QShortcut(QKeySequence("Ctrl+I"), self, lambda: self.editor_widget.insert_markdown("*", "*"))
        
        # Code
        QShortcut(QKeySequence("Ctrl+K"), self, lambda: self.editor_widget.insert_markdown("`", "`"))
    
    def apply_dark_theme(self):
        """Apply modern dark theme using QSS."""
        dark_style = """
        QMainWindow {
            background-color: #1e1e2e;
            color: #cdd6f4;
        }
        
        QMenuBar {
            background-color: #181825;
            color: #cdd6f4;
            border-bottom: 1px solid #313244;
        }
        
        QMenuBar::item:selected {
            background-color: #313244;
        }
        
        QToolBar {
            background-color: #181825;
            border: none;
            border-bottom: 1px solid #313244;
            spacing: 4px;
            padding: 8px;
        }
        
        QToolBar QToolButton {
            background-color: transparent;
            border: none;
            border-radius: 6px;
            padding: 6px;
            margin: 2px;
            color: #cdd6f4;
        }
        
        QToolBar QToolButton:hover {
            background-color: #313244;
        }
        
        QToolBar QToolButton:pressed {
            background-color: #45475a;
        }
        
        QStatusBar {
            background-color: #181825;
            color: #a6adc8;
            border-top: 1px solid #313244;
            font-size: 11px;
        }
        
        QStatusBar QLabel {
            padding: 0 8px;
        }
        
        QSplitter::handle {
            background-color: #313244;
            width: 1px;
        }
        
        QSplitter::handle:hover {
            background-color: #585b70;
        }
        """
        
        self.setStyleSheet(dark_style)
    
    def load_note(self, note_id: str):
        """Load selected note into editor."""
        # Auto-save current note if changed
        if self.current_note_id and self.editor_widget.get_content().strip():
            self.save_current_note()
        
        try:
            note = self.note_manager.get_note(note_id)
            if note:
                self.editor_widget.set_content(note.content)
                self.current_note_id = note_id
                self.setWindowTitle(f"TMapp - {note.title}")
                self.last_saved_label.setText("Loaded")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load note: {e}")
    
    def create_new_note(self):
        """Create a new note."""
        # Auto-save current note if changed
        if self.current_note_id and self.editor_widget.get_content().strip():
            self.save_current_note()
        
        try:
            # Clear editor for new note
            self.editor_widget.set_content("")
            self.current_note_id = None
            self.editor_widget.focus_editor()
            self.setWindowTitle("TMapp - New Note")
            self.statusBar().showMessage("New note created - start typing", 2000)
            self.last_saved_label.setText("Not saved")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to create note: {e}")
    
    def save_current_note(self):
        """Save current note content."""
        try:
            content = self.editor_widget.get_content()
            if not content.strip():
                self.statusBar().showMessage("Nothing to save", 2000)
                return
            
            # Extract title from first line
            title = content.split('\n')[0][:50] or "Untitled Note"
            
            if not self.current_note_id:
                # Create new note
                self.current_note_id = self.note_manager.create_note(content, title)
                self.sidebar.refresh_notes()
                self.sidebar.select_note(self.current_note_id)
            else:
                # Update existing note
                self.note_manager.update_note(self.current_note_id, content, title)
                self.sidebar.refresh_notes()
            
            self.setWindowTitle(f"TMapp - {title}")
            self.statusBar().showMessage("✓ Note saved and encrypted", 2000)
            self.last_saved_label.setText("Just saved")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save note: {e}")
    
    def delete_note(self, note_id: str):
        """Delete a note with confirmation."""
        reply = QMessageBox.question(
            self, "Delete Note",
            "Are you sure you want to delete this note?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.note_manager.delete_note(note_id)
                
                # Clear editor if deleting current note
                if self.current_note_id == note_id:
                    self.editor_widget.set_content("")
                    self.current_note_id = None
                    self.setWindowTitle("TMapp - Secure Notes")
                
                self.sidebar.refresh_notes()
                self.statusBar().showMessage("Note deleted", 2000)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete note: {e}")
    
    def delete_current_note(self):
        """Delete the currently selected note."""
        if self.current_note_id:
            self.delete_note(self.current_note_id)
    
    def focus_search(self):
        """Focus the search input in sidebar."""
        self.sidebar.search_input.setFocus()
    
    def export_note(self):
        """Export current note as Markdown file."""
        if not self.current_note_id:
            QMessageBox.information(self, "Export", "No note to export")
            return
        
        try:
            from PyQt5.QtWidgets import QFileDialog
            note = self.note_manager.get_note(self.current_note_id)
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Note", f"{note.title}.md", "Markdown Files (*.md)"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(note.content)
                self.statusBar().showMessage(f"Exported to {filename}", 3000)
                
        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Failed to export note: {e}")
    
    def on_content_changed(self):
        """Handle editor content changes."""
        if self.current_note_id:
            self.last_saved_label.setText("Unsaved changes")
    
    def load_initial_notes(self):
        """Load initial notes on startup."""
        self.sidebar.refresh_notes()
    
    def closeEvent(self, event):
        """Handle application close with security cleanup."""
        # Auto-save current work
        content = self.editor_widget.get_content()
        if content.strip():
            reply = QMessageBox.question(
                self, "Save Changes",
                "Do you want to save your changes before closing?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Yes:
                self.save_current_note()
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        
        # Security cleanup
        if self.encryption_service:
            del self.encryption_service
        
        if self.master_password:
            self.master_password = None
        
        event.accept()
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle global key presses."""
        # Escape key to focus editor
        if event.key() == Qt.Key_Escape:
            self.editor_widget.focus_editor()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        dialog.exec_()