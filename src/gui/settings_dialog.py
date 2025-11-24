from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QCheckBox,
                             QComboBox, QSpinBox, QMessageBox, QTabWidget,
                             QWidget, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class SettingsDialog(QDialog):
    """Settings dialog for TMapp customization."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("TMapp Settings")
        self.setFixedSize(500, 600)
        
        self.init_ui()
        self.apply_style()
        
        # Center on parent
        if parent:
            self.move(parent.geometry().center() - self.rect().center())
    
    def init_ui(self):
        """Setup settings UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Tab widget for different settings categories
        tabs = QTabWidget()
        
        # General settings
        general_tab = self.create_general_tab()
        tabs.addTab(general_tab, "General")
        
        # Editor settings
        editor_tab = self.create_editor_tab()
        tabs.addTab(editor_tab, "Editor")
        
        # Security settings
        security_tab = self.create_security_tab()
        tabs.addTab(security_tab, "Security")
        
        # Appearance settings
        appearance_tab = self.create_appearance_tab()
        tabs.addTab(appearance_tab, "Appearance")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def create_general_tab(self):
        """Create general settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Auto-save settings
        auto_save_group = QGroupBox("Auto-Save")
        auto_save_layout = QFormLayout(auto_save_group)
        
        self.auto_save_enabled = QCheckBox("Enable auto-save")
        self.auto_save_enabled.setChecked(True)
        auto_save_layout.addRow(self.auto_save_enabled)
        
        self.auto_save_interval = QSpinBox()
        self.auto_save_interval.setRange(10, 300)
        self.auto_save_interval.setValue(30)
        self.auto_save_interval.setSuffix(" seconds")
        auto_save_layout.addRow("Auto-save interval:", self.auto_save_interval)
        
        layout.addWidget(auto_save_group)
        
        # Startup settings
        startup_group = QGroupBox("Startup")
        startup_layout = QFormLayout(startup_group)
        
        self.load_last_note = QCheckBox("Load last opened note on startup")
        self.load_last_note.setChecked(True)
        startup_layout.addRow(self.load_last_note)
        
        layout.addWidget(startup_group)
        
        layout.addStretch()
        return widget
    
    def create_editor_tab(self):
        """Create editor settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Font settings
        font_group = QGroupBox("Font")
        font_layout = QFormLayout(font_group)
        
        self.font_family = QComboBox()
        self.font_family.addItems([
            "JetBrains Mono", "Consolas", "Monaco", "Fira Code", 
            "Source Code Pro", "Cascadia Code", "Roboto Mono"
        ])
        self.font_family.setCurrentText("JetBrains Mono")
        font_layout.addRow("Font family:", self.font_family)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(14)
        self.font_size.setSuffix(" pt")
        font_layout.addRow("Font size:", self.font_size)
        
        layout.addWidget(font_group)
        
        # Editor behavior
        behavior_group = QGroupBox("Behavior")
        behavior_layout = QFormLayout(behavior_group)
        
        self.word_wrap = QCheckBox("Word wrap")
        self.word_wrap.setChecked(True)
        behavior_layout.addRow(self.word_wrap)
        
        self.show_line_numbers = QCheckBox("Show line numbers")
        self.show_line_numbers.setChecked(False)
        behavior_layout.addRow(self.show_line_numbers)
        
        self.highlight_current_line = QCheckBox("Highlight current line")
        self.highlight_current_line.setChecked(True)
        behavior_layout.addRow(self.highlight_current_line)
        
        layout.addWidget(behavior_group)
        
        # Markdown settings
        markdown_group = QGroupBox("Markdown")
        markdown_layout = QFormLayout(markdown_group)
        
        self.auto_preview = QCheckBox("Auto-update preview")
        self.auto_preview.setChecked(True)
        markdown_layout.addRow(self.auto_preview)
        
        self.syntax_highlighting = QCheckBox("Syntax highlighting")
        self.syntax_highlighting.setChecked(True)
        markdown_layout.addRow(self.syntax_highlighting)
        
        layout.addWidget(markdown_group)
        
        layout.addStretch()
        return widget
    
    def create_security_tab(self):
        """Create security settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Password settings
        password_group = QGroupBox("Password")
        password_layout = QFormLayout(password_group)
        
        change_password_btn = QPushButton("Change Master Password")
        change_password_btn.clicked.connect(self.change_password)
        password_layout.addRow(change_password_btn)
        
        layout.addWidget(password_group)
        
        # Session settings
        session_group = QGroupBox("Session")
        session_layout = QFormLayout(session_group)
        
        self.auto_lock = QCheckBox("Auto-lock after inactivity")
        self.auto_lock.setChecked(False)
        session_layout.addRow(self.auto_lock)
        
        self.lock_timeout = QSpinBox()
        self.lock_timeout.setRange(1, 60)
        self.lock_timeout.setValue(10)
        self.lock_timeout.setSuffix(" minutes")
        session_layout.addRow("Lock timeout:", self.lock_timeout)
        
        layout.addWidget(session_group)
        
        # Data management
        data_group = QGroupBox("Data Management")
        data_layout = QVBoxLayout(data_group)
        
        export_data_btn = QPushButton("Export All Notes")
        export_data_btn.clicked.connect(self.export_all_notes)
        data_layout.addWidget(export_data_btn)
        
        import_data_btn = QPushButton("Import Notes")
        import_data_btn.clicked.connect(self.import_notes)
        data_layout.addWidget(import_data_btn)
        
        clear_data_btn = QPushButton("Clear All Data")
        clear_data_btn.setStyleSheet("QPushButton { color: #f38ba8; }")
        clear_data_btn.clicked.connect(self.clear_all_data)
        data_layout.addWidget(clear_data_btn)
        
        layout.addWidget(data_group)
        
        layout.addStretch()
        return widget
    
    def create_appearance_tab(self):
        """Create appearance settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Theme settings
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout(theme_group)
        
        self.theme = QComboBox()
        self.theme.addItems(["Dark", "Light", "Auto"])
        self.theme.setCurrentText("Dark")
        theme_layout.addRow("Theme:", self.theme)
        
        layout.addWidget(theme_group)
        
        # UI customization
        ui_group = QGroupBox("Interface")
        ui_layout = QFormLayout(ui_group)
        
        self.show_toolbar = QCheckBox("Show toolbar")
        self.show_toolbar.setChecked(True)
        ui_layout.addRow(self.show_toolbar)
        
        self.show_status_bar = QCheckBox("Show status bar")
        self.show_status_bar.setChecked(True)
        ui_layout.addRow(self.show_status_bar)
        
        self.sidebar_width = QSpinBox()
        self.sidebar_width.setRange(200, 400)
        self.sidebar_width.setValue(280)
        self.sidebar_width.setSuffix(" px")
        ui_layout.addRow("Sidebar width:", self.sidebar_width)
        
        layout.addWidget(ui_group)
        
        layout.addStretch()
        return widget
    
    def change_password(self):
        """Handle password change."""
        QMessageBox.information(self, "Change Password", 
                               "Password change functionality will be implemented in a future update.")
    
    def export_all_notes(self):
        """Export all notes."""
        QMessageBox.information(self, "Export", 
                               "Export functionality will be implemented in a future update.")
    
    def import_notes(self):
        """Import notes."""
        QMessageBox.information(self, "Import", 
                               "Import functionality will be implemented in a future update.")
    
    def clear_all_data(self):
        """Clear all data with confirmation."""
        reply = QMessageBox.question(
            self, "Clear All Data",
            "Are you sure you want to delete all notes and settings?\n\nThis action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Clear Data", 
                                   "Data clearing functionality will be implemented in a future update.")
    
    def save_settings(self):
        """Save settings."""
        # Here you would save settings to a config file
        QMessageBox.information(self, "Settings", "Settings saved successfully!")
        self.accept()
    
    def apply_style(self):
        """Apply modern styling to dialog."""
        self.setStyleSheet("""
        QDialog {
            background-color: #0f172a;
            color: #f1f5f9;
        }
        
        QTabWidget::pane {
            border: 1px solid #334155;
            background-color: #1e293b;
        }
        
        QTabBar::tab {
            background-color: #334155;
            color: #cbd5e1;
            padding: 8px 16px;
            margin-right: 2px;
            border-radius: 4px 4px 0 0;
        }
        
        QTabBar::tab:selected {
            background-color: #7c3aed;
            color: white;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #334155;
            border-radius: 8px;
            margin-top: 1ex;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #89b4fa;
        }
        
        QLineEdit, QComboBox, QSpinBox {
            background-color: #1e293b;
            border: 2px solid #334155;
            border-radius: 6px;
            padding: 6px 8px;
            color: #f1f5f9;
        }
        
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
            border-color: #7c3aed;
        }
        
        QPushButton {
            background-color: #7c3aed;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #8b5cf6;
        }
        
        QPushButton:pressed {
            background-color: #6d28d9;
        }
        
        QCheckBox {
            color: #cbd5e1;
        }
        
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border-radius: 3px;
            border: 2px solid #334155;
            background-color: #1e293b;
        }
        
        QCheckBox::indicator:checked {
            background-color: #7c3aed;
            border-color: #7c3aed;
        }
        
        QLabel {
            color: #cbd5e1;
        }
        """)