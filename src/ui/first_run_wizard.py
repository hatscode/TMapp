"""First-run wizard for TMapp password setup."""
import logging
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QCheckBox, QProgressBar, 
                              QFrame, QWidget, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

logger = logging.getLogger(__name__)


class FirstRunWizard(QDialog):
    """
    Single-window password setup dialog for first-time users.
    Creates master password with comprehensive security requirements.
    """
    
    wizard_completed = pyqtSignal(str)  # Emits master password
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.password_valid = False
        self.requirements_met = {
            'length': False,
            'uppercase': False,
            'lowercase': False,
            'digit': False,
            'special': False
        }
        
        self._setup_ui()
        self._apply_theme()
        
        # Make dialog modal
        self.setModal(True)
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.CustomizeWindowHint | 
            Qt.WindowType.WindowTitleHint
        )
        
        # Disable close button - user must complete setup
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
        
        logger.info("First-run wizard initialized")
    
    def _setup_ui(self):
        """Create the password setup UI."""
        self.setWindowTitle("TMapp - Setup")
        self.setMinimumSize(550, 580)
        self.setMaximumSize(550, 580)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(40, 30, 40, 30)
        
        # ===== HEADER =====
        # Logo/Icon
        logo = QLabel("🔐")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("font-size: 56px; margin: 8px;")
        
        # Title
        title = QLabel("Welcome to TMapp")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        
        # Subtitle
        subtitle = QLabel("Create your master password to secure your notes")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setWordWrap(True)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setObjectName("separator")
        
        # ===== PASSWORD INPUT =====
        password_label = QLabel("Master Password:")
        password_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        
        password_container = QHBoxLayout()
        password_container.setSpacing(8)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password (12+ characters)")
        self.password_input.setFont(QFont("Segoe UI", 12))
        self.password_input.setMinimumHeight(44)
        self.password_input.textChanged.connect(self._validate_password)
        
        self.toggle_password_btn = QPushButton("👁️")
        self.toggle_password_btn.setObjectName("toggle_btn")
        self.toggle_password_btn.setFixedSize(44, 44)
        self.toggle_password_btn.setToolTip("Show/hide password")
        self.toggle_password_btn.clicked.connect(self._toggle_password_visibility)
        
        password_container.addWidget(self.password_input)
        password_container.addWidget(self.toggle_password_btn)
        
        # ===== PASSWORD STRENGTH =====
        strength_layout = QHBoxLayout()
        
        self.strength_bar = QProgressBar()
        self.strength_bar.setMaximum(100)
        self.strength_bar.setValue(0)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setMaximumHeight(6)
        
        self.strength_text = QLabel("Weak")
        self.strength_text.setObjectName("strength_text")
        self.strength_text.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.strength_text.setMinimumWidth(70)
        
        strength_layout.addWidget(self.strength_bar, 1)
        strength_layout.addWidget(self.strength_text)
        
        # ===== REQUIREMENTS CHECKLIST =====
        requirements_grid = QGridLayout()
        requirements_grid.setSpacing(6)
        requirements_grid.setContentsMargins(0, 0, 0, 0)
        
        self.req_length = self._create_requirement_label("12+ characters")
        self.req_uppercase = self._create_requirement_label("Uppercase")
        self.req_lowercase = self._create_requirement_label("Lowercase")
        self.req_digit = self._create_requirement_label("Numbers")
        self.req_special = self._create_requirement_label("Special (!@#$)")
        
        # Add to grid (row, column)
        requirements_grid.addWidget(self.req_length, 0, 0)
        requirements_grid.addWidget(self.req_digit, 0, 1)
        requirements_grid.addWidget(self.req_uppercase, 1, 0)
        requirements_grid.addWidget(self.req_special, 1, 1)
        requirements_grid.addWidget(self.req_lowercase, 2, 0)
        
        # ===== CONFIRM PASSWORD =====
        confirm_label = QLabel("Confirm Password:")
        confirm_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        
        confirm_container = QHBoxLayout()
        confirm_container.setSpacing(8)
        
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setPlaceholderText("Re-enter password")
        self.confirm_input.setFont(QFont("Segoe UI", 12))
        self.confirm_input.setMinimumHeight(44)
        self.confirm_input.textChanged.connect(self._validate_confirmation)
        
        self.toggle_confirm_btn = QPushButton("👁️")
        self.toggle_confirm_btn.setObjectName("toggle_btn")
        self.toggle_confirm_btn.setFixedSize(44, 44)
        self.toggle_confirm_btn.setToolTip("Show/hide password")
        self.toggle_confirm_btn.clicked.connect(self._toggle_confirm_visibility)
        
        confirm_container.addWidget(self.confirm_input)
        confirm_container.addWidget(self.toggle_confirm_btn)
        
        # Match indicator
        self.match_label = QLabel("")
        self.match_label.setObjectName("match_label")
        self.match_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.match_label.setFont(QFont("Segoe UI", 10))
        
        # ===== ACKNOWLEDGMENT =====
        self.acknowledge_cb = QCheckBox("I understand this password cannot be recovered if lost")
        self.acknowledge_cb.setFont(QFont("Segoe UI", 10))
        self.acknowledge_cb.stateChanged.connect(self._update_continue_button)
        
        # ===== CONTINUE BUTTON =====
        self.continue_btn = QPushButton("Continue")
        self.continue_btn.setObjectName("continue_btn")
        self.continue_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.continue_btn.setMinimumHeight(44)
        self.continue_btn.setEnabled(False)
        self.continue_btn.clicked.connect(self._on_continue)
        
        # ===== ASSEMBLE LAYOUT =====
        main_layout.addWidget(logo)
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addWidget(separator)
        main_layout.addSpacing(8)
        main_layout.addWidget(password_label)
        main_layout.addLayout(password_container)
        main_layout.addLayout(strength_layout)
        main_layout.addSpacing(4)
        main_layout.addLayout(requirements_grid)
        main_layout.addSpacing(12)
        main_layout.addWidget(confirm_label)
        main_layout.addLayout(confirm_container)
        main_layout.addWidget(self.match_label)
        main_layout.addSpacing(8)
        main_layout.addWidget(self.acknowledge_cb)
        main_layout.addSpacing(12)
        main_layout.addWidget(self.continue_btn)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def _create_requirement_label(self, text: str) -> QLabel:
        """Create a requirement label with checkbox icon."""
        label = QLabel(f"○ {text}")
        label.setObjectName("requirement")
        label.setFont(QFont("Segoe UI", 9))
        label.setMinimumHeight(20)
        return label
    
    def _validate_password(self, password: str):
        """Validate password and update UI."""
        # Check requirements
        self.requirements_met['length'] = len(password) >= 12
        self.requirements_met['uppercase'] = any(c.isupper() for c in password)
        self.requirements_met['lowercase'] = any(c.islower() for c in password)
        self.requirements_met['digit'] = any(c.isdigit() for c in password)
        self.requirements_met['special'] = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?/~`" for c in password)
        
        # Update requirement labels
        self._update_requirement_label(self.req_length, self.requirements_met['length'])
        self._update_requirement_label(self.req_uppercase, self.requirements_met['uppercase'])
        self._update_requirement_label(self.req_lowercase, self.requirements_met['lowercase'])
        self._update_requirement_label(self.req_digit, self.requirements_met['digit'])
        self._update_requirement_label(self.req_special, self.requirements_met['special'])
        
        # Calculate strength
        strength = self._calculate_strength(password)
        self.strength_bar.setValue(strength)
        
        # Update strength indicator
        if strength < 40:
            self.strength_text.setText("Weak")
            self.strength_text.setStyleSheet("color: #DC2626;")
            self.strength_bar.setStyleSheet("QProgressBar::chunk { background-color: #DC2626; }")
        elif strength < 60:
            self.strength_text.setText("Fair")
            self.strength_text.setStyleSheet("color: #F59E0B;")
            self.strength_bar.setStyleSheet("QProgressBar::chunk { background-color: #F59E0B; }")
        elif strength < 80:
            self.strength_text.setText("Good")
            self.strength_text.setStyleSheet("color: #FBBF24;")
            self.strength_bar.setStyleSheet("QProgressBar::chunk { background-color: #FBBF24; }")
        elif strength < 90:
            self.strength_text.setText("Strong")
            self.strength_text.setStyleSheet("color: #10B981;")
            self.strength_bar.setStyleSheet("QProgressBar::chunk { background-color: #10B981; }")
        else:
            self.strength_text.setText("Excellent")
            self.strength_text.setStyleSheet("color: #3B82F6;")
            self.strength_bar.setStyleSheet("QProgressBar::chunk { background-color: #3B82F6; }")
        
        # Check if all requirements met
        self.password_valid = all(self.requirements_met.values())
        
        # Validate confirmation
        self._validate_confirmation(self.confirm_input.text())
        
        # Update continue button
        self._update_continue_button()
    
    def _update_requirement_label(self, label: QLabel, met: bool):
        """Update requirement label appearance."""
        text = label.text()[2:]  # Remove icon
        if met:
            label.setText(f"✓ {text}")
            label.setStyleSheet("color: #10B981;")
        else:
            label.setText(f"○ {text}")
            label.setStyleSheet("color: #6B7280;")
    
    def _calculate_strength(self, password: str) -> int:
        """Calculate password strength (0-100)."""
        if not password:
            return 0
        
        strength = 0
        
        # Length scoring
        if len(password) >= 8:
            strength += 15
        if len(password) >= 12:
            strength += 20
        if len(password) >= 16:
            strength += 15
        if len(password) >= 20:
            strength += 10
        
        # Character variety
        if any(c.islower() for c in password):
            strength += 10
        if any(c.isupper() for c in password):
            strength += 10
        if any(c.isdigit() for c in password):
            strength += 10
        if any(not c.isalnum() for c in password):
            strength += 10
        
        return min(strength, 100)
    
    def _validate_confirmation(self, confirm_password: str):
        """Validate password confirmation."""
        password = self.password_input.text()
        
        if not confirm_password:
            self.match_label.setText("")
            return
        
        if password == confirm_password:
            self.match_label.setText("✓ Passwords match")
            self.match_label.setStyleSheet("color: #10B981;")
        else:
            self.match_label.setText("✗ Passwords do not match")
            self.match_label.setStyleSheet("color: #DC2626;")
        
        self._update_continue_button()
    
    def _update_continue_button(self):
        """Update continue button enabled state."""
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        can_continue = (
            self.password_valid and 
            password == confirm and 
            len(confirm) > 0 and
            self.acknowledge_cb.isChecked()
        )
        
        self.continue_btn.setEnabled(can_continue)
    
    def _toggle_password_visibility(self):
        """Toggle master password visibility."""
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
    
    def _toggle_confirm_visibility(self):
        """Toggle confirm password visibility."""
        if self.confirm_input.echoMode() == QLineEdit.EchoMode.Password:
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
    
    def _on_continue(self):
        """Handle continue button click."""
        password = self.password_input.text()
        
        # Final validation
        if not self.password_valid:
            return
        
        if password != self.confirm_input.text():
            return
        
        if not self.acknowledge_cb.isChecked():
            return
        
        logger.info("Password setup completed")
        self.wizard_completed.emit(password)
        self.accept()
    
    def closeEvent(self, event):
        """Prevent closing dialog without completing setup."""
        event.ignore()
    
    def field(self, name: str) -> str:
        """Get field value (for compatibility with QWizard API)."""
        if name == "password":
            return self.password_input.text()
        return ""
    
    def _apply_theme(self):
        """Apply dark theme to wizard."""
        stylesheet = """
        QDialog {
            background-color: #0D1117;
        }
        
        QLabel {
            color: #F0F6FC;
        }
        
        QLabel#subtitle {
            color: #8B949E;
        }
        
        QLabel#requirement {
            padding: 2px 8px;
        }
        
        QLabel#match_label {
            padding: 4px;
            margin-top: 4px;
        }
        
        QFrame#separator {
            color: #30363D;
        }
        
        QLineEdit {
            background-color: #161B22;
            color: #F0F6FC;
            border: 2px solid #30363D;
            border-radius: 8px;
            padding: 10px 14px;
        }
        
        QLineEdit:focus {
            border-color: #2563EB;
        }
        
        QPushButton#toggle_btn {
            background-color: #161B22;
            border: 2px solid #30363D;
            border-radius: 8px;
            font-size: 20px;
        }
        
        QPushButton#toggle_btn:hover {
            background-color: #21262D;
            border-color: #2563EB;
        }
        
        QProgressBar {
            border: 1px solid #30363D;
            border-radius: 3px;
            background-color: #161B22;
        }
        
        QProgressBar::chunk {
            border-radius: 2px;
        }
        
        QCheckBox {
            color: #F0F6FC;
            spacing: 8px;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #30363D;
            border-radius: 4px;
            background-color: #161B22;
        }
        
        QCheckBox::indicator:checked {
            background-color: #2563EB;
            border-color: #2563EB;
        }
        
        QPushButton#continue_btn {
            background-color: #2563EB;
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            padding: 10px 32px;
        }
        
        QPushButton#continue_btn:hover {
            background-color: #3973f7;
        }
        
        QPushButton#continue_btn:pressed {
            background-color: #1746a2;
        }
        
        QPushButton#continue_btn:disabled {
            background-color: #2D333B;
            color: #6E7681;
        }
        """
        
        self.setStyleSheet(stylesheet)