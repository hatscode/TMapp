from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QListWidget, QListWidgetItem, QLabel,
                             QFrame, QMenu)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon
from datetime import datetime

class SidebarWidget(QWidget):
    """
    Modern sidebar with note list and search.
    Security Controls: Displays encrypted note titles safely
    """
    
    note_selected = pyqtSignal(str)  # Emits note ID
    new_note_requested = pyqtSignal()
    delete_note_requested = pyqtSignal(str)
    
    def __init__(self, note_manager, parent=None):
        super().__init__(parent)
        self.note_manager = note_manager
        self.notes_cache = []
        
        self.init_ui()
        self.apply_style()
    
    def init_ui(self):
        """Setup sidebar UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header with app branding
        header = self.create_header()
        layout.addWidget(header)
        
        # Search bar
        search_container = QFrame()
        search_container.setObjectName("searchContainer")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(12, 12, 12, 12)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search notes...")
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_input)
        
        layout.addWidget(search_container)
        
        # Quick filters
        filters = self.create_filters()
        layout.addWidget(filters)
        
        # Notes list
        self.notes_list = QListWidget()
        self.notes_list.setObjectName("notesList")
        self.notes_list.itemClicked.connect(self.on_note_clicked)
        self.notes_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.notes_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.notes_list)
        
        # New note button
        new_note_btn = QPushButton("+ New Note")
        new_note_btn.setObjectName("newNoteBtn")
        new_note_btn.clicked.connect(self.new_note_requested.emit)
        new_note_btn.setMinimumHeight(45)
        layout.addWidget(new_note_btn)
    
    def create_header(self) -> QFrame:
        """Create sidebar header with branding."""
        header = QFrame()
        header.setObjectName("sidebarHeader")
        header.setFixedHeight(60)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 12, 16, 12)
        
        # App icon and title
        title_label = QLabel("📝 TMapp")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Settings button (placeholder)
        settings_btn = QPushButton("⚙️")
        settings_btn.setFixedSize(32, 32)
        settings_btn.setObjectName("iconButton")
        layout.addWidget(settings_btn)
        
        return header
    
    def create_filters(self) -> QFrame:
        """Create quick filter buttons."""
        filters = QFrame()
        filters.setObjectName("filtersContainer")
        
        layout = QHBoxLayout(filters)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)
        
        filter_buttons = [
            ("📄 All", True),
            ("⭐ Favorites", False),
            ("🕒 Recent", False)
        ]
        
        for text, default in filter_buttons:
            btn = QPushButton(text)
            btn.setObjectName("filterButton")
            btn.setCheckable(True)
            btn.setChecked(default)
            btn.setMinimumHeight(32)
            layout.addWidget(btn)
        
        return filters
    
    def refresh_notes(self):
        """Refresh the notes list from database."""
        self.notes_list.clear()
        self.notes_cache = self.note_manager.list_notes()
        
        for note in self.notes_cache:
            self.add_note_item(note)
    
    def add_note_item(self, note: dict):
        """Add a note item to the list."""
        item = QListWidgetItem()
        
        # Create custom widget for note item
        widget = self.create_note_item_widget(note)
        
        item.setSizeHint(widget.sizeHint())
        item.setData(Qt.UserRole, note['id'])
        
        self.notes_list.addItem(item)
        self.notes_list.setItemWidget(item, widget)
    
    def create_note_item_widget(self, note: dict) -> QWidget:
        """Create custom widget for note list item."""
        widget = QFrame()
        widget.setObjectName("noteItem")
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # Title
        title_label = QLabel(note['title'] or "Untitled")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setWordWrap(False)
        layout.addWidget(title_label)
        
        # Timestamp
        updated_time = self.format_timestamp(note['updated_at'])
        time_label = QLabel(updated_time)
        time_label.setObjectName("timestampLabel")
        layout.addWidget(time_label)
        
        return widget
    
    def format_timestamp(self, timestamp_str: str) -> str:
        """Format timestamp to human-readable format."""
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            now = datetime.now()
            
            diff = now - dt
            
            if diff.days == 0:
                if diff.seconds < 3600:
                    mins = diff.seconds // 60
                    return f"{mins} min ago" if mins > 0 else "Just now"
                else:
                    hours = diff.seconds // 3600
                    return f"{hours}h ago"
            elif diff.days == 1:
                return "Yesterday"
            elif diff.days < 7:
                return f"{diff.days} days ago"
            else:
                return dt.strftime("%b %d, %Y")
        except:
            return "Unknown"
    
    def on_note_clicked(self, item: QListWidgetItem):
        """Handle note item click."""
        note_id = item.data(Qt.UserRole)
        if note_id:
            self.note_selected.emit(note_id)
    
    def on_search(self, text: str):
        """Handle search input."""
        if not text.strip():
            self.refresh_notes()
            return
        
        # Search notes
        results = self.note_manager.search_notes(text)
        
        self.notes_list.clear()
        for note in results:
            self.add_note_item(note)
    
    def show_context_menu(self, position):
        """Show context menu for note items."""
        item = self.notes_list.itemAt(position)
        if not item:
            return
        
        note_id = item.data(Qt.UserRole)
        
        menu = QMenu(self)
        delete_action = menu.addAction("🗑️ Delete")
        
        action = menu.exec_(self.notes_list.mapToGlobal(position))
        
        if action == delete_action:
            self.delete_note_requested.emit(note_id)
    
    def select_note(self, note_id: str):
        """Select a note in the list."""
        for i in range(self.notes_list.count()):
            item = self.notes_list.item(i)
            if item.data(Qt.UserRole) == note_id:
                self.notes_list.setCurrentItem(item)
                break
    
    def apply_style(self):
        """Apply modern styling to sidebar."""
        self.setStyleSheet("""
        QWidget {
            background-color: #181825;
            color: #cdd6f4;
        }
        
        #sidebarHeader {
            background-color: #1e1e2e;
            border-bottom: 1px solid #313244;
        }
        
        #searchContainer {
            background-color: #181825;
            border-bottom: 1px solid #313244;
        }
        
        QLineEdit {
            background-color: #1e1e2e;
            border: 2px solid #313244;
            border-radius: 8px;
            padding: 8px 12px;
            color: #cdd6f4;
            font-size: 13px;
        }
        
        QLineEdit:focus {
            border-color: #7c3aed;
        }
        
        #filtersContainer {
            background-color: #181825;
            border-bottom: 1px solid #313244;
        }
        
        #filterButton {
            background-color: transparent;
            border: 1px solid #313244;
            border-radius: 6px;
            padding: 4px 12px;
            color: #a6adc8;
            font-size: 11px;
        }
        
        #filterButton:checked {
            background-color: #7c3aed;
            border-color: #7c3aed;
            color: white;
        }
        
        #filterButton:hover {
            background-color: #313244;
        }
        
        #notesList {
            background-color: #181825;
            border: none;
            outline: none;
        }
        
        #notesList::item {
            background-color: transparent;
            border-bottom: 1px solid #313244;
        }
        
        #notesList::item:selected {
            background-color: #313244;
        }
        
        #notesList::item:hover {
            background-color: #1e1e2e;
        }
        
        #noteItem {
            background-color: transparent;
        }
        
        #timestampLabel {
            color: #585b70;
            font-size: 10px;
        }
        
        #newNoteBtn {
            background-color: #7c3aed;
            color: white;
            border: none;
            border-radius: 0;
            font-weight: bold;
            font-size: 14px;
        }
        
        #newNoteBtn:hover {
            background-color: #8b5cf6;
        }
        
        #newNoteBtn:pressed {
            background-color: #6d28d9;
        }
        
        #iconButton {
            background-color: transparent;
            border: none;
            border-radius: 6px;
            font-size: 16px;
        }
        
        #iconButton:hover {
            background-color: #313244;
        }
        """)