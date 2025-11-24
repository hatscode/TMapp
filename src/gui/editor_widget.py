from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QFrame, QLabel, QSplitter, QTabWidget)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QSyntaxHighlighter, QTextDocument
import re
import markdown2

class MarkdownHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Markdown."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Define formats
        self.heading_format = QTextCharFormat()
        self.heading_format.setForeground(QColor("#89b4fa"))
        self.heading_format.setFontWeight(QFont.Bold)
        
        self.bold_format = QTextCharFormat()
        self.bold_format.setForeground(QColor("#f38ba8"))
        self.bold_format.setFontWeight(QFont.Bold)
        
        self.italic_format = QTextCharFormat()
        self.italic_format.setForeground(QColor("#f9e2af"))
        self.italic_format.setFontItalic(True)
        
        self.code_format = QTextCharFormat()
        self.code_format.setForeground(QColor("#a6e3a1"))
        self.code_format.setFontFamily("JetBrains Mono")
        
        self.link_format = QTextCharFormat()
        self.link_format.setForeground(QColor("#74c7ec"))
        self.link_format.setUnderlineStyle(QTextCharFormat.SingleUnderline)
        
        self.list_format = QTextCharFormat()
        self.list_format.setForeground(QColor("#cba6f7"))
    
    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text."""
        # Headings
        heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        for match in heading_pattern.finditer(text):
            self.setFormat(match.start(1), len(match.group(1)), self.heading_format)
            self.setFormat(match.start(2), len(match.group(2)), self.heading_format)
        
        # Bold
        bold_pattern = re.compile(r'\*\*(.*?)\*\*')
        for match in bold_pattern.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self.bold_format)
        
        # Italic
        italic_pattern = re.compile(r'\*(.*?)\*')
        for match in italic_pattern.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self.italic_format)
        
        # Inline code
        code_pattern = re.compile(r'`([^`]+)`')
        for match in code_pattern.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self.code_format)
        
        # Links
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        for match in link_pattern.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self.link_format)
        
        # Lists
        list_pattern = re.compile(r'^(\s*[-*+]\s+|\s*\d+\.\s+)', re.MULTILINE)
        for match in list_pattern.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self.list_format)

class EditorWidget(QWidget):
    """Enhanced editor widget with Markdown support and preview."""
    
    content_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_mode = "edit"  # "edit", "preview", "split"
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(30000)  # Auto-save every 30 seconds
        
        self.init_ui()
        self.apply_style()
    
    def init_ui(self):
        """Setup the editor UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Mode selector toolbar
        self.mode_toolbar = self.create_mode_toolbar()
        layout.addWidget(self.mode_toolbar)
        
        # Main content area
        self.content_splitter = QSplitter(Qt.Vertical)
        
        # Editor
        self.editor = QTextEdit()
        self.editor.setFont(QFont("JetBrains Mono", 14))
        self.editor.setLineWrapMode(QTextEdit.WidgetWidth)
        self.editor.setAcceptRichText(False)  # Plain text for Markdown
        self.highlighter = MarkdownHighlighter(self.editor.document())
        self.editor.textChanged.connect(self.on_text_changed)
        
        # Preview
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setFont(QFont("JetBrains Mono", 14))
        
        # Add to splitter
        self.content_splitter.addWidget(self.editor)
        self.content_splitter.addWidget(self.preview)
        self.content_splitter.setSizes([1, 0])  # Start with editor only
        
        layout.addWidget(self.content_splitter)
        
        # Start in edit mode
        self.set_view_mode("edit")
    
    def create_mode_toolbar(self):
        """Create toolbar for view mode selection."""
        toolbar = QFrame()
        toolbar.setObjectName("editorToolbar")
        
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)
        
        # Mode buttons
        self.edit_btn = QPushButton("📝 Edit")
        self.edit_btn.setCheckable(True)
        self.edit_btn.setChecked(True)
        self.edit_btn.clicked.connect(lambda: self.set_view_mode("edit"))
        
        self.preview_btn = QPushButton("👁️ Preview")
        self.preview_btn.setCheckable(True)
        self.preview_btn.clicked.connect(lambda: self.set_view_mode("preview"))
        
        self.split_btn = QPushButton("⬌ Split")
        self.split_btn.setCheckable(True)
        self.split_btn.clicked.connect(lambda: self.set_view_mode("split"))
        
        layout.addWidget(self.edit_btn)
        layout.addWidget(self.preview_btn)
        layout.addWidget(self.split_btn)
        
        layout.addStretch()
        
        # Word count
        self.word_count = QLabel("0 words")
        self.word_count.setObjectName("wordCount")
        layout.addWidget(self.word_count)
        
        return toolbar
    
    def set_view_mode(self, mode: str):
        """Set the editor view mode."""
        self.current_mode = mode
        
        # Update button states
        self.edit_btn.setChecked(mode == "edit")
        self.preview_btn.setChecked(mode == "preview")
        self.split_btn.setChecked(mode == "split")
        
        if mode == "edit":
            self.content_splitter.setSizes([1, 0])
            self.editor.setFocus()
        elif mode == "preview":
            self.update_preview()
            self.content_splitter.setSizes([0, 1])
        elif mode == "split":
            self.update_preview()
            self.content_splitter.setSizes([1, 1])
    
    def update_preview(self):
        """Update the Markdown preview."""
        text = self.editor.toPlainText()
        if not text.strip():
            self.preview.setHtml("<p style='color: #6c7086; font-style: italic;'>Nothing to preview</p>")
            return
        
        try:
            # Convert Markdown to HTML
            html = markdown2.markdown(text, extras=['fenced-code-blocks', 'tables', 'task_list'])
            
            # Apply dark theme styling
            styled_html = f"""
            <style>
                body {{
                    background-color: #1e1e2e;
                    color: #cdd6f4;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 14px;
                    line-height: 1.6;
                    margin: 20px;
                }}
                
                h1, h2, h3, h4, h5, h6 {{
                    color: #89b4fa;
                    margin-top: 24px;
                    margin-bottom: 16px;
                    font-weight: bold;
                }}
                
                h1 {{ font-size: 28px; border-bottom: 2px solid #313244; padding-bottom: 8px; }}
                h2 {{ font-size: 24px; border-bottom: 1px solid #313244; padding-bottom: 6px; }}
                h3 {{ font-size: 20px; }}
                h4 {{ font-size: 18px; }}
                h5 {{ font-size: 16px; }}
                h6 {{ font-size: 14px; }}
                
                p {{ margin: 16px 0; }}
                
                strong {{ color: #f38ba8; font-weight: bold; }}
                em {{ color: #f9e2af; font-style: italic; }}
                
                code {{
                    background-color: #181825;
                    color: #a6e3a1;
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 13px;
                }}
                
                pre {{
                    background-color: #181825;
                    border: 1px solid #313244;
                    border-radius: 8px;
                    padding: 16px;
                    overflow-x: auto;
                    margin: 16px 0;
                }}
                
                pre code {{
                    background-color: transparent;
                    padding: 0;
                    border-radius: 0;
                }}
                
                blockquote {{
                    border-left: 4px solid #7c3aed;
                    padding-left: 16px;
                    margin: 16px 0;
                    color: #a6adc8;
                    font-style: italic;
                }}
                
                ul, ol {{
                    margin: 16px 0;
                    padding-left: 32px;
                }}
                
                li {{ margin: 8px 0; }}
                
                a {{
                    color: #74c7ec;
                    text-decoration: none;
                }}
                
                a:hover {{
                    text-decoration: underline;
                }}
                
                table {{
                    border-collapse: collapse;
                    margin: 16px 0;
                    width: 100%;
                }}
                
                th, td {{
                    border: 1px solid #313244;
                    padding: 8px 12px;
                    text-align: left;
                }}
                
                th {{
                    background-color: #181825;
                    color: #89b4fa;
                    font-weight: bold;
                }}
                
                tr:nth-child(even) {{
                    background-color: #181825;
                }}
                
                input[type="checkbox"] {{
                    margin-right: 8px;
                }}
            </style>
            {html}
            """
            
            self.preview.setHtml(styled_html)
            
        except Exception as e:
            self.preview.setHtml(f"<p style='color: #f38ba8;'>Preview error: {str(e)}</p>")
    
    def on_text_changed(self):
        """Handle text changes."""
        self.update_word_count()
        self.content_changed.emit()
        
        # Update preview if in split or preview mode
        if self.current_mode in ["split", "preview"]:
            # Debounce preview updates
            QTimer.singleShot(300, self.update_preview)
    
    def update_word_count(self):
        """Update word count display."""
        text = self.editor.toPlainText()
        words = len(text.split()) if text.strip() else 0
        chars = len(text)
        lines = text.count('\n') + 1
        
        self.word_count.setText(f"{words} words • {chars} chars • {lines} lines")
    
    def get_content(self) -> str:
        """Get editor content."""
        return self.editor.toPlainText()
    
    def set_content(self, content: str):
        """Set editor content."""
        self.editor.setPlainText(content)
        self.update_word_count()
        if self.current_mode in ["split", "preview"]:
            self.update_preview()
    
    def focus_editor(self):
        """Focus the editor."""
        self.editor.setFocus()
    
    def auto_save(self):
        """Auto-save functionality (signal to parent)."""
        if self.editor.document().isModified():
            self.content_changed.emit()
    
    def apply_style(self):
        """Apply styling to the editor widget."""
        self.setStyleSheet("""
        QWidget {
            background-color: #1e1e2e;
            color: #cdd6f4;
        }
        
        #editorToolbar {
            background-color: #181825;
            border-bottom: 1px solid #313244;
        }
        
        QPushButton {
            background-color: transparent;
            border: 1px solid #313244;
            border-radius: 6px;
            padding: 6px 12px;
            color: #cdd6f4;
            font-size: 12px;
        }
        
        QPushButton:checked {
            background-color: #7c3aed;
            border-color: #7c3aed;
            color: white;
        }
        
        QPushButton:hover {
            background-color: #313244;
        }
        
        #wordCount {
            color: #a6adc8;
            font-size: 11px;
            padding: 0 8px;
        }
        
        QTextEdit {
            background-color: #1e1e2e;
            color: #cdd6f4;
            border: none;
            selection-background-color: #7c3aed;
            selection-color: white;
        }
        
        QSplitter::handle {
            background-color: #313244;
            height: 2px;
        }
        
        QSplitter::handle:hover {
            background-color: #585b70;
        }
        """)
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_B:  # Ctrl+B for bold
                self.insert_markdown("**", "**")
                event.accept()
                return
            elif event.key() == Qt.Key_I:  # Ctrl+I for italic
                self.insert_markdown("*", "*")
                event.accept()
                return
            elif event.key() == Qt.Key_K:  # Ctrl+K for code
                self.insert_markdown("`", "`")
                event.accept()
                return
            elif event.key() == Qt.Key_Shift and event.key() == Qt.Key_7:  # Ctrl+Shift+7 for list
                self.insert_at_line_start("- ")
                event.accept()
                return
        
        super().keyPressEvent(event)
    
    def insert_markdown(self, prefix: str, suffix: str = ""):
        """Insert Markdown formatting around selected text."""
        cursor = self.editor.textCursor()
        selected_text = cursor.selectedText()
        
        if selected_text:
            # Wrap selected text
            replacement = f"{prefix}{selected_text}{suffix}"
            cursor.insertText(replacement)
        else:
            # Insert at cursor with placeholder
            cursor.insertText(f"{prefix}text{suffix}")
            # Select the placeholder
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, len(suffix) + 4)
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 4)
            self.editor.setTextCursor(cursor)
    
    def insert_at_line_start(self, text: str):
        """Insert text at the beginning of current line."""
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.insertText(text)
        self.editor.setTextCursor(cursor)