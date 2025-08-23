from PySide6.QtCore import QTimer
import os
import sys
import json
import logging
import urllib.parse
# requests is no longer needed for this file
from datetime import datetime
from PySide6 import QtWidgets, QtCore, QtGui, QtNetwork
from aicodeprep_gui import __version__


class VoteDialog(QtWidgets.QDialog):
    FEATURE_IDEAS = [
        "Idea 1: Add an optional preview pane to quickly view file contents - DONE",
        "Idea 2: Allow users to add additional folders to the same context block from any location.",
        "Idea 3: Optional Caching so only the files/folders that have changed are scanned and/or processed.",
        "Idea 4: Introduce partial or skeleton context for files, where only key details (e.g., file paths, function/class names) are included. This provides lightweight context without full file content, helping the AI recognize the file's existence with minimal data.",
        "Idea 5: Context7",
        "Idea 6: Create a 'Super Problem Solver' mode that leverages 3-4 AIs to collaboratively solve complex problems. This would send the context and prompt to multiple APIs, automatically compare outputs, and consolidate results for enhanced problem-solving.",
        "Idea 7: Auto Block Secrets - Automatically block sensitive information like API keys and secrets from being included in the context, ensuring user privacy and security.",
        "Idea 8: Add a command line option to immediately create context, skip UI"
    ]

    VOTE_OPTIONS = ["High Priority", "Medium Priority",
                    "Low Priority", "No Interest"]

    def __init__(self, user_uuid, network_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vote on New Features")
        self.setMinimumWidth(600)
        self.votes = {}
        self.user_uuid = user_uuid
        self.network_manager = network_manager

        layout = QtWidgets.QVBoxLayout(self)

        # Title
        title = QtWidgets.QLabel("Vote Screen!")
        title.setAlignment(QtCore.Qt.AlignHCenter)
        title.setStyleSheet(
            "font-size: 28px; color: #1fa31f; font-weight: bold; margin-bottom: 12px;")
        layout.addWidget(title)

        # Feature voting rows
        self.button_groups = []
        for idx, idea in enumerate(self.FEATURE_IDEAS):
            row = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(idea)
            label.setWordWrap(True)
            label.setMinimumWidth(220)
            row.addWidget(label, 2)
            btns = []
            for opt in self.VOTE_OPTIONS:
                btn = QtWidgets.QPushButton(opt)
                btn.setCheckable(True)
                btn.setMinimumWidth(120)
                btn.clicked.connect(self._make_vote_handler(idx, opt, btn))
                row.addWidget(btn, 1)
                btns.append(btn)
            self.button_groups.append(btns)
            layout.addLayout(row)
            layout.addSpacing(4)

        # Bottom buttons
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addStretch()
        self.vote_btn = QtWidgets.QPushButton("Vote!")
        self.vote_btn.clicked.connect(self.submit_votes)
        btn_row.addWidget(self.vote_btn)
        self.skip_btn = QtWidgets.QPushButton("Skip")
        self.skip_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.skip_btn)
        layout.addLayout(btn_row)

    def _make_vote_handler(self, idx, opt, btn):
        def handler():
            # Uncheck other buttons in this group
            for b in self.button_groups[idx]:
                if b is not btn:
                    b.setChecked(False)
                    b.setStyleSheet("")
            btn.setChecked(True)
            btn.setStyleSheet("background-color: #1fa31f; color: white;")
            self.votes[self.FEATURE_IDEAS[idx]] = opt
        return handler

    def submit_votes(self):
        # Collect votes for all features (if not voted, skip)
        details = {idea: self.votes.get(idea, None)
                   for idea in self.FEATURE_IDEAS}
        payload = {
            "user_id": self.user_uuid,
            "event_type": "feature_vote",
            "local_time": datetime.now().isoformat(),
            "details": details
        }
        try:
            endpoint_url = "https://wuu73.org/idea/aicp-metrics/event"
            request = QtNetwork.QNetworkRequest(QtCore.QUrl(endpoint_url))
            request.setHeader(
                QtNetwork.QNetworkRequest.ContentTypeHeader, "application/json")
            json_data = QtCore.QByteArray(json.dumps(payload).encode('utf-8'))
            self.network_manager.post(request, json_data)
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, "Error", f"Failed to submit votes: {e}")
        self.accept()


class ShareDialog(QtWidgets.QDialog):
    """A dialog to encourage users to share the application."""
    SHARE_URL = "https://wuu73.org/aicp"
    SHARE_TEXT = "I'm using aicodeprep-gui to easily prepare my code for LLMs. It's a huge time-saver! Check it out:"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Share AI Code Prep")
        self.setMinimumWidth(500)

        self.original_button_style = ""

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)

        title = QtWidgets.QLabel("Enjoying this tool? Share it!")
        title_font = title.font()
        title_font.setPointSize(title_font.pointSize() + 4)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        message = QtWidgets.QLabel(
            "If you find this tool useful, please consider sharing it with others. "
            "It's the best way to support its development and help fellow developers!"
        )
        message.setWordWrap(True)
        message.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(message)

        # Link copy section
        link_group = QtWidgets.QGroupBox("Copy the link")
        link_layout = QtWidgets.QHBoxLayout(link_group)
        self.link_input = QtWidgets.QLineEdit(self.SHARE_URL)
        self.link_input.setReadOnly(True)
        link_layout.addWidget(self.link_input)

        self.copy_button = QtWidgets.QPushButton("Copy")
        self.copy_button.clicked.connect(self.copy_link)
        self.original_button_style = self.copy_button.styleSheet()
        link_layout.addWidget(self.copy_button)
        layout.addWidget(link_group)

        # Social share section
        social_group = QtWidgets.QGroupBox("One-click sharing")
        social_layout = QtWidgets.QHBoxLayout(social_group)
        social_layout.addStretch()

        twitter_button = QtWidgets.QPushButton("Share on 𝕏 (Twitter)")
        twitter_button.clicked.connect(self.share_on_twitter)
        social_layout.addWidget(twitter_button)

        reddit_button = QtWidgets.QPushButton("Share on Reddit")
        reddit_button.clicked.connect(self.share_on_reddit)
        social_layout.addWidget(reddit_button)

        social_layout.addStretch()
        layout.addWidget(social_group)

        # Close button
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def copy_link(self):
        """Copies the link to the clipboard and provides visual feedback."""
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self.SHARE_URL)

        self.copy_button.setText("Copied!")
        self.copy_button.setStyleSheet(
            "background-color: #4CAF50; color: white;")

        # Reset button after 2 seconds
        QtCore.QTimer.singleShot(2000, self.reset_copy_button)

    def reset_copy_button(self):
        """Resets the copy button to its original state."""
        self.copy_button.setText("Copy")
        self.copy_button.setStyleSheet(self.original_button_style)

    def share_on_twitter(self):
        text = f"{self.SHARE_TEXT} {self.SHARE_URL}"
        encoded_text = urllib.parse.quote(text)
        url = f"https://twitter.com/intent/tweet?text={encoded_text}"
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def share_on_reddit(self):
        title = urllib.parse.quote(
            "Check out aicodeprep-gui for AI developers")
        url = urllib.parse.quote(self.SHARE_URL)
        reddit_url = f"https://www.reddit.com/submit?url={url}&title={title}"
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(reddit_url))


class DialogManager:
    def __init__(self, parent_window):
        self.parent = parent_window

    def open_links_dialog(self):
        """Shows a dialog with helpful links."""
        dialog = QtWidgets.QDialog(self.parent)
        dialog.setWindowTitle("Help / Links and Guides")
        dialog.setMinimumWidth(450)

        layout = QtWidgets.QVBoxLayout(dialog)

        title_label = QtWidgets.QLabel("Helpful Links & Guides")
        title_font = QtGui.QFont()
        title_font.setBold(True)
        title_font.setPointSize(self.parent.default_font.pointSize() + 2)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        layout.addSpacing(10)

        links_group = QtWidgets.QGroupBox(
            "Click a link to open in your browser")
        links_layout = QtWidgets.QVBoxLayout(links_group)

        new_link1 = QtWidgets.QLabel(
            '<a href="https://chat.z.ai/">GLM-4.5</a>')
        new_link1.setOpenExternalLinks(True)
        links_layout.addWidget(new_link1)

        new_link2 = QtWidgets.QLabel(
            '<a href="https://chat.qwen.ai">Qwen3 Coder, 2507, etc</a>')
        new_link2.setOpenExternalLinks(True)
        links_layout.addWidget(new_link2)

        link1 = QtWidgets.QLabel(
            '<a href="https://wuu73.org/blog/aiguide1.html">AI Coding on a Budget</a>')
        link1.setOpenExternalLinks(True)
        links_layout.addWidget(link1)

        link2 = QtWidgets.QLabel(
            '<a href="https://wuu73.org/aicp">App Home Page</a>')
        link2.setOpenExternalLinks(True)
        links_layout.addWidget(link2)

        link3 = QtWidgets.QLabel(
            '<a href="https://wuu73.org/blog/index.html">Quick Links to many AI web chats</a>')
        link3.setOpenExternalLinks(True)
        links_layout.addWidget(link3)

        layout.addWidget(links_group)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)

        dialog.exec()

    def _handle_bug_report_reply(self, reply):
        """Handles the network reply for the bug report submission."""
        try:
            if reply.error() == QtNetwork.QNetworkReply.NetworkError.NoError:
                QtWidgets.QMessageBox.information(
                    self.parent, "Thank you", "Your feedback/complaint was submitted successfully.")
            else:
                error_string = reply.errorString()
                response_data = bytes(reply.readAll()).decode('utf-8')
                QtWidgets.QMessageBox.critical(
                    self.parent, "Error", f"Submission failed: {error_string}. Response: {response_data}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self.parent, "Error", f"Could not process feedback response: {e}")
        finally:
            reply.deleteLater()

    def _handle_email_submit_reply(self, reply):
        """Handles the network reply for the email submission."""
        try:
            if reply.error() == QtNetwork.QNetworkReply.NetworkError.NoError:
                QtWidgets.QMessageBox.information(
                    self.parent, "Thank you", "Your email was submitted successfully.")
            else:
                error_string = reply.errorString()
                response_data = bytes(reply.readAll()).decode('utf-8')
                QtWidgets.QMessageBox.critical(
                    self.parent, "Error", f"Submission failed: {error_string}. Response: {response_data}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self.parent, "Error", f"Could not process email response: {e}")
        finally:
            reply.deleteLater()

    def open_complain_dialog(self):
        """Open the feedback/complain dialog."""
        class FeedbackDialog(QtWidgets.QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Send Ideas, bugs, thoughts!")
                self.setMinimumWidth(400)
                layout = QtWidgets.QVBoxLayout(self)

                layout.addWidget(QtWidgets.QLabel("Your Email (required):"))
                self.email_input = QtWidgets.QLineEdit()
                self.email_input.setPlaceholderText(
                    "you@example.com (required)")
                layout.addWidget(self.email_input)

                layout.addWidget(QtWidgets.QLabel("Message (required):"))
                self.msg_input = QtWidgets.QPlainTextEdit()
                self.msg_input.setPlaceholderText(
                    "Describe your idea, bug, or thought here... (required)")
                layout.addWidget(self.msg_input)

                self.status_label = QtWidgets.QLabel("")
                self.status_label.setStyleSheet("color: #d43c2c;")
                layout.addWidget(self.status_label)

                btns = QtWidgets.QDialogButtonBox(
                    QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
                btns.accepted.connect(self.accept)
                btns.rejected.connect(self.reject)
                layout.addWidget(btns)

            def get_data(self):
                return self.email_input.text().strip(), self.msg_input.toPlainText().strip()

        dlg = FeedbackDialog(self.parent)
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return

        email, message = dlg.get_data()
        if not email or not message:
            QtWidgets.QMessageBox.warning(
                self.parent, "Error", "Email and message are both required.")
            return

        try:
            # Submit bug report
            user_uuid = QtCore.QSettings(
                "aicodeprep-gui", "UserIdentity").value("user_uuid", "")
            payload = {
                "email": email,
                "data": {
                    "summary": message.splitlines()[0][:80] if message else "No summary",
                    "details": message
                },
                "source_identifier": "aicodeprep-gui"
            }
            endpoint_url = "https://wuu73.org/idea/collect/bug-report"
            request = QtNetwork.QNetworkRequest(QtCore.QUrl(endpoint_url))
            request.setHeader(
                QtNetwork.QNetworkRequest.ContentTypeHeader, "application/json")
            if user_uuid:
                request.setRawHeader(
                    b"X-Client-ID", user_uuid.encode('utf-8'))

            json_data = QtCore.QByteArray(
                json.dumps(payload).encode('utf-8'))
            reply = self.parent.network_manager.post(request, json_data)
            reply.finished.connect(
                lambda: self._handle_bug_report_reply(reply))

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self.parent, "Error", f"Could not submit feedback: {e}")

    def open_about_dialog(self):
        """Show About dialog with version, install age, and links."""
        # read install_date from user settings
        settings = QtCore.QSettings("aicodeprep-gui", "UserIdentity")
        install_date_str = settings.value("install_date", "")
        try:
            dt = datetime.fromisoformat(install_date_str)
            days_installed = (datetime.now() - dt).days
        except Exception:
            days_installed = 0

        version_str = __version__

        html = (
            f"<h2>aicodeprep-gui</h2>"
            f"<p>Installed version: {version_str}</p>"
            f"<p>Installed {days_installed} days ago.</p>"
            "<p>"
            '<br><a href="https://github.com/sponsors/detroittommy879">GitHub Sponsors</a><br>'
            '<a href="https://wuu73.org/aicp">AI Code Prep Homepage</a>'
            "</p>"
        )
        # show in rich-text message box
        dlg = QtWidgets.QMessageBox(self.parent)
        dlg.setWindowTitle("About aicodeprep-gui")
        dlg.setTextFormat(QtCore.Qt.RichText)
        dlg.setText(html)
        dlg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        dlg.exec()

    def add_new_preset_dialog(self):
        try:
            # Import the global preset manager instance
            from aicodeprep_gui.gui.settings.presets import global_preset_manager

            lbl, ok = QtWidgets.QInputDialog.getText(
                self.parent, "New preset", "Button label:")
            if not ok or not lbl.strip():
                logging.info(
                    "Add preset dialog canceled or empty label provided")
                return

            dlg = QtWidgets.QDialog(self.parent)
            dlg.setWindowTitle("Preset text")
            dlg.setMinimumSize(400, 300)
            v = QtWidgets.QVBoxLayout(dlg)
            v.addWidget(QtWidgets.QLabel("Enter the preset text:"))
            text_edit = QtWidgets.QPlainTextEdit()
            v.addWidget(text_edit)
            bb = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
            v.addWidget(bb)
            bb.accepted.connect(dlg.accept)
            bb.rejected.connect(dlg.reject)

            if dlg.exec() != QtWidgets.QDialog.Accepted:
                logging.info("Preset text dialog canceled")
                return

            txt = text_edit.toPlainText().strip()
            if not txt:
                QtWidgets.QMessageBox.warning(
                    self.parent, "Error", "Preset text cannot be empty.")
                logging.warning("Attempted to save preset with empty text")
                return

            if global_preset_manager.add_preset(lbl.strip(), txt):
                self.parent.preset_manager._add_preset_button(
                    lbl.strip(), txt, from_global=True)
                logging.info(f"Successfully added new preset: '{lbl.strip()}'")
            else:
                error_msg = f"Failed to save preset '{lbl.strip()}'. Check settings permissions and disk space."
                QtWidgets.QMessageBox.warning(
                    self.parent, "Error", error_msg)
                logging.error(
                    f"Failed to save preset '{lbl.strip()}' - global_preset_manager.add_preset returned False")
        except ImportError as e:
            error_msg = f"Failed to import preset settings module: {e}. Module path may be incorrect."
            QtWidgets.QMessageBox.critical(
                self.parent, "Import Error", error_msg)
            logging.error(f"Import error in add_new_preset_dialog: {e}")
        except Exception as e:
            error_msg = f"Unexpected error while adding preset: {e}"
            QtWidgets.QMessageBox.critical(
                self.parent, "Error", error_msg)
            logging.error(
                f"Unexpected error in add_new_preset_dialog: {e}", exc_info=True)

    def delete_preset_dialog(self):
        try:
            # Import the global preset manager instance
            from aicodeprep_gui.gui.settings.presets import global_preset_manager

            presets = global_preset_manager.get_all_presets()
            if not presets:
                QtWidgets.QMessageBox.information(
                    self.parent, "No Presets", "There are no presets to delete.")
                logging.info(
                    "Delete preset dialog: No presets available to delete")
                return

            preset_labels = [p[0] for p in presets]
            label_to_delete, ok = QtWidgets.QInputDialog.getItem(self.parent, "Delete Preset",
                                                                 "Select a preset to delete:", preset_labels, 0, False)

            if not ok or not label_to_delete:
                logging.info(
                    "Delete preset dialog canceled or no preset selected")
                return

            # Find the button widget corresponding to the label
            button_to_remove = None
            for i in range(self.parent.preset_strip.count()):
                item = self.parent.preset_strip.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if isinstance(widget, QtWidgets.QPushButton) and widget.text() == label_to_delete:
                        button_to_remove = widget
                        break

            if button_to_remove:
                # Call the existing delete logic, which includes the confirmation dialog.
                self.parent.preset_manager._delete_preset(
                    label_to_delete, button_to_remove, from_global=True)
                logging.info(
                    f"Successfully initiated deletion of preset: '{label_to_delete}'")
            else:
                error_msg = f"Could not find the corresponding button for preset '{label_to_delete}'. The UI might be out of sync with stored presets."
                QtWidgets.QMessageBox.warning(
                    self.parent, "Error", error_msg)
                logging.error(
                    f"UI sync error: Could not find button for preset '{label_to_delete}' in preset strip")
        except ImportError as e:
            error_msg = f"Failed to import preset settings module: {e}. Module path may be incorrect."
            QtWidgets.QMessageBox.critical(
                self.parent, "Import Error", error_msg)
            logging.error(f"Import error in delete_preset_dialog: {e}")
        except Exception as e:
            error_msg = f"Unexpected error while deleting preset: {e}"
            QtWidgets.QMessageBox.critical(
                self.parent, "Error", error_msg)
            logging.error(
                f"Unexpected error in delete_preset_dialog: {e}", exc_info=True)

    def open_share_dialog(self):
        """Shows a dialog encouraging the user to share the app."""
        dialog = ShareDialog(self.parent)
        dialog.exec()

    def open_activate_pro_dialog(self):
        dialog = ActivateProDialog(
            self.parent.GUMROAD_PRODUCT_ID,
            self.parent.network_manager,
            parent=self.parent)
        dialog.exec()


# --- ActivateProDialog for Pro license activation ---


class ActivateProDialog(QtWidgets.QDialog):
    RETRY_DELAYS = [1000, 2000, 4000]  # ms

    def __init__(self, product_id: str, network_manager: QtNetwork.QNetworkAccessManager, parent=None):
        super().__init__(parent)
        self.product_id = product_id
        self.network_manager = network_manager
        self.attempt = 0
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Activate Pro License")
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel(
            "Enter your Gumroad license key to activate Pro features:"))
        link = QtWidgets.QLabel(
            f'<a href="https://gumroad.com/l/{self.product_id}" '
            'style="color:#28a745;">Buy a Lifetime Pro License</a>')
        link.setOpenExternalLinks(True)
        layout.addWidget(link)
        self.license_key_input = QtWidgets.QLineEdit()
        self.license_key_input.setPlaceholderText("XXXX-XXXX-XXXX")
        layout.addWidget(self.license_key_input)
        self.status_label = QtWidgets.QLabel("")
        layout.addWidget(self.status_label)
        btns = QtWidgets.QHBoxLayout()
        self.activate_button = QtWidgets.QPushButton("Activate")
        self.activate_button.clicked.connect(self.on_activate)
        btns.addWidget(self.activate_button)
        cancel = QtWidgets.QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        btns.addWidget(cancel)
        layout.addLayout(btns)

    def on_activate(self):
        key = self.license_key_input.text().strip()
        if not key:
            QtWidgets.QMessageBox.warning(
                self, "Error", "Please enter a license key.")
            return
        if not self.product_id:
            QtWidgets.QMessageBox.critical(
                self, "Error", "Product ID is not set.")
            return
        self.activate_button.setEnabled(False)
        self.status_label.setText("Verifying license…")
        self.attempt = 0
        self.send_request(key)

    def send_request(self, key):
        self.attempt += 1
        url = QtCore.QUrl("https://api.gumroad.com/v2/licenses/verify")
        data = urllib.parse.urlencode({
            "product_id": self.product_id,
            "license_key": key,
            "increment_uses_count": "true"
        }).encode("utf-8")
        req = QtNetwork.QNetworkRequest(url)
        req.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader,
                      "application/x-www-form-urlencoded")
        self.reply = self.network_manager.post(req, data)
        self.reply.finished.connect(self.on_reply)

    def on_reply(self):
        err = self.reply.error()
        body = bytes(self.reply.readAll()).decode("utf-8", errors="ignore")
        self.reply.deleteLater()
        if err == QtNetwork.QNetworkReply.NetworkError.NoError:
            try:
                resp = json.loads(body)
            except:
                resp = {}
            if resp.get("success") and not resp.get("purchase", {}).get("refunded", False):
                # Check activation count and limit to 2 uses
                uses = resp.get("uses", 0)
                if uses > 2:
                    QtWidgets.QMessageBox.warning(
                        self, "Activation Limit Exceeded",
                        f"License key has been activated {uses} times. Only 2 activations are allowed. Please purchase a new license for additional installs.")
                    self.activate_button.setEnabled(True)
                    self.status_label.setText("")
                    return

                # persist activation globally
                try:
                    # Save license information to global settings
                    settings = QtCore.QSettings("aicodeprep-gui", "ProLicense")
                    license_key_value = key if "key" in locals(
                    ) else self.license_key_input.text().strip()
                    settings.setValue("license_key", license_key_value)
                    settings.setValue("license_verified", True)
                    settings.setValue(
                        "activation_date", QtCore.QDateTime.currentDateTime().toString())
                    settings.setValue("uses_count", uses)

                    # Set global QSettings value for pro_enabled
                    try:
                        settings.setValue("pro_enabled", True)
                    except Exception as e:
                        logging.error(
                            f"Failed to set pro_enabled in QSettings: {e}")

                except Exception as e:
                    QtWidgets.QMessageBox.warning(
                        self, "Warning",
                        f"Activated but failed to save license information: {e} (license_key={self.license_key_input.text().strip()})"
                    )
                QtWidgets.QMessageBox.information(
                    self, "Success",
                    "License verified! Please restart the app to enter Pro mode."
                )
                # close all windows so restart is clean
                QtWidgets.QApplication.instance().quit()
                return
            else:
                err_msg = resp.get(
                    "message") or "Invalid or refunded license key."
                QtWidgets.QMessageBox.warning(
                    self, "Activation Failed", err_msg)
                self.activate_button.setEnabled(True)
                self.status_label.setText("")
                return

        # network error or HTTP error
        if self.attempt < len(self.RETRY_DELAYS):
            delay = self.RETRY_DELAYS[self.attempt - 1]
            self.status_label.setText(
                f"Network error ({err}). Retrying in {delay//1000}s…"
            )
            QTimer.singleShot(delay, lambda: self.send_request(
                self.license_key_input.text().strip()))
        else:
            QtWidgets.QMessageBox.critical(
                self, "Error",
                "Could not reach the license server after multiple attempts.\n"
                "Please try again later or contact support."
            )
            self.activate_button.setEnabled(True)
            self.status_label.setText("")
