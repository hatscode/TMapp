from PyQt6.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
                              QLabel, QLineEdit, QPushButton, QTextEdit, 
                              QCheckBox, QProgressBar, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
import logging

logger = logging.getLogger(__name__)

class WelcomePage(QWizardPage):
    """Welcome page of the setup wizard."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Welcome to TMapp")
        self.setSubTitle("Secure, encrypted note-taking for your peace of mind")
        
        layout = QVBoxLayout()
        
        # Welcome message
        welcome_text = QLabel(
            "<h2>🔐 Welcome to TMapp</h2>"
            "<p>TMapp is a secure, privacy-focused note-taking application that uses "
            "military-grade encryption to protect your notes.</p>"
            "<p><b>Key Features:</b></p>"
            "<ul>"
            "<li>🔒 AES-256-GCM encryption for all your notes</li>"
            "<li>🛡️ Argon2id password hashing (OWASP recommended)</li>"
            "<li>📝 Markdown support with live preview</li>"
            "<li>🏷️ Tags and notebooks for organization</li>"
            "<li>🔍 Powerful search across all notes</li>"
            "<li>💾 Automatic encrypted backups</li>"
            "</ul>"
            "<p>Let's get started by creating your master password!</p>"
        )
        welcome_text.setWordWrap(True)
        layout.addWidget(welcome_text)
        
        layout.addStretch()
        self.setLayout(layout)


class SecurityExplanationPage(QWizardPage):
    """Explain the security model."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Understanding TMapp Security")
        self.setSubTitle("How we protect your data")
        
        layout = QVBoxLayout()
        
        # Security explanation
        security_text = QTextEdit()
        security_text.setReadOnly(True)
        security_text.setHtml(
            "<h3>🛡️ Your Security, Explained</h3>"
            "<p><b>Master Password:</b> Your master password is the key to all your encrypted notes. "
            "We use Argon2id, a state-of-the-art password hashing algorithm, to derive your encryption key.</p>"
            
            "<p><b>Encryption:</b> All notes are encrypted using AES-256-GCM, the same encryption "
            "used by governments and militaries worldwide. Each note has a unique encryption key.</p>"
            
            "<p><b>Zero-Knowledge:</b> Your password never leaves your device. We cannot recover "
            "your password or access your notes. This means:</p>"
            "<ul>"
            "<li>✅ Maximum security and privacy</li>"
            "<li>⚠️ If you forget your password, your notes cannot be recovered</li>"
            "</ul>"
            
            "<p><b>Best Practices:</b></p>"
            "<ul>"
            "<li>Use a strong, unique password (12+ characters)</li>"
            "<li>Include uppercase, lowercase, numbers, and symbols</li>"
            "<li>Don't reuse passwords from other services</li>"
            "<li>Consider using a password manager</li>"
            "<li>Store a backup of your password in a secure location</li>"
            "</ul>"
            
            "<p><b>Auto-Lock:</b> TMapp automatically locks after a period of inactivity "
            "(default: 5 minutes) to protect your notes if you step away.</p>"
        )
        layout.addWidget(security_text)
        
        self.setLayout(layout)


class PasswordCreationPage(QWizardPage):
    """Page for creating master password."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Create Your Master Password")
        self.setSubTitle("Choose a strong password to protect your notes")
        
        layout = QVBoxLayout()
        
        # Password input
        password_label = QLabel("Master Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter a strong password")
        self.password_input.textChanged.connect(self._validate_password)
        
        # Confirm password
        confirm_label = QLabel("Confirm Password:")
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setPlaceholderText("Re-enter your password")
        self.confirm_input.textChanged.connect(self._validate_password)
        
        # Show password checkbox
        self.show_password_cb = QCheckBox("Show password")
        self.show_password_cb.stateChanged.connect(self._toggle_password_visibility)
        
        # Password strength indicator
        self.strength_bar = QProgressBar()
        self.strength_bar.setMaximum(100)
        self.strength_bar.setValue(0)
        self.strength_label = QLabel("Password strength: ")
        
        # Validation message
        self.validation_label = QLabel("")
        self.validation_label.setWordWrap(True)
        self.validation_label.setStyleSheet("color: #e74c3c;")
        
        # Add widgets
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(confirm_label)
        layout.addWidget(self.confirm_input)
        layout.addWidget(self.show_password_cb)
        layout.addSpacing(10)
        layout.addWidget(self.strength_label)
        layout.addWidget(self.strength_bar)
        layout.addWidget(self.validation_label)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Register fields for wizard
        self.registerField("password*", self.password_input)
    
    def _toggle_password_visibility(self, state):
        """Toggle password visibility."""
        if state == Qt.CheckState.Checked.value:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
    
    def _calculate_password_strength(self, password: str) -> int:
        """Calculate password strength (0-100)."""
        if not password:
            return 0
        
        strength = 0
        
        # Length
        if len(password) >= 8:
            strength += 20
        if len(password) >= 12:
            strength += 20
        if len(password) >= 16:
            strength += 10
        
        # Character variety
        if any(c.islower() for c in password):
            strength += 10
        if any(c.isupper() for c in password):
            strength += 10
        if any(c.isdigit() for c in password):
            strength += 15
        if any(not c.isalnum() for c in password):
            strength += 15
        
        return min(strength, 100)
    
    def _validate_password(self):
        """Validate password and update UI."""
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        # Calculate strength
        strength = self._calculate_password_strength(password)
        self.strength_bar.setValue(strength)
        
        # Update strength label
        if strength < 40:
            self.strength_label.setText("Password strength: Weak")
            self.strength_bar.setStyleSheet("QProgressBar::chunk { background-color: #e74c3c; }")
        elif strength < 70:
            self.strength_label.setText("Password strength: Moderate")
            self.strength_bar.setStyleSheet("QProgressBar::chunk { background-color: #f39c12; }")
        else:
            self.strength_label.setText("Password strength: Strong")
            self.strength_bar.setStyleSheet("QProgressBar::chunk { background-color: #27ae60; }")
        
        # Validate
        if not password:
            self.validation_label.setText("")
            return False
        
        if len(password) < 8:
            self.validation_label.setText("⚠️ Password must be at least 8 characters")
            return False
        
        if confirm and password != confirm:
            self.validation_label.setText("⚠️ Passwords do not match")
            return False
        
        self.validation_label.setText("✓ Password is valid")
        self.validation_label.setStyleSheet("color: #27ae60;")
        return True
    
    def validatePage(self):
        """Validate before moving to next page."""
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        if len(password) < 8:
            self.validation_label.setText("⚠️ Password must be at least 8 characters")
            return False
        
        if password != confirm:
            self.validation_label.setText("⚠️ Passwords do not match")
            return False
        
        return True


class CompletionPage(QWizardPage):
    """Final completion page."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Setup Complete!")
        self.setSubTitle("You're ready to start using TMapp")
        
        layout = QVBoxLayout()
        
        completion_text = QLabel(
            "<h2>✅ All Set!</h2>"
            "<p>Your master password has been created and TMapp is ready to use.</p>"
            "<p><b>Quick Tips:</b></p>"
            "<ul>"
            "<li><b>Ctrl+N</b> - Create a new note</li>"
            "<li><b>Ctrl+K</b> - Quick search</li>"
            "<li><b>Ctrl+L</b> - Lock application</li>"
            "<li><b>Ctrl+B</b> - Bold text</li>"
            "<li><b>Ctrl+I</b> - Italic text</li>"
            "</ul>"
            "<p>Click <b>Finish</b> to start using TMapp!</p>"
        )
        completion_text.setWordWrap(True)
        layout.addWidget(completion_text)
        
        layout.addStretch()
        self.setLayout(layout)


class FirstRunWizard(QWizard):
    """First-run setup wizard."""
    
    wizard_completed = pyqtSignal(str)  # Emits master password
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("TMapp Setup Wizard")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setOption(QWizard.WizardOption.NoBackButtonOnStartPage)
        self.setMinimumSize(600, 500)
        
        # Add pages
        self.welcome_page = WelcomePage()
        self.security_page = SecurityExplanationPage()
        self.password_page = PasswordCreationPage()
        self.completion_page = CompletionPage()
        
        self.addPage(self.welcome_page)
        self.addPage(self.security_page)
        self.addPage(self.password_page)
        self.addPage(self.completion_page)
        
        # Connect signals
        self.finished.connect(self._on_finished)
        
        logger.info("First-run wizard initialized")
    
    def _on_finished(self, result):
        """Handle wizard completion."""
        if result == QWizard.DialogCode.Accepted:
            password = self.field("password")
            logger.info("First-run wizard completed successfully")
            self.wizard_completed.emit(password)
        else:
            logger.info("First-run wizard cancelled")