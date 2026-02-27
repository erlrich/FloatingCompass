# ============================================================
# Floating Protractor - QGIS Plugin
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
#floating_protractor_about_dialog.py
from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtCore import Qt

class FloatingProtractorAboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Floating Protractor")
        self.setFixedWidth(420)

        layout = QVBoxLayout(self)

        # Header Section dengan Ikon dan Judul
        header_layout = QVBoxLayout()                                     
        title = QLabel("Floating Protractor")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)                          

        info = QLabel(
            "Standalone floating angle measurement tool\n"
            "for RF & GIS workflows.\n\n"
            "Author  : Achmad Amrulloh\n"
            "Email   : achmad.amrulloh@gmail.com\n"
            "LinkedIn: https://www.linkedin.com/in/achmad-amrulloh/\n\n"
            "© 2026 Dinzo. All rights reserved."
        )
        info.setAlignment(Qt.AlignCenter)
        info.setWordWrap(True)
        info.setStyleSheet("margin-top: 10px; margin-bottom: 10px;")                                                            

        btn = QPushButton("OK")
        btn.setFixedWidth(80)                     
        btn.clicked.connect(self.accept)

        layout.addWidget(title)
        layout.addWidget(info)
        layout.addStretch()
        layout.addWidget(btn, 0, Qt.AlignCenter)
