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

# floating_protractor_plugin.py
import os
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon

from .floating_protractor_tool import FloatingProtractorMapTool
from .floating_protractor_about_dialog import FloatingProtractorAboutDialog


class FloatingProtractorPlugin:

    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.action = None
        self.tool = None

    def initGui(self):
        # ---- ICON PATH ----
        plugin_dir = os.path.dirname(__file__)
        icon_path = os.path.join(plugin_dir, "icon", "protractor.svg")

        # =========================
        # MAIN TOOL ACTION
        # =========================
        self.action = QAction(
            QIcon(icon_path),
            "Floating Protractor",
            self.iface.mainWindow()
        )
        self.action.setCheckable(True)
        # self.action.triggered.connect(self.toggle_tool)
        self.action.toggled.connect(self.toggle_tool)

        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("Floating Protractor", self.action)

        # =========================
        # ABOUT ACTION (WITH ICON)
        # =========================        
        about_icon_path = os.path.join(
            os.path.dirname(__file__),
            "icon",
            "information.svg"
        )

        self.action_about = QAction(
            QIcon(about_icon_path),
            "About Floating Protractor",
            self.iface.mainWindow()
        )
        self.action_about.triggered.connect(self.show_about_dialog)

        self.iface.addPluginToMenu("Floating Protractor", self.action_about)


        # =========================
        # CREATE TOOL ONCE (SINGLETON)
        # =========================
        self.tool = FloatingProtractorMapTool(self.iface)

        # =========================
        # PASS ACTION REFERENCE TO TOOL
        # =========================
        self.tool.plugin_action = self.action

    
    def show_about_dialog(self):
        dlg = FloatingProtractorAboutDialog(self.iface.mainWindow())
        dlg.exec_()


    def unload(self):
        # Remove toolbar/menu
        if self.action:
            self.iface.removeToolBarIcon(self.action)
            self.iface.removePluginMenu("Floating Protractor", self.action)
            self.action = None

        # FORCE cleanup map tool & overlay
        if self.tool:
            try:
                # Hide overlay explicitly
                if hasattr(self.tool, "overlay") and self.tool.overlay:
                    self.tool.overlay.setVisible(False)
                    self.tool.overlay = None

                # Unset map tool if active
                if self.canvas.mapTool() == self.tool:
                    self.canvas.unsetMapTool(self.tool)

            except Exception:
                pass

            self.tool = None


    def toggle_tool(self, checked):
        if checked:
            # activate protractor first
            self.canvas.setMapTool(self.tool)

            # 🔥 first-run message AFTER tool is active
            self.show_first_run_message()

        else:
            # deactivate → switch to pan
            self.iface.actionPan().trigger()
            self.action.setChecked(False)

    
    
    def show_first_run_message(self):
        from qgis.PyQt.QtWidgets import QMessageBox
        from qgis.PyQt.QtCore import QSettings

        s = QSettings()
        key = "FloatingProtractor/first_run_done"

        if s.value(key, False, bool):
            return

        QMessageBox.information(
            self.iface.mainWindow(),
            "Floating Protractor",
            "Floating Protractor by Achmad Amrulloh\n\n"
            "Standalone floating angle measurement tool\n"
            "for RF & GIS workflows.\n\n"
            "LinkedIn:\n"
            "https://www.linkedin.com/in/achmad-amrulloh/"
        )

        s.setValue(key, True)