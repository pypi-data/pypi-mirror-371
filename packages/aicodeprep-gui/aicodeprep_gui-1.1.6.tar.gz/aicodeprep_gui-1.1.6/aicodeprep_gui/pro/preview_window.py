"""Docked file preview window for pro features."""
import os
from PySide6 import QtWidgets, QtCore, QtGui
from aicodeprep_gui.smart_logic import is_binary_file

class FilePreviewDock(QtWidgets.QDockWidget):
    """A dockable window for previewing file contents."""

    def __init__(self, parent=None):
        super().__init__("File Preview", parent)
        self.setObjectName("file_preview_dock")
        self.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)

        # Create the content widget
        content = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)

        # Text preview area
        self.text_edit = QtWidgets.QPlainTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)

        # Font setup
        font = QtGui.QFont("Consolas", 10)
        font.setStyleHint(QtGui.QFont.Monospace)
        self.text_edit.setFont(font)

        # Status label
        self.status_label = QtWidgets.QLabel()
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666; font-style: italic;")

        layout.addWidget(self.text_edit)
        layout.addWidget(self.status_label)

        self.setWidget(content)
        self.setMinimumWidth(300)
        self.setMaximumWidth(600)

        # Hide initially
        self.hide()

    def preview_file(self, file_path):
        """Load and display file contents."""
        if not file_path or not os.path.isfile(file_path):
            self.clear_preview()
            return

        try:
            # Check if binary
            if is_binary_file(file_path):
                self.show_binary_warning(file_path)
                return

            # Read file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Truncate very large files
            max_chars = 100000
            if len(content) > max_chars:
                content = content[:max_chars] + "\n\n... [Content truncated]"

            self.text_edit.setPlainText(content)
            self.status_label.setText(f"Preview: {os.path.basename(file_path)}")

        except Exception as e:
            self.text_edit.setPlainText(f"Error loading file: {str(e)}")
            self.status_label.setText("Error")

    def show_binary_warning(self, file_path):
        """Show warning for binary files."""
        self.text_edit.setPlainText(
            f"[Binary file - contents not shown]\n\n"
            f"File: {os.path.basename(file_path)}\n"
            f"Size: {os.path.getsize(file_path):,} bytes"
        )
        self.status_label.setText("Binary file")

    def clear_preview(self):
        """Clear the preview."""
        self.text_edit.clear()
        self.status_label.setText("Select a file to preview")
