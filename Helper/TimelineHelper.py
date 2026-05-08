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
        self.scene.setBackgroundBrush(QBrush(QColor("#f8fbff")))

        self.START_HOUR, self.END_HOUR = 7, 21
        self.HOUR_WIDTH, self.ROW_HEIGHT = 160, 130
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

        dict_bn = {str(v(bn, "id")): v(bn, "ten") for bn in benh_nhan_list}
        dict_bs = {str(v(bs, "id")): v(bs, "ten") for bs in bac_si_list}
        dict_dv = {str(v(dv, "id")): v(dv, "ten_dich_vu") for dv in dich_vu_list}
        bs_ids = list(dict_bs.keys())

        total_width = (self.END_HOUR - self.START_HOUR) * self.HOUR_WIDTH
        total_height = self.TOP_MARGIN + len(bs_ids) * self.ROW_HEIGHT

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
            name_item = self.scene.addText(f"BS. {bs_name}", QFont("Segoe UI", 11, QFont.Weight.Bold))
            name_item.setDefaultTextColor(QColor("#0f172a"))
            name_item.setPos(10, y + self.ROW_HEIGHT / 2 - 15)

        for lich in lich_kham_list:
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
                y = self.TOP_MARGIN + y_idx * self.ROW_HEIGHT + 15

                card_width = self.HOUR_WIDTH * 1.4
                card_height = 95
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
                <div style="font-family: 'Segoe UI'; color: #0f172a;">
                    <b style="font-size: 10pt;">{ten_dv}</b><br/>
                    <span style="font-size: 9pt; color: #334155;">BN: {bn_name}</span><br/>
                    <span style="font-size: 9pt; color: #334155;">BS: {bs_name_card}</span><br/>
                    <span style="font-size: 9pt; color: #1d4ed8; font-weight: bold;">Gio: {l_gio}</span>
                </div>
                """

                text_item = QGraphicsTextItem()
                text_item.setHtml(html_content)
                text_item.setPos(x + 10, y + 7)
                text_item.setTextWidth(card_width - 18)
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

        self.scene.setSceneRect(0, 0, self.LEFT_MARGIN + total_width + 100, total_height + 100)
