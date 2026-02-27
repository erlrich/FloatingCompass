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

from qgis.gui import QgsMapCanvasItem
from qgis.PyQt.QtGui import QPen, QColor, QFont, QBrush, QPainter
from qgis.PyQt.QtCore import QPointF, QRectF, Qt
import math


class FloatingProtractorOverlay(QgsMapCanvasItem):

    def __init__(self, canvas, tool):
        super().__init__(canvas)
        self.tool = tool
        self.setZValue(1000)
        self.setVisible(False)

    # =================================================
    def paint(self, painter, option, widget):
        if self.tool.center is None:
            return

        painter.setRenderHint(QPainter.Antialiasing)
        c = self.tool.center

        # =====================
        # SAFE STATES
        # =====================
        arms = getattr(self.tool, "arms", [])
        arm_labels = getattr(self.tool, "arm_labels", ["A", "B", "C", "D", "E", "F"])

        show_arms = getattr(self.tool, "show_arms", True)
        show_arc = getattr(self.tool, "show_arc", True)
        show_angle_text = getattr(self.tool, "show_angle_text", True)
        mode = getattr(self.tool, "mode", "NORMAL")

        # interaction flag (robust)
        is_interacting = bool(
            getattr(self.tool, "_is_interacting", False)
            or getattr(self.tool, "active_handle", self.tool.HANDLE_NONE)
               != self.tool.HANDLE_NONE
        )

        active = self.tool.canvas.mapTool() == self.tool
        base_alpha = 220 if active else 120

        # =====================
        # COLORS
        # =====================
        ring_col = QColor(self.tool.color_ring)
        ring_col.setAlpha(base_alpha)

        text_col = QColor(self.tool.color_text)
        text_col.setAlpha(255 if active else 160)

        outline_col = QColor(self.tool.color_outline)
        shadow_col = QColor(self.tool.color_shadow)
        shadow_col.setAlpha(self.tool.text_shadow_alpha)

        r = self.tool.ring_radius
        ring_w = getattr(self.tool, "ring_line_width", 3)

        # =====================
        # FONTS (ADVANCE VISUAL FIX)
        # =====================
        label_font_size = getattr(self.tool, "label_font_size", 10)
        angle_font_size = getattr(self.tool, "angle_font_size", 10)

        label_font = QFont("Arial", label_font_size, QFont.Bold)
        angle_font = QFont("Arial", angle_font_size, QFont.Bold)

        # =====================
        # RING GLOW
        # =====================
        glow = QColor(ring_col)
        glow.setAlpha(self.tool.ring_glow_alpha)

        painter.setBrush(Qt.NoBrush)
        glow_pen = QPen(glow, ring_w + 4)
        glow_pen.setCapStyle(Qt.RoundCap)
        glow_pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(glow_pen)
        painter.drawEllipse(c, r, r)

        # =====================
        # ARMS
        # =====================
        if show_arms and arms:
            for idx, arm in enumerate(arms):
                if not arm.get("enabled"):
                    continue

                ang = float(arm.get("angle_deg", 0.0))
                radius = arm.get("radius_px") or r

                col = arm.get("color") or ring_col
                arm_col = QColor(col)
                arm_col.setAlpha(base_alpha)

                self.draw_arm(painter, ang, radius, arm_col)
                
                
                # LABEL (RADIAL POSITION + DIRECTIONAL ANCHOR)
                if (
                    show_angle_text
                    # allow label during interaction
                    # and not is_interacting
                    and idx < len(arm_labels)
                ):
                    label = arm_labels[idx]
                    if label:
                        rad = math.radians(ang)

                        # =====================
                        # RADIAL DIRECTION
                        # =====================
                        dx = math.sin(rad)
                        dy = -math.cos(rad)

                        # =====================
                        # DISTANCE SETUP
                        # =====================
                        endpoint_r = getattr(self.tool, "arm_endpoint_radius_px", 4)
                        arm_w = getattr(self.tool, "arm_line_width", 5)
                        gap = 8  # gap visual dari endpoint dot

                        label_dist = radius + endpoint_r + arm_w + gap

                        # Base radial point
                        lx = c.x() + label_dist * dx
                        ly = c.y() + label_dist * dy

                        # =====================
                        # TEXT METRICS
                        # =====================
                        fm = painter.fontMetrics()
                        br = fm.boundingRect(label)
                        w = br.width()
                        h = br.height()

                        # =====================
                        # DIRECTIONAL ANCHOR
                        # =====================
                        # Normalize angle to [0, 360)
                        a = ang % 360

                        # Default: center
                        ox = w / 2
                        oy = -h / 2

                        # Right side (45° – 135°): text grows to the right
                        if 45 <= a < 135:
                            ox = 0

                        # Left side (225° – 315°): text grows to the left
                        elif 225 <= a < 315:
                            ox = w

                        # Top / Bottom keep centered
                        # (315–360, 0–45, 135–225)

                        # Apply anchor offset
                        tx = lx - ox
                        ty = ly - oy

                        self.draw_shadow_text(
                            painter,
                            QPointF(tx, ty),
                            label,
                            label_font,
                            text_col,
                            outline_col,
                            shadow_col
                        )


        # =====================
        # ARC (NORMAL ONLY)
        # =====================
        if (
            show_arms
            and show_arc
            and mode == "NORMAL"
            and len(arms) >= 2
            and arms[0].get("enabled")
            and arms[1].get("enabled")
        ):
            a_start = arms[0]["angle_deg"] % 360
            span = (arms[1]["angle_deg"] - a_start) % 360

            if span > 0.5:
                arc_radius = 20
                arc_rect = QRectF(
                    c.x() - arc_radius,
                    c.y() - arc_radius,
                    arc_radius * 2,
                    arc_radius * 2
                )

                arc_col = QColor(self.tool.color_arc)
                arc_col.setAlpha(130 if active else 90)

                painter.setBrush(Qt.NoBrush)
                arc_w = getattr(self.tool, "arc_line_width", 0)
                if arc_w <= 0:
                    arc_w = max(2, ring_w - 1)

                arc_pen = QPen(arc_col, arc_w)

                arc_pen.setCapStyle(Qt.RoundCap)
                painter.setPen(arc_pen)
                painter.drawArc(
                    arc_rect,
                    int((90 - a_start) * 16),
                    int(-span * 16)
                )

        # =====================
        # RING + TICKS
        # =====================
        rw = ring_w + 2 if self.tool.hover_handle == self.tool.HANDLE_ROTATE_BOTH else ring_w
        ring_pen = QPen(ring_col, rw)
        ring_pen.setCapStyle(Qt.RoundCap)
        ring_pen.setJoinStyle(Qt.RoundJoin)

        painter.setBrush(Qt.NoBrush)  # anti fill
        painter.setPen(ring_pen)
        painter.drawEllipse(c, r, r)

        self.draw_degree_ticks(painter, c, r, ring_col)
        
        # =====================
        # CARDINAL DIRECTIONS
        # =====================
        self.draw_cardinal_directions(painter, c, r)
   
        # =====================
        # ANGLE TEXT (NORMAL ONLY)
        # =====================
        if (
            show_arms
            and show_angle_text
            # allow angle text during interaction
            # and not is_interacting
            and mode == "NORMAL"
            and len(arms) >= 2
            and arms[0].get("enabled")
            and arms[1].get("enabled")
        ):
            ang = (arms[1]["angle_deg"] - arms[0]["angle_deg"]) % 360

            text_pos = self.compute_angle_text_pos(
                c,
                arms[0]["angle_deg"],
                arms[1]["angle_deg"]
            )

            self.draw_shadow_text(
                painter,
                text_pos,
                f"{ang:.1f}°",
                angle_font,
                text_col,
                outline_col,
                shadow_col
            )

        # =====================
        # CENTER DOT (ALWAYS)
        # =====================
        center_dot = getattr(self.tool, "center_dot_radius_px", 6)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(ring_col))
        painter.drawEllipse(c, center_dot, center_dot)

        # =====================
        # CROSSHAIR (CONFIGURABLE)
        # =====================
        show_crosshair = getattr(self.tool, "show_crosshair", True)
        style = getattr(self.tool, "crosshair_style", "plus")
        size = getattr(self.tool, "crosshair_size_px", 20)
        thickness = getattr(self.tool, "crosshair_thickness", 1)
        col = getattr(self.tool, "crosshair_color", ring_col)

        if show_crosshair and style != "none":
            cross_col = QColor(col)
            cross_col.setAlpha(ring_col.alpha())

            if style == "dot":
                # small dot only (independent from center dot)
                r = max(2, int(size / 4))
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(cross_col))
                painter.drawEllipse(c, r, r)

            elif style == "plus":
                half = int(size)
                pen = QPen(cross_col, max(1, thickness))
                pen.setCapStyle(Qt.RoundCap)
                painter.setPen(pen)

                painter.drawLine(
                    c + QPointF(-half, 0),
                    c + QPointF(half, 0)
                )
                painter.drawLine(
                    c + QPointF(0, -half),
                    c + QPointF(0, half)
                )



    # =================================================
    def draw_shadow_text(
        self,
        painter,
        pos,
        text,
        font,
        fill_col,
        outline_col,
        shadow_col
    ):
        """
        Optimized shadow + outline text renderer.
        - No feature removed
        - Performance-safe
        - Advance Visual friendly
        """

        # =====================
        # GUARD (PERFORMANCE)
        # =====================
        if not text:
            return

        # kalau semua transparan, skip
        if (
            fill_col.alpha() == 0
            and outline_col.alpha() == 0
            and shadow_col.alpha() == 0
        ):
            return

        painter.save()
        painter.setFont(font)

        # =====================
        # SHADOW (WITH SETTINGS)
        # =====================
        shadow_enabled = getattr(self.tool, "shadow_enabled", True)
        if shadow_enabled and shadow_col.alpha() > 0:
            painter.setPen(shadow_col)
            painter.setBrush(Qt.NoBrush)
            painter.drawText(pos + QPointF(1.5, 1.5), text)  # Keep fixed offset

        # =====================
        # OUTLINE (WITH SETTINGS)
        # =====================
        outline_enabled = getattr(self.tool, "outline_enabled", True)
        if outline_enabled and outline_col.alpha() > 0:
            painter.setPen(outline_col)
            painter.setBrush(Qt.NoBrush)
            
            # tetap pakai 4 arah (fitur lama TIDAK dihapus)
            for dx, dy in (
                (-1, 0),
                (1, 0),
                (0, -1),
                (0, 1),
            ):
                painter.drawText(pos + QPointF(dx, dy), text)

        # =====================
        # MAIN TEXT (ALWAYS DRAW IF FILL COLOR HAS ALPHA)
        # =====================
        if fill_col.alpha() > 0:
            painter.setPen(fill_col)
            painter.setBrush(Qt.NoBrush)
            painter.drawText(pos, text)
        
        painter.restore()
    
       
    # =================================================
    # CARDINAL DIRECTIONS (STEP 3)
    # =================================================
    def draw_cardinal_directions(self, painter, center, radius):
        t = self.tool

        if not getattr(t, "show_cardinal", True):
            return

        from qgis.PyQt.QtGui import QFont, QColor, QPolygonF
        from qgis.PyQt.QtCore import QPointF
        import math

        col = QColor(t.color_ring)
        col.setAlpha(225)

        outline_col = QColor(t.color_outline)
        shadow_col = QColor(t.color_shadow)

        font = QFont("Arial", t.cardinal_font_size, QFont.Bold)

        items = [
            ("N",   0),
            ("E",  90),
            ("S", 180),
            ("W", 270),
        ]

        r = radius - t.cardinal_offset_px

        for text, deg in items:
            rad = math.radians(deg)
            x = center.x() + r * math.sin(rad)
            y = center.y() - r * math.cos(rad)

            painter.setFont(font)
            w = painter.fontMetrics().boundingRect(text).width()
            h = painter.fontMetrics().boundingRect(text).height()

            self.draw_shadow_text(
                painter,
                QPointF(x - w / 2, y + h / 2),
                text,
                font,
                col,
                outline_col,
                shadow_col
            )

            # =================================================
            # 🔥 NORTH ARROW — SINGLE MIRRORED BLADE
            # =================================================
            if text == "N" and getattr(t, "show_north_triangle", True):

                size = t.north_triangle_size_px * 2.0

                bx = x
                by = y - h / 2 + 1 # Tweak Arrow pos

                # =========================
                # BASE BLADE (LEFT SHAPE)
                # =========================
                tip = QPointF(bx, by - size * 0.95)
                base_left = QPointF(bx - size * 0.70, by + size * 0.45)
                base_center = QPointF(bx, by + size * 0.05)

                # mirror of base_left
                base_right = QPointF(
                    bx + (bx - base_left.x()),
                    base_left.y()
                )

                arrow_poly = QPolygonF([
                    tip,
                    base_right,
                    base_center,
                    base_left
                ])

                painter.save()
                pen = QPen(QColor("#000000"))   # black outline
                pen.setWidth(1)
                painter.setPen(pen)
                painter.setBrush(QColor("#E31B23"))   # RED
                painter.drawPolygon(arrow_poly)
                painter.restore()


    def compute_angle_text_pos(self, center, arm_a_angle, arm_b_angle):
        span = (arm_b_angle - arm_a_angle) % 360
        if span < 1:
            span = 1

        mid_angle = (arm_a_angle + span / 2) % 360
        rad = math.radians(mid_angle)

        dist = getattr(self.tool, "angle_text_distance_px", 20)

        x = center.x() + dist * math.sin(rad)
        y = center.y() - dist * math.cos(rad)
        return QPointF(x, y)


    def draw_arm(self, painter, angle, radius, color):
        rad = math.radians(angle)
        c = self.tool.center
        end = QPointF(
            c.x() + radius * math.sin(rad),
            c.y() - radius * math.cos(rad)
        )
        

        arm_w = getattr(self.tool, "arm_line_width", 5)
        w = arm_w + 2 if self.tool.hover_handle in (
            self.tool.HANDLE_ARM_A_ROTATE,
            self.tool.HANDLE_ARM_B_ROTATE,
            self.tool.HANDLE_ARM_A_RESIZE,
            self.tool.HANDLE_ARM_B_RESIZE
        ) else arm_w

        pen = QPen(color, w)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(c, end)

        ep = getattr(self.tool, "arm_endpoint_radius_px", 0)
        if ep <= 0:
            ep = max(3, arm_w - 1)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color))
        painter.drawEllipse(end, ep, ep)

    def draw_degree_ticks(self, painter, center, radius, ring_col):
        step = getattr(self.tool, "ring_tick_step_deg", 5)
        major = getattr(self.tool, "ring_major_tick_deg", 10)
        label_step = getattr(self.tool, "ring_label_step_deg", 30)
        ring_w = getattr(self.tool, "ring_line_width", 3)

        for deg in range(0, 360, step):
            rad = math.radians(deg)
            tick_len = 14 if deg % major == 0 else 8

            x1 = center.x() + (radius - tick_len) * math.sin(rad)
            y1 = center.y() - (radius - tick_len) * math.cos(rad)
            x2 = center.x() + radius * math.sin(rad)
            y2 = center.y() - radius * math.cos(rad)

            pen = QPen(ring_col, ring_w if deg % major == 0 else 1)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

            if deg % label_step == 0:
                self.draw_label(painter, center, radius, deg, ring_col)

    def draw_label(self, painter, center, radius, deg, ring_col):
        rad = math.radians(deg)
        rr = radius - 26

        x = center.x() + rr * math.sin(rad)
        y = center.y() - rr * math.cos(rad)

        font_sz = getattr(self.tool, "label_font_size", 9)
        self.draw_shadow_text(
            painter,
            QPointF(x - 10, y + 5),
            str(deg),
            QFont("Arial", font_sz, QFont.Bold),
            ring_col,
            QColor(self.tool.color_outline),
            QColor(self.tool.color_shadow)
        )

    def boundingRect(self):
        if self.tool.center is None:
            return QRectF()

        c = self.tool.center

        # =====================
        # HITUNG RADIUS TERJAUH
        # =====================
        max_radius = self.tool.ring_radius

        for arm in getattr(self.tool, "arms", []):
            if not arm.get("enabled"):
                continue
            r = arm.get("radius_px", 0)
            if r and r > max_radius:
                max_radius = r

        # =====================
        # PADDING AMAN
        # =====================
        # - label text
        # - shadow
        # - tick
        # - glow
        padding = (
            60  # label + shadow
            + self.tool.ring_glow_alpha // 2
            + 20
        )

        R = max_radius + padding

        return QRectF(
            c.x() - R,
            c.y() - R,
            R * 2,
            R * 2
        )

