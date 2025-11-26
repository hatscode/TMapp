"""Professional main window with theme support - COMPLETE VERSION."""
import logging  # Add this missing import
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QSplitter, QStatusBar, QToolBar, QLabel, QMessageBox,
                              QListWidget, QListWidgetItem, QTextEdit, QPushButton,
                              QToolButton, QMenu, QLineEdit, QFileDialog)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QAction, QKeySequence, QFont, QIcon, QTextCharFormat, QTextCursor

from src.core.config import AppConfig
from src.core.encryption import EncryptionService
from src.controllers.note_controller import NoteController
from src.controllers.notebook_controller import NotebookController
from src.ui.theme_manager import ThemeManager, ThemeMode

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Professional main window with modern UI."""
    
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
        self.current_note_id = None
        self.current_note = None
        self.is_modified = False
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        self.theme_manager.theme_changed.connect(self._on_theme_changed)
        
        self._setup_ui()
        self._apply_theme()
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_statusbar()
        self._setup_shortcuts()
        self._setup_auto_save()
        self._setup_auto_lock()
        self._load_data()
        
        logger.info("Main window initialized with professional UI")
    
    def _setup_ui(self):
        """Setup the professional 3-panel layout."""
        self.setWindowTitle("TMapp - Secure Note-Taking")
        self.setMinimumSize(1400, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Main splitter with 3 panels
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # ===== LEFT: SIDEBAR (280px) =====
        self.sidebar = self._create_sidebar()
        
        # ===== MIDDLE: NOTE LIST (350px) =====
        self.notes_panel = self._create_notes_panel()
        
        # ===== RIGHT: EDITOR (flexible) =====
        self.editor_panel = self._create_editor_panel()
        
        # Add to splitter
        self.main_splitter.addWidget(self.sidebar)
        self.main_splitter.addWidget(self.notes_panel)
        self.main_splitter.addWidget(self.editor_panel)
        
        # Set initial sizes
        self.main_splitter.setSizes([280, 350, 770])
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 0)
        self.main_splitter.setStretchFactor(2, 1)
        
        main_layout.addWidget(self.main_splitter)
    
    def _create_sidebar(self) -> QWidget:
        """Create professional sidebar with navigation."""
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setMinimumWidth(200)
        sidebar.setMaximumWidth(400)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Logo/Title
        title = QLabel("TMapp")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("padding: 8px 0px;")
        layout.addWidget(title)
        
        layout.addSpacing(16)
        
        # Quick Access Section
        quick_label = QLabel("QUICK ACCESS")
        quick_label.setObjectName("secondaryLabel")
        quick_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        quick_label.setStyleSheet("padding: 4px 8px;")
        layout.addWidget(quick_label)
        
        # Quick access buttons
        self.btn_all_notes = self._create_sidebar_button("All Notes", "list")
        self.btn_all_notes.clicked.connect(self._show_all_notes)
        layout.addWidget(self.btn_all_notes)
        
        self.btn_recent = self._create_sidebar_button("Recent", "clock")
        self.btn_recent.clicked.connect(self._show_recent)
        layout.addWidget(self.btn_recent)
        
        self.btn_favorites = self._create_sidebar_button("Favorites", "star")
        self.btn_favorites.clicked.connect(self._show_favorites)
        layout.addWidget(self.btn_favorites)
        
        self.btn_trash = self._create_sidebar_button("Trash", "trash")
        self.btn_trash.clicked.connect(self._show_trash)
        layout.addWidget(self.btn_trash)
        
        layout.addSpacing(24)
        
        # Notebooks Section
        notebooks_label = QLabel("NOTEBOOKS")
        notebooks_label.setObjectName("secondaryLabel")
        notebooks_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        notebooks_label.setStyleSheet("padding: 4px 8px;")
        layout.addWidget(notebooks_label)
        
        # Notebooks container
        self.notebooks_container = QWidget()
        self.notebooks_layout = QVBoxLayout(self.notebooks_container)
        self.notebooks_layout.setContentsMargins(0, 0, 0, 0)
        self.notebooks_layout.setSpacing(4)
        layout.addWidget(self.notebooks_container)
        
        layout.addStretch()
        
        return sidebar
    
    def _create_sidebar_button(self, text: str, icon_name: str) -> QPushButton:
        """Create styled sidebar button."""
        btn = QPushButton(text)
        btn.setObjectName("secondaryButton")
        btn.setStyleSheet("""
            QPushButton#secondaryButton {
                text-align: left;
                padding: 10px 12px;
                font-size: 14px;
                font-weight: 500;
            }
        """)
        return btn
    
    def _create_notes_panel(self) -> QWidget:
        """Create notes list panel."""
        panel = QWidget()
        panel.setMinimumWidth(300)
        panel.setMaximumWidth(600)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Header with title and new button
        header = QHBoxLayout()
        
        self.notes_title = QLabel("All Notes")
        self.notes_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.addWidget(self.notes_title)
        
        header.addStretch()
        
        btn_new_note = QPushButton("New Note")
        btn_new_note.setFont(QFont("Segoe UI", 12))
        btn_new_note.clicked.connect(self._new_note)
        header.addWidget(btn_new_note)
        
        layout.addLayout(header)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search notes...")
        self.search_box.textChanged.connect(self._on_search)
        layout.addWidget(self.search_box)
        
        # Notes list
        self.notes_list = QListWidget()
        self.notes_list.itemClicked.connect(self._on_note_selected)
        layout.addWidget(self.notes_list)
        
        return panel
    
    def _create_editor_panel(self) -> QWidget:
        """Create rich text editor panel."""
        panel = QWidget()
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(12)
        
        # Editor header
        header = QHBoxLayout()
        
        editor_label = QLabel("Editor")
        editor_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.addWidget(editor_label)
        
        header.addStretch()
        
        # Theme toggle button
        self.btn_theme_toggle = QToolButton()
        self.btn_theme_toggle.setText("Dark")
        self.btn_theme_toggle.setToolTip("Toggle Dark/Light Theme")
        self.btn_theme_toggle.clicked.connect(self._toggle_theme)
        header.addWidget(self.btn_theme_toggle)
        
        layout.addLayout(header)
        
        # Title input
        self.editor_title = QLineEdit()
        self.editor_title.setPlaceholderText("Note title...")
        self.editor_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.editor_title.setStyleSheet("QLineEdit { padding: 12px; }")
        self.editor_title.textChanged.connect(self._on_title_changed)
        layout.addWidget(self.editor_title)
        
        # Formatting toolbar
        toolbar = self._create_formatting_toolbar()
        layout.addWidget(toolbar)
        
        # Editor content
        self.editor_content = QTextEdit()
        self.editor_content.setPlaceholderText("Start writing your note...\n\nSupports Markdown formatting")
        self.editor_content.setFont(QFont("Segoe UI", 16))
        self.editor_content.textChanged.connect(self._on_content_changed)
        layout.addWidget(self.editor_content)
        
        # Metadata bar
        metadata = QHBoxLayout()
        
        self.word_count_label = QLabel("0 words")
        self.word_count_label.setObjectName("secondaryLabel")
        metadata.addWidget(self.word_count_label)
        
        metadata.addStretch()
        
        self.autosave_label = QLabel("All changes saved")
        self.autosave_label.setObjectName("secondaryLabel")
        metadata.addWidget(self.autosave_label)
        
        layout.addLayout(metadata)
        
        return panel
    
    def _create_formatting_toolbar(self) -> QWidget:
        """Create formatting toolbar for editor."""
        toolbar = QWidget()
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Bold
        btn_bold = QToolButton()
        btn_bold.setText("B")
        btn_bold.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        btn_bold.setToolTip("Bold (Ctrl+B)")
        btn_bold.clicked.connect(self._format_bold)
        layout.addWidget(btn_bold)
        
        # Italic
        btn_italic = QToolButton()
        btn_italic.setText("I")
        btn_italic.setFont(QFont("Segoe UI", 12, QFont.Weight.Normal))
        btn_italic.setStyleSheet("font-style: italic;")
        btn_italic.setToolTip("Italic (Ctrl+I)")
        btn_italic.clicked.connect(self._format_italic)
        layout.addWidget(btn_italic)
        
        # Underline
        btn_underline = QToolButton()
        btn_underline.setText("U")
        btn_underline.setFont(QFont("Segoe UI", 12))
        btn_underline.setStyleSheet("text-decoration: underline;")
        btn_underline.setToolTip("Underline (Ctrl+U)")
        btn_underline.clicked.connect(self._format_underline)
        layout.addWidget(btn_underline)
        
        layout.addSpacing(12)
        
        # Image
        btn_image = QToolButton()
        btn_image.setText("IMG")
        btn_image.setToolTip("Insert Image")
        btn_image.clicked.connect(self._insert_image)
        layout.addWidget(btn_image)
        
        layout.addStretch()
        
        return toolbar
    
    def _setup_menu_bar(self):
        """Setup menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Note", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.triggered.connect(self._new_note)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        self.lock_action = QAction("Lock", self)
        self.lock_action.setShortcut(QKeySequence("Ctrl+L"))
        self.lock_action.triggered.connect(self._toggle_lock)
        file_menu.addAction(self.lock_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        theme_action = QAction("Toggle Theme", self)
        theme_action.setShortcut(QKeySequence("Ctrl+T"))
        theme_action.triggered.connect(self._toggle_theme)
        view_menu.addAction(theme_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
    
    def _setup_toolbar(self):
        """Setup toolbar."""
        pass
    
    def _setup_statusbar(self):
        """Setup status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        self.encryption_label = QLabel("Encrypted")
        self.encryption_label.setObjectName("secondaryLabel")
        self.statusbar.addPermanentWidget(self.encryption_label)
        
        self.statusbar.showMessage("Ready")
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        pass
    
    def _setup_auto_save(self):
        """Setup auto-save timer."""
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save)
        self.auto_save_timer.start(2000)  # 2 seconds
    
    def _setup_auto_lock(self):
        """Setup auto-lock timer."""
        timeout = self.config.get("auto_lock_timeout", 300) * 1000
        self.auto_lock_timer = QTimer()
        self.auto_lock_timer.timeout.connect(self._lock_application)
        if timeout > 0:
            self.auto_lock_timer.start(timeout)
    
    def _apply_theme(self):
        """Apply current theme stylesheet."""
        stylesheet = self.theme_manager.get_stylesheet()
        self.setStyleSheet(stylesheet)
        
        # Update theme toggle button
        if self.theme_manager.current_theme == ThemeMode.DARK:
            if hasattr(self, 'btn_theme_toggle'):
                self.btn_theme_toggle.setText("Dark")
        else:
            if hasattr(self, 'btn_theme_toggle'):
                self.btn_theme_toggle.setText("Light")
    
    def _toggle_theme(self):
        """Toggle between dark and light themes."""
        self.theme_manager.toggle_theme()
        self.config.set("theme", self.theme_manager.current_theme.value)
        self.config.save()
    
    def _on_theme_changed(self, theme_mode: str):
        """Handle theme change."""
        self._apply_theme()
        logger.info(f"Theme changed to: {theme_mode}")
    
    def _load_data(self):
        """Load initial data."""
        try:
            # Load notebooks
            notebooks = self.notebook_controller.get_all_notebooks()
            for notebook in notebooks:
                btn = self._create_sidebar_button(notebook.name, "folder")
                btn.clicked.connect(lambda checked, nb_id=notebook.id: self._show_notebook_notes(nb_id))
                self.notebooks_layout.addWidget(btn)
            
            # Load all notes
            self._show_all_notes()
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load data:\n{str(e)}")
    
    # ===== NOTE DISPLAY METHODS =====
    
    def _show_all_notes(self):
        """Show all notes."""
        self.notes_title.setText("All Notes")
        notes = self.note_controller.get_all_notes()
        self._populate_notes_list(notes)
    
    def _show_recent(self):
        """Show recent notes."""
        self.notes_title.setText("Recent")
        notes = self.note_controller.get_all_notes()
        self._populate_notes_list(notes[:20])
    
    def _show_favorites(self):
        """Show favorite notes."""
        self.notes_title.setText("Favorites")
        notes = self.note_controller.get_favorite_notes()
        self._populate_notes_list(notes)
    
    def _show_trash(self):
        """Show deleted notes."""
        self.notes_title.setText("Trash")
        notes = self.note_controller.get_deleted_notes()
        self._populate_notes_list(notes)
    
    def _show_notebook_notes(self, notebook_id: str):
        """Show notes from specific notebook."""
        notebook = self.notebook_controller.get_notebook(notebook_id)
        if notebook:
            self.notes_title.setText(notebook.name)
            notes = self.note_controller.get_notes_by_notebook(notebook_id)
            self._populate_notes_list(notes)
    
    def _populate_notes_list(self, notes):
        """Populate notes list widget."""
        self.notes_list.clear()
        for note in notes:
            item = QListWidgetItem(note.title or "Untitled")
            item.setData(Qt.ItemDataRole.UserRole, note.id)
            
            preview = note.get_plain_text()[:100] if note.content else ""
            if preview:
                item.setToolTip(preview)
            
            self.notes_list.addItem(item)
    
    def _on_note_selected(self, item: QListWidgetItem):
        """Handle note selection."""
        note_id = item.data(Qt.ItemDataRole.UserRole)
        self._load_note(note_id)
    
    def _load_note(self, note_id: str):
        """Load note into editor."""
        try:
            if self.is_modified and self.current_note:
                self._save_current_note()
            
            note = self.note_controller.get_note(note_id)
            if note:
                self.current_note = note
                self.current_note_id = note_id
                
                self.editor_title.setText(note.title or "")
                content = note.get_plain_text()
                self.editor_content.setText(content)
                
                self.is_modified = False
                self._update_word_count()
                
                logger.info(f"Loaded note: {note_id}")
        
        except Exception as e:
            logger.error(f"Failed to load note: {e}")
            QMessageBox.warning(self, "Error", f"Failed to load note:\n{str(e)}")
    
    # ===== NOTE EDITING METHODS =====
    
    def _new_note(self):
        """Create a new note."""
        try:
            if self.is_modified and self.current_note:
                self._save_current_note()
            
            default_notebook = self.notebook_controller.get_default_notebook()
            note = self.note_controller.create_note(
                title="Untitled Note",
                content="",
                notebook_id=default_notebook.id if default_notebook else None
            )
            
            if note:
                self.current_note = note
                self.current_note_id = note.id
                self.editor_title.setText(note.title)
                self.editor_content.clear()
                self.is_modified = False
                
                self._show_all_notes()
                
                self.statusbar.showMessage(f"Created new note", 3000)
                logger.info(f"Created note: {note.id}")
            else:
                self.statusbar.showMessage("Failed to create note", 3000)
        
        except Exception as e:
            logger.error(f"Failed to create note: {e}")
            QMessageBox.warning(self, "Error", f"Failed to create note:\n{str(e)}")
    
    def _on_title_changed(self, text: str):
        """Handle title change."""
        self.is_modified = True
        self.autosave_label.setText("Unsaved changes...")
    
    def _on_content_changed(self):
        """Handle content change."""
        self.is_modified = True
        self.autosave_label.setText("Unsaved changes...")
        self._update_word_count()
    
    def _update_word_count(self):
        """Update word count label."""
        text = self.editor_content.toPlainText()
        words = len(text.split()) if text else 0
        self.word_count_label.setText(f"{words} words")
    
    def _auto_save(self):
        """Auto-save current note."""
        if self.is_modified and self.current_note:
            self._save_current_note()
    
    def _save_current_note(self):
        """Save current note."""
        try:
            if not self.current_note:
                return
            
            self.current_note.title = self.editor_title.text() or "Untitled"
            
            content = self.editor_content.toPlainText()
            self.current_note.set_content(content)
            
            self.current_note.updated_at = datetime.now()
            
            if self.note_controller.update_note(self.current_note):
                self.is_modified = False
                self.autosave_label.setText("All changes saved")
                
                for i in range(self.notes_list.count()):
                    item = self.notes_list.item(i)
                    if item.data(Qt.ItemDataRole.UserRole) == self.current_note.id:
                        item.setText(self.current_note.title)
                        break
                
                logger.info(f"Saved note: {self.current_note.id}")
            else:
                self.autosave_label.setText("Save failed!")
        
        except Exception as e:
            logger.error(f"Failed to save note: {e}", exc_info=True)
            self.autosave_label.setText(f"Save error!")
    
    def _on_search(self, query: str):
        """Handle search."""
        if not query:
            self._show_all_notes()
            return
        
        notes = self.note_controller.search_notes(query)
        self._populate_notes_list(notes)
    
    # ===== FORMATTING METHODS =====
    
    def _format_bold(self):
        """Apply bold formatting."""
        cursor = self.editor_content.textCursor()
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Weight.Bold if cursor.charFormat().fontWeight() != QFont.Weight.Bold else QFont.Weight.Normal)
        cursor.mergeCharFormat(fmt)
    
    def _format_italic(self):
        """Apply italic formatting."""
        cursor = self.editor_content.textCursor()
        fmt = QTextCharFormat()
        fmt.setFontItalic(not cursor.charFormat().fontItalic())
        cursor.mergeCharFormat(fmt)
    
    def _format_underline(self):
        """Apply underline formatting."""
        cursor = self.editor_content.textCursor()
        fmt = QTextCharFormat()
        fmt.setFontUnderline(not cursor.charFormat().fontUnderline())
        cursor.mergeCharFormat(fmt)
    
    def _insert_image(self):
        """Insert image into note."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg)"
        )
        
        if file_path:
            self.statusbar.showMessage("Image insertion coming soon...", 3000)
            logger.info(f"Image selected: {file_path}")
    
    # ===== SECURITY METHODS =====
    
    def _toggle_lock(self):
        """Toggle lock state."""
        if self.is_locked:
            self._unlock_application()
        else:
            self._lock_application()
    
    def _lock_application(self):
        """Lock the application."""
        if not self.is_locked:
            if self.is_modified and self.current_note:
                self._save_current_note()
            
            self.is_locked = True
            self.encryption_service.clear_cached_key()
            self.lock_action.setText("Unlock")
            self.statusbar.showMessage("Application locked")
            self.locked.emit()
            
            self.editor_title.clear()
            self.editor_content.clear()
            self.current_note = None
            self.current_note_id = None
            
            logger.info("Application locked")
    
    def _unlock_application(self):
        """Unlock the application."""
        self.is_locked = False
        self.lock_action.setText("Lock")
        self.statusbar.showMessage("Application unlocked")
        self.unlocked.emit()
        logger.info("Application unlocked")
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.is_modified and self.current_note:
            self._save_current_note()
        
        splitter_sizes = self.main_splitter.sizes()
        if len(splitter_sizes) >= 2:
            self.config.set("sidebar_width", splitter_sizes[0])
            self.config.set("notes_panel_width", splitter_sizes[1])
        self.config.save()
        
        self.encryption_service.clear_cached_key()
        
        logger.info("Application closing")
        event.accept()