# ============================================================
# Floating Compass - QGIS Plugin
#
# Author   : Achmad Amrulloh
# Email    : achmad.amrulloh@gmail.com
# LinkedIn : https://www.linkedin.com/in/achmad-amrulloh/
#
# © 2026 Dinzo. All rights reserved.
#
# This software is provided as freeware.
# Redistribution, modification, or reuse without
# proper attribution is not permitted.
# ============================================================
# floating_compass_news_dialog.py

from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextBrowser,
    QCheckBox,
)
from qgis.PyQt.QtGui import QDesktopServices, QFont
from qgis.PyQt.QtCore import Qt, QUrl
from qgis.core import QgsMessageLog, Qgis


class NewsDialog(QDialog):
    """
    Dialog untuk menampilkan news dari GitHub JSON.

    Behavior:
    - Render HTML sederhana pakai QTextBrowser
    - Klik link -> buka browser default
    - "Mark as read" checkbox untuk tandai sudah dibaca
    """

    def __init__(self, news_items, parent=None, mark_all_callback=None):
        """
        Args:
            news_items (list[dict]): List news dari NewsManager
            parent: Parent widget
            mark_all_callback (callable): Function untuk mark all as read
        """
        super().__init__(parent)
        self.setWindowTitle("Floating Compass — News")
        self.setMinimumSize(560, 480)

        self.news_items = news_items
        self.mark_all_callback = mark_all_callback

        self._build_ui()

    # ---------------------------------------------------------
    # UI BUILDER
    # ---------------------------------------------------------

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("📢 What's New")
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(13)
        header.setFont(header_font)
        layout.addWidget(header)

        # Subheader
        subheader = QLabel(
            f"{len(self.news_items)} unread item(s) — "
            "click any link to open in browser"
        )
        subheader.setStyleSheet("color: gray; margin-bottom: 8px;")
        layout.addWidget(subheader)

        # News content (QTextBrowser)
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)  # kita handle manual
        self.browser.anchorClicked.connect(self._on_anchor_clicked)
        self.browser.setHtml(self._build_html())
        layout.addWidget(self.browser)

        # Mark as read checkbox
        self.mark_all_cb = QCheckBox("Mark all as read when closing")
        self.mark_all_cb.setChecked(True)
        layout.addWidget(self.mark_all_cb)

        # Buttons
        layout.addLayout(self._build_buttons())

    def _build_buttons(self):
        h = QHBoxLayout()

        btn_close = QPushButton("Close")
        btn_close.setMinimumWidth(100)
        btn_close.clicked.connect(self.accept)

        h.addStretch()
        h.addWidget(btn_close)

        return h

    # ---------------------------------------------------------
    # HTML BUILDER
    # ---------------------------------------------------------

    def _build_html(self):
        """
        Build HTML dari news_items.

        Returns:
            str: HTML string
        """
        if not self.news_items:
            return "<p><i>No news available.</i></p>"

        # Priority color mapping
        priority_colors = {
            "high":   "#D32F2F",  # red
            "medium": "#F57C00",  # orange
            "low":    "#388E3C",  # green
        }

        html_parts = [
            "<html><body style='font-family: Arial, sans-serif; "
            "font-size: 10pt; color: #222;'>"
        ]

        for item in self.news_items:
            title    = item.get("title", "Untitled")
            date     = item.get("date", "")
            content  = item.get("content", "")
            link     = item.get("link", "")
            priority = item.get("priority", "low")

            color = priority_colors.get(priority, "#666")

            # Item header with priority badge
            html_parts.append(
                f"<div style='margin-bottom: 16px; "
                f"padding: 10px; "
                f"border-left: 4px solid {color}; "
                f"background: #FAFAFA;'>"
            )

            # Title + date
            html_parts.append(
                f"<div style='margin-bottom: 4px;'>"
                f"<b style='font-size: 11pt;'>{title}</b>"
                f"<span style='color: #888; font-size: 9pt; "
                f"margin-left: 8px;'>— {date}</span>"
                f"</div>"
            )

            # Content
            html_parts.append(
                f"<div style='margin-bottom: 6px;'>{content}</div>"
            )

            # Link
            if link:
                html_parts.append(
                    f"<a href='{link}' "
                    f"style='color: #1976D2; text-decoration: none;'>"
                    f"→ Open link</a>"
                )

            html_parts.append("</div>")

        html_parts.append("</body></html>")

        return "".join(html_parts)

    # ---------------------------------------------------------
    # EVENT HANDLERS
    # ---------------------------------------------------------

    def _on_anchor_clicked(self, url):
        """
        Handle klik link — buka di browser default.

        Args:
            url (QUrl): URL yang diklik
        """
        QDesktopServices.openUrl(url)

    # ---------------------------------------------------------
    # OVERRIDE
    # ---------------------------------------------------------

    def accept(self):
        """
        Override accept — mark as read kalau checkbox dicentang.
        """
        if self.mark_all_cb.isChecked() and self.mark_all_callback:
            try:
                self.mark_all_callback()
            except (RuntimeError, TypeError) as e:
                QgsMessageLog.logMessage(
                    f"News dialog: mark_all_callback failed — {e}",
                    "Floating Compass",
                    Qgis.MessageLevel.Info,
                )

        super().accept()