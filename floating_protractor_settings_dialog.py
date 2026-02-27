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

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QMessageBox, QComboBox, 
    QGroupBox, QFormLayout, QCheckBox, QSpinBox, QLineEdit, 
    QHBoxLayout, QPushButton, QLabel, QColorDialog
)
from qgis.PyQt.QtCore import QSettings, Qt
from qgis.PyQt.QtGui import QColor



class FloatingProtractorSettingsDialog(QDialog):

    SETTINGS_GROUP = "FloatingProtractor"

    def __init__(self, tool, parent=None):
        super().__init__(parent)
        self.tool = tool
        self.settings = QSettings()

        self.setWindowTitle("Floating Protractor Settings")
        self.resize(580, 560)

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # =================================================
        # CREATE ALL WIDGETS (UNCHANGED)
        # =================================================

        # --- Mode ---
        self.cmb_mode = QComboBox()
        self.cmb_mode.addItems(["NORMAL", "SITE_AUDIT", "MULTI"])

        self.spin_multi_sector = QSpinBox()
        self.spin_multi_sector.setRange(2, 6)
        self.spin_multi_sector.setSuffix(" arms")

        # --- Behaviour / Interaction ---
        self.chk_snap = QCheckBox("Enable Snap")
        self.spin_snap_step = QSpinBox()
        self.spin_snap_step.setRange(1, 30)
        self.spin_snap_step.setSuffix(" °")

        self.spin_hold_ms = QSpinBox()
        self.spin_hold_ms.setRange(500, 5000)
        self.spin_hold_ms.setSingleStep(250)
        self.spin_hold_ms.setSuffix(" ms")

        self.spin_hold_cancel_px = QSpinBox()
        self.spin_hold_cancel_px.setRange(1, 20)
        self.spin_hold_cancel_px.setSuffix(" px")

        self.spin_hit_center = QSpinBox()
        self.spin_hit_endpoint = QSpinBox()
        self.spin_hit_arm = QSpinBox()
        self.spin_hit_ring = QSpinBox()
        # --- Advanced Hit Test Control ---
        self.chk_enable_hit_test = QCheckBox("Enable Advanced Hit Test Settings")

        
        for w in (self.spin_hit_center, self.spin_hit_endpoint, self.spin_hit_arm, self.spin_hit_ring):
            w.setRange(4, 40)
            w.setSuffix(" px")
        # ==================
        # --- Visibility ---
        # ==================
        self.chk_show_arms = QCheckBox("Show Arms")
        self.chk_show_arc = QCheckBox("Show Arc Highlight")
        self.chk_show_angle_text = QCheckBox("Show Angle Text")
        self.chk_show_brand = QCheckBox("Show Compass / Brand Text")
        self.chk_show_cardinal = QCheckBox("Show Cardinal Directions (N / E / S / W)")
        self.chk_show_north_tri = QCheckBox("Show North Triangle")


        # =================
        # --- Crosshair ---
        # =================
        self.chk_show_crosshair = QCheckBox("Show Crosshair")

        self.cmb_crosshair_style = QComboBox()
        self.cmb_crosshair_style.addItems(["Plus", "Dot", "None"])

        self.spin_crosshair_size = QSpinBox()
        self.spin_crosshair_size.setRange(4, 50)
        self.spin_crosshair_size.setSuffix(" px")

        self.spin_crosshair_thickness = QSpinBox()
        self.spin_crosshair_thickness.setRange(1, 6)

        # Crosshair color
        self.c_crosshair = QPushButton()
        self.c_crosshair.setFixedWidth(40)
        self.c_crosshair._value = "#FFFF00"
        self.c_crosshair.setStyleSheet(
            f"background-color:{self.c_crosshair._value}; border: 1px solid #666;"
        )

        def pick_crosshair_color():
            c = QColorDialog.getColor(QColor(self.c_crosshair._value), self)
            if c.isValid():
                self.c_crosshair._value = c.name()
                self.c_crosshair.setStyleSheet(
                    f"background-color:{self.c_crosshair._value}; border: 1px solid #666;"
                )

        self.c_crosshair.clicked.connect(pick_crosshair_color)

        # --- Labels ---
        self.edit_label_A = QLineEdit()
        self.edit_label_B = QLineEdit()
        self.edit_label_C = QLineEdit()
        self.edit_label_D = QLineEdit()
        self.edit_label_E = QLineEdit()
        self.edit_label_F = QLineEdit()

        # --- Fonts ---
        self.spin_angle_font = QSpinBox()
        self.spin_angle_font.setRange(6, 24)

        self.spin_label_font = QSpinBox()
        self.spin_label_font.setRange(6, 24)

        # --- Text effects ---
        self.chk_outline_enabled = QCheckBox("Show Text Outline")
        self.chk_shadow_enabled = QCheckBox("Show Text Shadow")

        # --- Visual Style ---
        self.spin_center_dot = QSpinBox()
        self.spin_center_dot.setRange(2, 20)
        self.spin_center_dot.setSuffix(" px")

        self.spin_endpoint_dot = QSpinBox()
        self.spin_endpoint_dot.setRange(2, 20)
        self.spin_endpoint_dot.setSuffix(" px")

        self.spin_tick_step = QSpinBox()
        self.spin_major_tick = QSpinBox()
        self.spin_label_step = QSpinBox()
        
        self.spin_arc_thickness = QSpinBox()
        self.spin_arc_thickness.setRange(1, 10)
        self.spin_arc_thickness.setSuffix(" px")
        self.spin_arc_thickness.setSingleStep(1)

        self.spin_angle_text_distance = QSpinBox()
        self.spin_angle_text_distance.setRange(10, 200)
        self.spin_angle_text_distance.setSuffix(" px")
        self.spin_angle_text_distance.setSingleStep(5)


        for w in (self.spin_tick_step, self.spin_major_tick, self.spin_label_step):
            w.setRange(1, 90)
            w.setSuffix(" °")

        self.spin_arm_radius_min = QSpinBox()
        self.spin_arm_radius_min.setRange(10, 250)
        self.spin_arm_radius_min.setSingleStep(5)
        self.spin_arm_radius_min.setSuffix(" px")

        self.spin_ring_radius_min = QSpinBox()
        self.spin_ring_radius_min.setRange(10, 300)
        self.spin_ring_radius_min.setSingleStep(5)
        self.spin_ring_radius_min.setSuffix(" px")

        self.spin_ring_radius_max = QSpinBox()
        self.spin_ring_radius_max.setRange(50, 500)
        self.spin_ring_radius_max.setSingleStep(5)
        self.spin_ring_radius_max.setSuffix(" px")

        # --- Colors ---
        def make_color_button():
            btn = QPushButton()
            btn.setFixedWidth(40)
            btn._value = "#FFFFFF"
            btn.setStyleSheet(f"background-color:{btn._value}; border:1px solid #666;")

            def pick():
                c = QColorDialog.getColor(QColor(btn._value), self)
                if c.isValid():
                    btn._value = c.name()
                    btn.setStyleSheet(f"background-color:{btn._value}; border:1px solid #666;")
            btn.clicked.connect(pick)
            return btn

        self.c_ring = make_color_button()
        self.c_arc = make_color_button()
        self.c_text = make_color_button()

        self.c_arm_a = make_color_button()
        self.c_arm_b = make_color_button()
        self.c_arm_c = make_color_button()
        self.c_arm_d = make_color_button()
        self.c_arm_e = make_color_button()
        self.c_arm_f = make_color_button()

        self.spin_glow_alpha = QSpinBox()
        self.spin_glow_alpha.setRange(0, 255)
        self.spin_glow_alpha.setSingleStep(5)

        self.spin_shadow_alpha = QSpinBox()
        self.spin_shadow_alpha.setRange(0, 255)
        self.spin_shadow_alpha.setSingleStep(5)
        
        # =================================================
        # CARDINAL DIRECTIONS
        # =================================================
        grp_cardinal = QGroupBox("Cardinal Directions")
        f_card = QFormLayout(grp_cardinal)

        # =====================
        # UX LABEL IMPROVEMENT
        # =====================
        self.chk_show_cardinal.setText(
            "Show Cardinal Directions (N / E / S / W)"
        )
        self.chk_show_north_tri.setText(
            "Show North Triangle"
        )

        self.spin_cardinal_font = QSpinBox()
        self.spin_cardinal_font.setRange(8, 32)

        self.spin_cardinal_offset = QSpinBox()
        self.spin_cardinal_offset.setRange(8, 100)
        self.spin_cardinal_offset.setSuffix(" px")
        self.spin_cardinal_offset.setSingleStep(2)

        f_card.addRow(self.chk_show_cardinal)
        f_card.addRow(self.chk_show_north_tri)
        f_card.addRow("Font Size:", self.spin_cardinal_font)
        f_card.addRow("Offset from Ring:", self.spin_cardinal_offset)
        
        # =================================================
        # TAB: GENERAL
        # =================================================
        tab_general = QWidget()
        v_general = QVBoxLayout(tab_general)

        grp_mode = QGroupBox("Mode Configuration")
        f_mode = QFormLayout(grp_mode)
        f_mode.addRow("Mode:", self.cmb_mode)
        self.lbl_multi_sector = QLabel("Multi Sector Count:")
        f_mode.addRow(self.lbl_multi_sector, self.spin_multi_sector)

        v_general.addWidget(grp_mode)
        v_general.addStretch()
        self.tabs.addTab(tab_general, "General")

        # =================================================
        # TAB: INTERACTION
        # =================================================
        tab_inter = QWidget()
        v_inter = QVBoxLayout(tab_inter)

        grp_snap = QGroupBox("Snapping")
        f_snap = QFormLayout(grp_snap)
        f_snap.addRow(self.chk_snap)
        f_snap.addRow("Snap Step:", self.spin_snap_step)

        grp_gesture = QGroupBox("Gesture")
        f_gesture = QFormLayout(grp_gesture)
        f_gesture.addRow("Hold Time:", self.spin_hold_ms)
        f_gesture.addRow("Hold Cancel Threshold:", self.spin_hold_cancel_px)
        
        grp_hit = QGroupBox("Hit Test Sensitivity")
        f_hit = QFormLayout(grp_hit)

        # master enable
        f_hit.addRow(self.chk_enable_hit_test)

        # advanced controls
        f_hit.addRow("Center Hit:", self.spin_hit_center)
        f_hit.addRow("Endpoint Hit:", self.spin_hit_endpoint)
        f_hit.addRow("Arm Line Hit:", self.spin_hit_arm)
        f_hit.addRow("Ring Hit:", self.spin_hit_ring)


        v_inter.addWidget(grp_snap)
        v_inter.addWidget(grp_gesture)
        v_inter.addWidget(grp_hit)
        v_inter.addStretch()
        self.tabs.addTab(tab_inter, "Interaction")

        # =================================================
        # TAB: VISIBILITY
        # =================================================
        tab_vis = QWidget()
        v_vis = QVBoxLayout(tab_vis)

        grp_elements = QGroupBox("Elements")
        v_elem = QVBoxLayout(grp_elements)
        v_elem.addWidget(self.chk_show_arms)
        v_elem.addWidget(self.chk_show_arc)
        v_elem.addWidget(self.chk_show_angle_text)

        grp_cross = QGroupBox("Crosshair")
        f_cross = QFormLayout(grp_cross)
        f_cross.addRow(self.chk_show_crosshair)
        f_cross.addRow("Style:", self.cmb_crosshair_style)
        f_cross.addRow("Size:", self.spin_crosshair_size)
        f_cross.addRow("Thickness:", self.spin_crosshair_thickness)

        v_vis.addWidget(grp_elements)
        v_vis.addWidget(grp_cross)
        v_vis.addStretch()
        self.tabs.addTab(tab_vis, "Visibility")

        # =================================================
        # TAB: LABELS & TEXT
        # =================================================
        tab_lbl = QWidget()
        v_lbl = QVBoxLayout(tab_lbl)

        grp_labels = QGroupBox("Arm Labels")
        f_lbl = QFormLayout(grp_labels)
        f_lbl.addRow("Arm A:", self.edit_label_A)
        f_lbl.addRow("Arm B:", self.edit_label_B)
        f_lbl.addRow("Arm C:", self.edit_label_C)
        f_lbl.addRow("Arm D:", self.edit_label_D)
        f_lbl.addRow("Arm E:", self.edit_label_E)
        f_lbl.addRow("Arm F:", self.edit_label_F)

        grp_font = QGroupBox("Font")
        f_font = QFormLayout(grp_font)
        f_font.addRow("Angle Font Size:", self.spin_angle_font)
        f_font.addRow("Label Font Size:", self.spin_label_font)

        grp_fx = QGroupBox("Text Effects")
        v_fx = QVBoxLayout(grp_fx)
        v_fx.addWidget(self.chk_outline_enabled)
        v_fx.addWidget(self.chk_shadow_enabled)
        
        grp_text_layout = QGroupBox("Text Layout")
        f_text_layout = QFormLayout(grp_text_layout)
        f_text_layout.addRow("Angle Text Distance:", self.spin_angle_text_distance)

        v_lbl.addWidget(grp_labels)
        v_lbl.addWidget(grp_font)
        v_lbl.addWidget(grp_fx)
        v_lbl.addWidget(grp_text_layout)
        v_lbl.addStretch()
        self.tabs.addTab(tab_lbl, "Labels & Text")
        

        # =================================================
        # TAB: VISUAL STYLE
        # =================================================
        tab_visual = QWidget()
        v_visual = QVBoxLayout(tab_visual)

        grp_geo = QGroupBox("Geometry")
        f_geo = QFormLayout(grp_geo)
        f_geo.addRow("Center Dot Radius:", self.spin_center_dot)
        f_geo.addRow("Endpoint Dot Radius:", self.spin_endpoint_dot)

        grp_ticks = QGroupBox("Ring & Ticks")
        f_ticks = QFormLayout(grp_ticks)
        f_ticks.addRow("Tick Step:", self.spin_tick_step)
        f_ticks.addRow("Major Tick:", self.spin_major_tick)
        f_ticks.addRow("Label Step:", self.spin_label_step)
        f_ticks.addRow("Arc Highlight Thickness:", self.spin_arc_thickness)

        grp_radius = QGroupBox("Radius Limits")
        f_radius = QFormLayout(grp_radius)
        f_radius.addRow("Arm Radius Min:", self.spin_arm_radius_min)
        f_radius.addRow("Ring Radius Min:", self.spin_ring_radius_min)
        f_radius.addRow("Ring Radius Max:", self.spin_ring_radius_max)

        v_visual.addWidget(grp_geo)
        v_visual.addWidget(grp_ticks)
        v_visual.addWidget(grp_radius)
        v_visual.addStretch()
        self.tabs.addTab(tab_visual, "Visual Style")

        # =================================================
        # TAB: COLORS
        # =================================================
        tab_colors = QWidget()
        v_col = QVBoxLayout(tab_colors)

        grp_core = QGroupBox("Core Colors")
        f_core = QFormLayout(grp_core)
        f_core.addRow("Ring:", self.c_ring)
        f_core.addRow("Arc Highlight:", self.c_arc)
        f_core.addRow("Angle Text:", self.c_text)

        grp_arms = QGroupBox("Arm Colors")
        f_arms = QFormLayout(grp_arms)
        f_arms.addRow("Arm A:", self.c_arm_a)
        f_arms.addRow("Arm B:", self.c_arm_b)
        f_arms.addRow("Arm C:", self.c_arm_c)
        f_arms.addRow("Arm D:", self.c_arm_d)
        f_arms.addRow("Arm E:", self.c_arm_e)
        f_arms.addRow("Arm F:", self.c_arm_f)

        grp_fx_col = QGroupBox("Effects")
        f_fx_col = QFormLayout(grp_fx_col)
        f_fx_col.addRow("Ring Glow Alpha:", self.spin_glow_alpha)
        f_fx_col.addRow("Text Shadow Alpha:", self.spin_shadow_alpha)
        f_fx_col.addRow("Crosshair Color:", self.c_crosshair)

        v_col.addWidget(grp_core)
        v_col.addWidget(grp_arms)
        v_col.addWidget(grp_fx_col)
        v_col.addStretch()
        self.tabs.addTab(tab_colors, "Colors")
        
        # Pindahkan Cardinal ke Tab General
        v_general.insertWidget(1, grp_cardinal)

        # =================================================
        # BUTTON BAR (UNCHANGED)
        # =================================================
        btns = QHBoxLayout()
        self.btn_reset = QPushButton("Reset to Default")
        self.btn_export = QPushButton("Export JSON")
        self.btn_import = QPushButton("Import JSON")
        btns.addWidget(self.btn_reset)
        btns.addWidget(self.btn_export)
        btns.addWidget(self.btn_import)
        btns.addStretch()
        self.btn_apply = QPushButton("Apply")
        self.btn_ok = QPushButton("OK")
        self.btn_cancel = QPushButton("Cancel")
        btns.addWidget(self.btn_apply)
        btns.addWidget(self.btn_ok)
        btns.addWidget(self.btn_cancel)
        layout.addLayout(btns)

        # =================================================
        # SIGNALS (UNCHANGED)
        # =================================================
        self.btn_apply.clicked.connect(self.on_apply)
        self.btn_ok.clicked.connect(self.on_ok)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_reset.clicked.connect(self.on_reset_default)
        self.btn_export.clicked.connect(self.on_export_json)
        self.btn_import.clicked.connect(self.on_import_json)

        self.load_settings()
        self.chk_enable_hit_test.toggled.connect(self._on_toggle_hit_test)
        
        # Default: advanced hit test disabled
        self._set_hit_test_enabled(False)
        self.chk_enable_hit_test.setChecked(False)

        self.chk_show_crosshair.toggled.connect(self._update_crosshair_ui_state)
        self.cmb_crosshair_style.currentTextChanged.connect(self._update_crosshair_ui_state)
        self._update_crosshair_ui_state()

        self.cmb_mode.currentTextChanged.connect(self._update_mode_ui_state)
        self._update_mode_ui_state()
        

    # =================================================
    def load_settings(self):
        s = self.settings
        s.beginGroup(self.SETTINGS_GROUP)

        def _qs_int(key, default):
            v = s.value(key, None)
            return int(v) if v is not None else default

        def _qs_bool(key, default):
            v = s.value(key, None)
            if v is None:
                return default
            return str(v).lower() in ("1", "true", "yes", "on")

        def _qs_str(key, default):
            return str(s.value(key, default))

        # =================================================
        # MODE & BEHAVIOUR (RAW LOAD FROM SETTINGS)
        # =================================================
        self.cmb_mode.setCurrentText(_qs_str("mode", "NORMAL"))
        self.spin_multi_sector.setValue(_qs_int("multi_sector_count", 2))

        self.chk_snap.setChecked(_qs_bool("snap_enabled", True))
        self.spin_snap_step.setValue(_qs_int("snap_step_deg", 5))
        self.spin_hold_ms.setValue(_qs_int("hold_to_open_settings_ms", 1250))
        self.spin_hold_cancel_px.setValue(_qs_int("hold_cancel_threshold_px", 4))

        # Visibility
        self.chk_show_arms.setChecked(_qs_bool("show_arms", True))
        self.chk_show_arc.setChecked(_qs_bool("show_arc", True))
        self.chk_show_angle_text.setChecked(_qs_bool("show_angle_text", True))
        self.chk_show_cardinal.setChecked(_qs_bool("show_cardinal", True))
        self.chk_show_north_tri.setChecked(_qs_bool("show_north_triangle", True))
        

        # Text effects
        self.chk_outline_enabled.setChecked(_qs_bool("outline_enabled", True))
        self.chk_shadow_enabled.setChecked(_qs_bool("shadow_enabled", False))

        # =================================================
        # LABELS
        # =================================================
        self.edit_label_A.setText(_qs_str("label_A", "A"))
        self.edit_label_B.setText(_qs_str("label_B", "B"))
        self.edit_label_C.setText(_qs_str("label_C", "C"))
        self.edit_label_D.setText(_qs_str("label_D", "D"))
        self.edit_label_E.setText(_qs_str("label_E", "E"))
        self.edit_label_F.setText(_qs_str("label_F", "F"))


        # =================================================
        # VISUALS & HIT TEST
        # =================================================
        self.spin_hit_center.setValue(_qs_int("hit_center_px", 14))
        self.spin_hit_endpoint.setValue(_qs_int("hit_endpoint_px", 12))
        self.spin_hit_arm.setValue(_qs_int("hit_arm_line_px", 8))
        self.spin_hit_ring.setValue(_qs_int("hit_ring_px", 10))

        self.spin_center_dot.setValue(_qs_int("center_dot_radius_px", 6))
        self.spin_endpoint_dot.setValue(_qs_int("arm_endpoint_radius_px", 4))

        self.spin_tick_step.setValue(_qs_int("ring_tick_step_deg", 1))
        self.spin_major_tick.setValue(_qs_int("ring_major_tick_deg", 5))
        self.spin_label_step.setValue(_qs_int("ring_label_step_deg", 10))
        self.spin_arc_thickness.setValue(_qs_int("arc_line_width", 3))
        self.spin_angle_text_distance.setValue(_qs_int("angle_text_distance_px", 20))

        self.spin_angle_font.setValue(_qs_int("angle_font_size", 10))
        self.spin_label_font.setValue(_qs_int("label_font_size", 10))

        self.spin_arm_radius_min.setValue(_qs_int("arm_radius_min", 50))
        self.spin_ring_radius_min.setValue(_qs_int("ring_radius_min", 50))
        self.spin_ring_radius_max.setValue(_qs_int("ring_radius_max", 250))
        self.tool.ring_radius = _qs_int("ring_radius", 200)
                
        self.spin_cardinal_font.setValue(_qs_int("cardinal_font_size", 18))
        self.spin_cardinal_offset.setValue(_qs_int("cardinal_offset_px", 32))
        if not hasattr(self.tool, "north_triangle_size_px"):
            self.tool.north_triangle_size_px = 10

        self.tool.north_triangle_size_px = _qs_int("north_triangle_size_px", 8)

        # =================================================
        # COLORS
        # =================================================
        color_maps = [
            (self.c_ring, "color_ring", "#FFFF00"),
            (self.c_arc, "color_arc", "#FF8C00"),
            (self.c_arm_a, "color_arm_a", "#FF0000"),
            (self.c_arm_b, "color_arm_b", "#FFFF00"),
            (self.c_arm_c, "color_arm_c", "#00FF00"),
            (self.c_arm_d, "color_arm_d", "#FF007F"),
            (self.c_arm_e, "color_arm_e", "#FFA500"),
            (self.c_arm_f, "color_arm_f", "#0000FF"),
            (self.c_text, "color_text", "#FFFF00"),
        ]

        for btn, key, default in color_maps:
            val = QColor(_qs_str(key, default))
            btn._value = val.name()
            btn.setStyleSheet(
                f"background-color:{btn._value}; border: 1px solid #666;"
            )

        self.spin_glow_alpha.setValue(_qs_int("ring_glow_alpha", 200))
        self.spin_shadow_alpha.setValue(_qs_int("text_shadow_alpha", 120))

        s.endGroup()

        # =================================================
        # 🔒 FINAL UI MODE CONSISTENCY (POST-LOAD OVERRIDE)
        # =================================================
        mode = self.cmb_mode.currentText()

        if mode == "NORMAL":
            # NORMAL selalu 2 arms (UI only)
            self.spin_multi_sector.setValue(2)
            self.spin_multi_sector.setEnabled(False)

        elif mode == "SITE_AUDIT":
            # SITE_AUDIT selalu 3 arms
            self.spin_multi_sector.setValue(3)
            self.spin_multi_sector.setEnabled(False)

        elif mode == "MULTI":
            # MULTI bebas 3–6
            self.spin_multi_sector.setEnabled(True)

        else:
            # Defensive fallback
            self.spin_multi_sector.setEnabled(False)
        
        # =================================================
        # LOAD CROSSHAIR SETTINGS
        # =================================================
        self.chk_show_crosshair.setChecked(
            _qs_bool("show_crosshair", True)
        )

        style = _qs_str("crosshair_style", "plus").lower()
        if style == "dot":
            self.cmb_crosshair_style.setCurrentText("Dot")
        elif style == "none":
            self.cmb_crosshair_style.setCurrentText("None")
        else:
            self.cmb_crosshair_style.setCurrentText("Plus")

        self.spin_crosshair_size.setValue(
            _qs_int("crosshair_size_px", 20)
        )

        self.spin_crosshair_thickness.setValue(
            _qs_int("crosshair_thickness", 2)
        )

        col = QColor(_qs_str("crosshair_color", "#FFFF00"))
        self.c_crosshair._value = col.name()
        self.c_crosshair.setStyleSheet(
            f"background-color:{self.c_crosshair._value}; border: 1px solid #666;"
        )

        # enforce UI dependency after load
        self._update_crosshair_ui_state()


        
    # =================================================
    # CROSSHAIR UI STATE LOGIC
    # =================================================
    def _update_crosshair_ui_state(self):
        enabled = self.chk_show_crosshair.isChecked()
        style = self.cmb_crosshair_style.currentText()

        # master enable
        self.cmb_crosshair_style.setEnabled(enabled)
        self.spin_crosshair_size.setEnabled(enabled)
        self.spin_crosshair_thickness.setEnabled(enabled)
        self.c_crosshair.setEnabled(enabled)

        if not enabled:
            return

        # style-specific rules
        if style == "None":
            self.spin_crosshair_size.setEnabled(False)
            self.spin_crosshair_thickness.setEnabled(False)
            self.c_crosshair.setEnabled(False)

        elif style == "Dot":
            self.spin_crosshair_size.setEnabled(True)
            # thickness optional, keep enabled
            self.spin_crosshair_thickness.setEnabled(True)
            self.c_crosshair.setEnabled(True)

        else:  # Plus
            self.spin_crosshair_size.setEnabled(True)
            self.spin_crosshair_thickness.setEnabled(True)
            self.c_crosshair.setEnabled(True)

    
    def _set_hit_test_enabled(self, enabled: bool):
        for w in (
            self.spin_hit_center,
            self.spin_hit_endpoint,
            self.spin_hit_arm,
            self.spin_hit_ring,
        ):
            w.setEnabled(enabled)
    
    def _on_toggle_hit_test(self, checked: bool):
        if checked:
            ret = QMessageBox.warning(
                self,
                "Advanced Interaction Settings",
                "Hit Test Sensitivity affects how precisely the protractor responds to mouse interaction.\n\n"
                "Changing these values may make the tool harder to use or behave unexpectedly.\n\n"
                "This option is recommended for advanced users only.\n\n"
                "Do you want to continue?",
                QMessageBox.Yes | QMessageBox.Cancel,
                QMessageBox.Cancel
            )

            if ret != QMessageBox.Yes:
                self.chk_enable_hit_test.setChecked(False)
                return

        self._set_hit_test_enabled(checked)


    
    # =================================================
    # UI MODE STATE HANDLER
    # =================================================
    def _update_mode_ui_state(self):
        mode = self.cmb_mode.currentText()

        # helper: hide/show Multi Sector row cleanly
        def set_multi_sector_visible(visible: bool):
            self.spin_multi_sector.setVisible(visible)
            if hasattr(self, "lbl_multi_sector"):
                self.lbl_multi_sector.setVisible(visible)


        if mode == "NORMAL":
            # NORMAL → fixed 2 arms, no UI noise
            self.spin_multi_sector.setRange(2, 2)
            self.spin_multi_sector.setValue(2)
            self.spin_multi_sector.setEnabled(False)
            set_multi_sector_visible(False)

        elif mode == "SITE_AUDIT":
            # SITE_AUDIT → fixed 3 arms
            self.spin_multi_sector.setRange(3, 3)
            self.spin_multi_sector.setValue(3)
            self.spin_multi_sector.setEnabled(False)
            set_multi_sector_visible(False)

        elif mode == "MULTI":
            # MULTI → user-controlled
            self.spin_multi_sector.setRange(3, 6)
            self.spin_multi_sector.setEnabled(True)
            set_multi_sector_visible(True)

        else:
            self.spin_multi_sector.setEnabled(False)
            set_multi_sector_visible(False)



    
    def on_reset_default(self):
        s = self.settings
        s.beginGroup(self.SETTINGS_GROUP)
        s.remove("")  # Clear all

        # =====================
        # MODE
        # =====================
        s.setValue("mode", "NORMAL")
        s.setValue("multi_sector_count", 2)

        # =====================
        # BEHAVIOUR
        # =====================
        s.setValue("snap_enabled", True)
        s.setValue("snap_step_deg", 5)
        s.setValue("hold_to_open_settings_ms", 1250)
        s.setValue("hold_cancel_threshold_px", 4)

        # =====================
        # VISIBILITY
        # =====================
        s.setValue("show_arms", True)
        s.setValue("show_arc", True)
        s.setValue("show_angle_text", True)
        s.setValue("show_cardinal", True)
        s.setValue("show_north_triangle", True)
        s.setValue("show_crosshair", True)

        # =====================
        # CARDINAL
        # =====================
        s.setValue("cardinal_font_size", 18)
        s.setValue("cardinal_offset_px", 60)
        s.setValue("north_triangle_size_px", 8)

        # =====================
        # HIT TEST
        # =====================
        s.setValue("hit_center_px", 14)
        s.setValue("hit_endpoint_px", 12)
        s.setValue("hit_arm_line_px", 8)
        s.setValue("hit_ring_px", 10)

        # =====================
        # GEOMETRY
        # =====================
        s.setValue("arm_radius_max", 600)
        s.setValue("arm_line_width", 5)
        s.setValue("ring_line_width", 3)
        s.setValue("ring_radius", 200)
        s.setValue("center_dot_radius_px", 6)
        s.setValue("arm_endpoint_radius_px", 4)
        s.setValue("arm_radius_min", 50)
        s.setValue("ring_radius_min", 50)
        s.setValue("ring_radius_max", 250)

        # =====================
        # RING & TICKS
        # =====================
        s.setValue("ring_tick_step_deg", 1)
        s.setValue("ring_major_tick_deg", 5)
        s.setValue("ring_label_step_deg", 10)
        s.setValue("arc_line_width", 3)
        s.setValue("angle_text_distance_px", 20)

        # =====================
        # FONT
        # =====================
        s.setValue("angle_font_size", 10)
        s.setValue("label_font_size", 10)

        # =====================
        # TEXT EFFECTS
        # =====================
        s.setValue("outline_enabled", True)
        s.setValue("shadow_enabled", False)
        s.setValue("text_shadow_alpha", 120)

        # =====================
        # COLORS
        # =====================
        s.setValue("color_ring", "#ffff00")
        s.setValue("color_arc", "#ff8c00")
        s.setValue("color_text", "#ffff00")

        s.setValue("color_arm_a", "#ff0000")
        s.setValue("color_arm_b", "#ffff00")
        s.setValue("color_arm_c", "#00ff00")
        s.setValue("color_arm_d", "#ff007f")
        s.setValue("color_arm_e", "#ffa500")
        s.setValue("color_arm_f", "#0000ff")

        s.setValue("ring_glow_alpha", 255)

        # =====================
        # CROSSHAIR
        # =====================
        s.setValue("crosshair_style", "plus")
        s.setValue("crosshair_size_px", 20)
        s.setValue("crosshair_thickness", 2)
        s.setValue("crosshair_color", "#ffff00")

        # =====================
        # ARM DEFAULTS
        # =====================
        angles = [0.0, 120.0, 240.0, 60.0, 180.0, 300.0]
        colors = ["#ff0000", "#ffff00", "#00ff00", "#ff007f", "#ffa500", "#0000ff"]

        for i in range(6):
            s.setValue(f"arm_{i}_angle", angles[i])
            s.setValue(f"arm_{i}_color", colors[i])
            s.setValue(f"arm_{i}_enabled", i < 2)
            s.setValue(f"arm_{i}_radius", 240)

        s.endGroup()

        self.load_settings()
        self.tool.apply_settings({"mode": "NORMAL"})
    
    def on_export_json(self):
        import json
        from qgis.PyQt.QtWidgets import QFileDialog

        path, _ = QFileDialog.getSaveFileName(
            self, "Export Protractor Settings", "", "JSON (*.json)"
        )
        if not path:
            return

        try:
            s = self.settings
            s.beginGroup(self.SETTINGS_GROUP)

            data = {}
            for key in s.childKeys():
                data[key] = s.value(key)

            s.endGroup()

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            QMessageBox.information(
                self,
                "Export Successful",
                f"Settings successfully exported to:\n{path}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export settings.\n\nError:\n{e}"
            )


    
    def on_import_json(self):
        import json
        from qgis.PyQt.QtWidgets import QFileDialog

        path, _ = QFileDialog.getOpenFileName(
            self, "Import Protractor Settings", "", "JSON (*.json)"
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                raise ValueError("Invalid JSON format (root must be an object).")

            s = self.settings
            s.beginGroup(self.SETTINGS_GROUP)
            for k, v in data.items():
                s.setValue(k, v)
            s.endGroup()

            # reload dialog UI
            self.load_settings()

            # apply live to tool
            self.tool.apply_settings(data)

            QMessageBox.information(
                self,
                "Import Successful",
                f"Settings successfully imported from:\n{path}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Failed",
                f"Failed to import settings.\n\nError:\n{e}"
            )




    def collect(self):
        data = {
            # =====================
            # MODE
            # =====================
            "mode": self.cmb_mode.currentText(),
            "multi_sector_count": self.spin_multi_sector.value(),

            # =====================
            # BEHAVIOUR
            # =====================
            "snap_enabled": self.chk_snap.isChecked(),
            "snap_step_deg": self.spin_snap_step.value(),
            "hold_to_open_settings_ms": self.spin_hold_ms.value(),
            "hold_cancel_threshold_px": self.spin_hold_cancel_px.value(),

            # =====================
            # VISIBILITY
            # =====================
            "show_arms": self.chk_show_arms.isChecked(),
            "show_arc": self.chk_show_arc.isChecked(),
            "show_angle_text": self.chk_show_angle_text.isChecked(),
            "show_cardinal": self.chk_show_cardinal.isChecked(),
            "show_north_triangle": self.chk_show_north_tri.isChecked(),
            "cardinal_font_size": self.spin_cardinal_font.value(),
            "cardinal_offset_px": self.spin_cardinal_offset.value(),


            # =====================
            # TEXT EFFECTS
            # =====================
            "outline_enabled": self.chk_outline_enabled.isChecked(),
            "shadow_enabled": self.chk_shadow_enabled.isChecked(),

            # =====================
            # HIT TEST
            # =====================
            "hit_center_px": self.spin_hit_center.value(),
            "hit_endpoint_px": self.spin_hit_endpoint.value(),
            "hit_arm_line_px": self.spin_hit_arm.value(),
            "hit_ring_px": self.spin_hit_ring.value(),

            # =====================
            # ADVANCED VISUAL
            # =====================
            "center_dot_radius_px": self.spin_center_dot.value(),
            "arm_endpoint_radius_px": self.spin_endpoint_dot.value(),
            "ring_tick_step_deg": self.spin_tick_step.value(),
            "ring_major_tick_deg": self.spin_major_tick.value(),
            "ring_label_step_deg": self.spin_label_step.value(),
            "arc_line_width": self.spin_arc_thickness.value(),
            "angle_text_distance_px": self.spin_angle_text_distance.value(),
            "angle_font_size": self.spin_angle_font.value(),
            "label_font_size": self.spin_label_font.value(),
            "arm_radius_min": self.spin_arm_radius_min.value(),
            "arm_radius_max": self.tool.arm_radius_max,
            "arm_line_width": self.tool.arm_line_width,
            "ring_radius_min": self.spin_ring_radius_min.value(),
            "ring_radius_max": self.spin_ring_radius_max.value(),
            "ring_line_width": self.tool.ring_line_width,

            # =====================
            # COLORS
            # =====================
            "color_ring": self.c_ring._value,
            "color_arc": self.c_arc._value,
            "color_arm_a": self.c_arm_a._value,
            "color_arm_b": self.c_arm_b._value,
            "color_arm_c": self.c_arm_c._value,
            "color_arm_d": self.c_arm_d._value,
            "color_arm_e": self.c_arm_e._value,
            "color_arm_f": self.c_arm_f._value,
            "color_text": self.c_text._value,

            "ring_glow_alpha": self.spin_glow_alpha.value(),
            "text_shadow_alpha": self.spin_shadow_alpha.value(),

            # =====================
            # 🔥 CROSSHAIR (NEW)
            # =====================
            "show_crosshair": self.chk_show_crosshair.isChecked(),
            "crosshair_style": self.cmb_crosshair_style.currentText().lower(),
            "crosshair_size_px": self.spin_crosshair_size.value(),
            "crosshair_thickness": self.spin_crosshair_thickness.value(),
            "crosshair_color": self.c_crosshair._value,
        }

        # =====================
        # OPTIONAL COLORS (DEFENSIVE)
        # =====================
        if hasattr(self, "c_outline"):
            data["color_outline"] = self.c_outline._value

        if hasattr(self, "c_shadow"):
            data["color_shadow"] = self.c_shadow._value

        # =====================
        # LABELS
        # =====================
        for lbl in ["A", "B", "C", "D", "E", "F"]:
            edit = getattr(self, f"edit_label_{lbl}", None)
            if edit:
                data[f"label_{lbl}"] = edit.text().strip() or lbl

        return data
    

    def on_apply(self):
        data = self.collect()
        s = self.settings
        s.beginGroup(self.SETTINGS_GROUP)

        # =====================
        # SAVE ALL SETTINGS FROM UI
        # =====================
        # ⚠️ JANGAN FILTER KEY
        # semua field dari collect() harus disimpan
        for k, v in data.items():
            s.setValue(k, v)

        # =====================
        # SAVE MODE STATE (EXPLICIT)
        # =====================
        # (hindari bug mode revert)
        if "mode" in data:
            s.setValue("mode", data["mode"])

        if "multi_sector_count" in data:
            s.setValue("multi_sector_count", int(data["multi_sector_count"]))

        # =====================
        # SAVE ARM STATE (STEP 21 FINAL)
        # =====================
        tool = self.tool

        # pastikan arm model tersedia
        if hasattr(tool, "_init_arms_if_needed"):
            tool._init_arms_if_needed()

        for idx, arm in enumerate(getattr(tool, "arms", [])):
            # angle
            s.setValue(
                f"arm_{idx}_angle",
                float(arm.get("angle_deg", 0.0))
            )

            # radius (hanya valid)
            rad = arm.get("radius_px", 0)
            if rad and rad > 0:
                s.setValue(f"arm_{idx}_radius", int(rad))

            # enabled
            s.setValue(
                f"arm_{idx}_enabled",
                bool(arm.get("enabled", False))
            )

            # color (🔥 WAJIB agar advanced visual sinkron)
            col = arm.get("color")
            if col is not None:
                try:
                    s.setValue(f"arm_{idx}_color", col.name())
                except Exception:
                    pass

        s.endGroup()

        # =====================
        # APPLY TO RUNTIME (SETELAH SAVE)
        # =====================
        # ⚠️ KRITIS: apply_settings HARUS pakai data hasil collect
        self.tool.apply_settings(data)




    def on_ok(self):
        self.on_apply()
        self.accept()
