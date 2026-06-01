from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPen, QBrush, QPainterPath, QPainter
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsScene, QGraphicsTextItem


class TimelineDrawer:
    def __init__(self, graphics_view):
        self.view = graphics_view
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setStyleSheet("background: transparent; border: none;")
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scene.setBackgroundBrush(QBrush(QColor("#f8fbff")))

        self.START_HOUR, self.END_HOUR = 7, 21
        self.HOUR_WIDTH, self.ROW_HEIGHT = 190, 120
        self.LEFT_MARGIN, self.TOP_MARGIN = 200, 60

        self.COLORS = [
            QColor("#dbeafe"),
            QColor("#bfdbfe"),
            QColor("#ccfbf1"),
            QColor("#ede9fe"),
            QColor("#ffe4e6"),
        ]

    def draw(self, lich_kham_list, benh_nhan_list, bac_si_list, dich_vu_list, target_date=None):
        self.scene.clear()

        if not target_date:
            target_date = datetime.now().strftime("%Y-%m-%d")

        def v(obj, *keys):
            for key in keys:
                res = getattr(obj, key, None) or (obj.get(key) if isinstance(obj, dict) else None)
                if res is not None:
                    return res
            return ""

        lich_trong_ngay = []
        seen_bs_ids = set()
        first_time_by_bs = {}
        for lich in lich_kham_list:
            l_ngay = str(v(lich, "ngay_kham")).strip()
            if target_date not in l_ngay:
                continue
            lich_trong_ngay.append(lich)
            l_bs_id = str(v(lich, "bacsi_id")).strip()
            if not l_bs_id:
                continue
            seen_bs_ids.add(l_bs_id)
            l_gio = str(v(lich, "gio_kham")).strip()
            if l_bs_id not in first_time_by_bs:
                first_time_by_bs[l_bs_id] = l_gio
            else:
                first_time_by_bs[l_bs_id] = min(first_time_by_bs[l_bs_id], l_gio)

        dict_bn = {str(v(bn, "id")): v(bn, "ten") for bn in benh_nhan_list}
        dict_bs = {str(v(bs, "id")): v(bs, "ten") for bs in bac_si_list if str(v(bs, "id")) in seen_bs_ids}
        dict_dv = {str(v(dv, "id")): v(dv, "ten_dich_vu") for dv in dich_vu_list}
        bs_ids = sorted(seen_bs_ids, key=lambda bs_id: (first_time_by_bs.get(bs_id, "99:99"), dict_bs.get(bs_id, "")))

        viewport = self.view.viewport().size()
        available_height = max(320, viewport.height() - 30)
        self.LEFT_MARGIN = 230
        self.HOUR_WIDTH = 190
        total_width = (self.END_HOUR - self.START_HOUR) * self.HOUR_WIDTH

        row_count = max(1, len(bs_ids))
        min_row_height = 118
        chart_height = max(available_height - self.TOP_MARGIN - 30, row_count * min_row_height)
        self.ROW_HEIGHT = chart_height / row_count
        total_height = self.TOP_MARGIN + row_count * self.ROW_HEIGHT

        for h in range(self.START_HOUR, self.END_HOUR + 1):
            x = self.LEFT_MARGIN + (h - self.START_HOUR) * self.HOUR_WIDTH
            self.scene.addLine(
                x,
                20,
                x,
                total_height,
                QPen(QColor("#d7e3f4"), 1, Qt.PenStyle.DashLine),
            )
            lbl = self.scene.addText(f"{h}:00", QFont("Segoe UI", 10, QFont.Weight.Bold))
            lbl.setDefaultTextColor(QColor("#64748b"))
            lbl.setPos(x - 20, 0)

        for i, bs_id in enumerate(bs_ids):
            y = self.TOP_MARGIN + i * self.ROW_HEIGHT
            self.scene.addLine(
                self.LEFT_MARGIN,
                y,
                self.LEFT_MARGIN + total_width,
                y,
                QPen(QColor("#e2e8f0"), 1),
            )

            bs_name = dict_bs.get(bs_id, "Unknown")
            label_x = 16
            label_y = y + self.ROW_HEIGHT / 2 - 24
            label_width = self.LEFT_MARGIN - 36
            label_height = 48
            label_path = QPainterPath()
            label_path.addRoundedRect(label_x, label_y, label_width, label_height, 14, 14)
            self.scene.addPath(
                label_path,
                QPen(QColor("#bfdbfe"), 1),
                QBrush(QColor("#eff6ff"))
            )
            name_item = self.scene.addText(f"BS. {bs_name}", QFont("Segoe UI", 11, QFont.Weight.Bold))
            name_item.setDefaultTextColor(QColor("#0f172a"))
            name_item.setPos(label_x + 12, label_y + 12)

        self.scene.addLine(
            self.LEFT_MARGIN,
            total_height,
            self.LEFT_MARGIN + total_width,
            total_height,
            QPen(QColor("#e2e8f0"), 1),
        )

        for lich in lich_trong_ngay:
            l_ngay = str(v(lich, "ngay_kham")).strip()
            l_bs_id = str(v(lich, "bacsi_id"))

            if target_date not in l_ngay or l_bs_id not in bs_ids:
                continue

            try:
                l_id = str(v(lich, "id"))
                l_gio = v(lich, "gio_kham")
                l_dv_id = str(v(lich, "dichvu_id"))
                hour, minute = map(int, l_gio.split(":"))

                if not (self.START_HOUR <= hour <= self.END_HOUR):
                    continue

                x = self.LEFT_MARGIN + (hour - self.START_HOUR) * self.HOUR_WIDTH + (minute / 60) * self.HOUR_WIDTH
                y_idx = bs_ids.index(l_bs_id)
                row_padding = min(14, max(8, self.ROW_HEIGHT * 0.12))
                y = self.TOP_MARGIN + y_idx * self.ROW_HEIGHT + row_padding

                card_width = max(self.HOUR_WIDTH * 1.16, 150)
                card_height = max(76, min(self.ROW_HEIGHT - row_padding * 2, 94))
                color = self.COLORS[y_idx % len(self.COLORS)]

                shadow = QPainterPath()
                shadow.addRoundedRect(x + 4, y + 5, card_width, card_height, 14, 14)
                shadow_item = self.scene.addPath(
                    shadow,
                    QPen(Qt.PenStyle.NoPen),
                    QBrush(QColor(148, 163, 184, 55)),
                )
                shadow_item.setZValue(1)

                path = QPainterPath()
                path.addRoundedRect(x, y, card_width, card_height, 14, 14)
                border_pen = QPen(QColor("#ffffff"), 1)
                path_item = self.scene.addPath(path, border_pen, QBrush(color))
                path_item.setZValue(2)
                path_item.setFlags(path_item.flags() | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                path_item.setData(Qt.ItemDataRole.UserRole, l_id)

                ten_dv = dict_dv.get(l_dv_id, "Kham benh")
                bn_name = dict_bn.get(str(v(lich, "benhnhan_id")), "Khong ro")
                bs_name_card = dict_bs.get(l_bs_id, "Khong ro")

                html_content = f"""
                <div style="font-family: 'Segoe UI'; color: #0f172a; line-height: 1.08;">
                    <b style="font-size: 9.5pt;">{ten_dv}</b><br/>
                    <span style="font-size: 8.5pt; color: #334155;">BN: {bn_name}</span><br/>
                    <span style="font-size: 8.5pt; color: #334155;">BS: {bs_name_card}</span><br/>
                    <span style="font-size: 8.5pt; color: #1d4ed8; font-weight: bold;">Gio: {l_gio}</span>
                </div>
                """

                text_item = QGraphicsTextItem()
                text_item.document().setDocumentMargin(0)
                text_item.setHtml(html_content)
                text_item.setPos(x + 10, y + 9)
                text_item.setTextWidth(card_width - 20)
                text_item.setZValue(3)
                text_item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
                self.scene.addItem(text_item)
            except Exception as e:
                print(f"Loi ve the timeline: {e}")
                continue

        now = datetime.now()
        if self.START_HOUR <= now.hour <= self.END_HOUR and target_date == now.strftime("%Y-%m-%d"):
            curr_x = self.LEFT_MARGIN + (now.hour - self.START_HOUR) * self.HOUR_WIDTH + (now.minute / 60) * self.HOUR_WIDTH
            pen = QPen(QColor("#2563eb"), 2)
            self.scene.addLine(curr_x, 0, curr_x, total_height, pen)
            self.scene.addEllipse(curr_x - 5, 0, 10, 10, QPen(Qt.PenStyle.NoPen), QBrush(QColor("#2563eb")))

        scene_width = self.LEFT_MARGIN + total_width + 40
        scene_height = total_height + 30
        self.scene.setSceneRect(0, 0, scene_width, scene_height)
