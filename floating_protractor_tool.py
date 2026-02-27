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

from qgis.PyQt.QtCore import Qt, QPointF, QSettings, QTimer
from qgis.PyQt.QtGui import QGuiApplication
from qgis.gui import QgsMapTool
import math

from .floating_protractor_overlay import FloatingProtractorOverlay
from .floating_protractor_settings_dialog import FloatingProtractorSettingsDialog


class FloatingProtractorMapTool(QgsMapTool):

    HANDLE_NONE = 0
    HANDLE_CENTER_MOVE = 1
    HANDLE_ARM_A_ROTATE = 2
    HANDLE_ARM_B_ROTATE = 3
    HANDLE_ARM_A_RESIZE = 4
    HANDLE_ARM_B_RESIZE = 5
    HANDLE_ROTATE_BOTH = 6
    HANDLE_RING_RESIZE = 7

    SETTINGS_GROUP = "FloatingProtractor"

    ARM_RADIUS_MIN = 50
    RING_RADIUS_MIN = 40
    RING_RADIUS_MAX = 250

    def __init__(self, iface):
        super().__init__(iface.mapCanvas())
        self.canvas = iface.mapCanvas()
        self.iface = iface

        # =====================
        # LOAD SETTINGS
        # =====================
        s = QSettings()
        s.beginGroup(self.SETTINGS_GROUP)
        
        # =====================
        # CARDINAL DIRECTIONS (STEP 3)
        # =====================
        self.show_cardinal = True
        self.show_north_triangle = True

        self.cardinal_font_size = 11
        self.cardinal_offset_px = 18     # jarak ke dalam ring
        self.north_triangle_size_px = 7  # tinggi segitiga


        # =====================
        # SAFE INT READER
        # =====================
        def _qs_int(key, default):
            try:
                v = s.value(key, None)
                if v is None:
                    return default
                return int(v)
            except Exception:
                return default

        # =====================
        # ARM LABELS
        # =====================
        self.arm_labels = [
            s.value("label_A", "A"),
            s.value("label_B", "B"),
            s.value("label_C", "C"),
            s.value("label_D", "D"),
            s.value("label_E", "E"),
            s.value("label_F", "F"),
        ]

        # =====================
        # MODE STATE
        # =====================
        self.mode = s.value("mode", "NORMAL")
        self.multi_sector_count = _qs_int("multi_sector_count", 3)

        # =====================
        # BEHAVIOUR (PATCHED: Visibility Checkboxes)
        # =====================
        self.snap_enabled = str(s.value("snap_enabled", "true")).lower() == "true"
        self.snap_step = _qs_int("snap_step_deg", 5)

        # ✅ FIX: Memastikan status checkbox dibaca saat reload
        self.show_arms = str(s.value("show_arms", "true")).lower() == "true"
        self.show_arc = str(s.value("show_arc", "true")).lower() == "true"
        self.show_angle_text = str(s.value("show_angle_text", "true")).lower() == "true"
        
        # 🔥 NEW: Load text effects settings
        self.outline_enabled = str(s.value("outline_enabled", "true")).lower() == "true"
        self.shadow_enabled = str(s.value("shadow_enabled", "true")).lower() == "true"

        # 🔥 FIX UTAMA (Hold Time)
        self.hold_to_open_settings_ms = _qs_int("hold_to_open_settings_ms", 1500)
        if self.hold_to_open_settings_ms < 500:
            self.hold_to_open_settings_ms = 500

        self.hold_cancel_threshold_px = _qs_int("hold_cancel_threshold_px", 4)

        # =====================
        # GEOMETRY
        # =====================
        self.arm_radius_min = _qs_int("arm_radius_min", 50)
        self.arm_radius_max = _qs_int("arm_radius_max", 600)

        self.ring_radius = _qs_int("ring_radius", 200)
        self.ring_radius_min = _qs_int("ring_radius_min", 40)
        self.ring_radius_max = _qs_int("ring_radius_max", 250)

        self.arm_line_width = _qs_int("arm_line_width", 5)
        self.ring_line_width = _qs_int("ring_line_width", 3)

        self.arm_a_radius = _qs_int("arm_a_radius", 90)
        self.arm_b_radius = _qs_int("arm_b_radius", 120)

        # =====================
        # HIT TEST
        # =====================
        self.hit_center = _qs_int("hit_center_px", 14)
        self.hit_endpoint = _qs_int("hit_endpoint_px", 12)
        self.hit_arm_line = _qs_int("hit_arm_line_px", 8)
        self.hit_ring = _qs_int("hit_ring_px", 10)

        # =====================
        # VISUAL
        # =====================
        self.center_dot_radius_px = _qs_int("center_dot_radius_px", 6)
        self.arm_endpoint_radius_px = _qs_int("arm_endpoint_radius_px", 4)

        self.ring_tick_step_deg = _qs_int("ring_tick_step_deg", 1)
        self.ring_major_tick_deg = _qs_int("ring_major_tick_deg", 5)
        self.ring_label_step_deg = _qs_int("ring_label_step_deg", 10)

        self.angle_font_size = _qs_int("angle_font_size", 10)
        self.label_font_size = _qs_int("label_font_size", 10)
        
        self.arc_line_width = _qs_int("arc_line_width", 3)
        self.angle_text_distance_px = _qs_int("angle_text_distance_px", 20)


        # =====================
        # COLORS (PATCHED: Default Colors A=Red, B=Yellow)
        # =====================
        from qgis.PyQt.QtGui import QColor

        self.color_ring = QColor(s.value("color_ring", "#FFFF00"))
        self.color_arc = QColor(s.value("color_arc", "#FF8C00"))
        # Default Arm A: Merah, B: Kuning sesuai permintaan
        self.color_arm_a = QColor(s.value("color_arm_a", "#FF0000"))
        self.color_arm_b = QColor(s.value("color_arm_b", "#FFFF00"))
        self.color_text = QColor(s.value("color_text", "#FFFF00"))
        self.color_outline = QColor(s.value("color_outline", "#000000"))
        self.color_shadow = QColor(s.value("color_shadow", "#000000"))

        self.ring_glow_alpha = _qs_int("ring_glow_alpha", 255)
        self.text_shadow_alpha = _qs_int("text_shadow_alpha", 120)
        
        # =====================
        # CROSSHAIR STATE (NEW)
        # =====================
        self.show_crosshair = str(
            s.value("show_crosshair", "true")
        ).lower() == "true"

        self.crosshair_style = str(
            s.value("crosshair_style", "plus")
        ).lower()

        self.crosshair_size_px = _qs_int(
            "crosshair_size_px", 18
        )

        self.crosshair_thickness = _qs_int(
            "crosshair_thickness", 1
        )

        try:
            self.crosshair_color = QColor(
                s.value("crosshair_color", self.color_ring.name())
            )
        except Exception:
            self.crosshair_color = QColor(self.color_ring)

        
        # =====================
        # LOAD ARM STATE CACHE
        # =====================
        self._arm_state_cache = []
        for i in range(6):
            enabled_val = s.value(f"arm_{i}_enabled", None)
            if enabled_val in ("true", "True", True):
                enabled_val = True
            elif enabled_val in ("false", "False", False):
                enabled_val = False
            else:
                enabled_val = None

            self._arm_state_cache.append({
                "angle": s.value(f"arm_{i}_angle", None, float),
                "radius": s.value(f"arm_{i}_radius", None, float),
                "enabled": enabled_val,
                "color": s.value(f"arm_{i}_color", None),
            })

        s.endGroup()

        # =====================
        # STATE
        # =====================
        self.center = None
        self.arm_a_angle = 0.0
        self.arm_b_angle = 90.0

        self.active_handle = self.HANDLE_NONE
        self.last_mouse = None
        self.is_free_mode = False
        self.hover_handle = self.HANDLE_NONE

        self._holding_center = False
        self._hold_start_pos = None

        self.hold_timer = QTimer()
        self.hold_timer.setSingleShot(True)
        self.hold_timer.timeout.connect(self.open_settings_dialog)

        # =====================
        # ARM MODEL
        # =====================
        self.arms = []
        self.arms_initialized = False

        # =====================
        # OVERLAY
        # =====================
        self.overlay = FloatingProtractorOverlay(self.canvas, self)
        self.overlay.setVisible(False)
        
        # =================================================
        # FORCE LOAD CURRENT SETTINGS ON INIT
        # =================================================
        self._load_settings_from_qsettings()
    
    
    def _init_arms_if_needed(self):
        if self.arms_initialized:
            return

        from qgis.PyQt.QtGui import QColor
        from qgis.PyQt.QtCore import QSettings

        self.arms = []
        arm_ids = "ABCDEF"

        # Preset Defaults (ANGLE & COLOR ONLY)
        default_angles = [0.0, 120.0, 240.0, 60.0, 180.0, 300.0]
        default_colors = ["#FF0000", "#FFFF00", "#00FF00", "#FF007F", "#FFA500", "#0000FF"]

        s = QSettings()
        s.beginGroup(self.SETTINGS_GROUP)

        for idx, aid in enumerate(arm_ids):
            # =========================
            # LOAD STATE FROM SETTINGS
            # =========================

            # Angle
            q_angle = s.value(f"arm_{idx}_angle", default_angles[idx], type=float)

            # Color
            q_color = s.value(f"arm_{idx}_color", default_colors[idx])

            # Enabled
            q_enabled_raw = s.value(f"arm_{idx}_enabled", None)
            if q_enabled_raw is None:
                q_enabled = False
            else:
                q_enabled = str(q_enabled_raw).lower() == "true"

            # Radius (SAFE DEFAULT)
            q_radius = s.value(f"arm_{idx}_radius", None)
            if q_radius is not None:
                try:
                    q_radius = int(q_radius)
                except Exception:
                    q_radius = None

            # =========================
            # 🔒 SOLID DEFAULT RADIUS
            # =========================
            if q_radius is None:
                q_radius = self.clamp(
                    self.ring_radius,
                    self.arm_radius_min,
                    self.arm_radius_max
                )
            
            
            self.arms.append({
                "id": aid,
                "index": idx,
                "angle_deg": q_angle,
                "radius_px": q_radius,   # <-- TIDAK PERNAH None
                "color": QColor(q_color),
                "enabled": q_enabled,
                "rotatable": True,
                "initialized": True
            })

        s.endGroup()

        # Sync legacy helper attributes
        if len(self.arms) >= 2:
            self.arm_a_angle = self.arms[0]["angle_deg"]
            self.arm_b_angle = self.arms[1]["angle_deg"]

        self.arms_initialized = True



    
    def apply_mode_preset(self, mode, sector_count=None):
        self._init_arms_if_needed()
        mode = (mode or "NORMAL").upper()
        
        # Hitung berapa arm yang aktif
        if mode == "NORMAL":
            active_limit = 2
        elif mode == "SITE_AUDIT":
            active_limit = 3
        else: # MULTI
            active_limit = int(sector_count or 3)

        default_angles = [0.0, 120.0, 240.0, 60.0, 180.0, 300.0]

        for idx, arm in enumerate(self.arms):
            if idx < active_limit:
                arm["enabled"] = True
                # Jika di mode MULTI dan arm baru saja diaktifkan, gunakan preset
                if mode == "MULTI" and not arm.get("initialized_multi"):
                    arm["angle_deg"] = default_angles[idx]
                    arm["initialized_multi"] = True
            else:
                arm["enabled"] = False

        # ✅ FIXED: Baris self.show_arc = (mode == "NORMAL") DIHAPUS 
        # agar tidak menimpa pilihan pengguna dari checkbox.

    
    # =====================
    # Tool lifecycle
    # =====================
    def deactivate(self):
        """
        Tool deactivated (e.g. switch to Pan Map).
        Keep protractor visible, disable interaction only.
        """
        self.hold_timer.stop()
        self._holding_center = False
        self._hold_start_pos = None

        self.active_handle = self.HANDLE_NONE
        self.last_mouse = None
        self.is_free_mode = False

        super().deactivate()



    def activate(self):
        """
        Called when protractor tool becomes active again.
        Restore overlay if protractor already exists.
        """
        super().activate()

        # =====================
        # PHASE 1 INIT (SAFE)
        # =====================
        # DO NOT init arms here
        # wait until first click (center defined)
        # One-time legacy → arm model migration
        # self._init_arms_if_needed()

        # Apply mode preset (does NOT change visuals in Phase 1)
        # self.apply_mode_preset(self.mode, self.multi_sector_count)

        if self.center is not None:
            self.overlay.prepareGeometryChange()
            self.overlay.setVisible(True)
            self.overlay.update()


    # =====================
    # Mouse Events
    # =====================
    def canvasPressEvent(self, event):
        pos = QPointF(event.pos())

        # First click → create protractor
        if self.center is None:
            self.center = pos

            from qgis.PyQt.QtCore import QSettings
            s = QSettings()
            s.beginGroup(self.SETTINGS_GROUP)

            # =====================
            # RESTORE RING
            # =====================
            self.ring_radius = s.value("ring_radius", self.ring_radius, int)

            # =====================
            # RESTORE ARM SNAPSHOT
            # =====================
            arm_snapshot = []
            for i in range(6):
                arm_snapshot.append({
                    "angle": s.value(f"arm_{i}_angle", None),
                    "radius": s.value(f"arm_{i}_radius", None),
                    "enabled": s.value(f"arm_{i}_enabled", None),
                    "color": s.value(f"arm_{i}_color", None),
                })

            s.endGroup()

            # =====================
            # INIT ARM MODEL (ONCE)
            # =====================
            self._init_arms_if_needed()
            
            # =====================
            # APPLY MODE PRESET (FIX NORMAL ARM NOT SHOWING)
            # =====================
            self.apply_mode_preset(self.mode, self.multi_sector_count)

            # =====================
            # APPLY SNAPSHOT (SAFE)
            # =====================
            for idx, arm in enumerate(self.arms):
                snap = arm_snapshot[idx]

                # enabled
                if snap["enabled"] is not None:
                    arm["enabled"] = str(snap["enabled"]).lower() == "true"

                # angle
                if snap["angle"] is not None:
                    try:
                        arm["angle_deg"] = float(snap["angle"])
                    except Exception:
                        pass

                # radius (🔥 FIX UTAMA)
                raw_radius = None
                if snap["radius"] is not None:
                    try:
                        raw_radius = int(snap["radius"])
                    except Exception:
                        raw_radius = None

                if raw_radius is None:
                    raw_radius = self.ring_radius

                arm["radius_px"] = self.clamp(
                    raw_radius,
                    self.arm_radius_min,
                    self.arm_radius_max
                )

                # color
                if snap["color"] is not None:
                    try:
                        from qgis.PyQt.QtGui import QColor
                        arm["color"] = QColor(snap["color"])
                    except Exception:
                        pass

            # sync helper fields
            if len(self.arms) >= 2:
                self.arm_a_angle = self.arms[0]["angle_deg"]
                self.arm_b_angle = self.arms[1]["angle_deg"]

            self.overlay.prepareGeometryChange()
            self.overlay.setVisible(True)
            self.overlay.update()
            return
        
        # =====================
        # RIGHT CLICK HANDLING (FIXED)→ CONTEXT MENU (STEP 1)
        # =====================
        if event.button() == Qt.RightButton:
            # PRIORITY 1: CENTER → RESIZE RING (OLD BEHAVIOR)
            if self.dist(pos, self.center) <= self.hit_center:
                self.active_handle = self.HANDLE_RING_RESIZE
                self.last_mouse = pos
                return

            # PRIORITY 2: RING → CONTEXT MENU
            if abs(self.dist(pos, self.center) - self.ring_radius) <= self.hit_ring:
                self._showContextMenu(event)
                return


        
        # =====================
        # MARK INTERACTION START
        # =====================
        self._is_interacting = True
        self.overlay.prepareGeometryChange()

        # =====================
        # CENTER
        # =====================
        if self.dist(pos, self.center) <= self.hit_center:
            if event.button() == Qt.LeftButton:
                self.active_handle = self.HANDLE_CENTER_MOVE
                self.last_mouse = pos

                self._holding_center = True
                self._hold_start_pos = pos
                self.hold_timer.start(self.hold_to_open_settings_ms)
                return

            elif event.button() == Qt.RightButton:
                self.active_handle = self.HANDLE_RING_RESIZE
                self.last_mouse = pos
                return

        # =====================
        # MULTI-ARM HIT TEST
        # =====================
        best_arm = None
        best_dist = None
        best_mode = None

        for idx, arm in enumerate(getattr(self, "arms", [])):
            if not arm.get("enabled") or not arm.get("rotatable"):
                continue

            radius = arm.get("radius_px")
            if radius is None:
                continue  # 🔒 HARD GUARD

            ang = arm["angle_deg"]
            rad = math.radians(ang)

            end = QPointF(
                self.center.x() + radius * math.sin(rad),
                self.center.y() - radius * math.cos(rad)
            )

            d_ep = self.dist(pos, end)
            if d_ep <= self.hit_endpoint:
                if best_dist is None or d_ep < best_dist:
                    best_arm = idx
                    best_dist = d_ep
                    best_mode = "endpoint"
                continue

            d_ln = self.point_to_line_dist(pos, self.center, end)
            if d_ln <= self.hit_arm_line:
                if best_dist is None or d_ln < best_dist:
                    best_arm = idx
                    best_dist = d_ln
                    best_mode = "line"

        if best_arm is not None:
            self.active_arm_index = best_arm
            self.last_mouse = pos
            self.active_handle = (
                self.HANDLE_ARM_A_RESIZE if best_mode == "endpoint"
                else self.HANDLE_ARM_A_ROTATE
            )
            return

        # =====================
        # RING → ROTATE BOTH
        # =====================
        if abs(self.dist(pos, self.center) - self.ring_radius) <= self.hit_ring:
            self.active_handle = self.HANDLE_ROTATE_BOTH
            self.last_mouse = pos




    def canvasMoveEvent(self, event):
        if self.center is None:
            return

        # 🔥 PENTING: beri tahu QGIS geometry berubah
        self.overlay.prepareGeometryChange()
        pos = QPointF(event.pos())

        # =====================
        # HOVER DETECTION
        # =====================
        self.hover_handle = self.HANDLE_NONE
        tooltip = ""
        cursor = Qt.ArrowCursor

        if self.dist(pos, self.center) <= self.hit_center:
            self.hover_handle = self.HANDLE_CENTER_MOVE
            tooltip = "Move Protractor (Hold = Settings)"
            cursor = Qt.SizeAllCursor
        else:
            for idx, arm in enumerate(getattr(self, "arms", [])):
                if not arm.get("enabled") or not arm.get("rotatable"):
                    continue

                ang = arm.get("angle_deg", 0.0)
                rad = math.radians(ang)

                # ===============================
                # 🔒 SAFETY GUARD: radius valid
                # ===============================
                radius = arm.get("radius_px")
                if radius is None:
                    radius = self.ring_radius

                if radius is None:
                    continue  # hard guard, jangan crash

                end = QPointF(
                    self.center.x() + radius * math.sin(rad),
                    self.center.y() - radius * math.cos(rad)
                )

                if self.dist(pos, end) <= self.hit_endpoint:
                    self.hover_handle = self.HANDLE_ARM_A_RESIZE
                    tooltip = f"Resize Arm {arm.get('id', '')}"
                    cursor = Qt.SizeVerCursor
                    break

                if self.point_to_line_dist(pos, self.center, end) <= self.hit_arm_line:
                    self.hover_handle = self.HANDLE_ARM_A_ROTATE
                    tooltip = f"Rotate Arm {arm.get('id', '')} (Shift = Free)"
                    cursor = Qt.CrossCursor
                    break

            if self.hover_handle == self.HANDLE_NONE:
                if (
                    self.ring_radius is not None and
                    abs(self.dist(pos, self.center) - self.ring_radius) <= self.hit_ring
                ):
                    self.hover_handle = self.HANDLE_ROTATE_BOTH
                    tooltip = "Rotate Both Arms / Resize Ring (RMB)"
                    cursor = Qt.OpenHandCursor

        self.canvas.setCursor(cursor)
        self.iface.mainWindow().statusBar().showMessage(tooltip)

        if self.active_handle == self.HANDLE_NONE:
            self.overlay.update()
            return

        # =====================
        # INTERACTION ACTIVE
        # =====================
        self._is_interacting = True

        # long-press guard
        if self._holding_center:
            if self.dist(pos, self._hold_start_pos) > self.hold_cancel_threshold_px:
                self._holding_center = False
                self.hold_timer.stop()
            else:
                return

        self.is_free_mode = bool(event.modifiers() & Qt.ShiftModifier)

        # =====================
        # MOVE / ROTATE / RESIZE
        # =====================
        if self.active_handle == self.HANDLE_CENTER_MOVE:
            self.center = pos

        elif self.active_handle == self.HANDLE_RING_RESIZE:
            dy = self.last_mouse.y() - pos.y()
            step = int(dy / 2)
            if step:
                self.ring_radius = self.clamp(
                    self.ring_radius + step,
                    self.ring_radius_min,
                    self.ring_radius_max
                )
                self.last_mouse = pos

        elif self.active_handle == self.HANDLE_ARM_A_ROTATE:
            arm = self.arms[self.active_arm_index]
            ang = self.bearing(self.center, pos)
            arm["angle_deg"] = ang if self.is_free_mode else self.snap(ang)

        elif self.active_handle == self.HANDLE_ROTATE_BOTH:
            a1 = self.bearing(self.center, self.last_mouse)
            a2 = self.bearing(self.center, pos)
            delta = a2 - a1
            delta = delta if self.is_free_mode else self.snap(delta)

            for arm in self.arms:
                if arm.get("enabled") and arm.get("rotatable"):
                    arm["angle_deg"] += delta

            self.last_mouse = pos

        elif self.active_handle == self.HANDLE_ARM_A_RESIZE:
            arm = self.arms[self.active_arm_index]
            arm["radius_px"] = self.clamp(
                self.dist(self.center, pos),
                self.arm_radius_min,
                self.arm_radius_max
            )

        self.overlay.update()




    def canvasReleaseEvent(self, event):
        # stop long-press
        self.hold_timer.stop()
        self._holding_center = False
        self._hold_start_pos = None

        # reset interaction state
        self.active_handle = self.HANDLE_NONE
        self.last_mouse = None
        self.is_free_mode = False

        # 🔥 END INTERACTION
        self._is_interacting = False

        # 🔥 geometry sudah stabil → refresh bounding
        self.overlay.prepareGeometryChange()

        if hasattr(self, "active_arm_index"):
            self.active_arm_index = None
        
        # =====================
        # AUTO PERSIST GEOMETRY
        # =====================
        from qgis.PyQt.QtCore import QSettings
        s = QSettings()
        s.beginGroup(self.SETTINGS_GROUP)

        # persist ring radius
        s.setValue("ring_radius", int(self.ring_radius))

        # persist arm radius & angle
        for idx, arm in enumerate(getattr(self, "arms", [])):
            if arm.get("enabled"):
                if arm.get("radius_px") is not None:
                    s.setValue(f"arm_{idx}_radius", int(arm["radius_px"]))
                s.setValue(f"arm_{idx}_angle", float(arm.get("angle_deg", 0.0)))

        s.endGroup()

        self.overlay.update()


    # =====================
    # SETTINGS
    # =====================
    def open_settings_dialog(self):
        self._holding_center = False
        self.active_handle = self.HANDLE_NONE
        dlg = FloatingProtractorSettingsDialog(self, self.iface.mainWindow())
        dlg.exec_()
    
    
    # =====================
    # CONTEXT MENU (RIGHT CLICK ON RING)
    # =====================
    def _showContextMenu(self, event):
        """
        Show quick context menu when user right-clicks on protractor ring.
        STEP 1 (Final):
        - Settings…
        - Mode: NORMAL
        - Mode: SITE_AUDIT (3 arms only)
        - Mode: MULTI → 4 / 5 / 6 Arms
        """

        if self.center is None:
            return

        pos = QPointF(event.pos())

        # klik harus tepat di area ring
        if abs(self.dist(pos, self.center) - self.ring_radius) > self.hit_ring:
            return

        from qgis.PyQt.QtWidgets import QMenu, QAction
        from qgis.PyQt.QtGui import QIcon
        import os

        menu = QMenu(self.canvas)
        plugin_dir = os.path.dirname(__file__)
        icon_dir = os.path.join(plugin_dir, "icon")

        # -----------------
        # Settings
        # -----------------
        act_settings = QAction(
            QIcon(os.path.join(icon_dir, "settings.svg")),
            "Settings…",
            self.canvas
        )
        
        act_settings.triggered.connect(self.open_settings_dialog)
        menu.addAction(act_settings)

        menu.addSeparator()

        # -----------------
        # Mode → NORMAL
        # -----------------
        act_normal = QAction(
            QIcon(os.path.join(icon_dir, "mode_normal.svg")),
            "Mode → NORMAL",
            self.canvas
        )
        act_normal.triggered.connect(
            lambda: self.apply_settings({"mode": "NORMAL"})
        )
        menu.addAction(act_normal)

        # -----------------
        # Mode → SITE_AUDIT (3 arms only)
        # -----------------
        act_site = QAction(
            QIcon(os.path.join(icon_dir, "mode_site_audit.svg")),
            "Mode → SITE_AUDIT (3 Arms)",
            self.canvas
        )
        act_site.triggered.connect(
            lambda: self.apply_settings({"mode": "SITE_AUDIT"})
        )
        menu.addAction(act_site)

        # -----------------
        # Mode → MULTI (Submenu)
        # -----------------
        menu_multi = QMenu("Mode → MULTI", menu)
        menu_multi.setIcon(
            QIcon(os.path.join(icon_dir, "mode_multi.svg"))
        )

        
        for arms in (4, 5, 6):

            if arms == 4:
                icon_name = "arms_4.svg"
            elif arms == 5:
                icon_name = "arms_5.svg"
            else:
                icon_name = "arms_6.svg"

            act = QAction(
                QIcon(os.path.join(icon_dir, icon_name)),
                f"{arms} Arms",
                self.canvas
            )

            act.triggered.connect(
                lambda checked=False, n=arms: self.apply_settings({
                    "mode": "MULTI",
                    "multi_sector_count": n
                })
            )

            menu_multi.addAction(act)
            
        menu.addMenu(menu_multi)
        
        # tampilkan menu
        menu.exec_(self.canvas.mapToGlobal(event.pos()))


    
    
    # =====================
    # APPLY SETTINGS (LIVE)
    # =====================
    def apply_settings(self, s):
        from qgis.PyQt.QtGui import QColor
        from qgis.PyQt.QtCore import QSettings

        # =====================
        # MODE STATE (TRACK OLD)
        # =====================
        old_mode = getattr(self, "mode", "NORMAL")
        old_sector_count = getattr(self, "multi_sector_count", 3)

        if "mode" in s:
            self.mode = s["mode"]

        if "multi_sector_count" in s:
            self.multi_sector_count = int(s["multi_sector_count"])

        # =====================
        # ARM LABELS
        # =====================
        if not hasattr(self, "arm_labels"):
            self.arm_labels = ["A", "B", "C", "D", "E", "F"]

        for idx, key in enumerate([f"label_{l}" for l in "ABCDEF"]):
            if key in s:
                val = str(s[key]).strip()
                self.arm_labels[idx] = val if val else self.arm_labels[idx]

        def to_int(v, default=0):
            try:
                return int(v)
            except Exception:
                return default

        # =====================
        # BEHAVIOUR
        # =====================
        if "snap_enabled" in s:
            self.snap_enabled = bool(s["snap_enabled"])

        if "snap_step_deg" in s:
            self.snap_step = to_int(s["snap_step_deg"], self.snap_step)

        if "hold_to_open_settings_ms" in s:
            self.hold_to_open_settings_ms = to_int(
                s["hold_to_open_settings_ms"],
                self.hold_to_open_settings_ms
            )

        if "hold_cancel_threshold_px" in s:
            self.hold_cancel_threshold_px = to_int(
                s["hold_cancel_threshold_px"],
                self.hold_cancel_threshold_px
            )

        # =====================
        # VISIBILITY
        # =====================
        if "show_arms" in s:
            self.show_arms = bool(s["show_arms"])

        if "show_arc" in s:
            self.show_arc = bool(s["show_arc"])

        if "show_angle_text" in s:
            self.show_angle_text = bool(s["show_angle_text"])

        if "outline_enabled" in s:
            self.outline_enabled = bool(s["outline_enabled"])

        if "shadow_enabled" in s:
            self.shadow_enabled = bool(s["shadow_enabled"])
        
        # =====================
        # CARDINAL DIRECTIONS (STEP 3)
        # =====================
        if "show_cardinal" in s:
            self.show_cardinal = bool(s["show_cardinal"])

        if "show_north_triangle" in s:
            self.show_north_triangle = bool(s["show_north_triangle"])
        
        if "north_triangle_size_px" in s:
            self.north_triangle_size_px = int(s["north_triangle_size_px"])

        if "cardinal_font_size" in s:
            self.cardinal_font_size = int(s["cardinal_font_size"])

        if "cardinal_offset_px" in s:
            self.cardinal_offset_px = int(s["cardinal_offset_px"])


        # =====================
        # HIT TEST
        # =====================
        if "hit_center_px" in s:
            self.hit_center = to_int(s["hit_center_px"], self.hit_center)

        if "hit_endpoint_px" in s:
            self.hit_endpoint = to_int(s["hit_endpoint_px"], self.hit_endpoint)

        if "hit_arm_line_px" in s:
            self.hit_arm_line = to_int(s["hit_arm_line_px"], self.hit_arm_line)

        if "hit_ring_px" in s:
            self.hit_ring = to_int(s["hit_ring_px"], self.hit_ring)

        # =====================
        # ADVANCED VISUAL
        # =====================
        if "center_dot_radius_px" in s:
            self.center_dot_radius_px = to_int(
                s["center_dot_radius_px"], self.center_dot_radius_px
            )

        if "arm_endpoint_radius_px" in s:
            self.arm_endpoint_radius_px = to_int(
                s["arm_endpoint_radius_px"], self.arm_endpoint_radius_px
            )
        
        if "ring_radius" in s:
            self.ring_radius = to_int(
                s["ring_radius"], self.ring_radius
            )
        
        if "ring_tick_step_deg" in s:
            self.ring_tick_step_deg = to_int(
                s["ring_tick_step_deg"], self.ring_tick_step_deg
            )

        if "ring_major_tick_deg" in s:
            self.ring_major_tick_deg = to_int(
                s["ring_major_tick_deg"], self.ring_major_tick_deg
            )

        if "ring_label_step_deg" in s:
            self.ring_label_step_deg = to_int(
                s["ring_label_step_deg"], self.ring_label_step_deg
            )

        if "angle_font_size" in s:
            self.angle_font_size = to_int(
                s["angle_font_size"], self.angle_font_size
            )

        if "label_font_size" in s:
            self.label_font_size = to_int(
                s["label_font_size"], self.label_font_size
            )

        if "arm_radius_min" in s:
            self.arm_radius_min = to_int(
                s["arm_radius_min"], self.arm_radius_min
            )
        
        if "arm_radius_max" in s:
            self.arm_radius_max = to_int(
                s["arm_radius_max"], self.arm_radius_max
            )
        
        if "ring_radius_min" in s:
            self.ring_radius_min = to_int(
                s["ring_radius_min"], self.ring_radius_min
            )

        if "ring_radius_max" in s:
            self.ring_radius_max = to_int(
                s["ring_radius_max"], self.ring_radius_max
            )

        if "arc_line_width" in s:
            self.arc_line_width = int(s["arc_line_width"])
            
        if "arm_line_width" in s:
            self.arm_line_width = int(s["arm_line_width"])
            
        if "ring_line_width" in s:
            self.ring_line_width = int(s["ring_line_width"])
            

        if "angle_text_distance_px" in s:
            self.angle_text_distance_px = int(s["angle_text_distance_px"])

        # =====================
        # COLORS
        # =====================
        if "color_ring" in s:
            self.color_ring = QColor(s["color_ring"])

        if "color_arc" in s:
            self.color_arc = QColor(s["color_arc"])

        if "color_text" in s:
            self.color_text = QColor(s["color_text"])

        if "color_outline" in s:
            self.color_outline = QColor(s["color_outline"])

        if "color_shadow" in s:
            self.color_shadow = QColor(s["color_shadow"])

        if "ring_glow_alpha" in s:
            self.ring_glow_alpha = to_int(
                s["ring_glow_alpha"], self.ring_glow_alpha
            )

        if "text_shadow_alpha" in s:
            self.text_shadow_alpha = to_int(
                s["text_shadow_alpha"], self.text_shadow_alpha
            )

        # =====================
        # CROSSHAIR
        # =====================
        if "show_crosshair" in s:
            self.show_crosshair = bool(s["show_crosshair"])

        if "crosshair_style" in s:
            self.crosshair_style = str(s["crosshair_style"]).lower()

        if "crosshair_size_px" in s:
            self.crosshair_size_px = to_int(
                s["crosshair_size_px"], self.crosshair_size_px
            )

        if "crosshair_thickness" in s:
            self.crosshair_thickness = to_int(
                s["crosshair_thickness"], self.crosshair_thickness
            )

        if "crosshair_color" in s:
            try:
                self.crosshair_color = QColor(s["crosshair_color"])
            except Exception:
                pass

        # =====================
        # ARM MODEL + COLORS
        # =====================
        self._init_arms_if_needed()

        arm_color_keys = [
            "color_arm_a",
            "color_arm_b",
            "color_arm_c",
            "color_arm_d",
            "color_arm_e",
            "color_arm_f",
        ]

        for idx, key in enumerate(arm_color_keys):
            if key in s and idx < len(self.arms):
                try:
                    self.arms[idx]["color"] = QColor(s[key])
                except Exception:
                    pass

        # =====================
        # MODE PRESET
        # =====================
        need_apply_preset = False

        if old_mode != self.mode:
            need_apply_preset = True

        if self.mode == "MULTI" and old_sector_count != self.multi_sector_count:
            need_apply_preset = True

        if need_apply_preset:
            self.apply_mode_preset(self.mode, self.multi_sector_count)

        # =====================
        # PERSIST ARM STATE (SAFE)
        # =====================
        qs = QSettings()
        qs.beginGroup(self.SETTINGS_GROUP)

        for idx, arm in enumerate(getattr(self, "arms", [])):
            qs.setValue(f"arm_{idx}_angle", float(arm.get("angle_deg", 0.0)))

            raw_radius = arm.get("radius_px")
            if raw_radius is None:
                raw_radius = self.ring_radius

            raw_radius = self.clamp(
                raw_radius,
                self.arm_radius_min,
                self.arm_radius_max
            )

            qs.setValue(f"arm_{idx}_radius", int(raw_radius))
            qs.setValue(
                f"arm_{idx}_enabled",
                bool(arm.get("enabled", False))
            )

            col = arm.get("color")
            if col is not None:
                qs.setValue(f"arm_{idx}_color", col.name())

        qs.endGroup()

        # =====================
        # REDRAW
        # =====================
        if self.overlay:
            self.overlay.update()

    
    def _load_settings_from_qsettings(self):
        """
        Ensure settings exist.
        If empty (after console reset), write default first.
        Then sync to runtime.
        """

        from qgis.PyQt.QtCore import QSettings

        s = QSettings()
        s.beginGroup(self.SETTINGS_GROUP)

        # =============================
        # If group empty → write defaults
        # =============================
        if not s.allKeys():
            s.setValue("mode", "NORMAL")
            s.setValue("multi_sector_count", 2)

            s.setValue("ring_radius", 200)
            s.setValue("arm_radius_min", 50)
            s.setValue("arm_radius_max", 600)

            s.setValue("cardinal_font_size", 18)
            s.setValue("cardinal_offset_px", 60)
            s.setValue("north_triangle_size_px", 8)

            s.setValue("show_cardinal", True)
            s.setValue("show_north_triangle", True)

            s.setValue("crosshair_size_px", 20)

            s.sync()

        def _qs_int(key, default):
            return int(s.value(key, default))

        def _qs_bool(key, default):
            return str(s.value(key, default)).lower() in ("true", "1")

        # =============================
        # Sync runtime
        # =============================
        self.mode = s.value("mode", "NORMAL")
        self.multi_sector_count = _qs_int("multi_sector_count", 2)

        self.ring_radius = _qs_int("ring_radius", 200)
        self.arm_radius_min = _qs_int("arm_radius_min", 50)
        self.arm_radius_max = _qs_int("arm_radius_max", 600)

        self.cardinal_font_size = _qs_int("cardinal_font_size", 18)
        self.cardinal_offset_px = _qs_int("cardinal_offset_px", 60)
        self.north_triangle_size_px = _qs_int("north_triangle_size_px", 8)

        self.show_cardinal = _qs_bool("show_cardinal", True)
        self.show_north_triangle = _qs_bool("show_north_triangle", True)

        self.crosshair_size_px = _qs_int("crosshair_size_px", 20)

        s.endGroup()

        
        if self.overlay:
            self.overlay.update()
    
    
    # =====================
    # Helpers
    # =====================
    def snap(self, angle):
        if not self.snap_enabled:
            return angle
        return round(angle / self.snap_step) * self.snap_step

    def arm_a_endpoint(self):
        return self.endpoint(self.arm_a_angle, self.arm_a_radius)

    def arm_b_endpoint(self):
        return self.endpoint(self.arm_b_angle, self.arm_b_radius)

    def endpoint(self, angle, radius):
        rad = math.radians(angle)
        return QPointF(
            self.center.x() + radius * math.sin(rad),
            self.center.y() - radius * math.cos(rad)
        )

    def bearing(self, p1, p2):
        dx = p2.x() - p1.x()
        dy = p1.y() - p2.y()
        return (math.degrees(math.atan2(dx, dy)) + 360) % 360

    def dist(self, p1, p2):
        return math.hypot(p1.x() - p2.x() - 0, p1.y() - p2.y() - 0)

    def clamp(self, v, vmin, vmax):
        return max(vmin, min(vmax, v))

    def point_to_line_dist(self, p, a, b):
        px, py = p.x(), p.y()
        ax, ay = a.x(), a.y()
        bx, by = b.x(), b.y()
        dx, dy = bx - ax, by - ay
        if dx == 0 and dy == 0:
            return self.dist(p, a)
        t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
        t = max(0, min(1, t))
        proj = QPointF(ax + t * dx, ay + t * dy)
        return self.dist(p, proj)

    def keyPressEvent(self, event):
        # =====================
        # RESET CEPAT (Shortcut: R) → Reset ke default settings
        # TOGGLE SNAP (Shortcut: S) → Menampilkan Snap degrees      
        # =====================

        if event.key() == Qt.Key_S:
            self.snap_enabled = not self.snap_enabled

            # optional: feedback ringan (status bar, tidak ke canvas)
            state = "ON" if self.snap_enabled else "OFF"
            try:
                self.iface.statusBarIface().showMessage(
                    f"Protractor Snap {state} ({self.snap_step}°)", 2000
                )
            except Exception:
                pass

            self.overlay.update()
            return
            
        if event.key() == Qt.Key_R and self.center is not None:
            s = QSettings()
            s.beginGroup(self.SETTINGS_GROUP)

            self.ring_radius = s.value("ring_radius", 100, int)
            self.arm_a_radius = s.value("arm_a_radius", 90, int)
            self.arm_b_radius = s.value("arm_b_radius", 120, int)

            self.arm_a_angle = 0.0
            self.arm_b_angle = 90.0

            s.endGroup()

            # bounding berubah → wajib
            self.overlay.prepareGeometryChange()
            self.overlay.update()
            return

        # =====================
        # CLEAR PROTRACTOR (ESC)
        # =====================
        if event.key() == Qt.Key_Escape and self.center is not None:
            self.overlay.prepareGeometryChange()
            self.center = None
            self.overlay.setVisible(False)
            self.overlay.update()

            # 🔥 switch back to Pan tool
            self.iface.actionPan().trigger()
            # 🔥 force uncheck protractor toolbar button
            if hasattr(self, "plugin_action") and self.plugin_action:
                self.plugin_action.setChecked(False)
            return



    def invalidate_geometry(self):
        """
        Force QGraphicsScene to re-evaluate boundingRect.
        MUST be called when center / radius changes from None.
        """
        self.prepareGeometryChange()
