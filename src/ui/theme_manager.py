"""Professional theme manager with dark/light mode support."""
import logging
from enum import Enum
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)


class ThemeMode(Enum):
    """Theme modes."""
    DARK = "dark"
    LIGHT = "light"


class ThemeManager(QObject):
    """
    Manages application theming with professional dark/light modes.
    Uses the exact color palette from requirements.
    """
    
    theme_changed = pyqtSignal(str)  # Emits theme mode
    
    # Dark Theme Colors (Default)
    DARK_THEME = {
        'bg_main': '#0D1117',
        'bg_panel': '#161B22',
        'bg_card': '#161B22',
        'text_primary': '#F0F6FC',
        'text_secondary': '#8B949E',
        'accent': '#2563EB',
        'accent_hover': '#3973f7',
        'accent_active': '#1746a2',
        'success': '#22C55E',
        'success_bg': 'rgba(34,197,94,0.15)',
        'error': '#DC2626',
        'error_bg': 'rgba(220,38,38,0.15)',
        'warning': '#F59E0B',
        'warning_bg': 'rgba(245,158,11,0.15)',
        'disabled': '#2D333B',
        'disabled_text': '#6E7681',
        'border': '#21262D',
        'border_light': '#30363D',
        'input_bg': '#161B22',
        'input_border': '#30363D',
        'input_placeholder': '#8B949E',
        'shadow': '0 6px 24px rgba(0,0,0,0.25)',
        'panel_shadow': '0 2px 8px rgba(0,0,0,0.18)',
    }
    
    # Light Theme Colors
    LIGHT_THEME = {
        'bg_main': '#FFFFFF',
        'bg_panel': '#F6F8FA',
        'bg_card': '#FFFFFF',
        'text_primary': '#24292F',
        'text_secondary': '#57606A',
        'accent': '#2563EB',
        'accent_hover': '#3973f7',
        'accent_active': '#1746a2',
        'success': '#22C55E',
        'success_bg': 'rgba(34,197,94,0.1)',
        'error': '#DC2626',
        'error_bg': 'rgba(220,38,38,0.1)',
        'warning': '#F59E0B',
        'warning_bg': 'rgba(245,158,11,0.1)',
        'disabled': '#E7ECF0',
        'disabled_text': '#8C959F',
        'border': '#D0D7DE',
        'border_light': '#E7ECF0',
        'input_bg': '#FFFFFF',
        'input_border': '#D0D7DE',
        'input_placeholder': '#8C959F',
        'shadow': '0 6px 24px rgba(140,149,159,0.15)',
        'panel_shadow': '0 2px 8px rgba(140,149,159,0.1)',
    }
    
    def __init__(self):
        """Initialize theme manager."""
        super().__init__()
        self.current_theme = ThemeMode.DARK
        self.colors = self.DARK_THEME.copy()
        logger.info("ThemeManager initialized with dark theme")
    
    def set_theme(self, theme_mode: ThemeMode):
        """Set application theme."""
        self.current_theme = theme_mode
        
        if theme_mode == ThemeMode.DARK:
            self.colors = self.DARK_THEME.copy()
        else:
            self.colors = self.LIGHT_THEME.copy()
        
        logger.info(f"Theme changed to: {theme_mode.value}")
        self.theme_changed.emit(theme_mode.value)
    
    def toggle_theme(self):
        """Toggle between dark and light themes."""
        if self.current_theme == ThemeMode.DARK:
            self.set_theme(ThemeMode.LIGHT)
        else:
            self.set_theme(ThemeMode.DARK)
    
    def get_stylesheet(self) -> str:
        """Generate complete QSS stylesheet for current theme."""
        c = self.colors
        
        return f"""
        /* ===== MAIN WINDOW ===== */
        QMainWindow {{
            background-color: {c['bg_main']};
            color: {c['text_primary']};
        }}
        
        QWidget {{
            background-color: {c['bg_main']};
            color: {c['text_primary']};
            font-family: 'Segoe UI', 'Inter', -apple-system, system-ui, sans-serif;
            font-size: 14px;
        }}
        
        /* ===== TOOLBAR ===== */
        QToolBar {{
            background-color: {c['bg_panel']};
            border-bottom: 1px solid {c['border']};
            spacing: 8px;
            padding: 8px;
        }}
        
        QToolBar QToolButton {{
            background-color: transparent;
            border: none;
            border-radius: 6px;
            padding: 8px;
            color: {c['text_primary']};
        }}
        
        QToolBar QToolButton:hover {{
            background-color: rgba(37, 99, 235, 0.1);
        }}
        
        QToolBar QToolButton:pressed {{
            background-color: {c['accent']};
        }}
        
        /* ===== SIDEBAR ===== */
        QWidget#sidebar {{
            background-color: {c['bg_panel']};
            border-right: 1px solid {c['border']};
        }}
        
        /* ===== BUTTONS ===== */
        QPushButton {{
            background-color: {c['accent']};
            color: {c['text_primary']};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
        }}
        
        QPushButton:hover {{
            background-color: {c['accent_hover']};
        }}
        
        QPushButton:pressed {{
            background-color: {c['accent_active']};
        }}
        
        QPushButton:disabled {{
            background-color: {c['disabled']};
            color: {c['disabled_text']};
        }}
        
        QPushButton#secondaryButton {{
            background-color: transparent;
            border: 1px solid {c['border_light']};
            color: {c['text_primary']};
        }}
        
        QPushButton#secondaryButton:hover {{
            background-color: {c['bg_panel']};
            border-color: {c['accent']};
        }}
        
        QPushButton#dangerButton {{
            background-color: {c['error']};
        }}
        
        QPushButton#dangerButton:hover {{
            background-color: #B91C1C;
        }}
        
        /* ===== TEXT EDIT / EDITOR ===== */
        QTextEdit {{
            background-color: {c['input_bg']};
            color: {c['text_primary']};
            border: 1px solid {c['input_border']};
            border-radius: 8px;
            padding: 16px;
            font-size: 16px;
            line-height: 1.6;
            selection-background-color: {c['accent']};
            selection-color: white;
        }}
        
        QTextEdit:focus {{
            border-color: {c['accent']};
            outline: none;
        }}
        
        /* ===== LINE EDIT ===== */
        QLineEdit {{
            background-color: {c['input_bg']};
            color: {c['text_primary']};
            border: 1px solid {c['input_border']};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
        }}
        
        QLineEdit:focus {{
            border-color: {c['accent']};
            outline: none;
        }}
        
        QLineEdit::placeholder {{
            color: {c['input_placeholder']};
        }}
        
        /* ===== LIST WIDGET (Note List) ===== */
        QListWidget {{
            background-color: {c['bg_panel']};
            border: none;
            outline: none;
        }}
        
        QListWidget::item {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 12px;
            margin: 4px 8px;
        }}
        
        QListWidget::item:hover {{
            background-color: rgba(37, 99, 235, 0.1);
            border-color: {c['border_light']};
        }}
        
        QListWidget::item:selected {{
            background-color: rgba(37, 99, 235, 0.2);
            border-color: {c['accent']};
        }}
        
        /* ===== TREE WIDGET (Notebooks) ===== */
        QTreeWidget {{
            background-color: {c['bg_panel']};
            border: none;
            outline: none;
        }}
        
        QTreeWidget::item {{
            padding: 6px;
            border-radius: 4px;
        }}
        
        QTreeWidget::item:hover {{
            background-color: rgba(37, 99, 235, 0.1);
        }}
        
        QTreeWidget::item:selected {{
            background-color: rgba(37, 99, 235, 0.2);
        }}
        
        /* ===== SCROLLBAR ===== */
        QScrollBar:vertical {{
            background-color: {c['bg_panel']};
            width: 12px;
            border: none;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {c['border_light']};
            border-radius: 6px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {c['text_secondary']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background-color: {c['bg_panel']};
            height: 12px;
            border: none;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {c['border_light']};
            border-radius: 6px;
            min-width: 30px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {c['text_secondary']};
        }}
        
        /* ===== MENU BAR ===== */
        QMenuBar {{
            background-color: {c['bg_panel']};
            border-bottom: 1px solid {c['border']};
            padding: 4px;
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 6px 12px;
            border-radius: 4px;
        }}
        
        QMenuBar::item:selected {{
            background-color: rgba(37, 99, 235, 0.1);
        }}
        
        QMenu {{
            background-color: {c['bg_panel']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 4px;
        }}
        
        QMenu::item {{
            padding: 8px 24px;
            border-radius: 4px;
        }}
        
        QMenu::item:selected {{
            background-color: rgba(37, 99, 235, 0.15);
        }}
        
        /* ===== STATUS BAR ===== */
        QStatusBar {{
            background-color: {c['bg_panel']};
            border-top: 1px solid {c['border']};
            color: {c['text_secondary']};
        }}
        
        /* ===== SPLITTER ===== */
        QSplitter::handle {{
            background-color: {c['border']};
            width: 1px;
            height: 1px;
        }}
        
        QSplitter::handle:hover {{
            background-color: {c['accent']};
        }}
        
        /* ===== TAB WIDGET ===== */
        QTabWidget::pane {{
            border: 1px solid {c['border']};
            border-radius: 8px;
            background-color: {c['bg_card']};
        }}
        
        QTabBar::tab {{
            background-color: {c['bg_panel']};
            border: 1px solid {c['border']};
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            padding: 8px 16px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {c['bg_card']};
            border-bottom-color: {c['bg_card']};
        }}
        
        QTabBar::tab:hover {{
            background-color: rgba(37, 99, 235, 0.1);
        }}
        
        /* ===== LABELS ===== */
        QLabel {{
            background-color: transparent;
            color: {c['text_primary']};
        }}
        
        QLabel#secondaryLabel {{
            color: {c['text_secondary']};
        }}
        
        /* ===== CHECKBOX ===== */
        QCheckBox {{
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {c['border_light']};
            border-radius: 4px;
            background-color: {c['input_bg']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {c['accent']};
            border-color: {c['accent']};
            image: url(:/icons/check.svg);
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {c['accent']};
        }}
        
        /* ===== COMBO BOX ===== */
        QComboBox {{
            background-color: {c['input_bg']};
            border: 1px solid {c['input_border']};
            border-radius: 6px;
            padding: 6px 12px;
            min-width: 100px;
        }}
        
        QComboBox:hover {{
            border-color: {c['accent']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {c['bg_panel']};
            border: 1px solid {c['border']};
            border-radius: 6px;
            selection-background-color: rgba(37, 99, 235, 0.2);
        }}
        
        /* ===== PROGRESS BAR ===== */
        QProgressBar {{
            background-color: {c['border']};
            border: none;
            border-radius: 4px;
            height: 8px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {c['accent']};
            border-radius: 4px;
        }}
        """
    
    def get_color(self, key: str) -> str:
        """Get specific color value from current theme."""
        return self.colors.get(key, '#FFFFFF')