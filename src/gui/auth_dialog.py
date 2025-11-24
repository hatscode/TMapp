from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QProgressBar,
                             QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap

class AuthDialog(QDialog):
    """Modern authentication dialog with security features."""
    
    password_entered = pyqtSignal(str)
    
    def __init__(self, auth_manager, parent=None):
        super().__init__(parent)
        self.auth_manager = auth_manager
        self.password = None
        self.failed_attempts = 0
        
        self.setWindowTitle("TMapp Authentication")
        self.setFixedSize(400, 500)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        
        self.init_ui()
        self.apply_style()
        
        # Center on parent
        if parent:
            self.move(parent.geometry().center() - self.rect().center())
    
    def init_ui(self):
        """Setup authentication UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Logo/Title area
        title_frame = QFrame()
        title_layout = QVBoxLayout(title_frame)
        
        # App icon
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setText("🛡️")
        title_layout.addWidget(icon_label)
        
        # App title
        title_label = QLabel("TMapp")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        
        # Subtitle
        subtitle = QLabel("Secure Note-Taking Application")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #7c3aed; font-size: 12px;")
        title_layout.addWidget(subtitle)
        
        layout.addWidget(title_frame)
        
        # Authentication form
        if self.auth_manager.is_first_run():
            self.create_setup_form(layout)
        else:
            self.create_login_form(layout)
    
    def create_setup_form(self, layout):
        """Create password setup form for first run."""
        info_label = QLabel("Create your master password to secure your notes")
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # Password requirements
        req_frame = QFrame()
        req_frame.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        req_layout = QVBoxLayout(req_frame)
        
        req_title = QLabel("Password Requirements:")
        req_title.setStyleSheet("font-weight: bold; color: #f1f5f9;")
        req_layout.addWidget(req_title)
        
        requirements = [
            "• At least 12 characters",
            "• Uppercase and lowercase letters", 
            "• Numbers and special characters"
        ]
        
        for req in requirements:
            req_label = QLabel(req)
            req_label.setStyleSheet("color: #cbd5e1; font-size: 11px;")
            req_layout.addWidget(req_label)
        
        layout.addWidget(req_frame)
        
        # Password inputs
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setMinimumHeight(40)
        layout.addWidget(self.password_input)
        
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setPlaceholderText("Confirm password")
        self.confirm_input.setMinimumHeight(40)
        layout.addWidget(self.confirm_input)
        
        # Show password checkbox
        self.show_password = QCheckBox("Show password")
        self.show_password.toggled.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password)
        
        # Create button
        self.create_btn = QPushButton("Create Password")
        self.create_btn.setMinimumHeight(45)
        self.create_btn.clicked.connect(self.setup_password)
        layout.addWidget(self.create_btn)
        
        # Connect Enter key
        self.confirm_input.returnPressed.connect(self.setup_password)
    
    def create_login_form(self, layout):
        """Create login form for existing users."""
        info_label = QLabel("Enter your master password")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Master password")
        self.password_input.setMinimumHeight(40)
        self.password_input.textChanged.connect(self.on_password_changed)
        layout.addWidget(self.password_input)
        
        # Show password checkbox
        self.show_password = QCheckBox("Show password")
        self.show_password.toggled.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password)
        
        # Login button
        self.login_btn = QPushButton("Unlock")
        self.login_btn.setMinimumHeight(45)
        self.login_btn.clicked.connect(self.verify_password)
        self.login_btn.setEnabled(False)
        layout.addWidget(self.login_btn)
        
        # Failed attempts indicator
        self.attempts_label = QLabel("")
        self.attempts_label.setAlignment(Qt.AlignCenter)
        self.attempts_label.setStyleSheet("color: #ef4444;")
        layout.addWidget(self.attempts_label)
        
        # Connect Enter key
        self.password_input.returnPressed.connect(self.verify_password)
        
        # Focus password input
        self.password_input.setFocus()
    
    def setup_password(self):
        """Handle password setup."""
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
        
        success, message = self.auth_manager.setup_password(password)
        if success:
            self.password = password
            self.accept()
        else:
            QMessageBox.warning(self, "Error", message)
    
    def verify_password(self):
        """Handle password verification."""
        if not self.login_btn.isEnabled():
            return
            
        password = self.password_input.text()
        success, message = self.auth_manager.verify_password(password)
        
        if success:
            self.password = password
            self.accept()
        else:
            self.failed_attempts += 1
            self.attempts_label.setText(message)
            self.password_input.clear()
            self.password_input.setFocus()
            
            # Shake animation for failed attempts
            self.shake_animation()
    
    def on_password_changed(self):
        """Enable/disable login button based on input."""
        has_password = bool(self.password_input.text().strip())
        self.login_btn.setEnabled(has_password)
    
    def toggle_password_visibility(self, checked):
        """Toggle password visibility."""
        mode = QLineEdit.Normal if checked else QLineEdit.Password
        self.password_input.setEchoMode(mode)
        if hasattr(self, 'confirm_input'):
            self.confirm_input.setEchoMode(mode)
    
    def shake_animation(self):
        """Simple shake animation for failed login."""
        original_pos = self.pos()
        for i in range(5):
            QTimer.singleShot(i * 50, lambda: self.move(original_pos.x() + (10 if i % 2 else -10), original_pos.y()))
        QTimer.singleShot(250, lambda: self.move(original_pos))
    
    def get_password(self) -> str:
        """Return entered password."""
        return self.password
    
    def apply_style(self):
        """Apply modern styling to dialog."""
        self.setStyleSheet("""
        QDialog {
            background-color: #0f172a;
            color: #f1f5f9;
        }
        
        QLineEdit {
            background-color: #1e293b;
            border: 2px solid #334155;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
            color: #f1f5f9;
        }
        
        QLineEdit:focus {
            border-color: #7c3aed;
        }
        
        QPushButton {
            background-color: #7c3aed;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            font-size: 14px;
        }
        
        QPushButton:hover {
            background-color: #8b5cf6;
        }
        
        QPushButton:pressed {
            background-color: #6d28d9;
        }
        
        QPushButton:disabled {
            background-color: #334155;
            color: #64748b;
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
        """)