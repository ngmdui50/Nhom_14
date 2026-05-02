from PyQt6.QtWidgets import QGraphicsScene, QGraphicsTextItem, QGraphicsItem
from PyQt6.QtGui import QColor, QFont, QPen, QBrush, QPainterPath, QPainter
from PyQt6.QtCore import Qt
from datetime import datetime

class TimelineDrawer:
    def __init__(self, graphics_view):
        self.view = graphics_view
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 💎 ĐỒNG BỘ NỀN VỚI GIAO DIỆN PREMIUM (Midnight/Dark Mode)
        self.view.setStyleSheet("background-color: transparent; border: none;")
        self.scene.setBackgroundBrush(QBrush(QColor("#151A27"))) # Màu nền Card tối

        # Giao diện nâng cấp: Nới rộng không gian để thẻ to và đẹp hơn
        self.START_HOUR, self.END_HOUR = 7, 21
        self.HOUR_WIDTH, self.ROW_HEIGHT = 160, 130
        self.LEFT_MARGIN, self.TOP_MARGIN = 200, 60
        
        # 💎 BẢNG MÀU THẺ NEON DÀNH CHO DARK MODE
        self.COLORS = [
            QColor("#7380E8"), # Soft Indigo (Trùng gradient chính)
            QColor("#0EA5E9"), # Neon Sky Blue
            QColor("#10B981"), # Emerald Green
            QColor("#D946EF"), # Neon Fuchsia
            QColor("#F43F5E")  # Rose Red
        ]

    def draw(self, lich_kham_list, benh_nhan_list, bac_si_list, dich_vu_list, target_date=None):
        self.scene.clear() 
        
        if not target_date:
            target_date = datetime.now().strftime("%Y-%m-%d")
        
        # Hàm lấy giá trị an toàn
        def v(obj, *keys):
            for k in keys:
                res = getattr(obj, k, None) or (obj.get(k) if isinstance(obj, dict) else None)
                if res is not None: return res
            return ""

        # 1. MAPPING DATA
        dict_bn = {str(v(bn, 'id')): v(bn, 'ten') for bn in benh_nhan_list}
        dict_bs = {str(v(bs, 'id')): v(bs, 'ten') for bs in bac_si_list}
        dict_dv = {str(v(dv, 'id')): v(dv, 'ten_dich_vu') for dv in dich_vu_list}
        bs_ids = list(dict_bs.keys())

        # --- VẼ TRỤC GIỜ (HEADER) ---
        total_width = (self.END_HOUR - self.START_HOUR) * self.HOUR_WIDTH
        for h in range(self.START_HOUR, self.END_HOUR + 1):
            x = self.LEFT_MARGIN + (h - self.START_HOUR) * self.HOUR_WIDTH
            # 💎 Màu viền kẻ dọc
            self.scene.addLine(x, 20, x, self.TOP_MARGIN + len(bs_ids) * self.ROW_HEIGHT, QPen(QColor("#2A3143"), 1, Qt.PenStyle.DashLine))
            lbl = self.scene.addText(f"{h}:00", QFont("Segoe UI", 10, QFont.Weight.Bold))
            # 💎 Màu chữ trục giờ
            lbl.setDefaultTextColor(QColor("#94A3B8"))
            lbl.setPos(x - 20, 0)

        # --- VẼ SIDEBAR (DANH SÁCH BÁC SĨ) ---
        for i, bs_id in enumerate(bs_ids):
            y = self.TOP_MARGIN + i * self.ROW_HEIGHT
            # 💎 Màu viền kẻ ngang
            self.scene.addLine(self.LEFT_MARGIN, y, self.LEFT_MARGIN + total_width, y, QPen(QColor("#1E2538"), 1))
            
            bs_name = dict_bs.get(bs_id, "Unknown")
            name_item = self.scene.addText(f"🩺 {bs_name}", QFont("Segoe UI", 11, QFont.Weight.Bold))
            # 💎 Màu tên Bác sĩ
            name_item.setDefaultTextColor(QColor("#E2E8F0"))
            name_item.setPos(10, y + self.ROW_HEIGHT/2 - 15)

        # --- VẼ CÁC THẺ LỊCH KHÁM (RICH TEXT CARD) ---
        for lich in lich_kham_list:
            l_ngay = str(v(lich, 'ngay_kham')).strip()
            l_bs_id = str(v(lich, 'bacsi_id'))
            
            if target_date not in l_ngay or l_bs_id not in bs_ids:
                continue
            
            try:
                # 1. Lấy ID Lịch Khám và các thông tin cơ bản
                l_id = str(v(lich, 'id'))
                l_gio = v(lich, 'gio_kham')
                l_dv_id = str(v(lich, 'dichvu_id'))
                
                # 2. TÍNH TOÁN TỌA ĐỘ VÀ VỊ TRÍ
                hour, minute = map(int, l_gio.split(":"))
                
                if not (self.START_HOUR <= hour <= self.END_HOUR): continue

                x = self.LEFT_MARGIN + (hour - self.START_HOUR) * self.HOUR_WIDTH + (minute / 60) * self.HOUR_WIDTH
                y_idx = bs_ids.index(l_bs_id)
                y = self.TOP_MARGIN + y_idx * self.ROW_HEIGHT + 15
                
                # Chiều dài, rộng của thẻ
                card_width = self.HOUR_WIDTH * 1.4
                card_height = 95
                color = self.COLORS[y_idx % len(self.COLORS)]
                
                # 3. Vẽ bóng đổ (Shadow)
                shadow = QPainterPath()
                shadow.addRoundedRect(x + 3, y + 4, card_width, card_height, 12, 12)
                shadow_item = self.scene.addPath(shadow, QPen(Qt.PenStyle.NoPen), QBrush(QColor(0, 0, 0, 80)))
                shadow_item.setZValue(1) # Bóng đổ ở lớp thấp nhất

                # 4. Vẽ thẻ bo tròn chính
                path = QPainterPath()
                path.addRoundedRect(x, y, card_width, card_height, 12, 12)
                border_pen = QPen(QColor(255, 255, 255, 40), 1) 
                
                # GÁN SỰ KIỆN CLICK CHO THẺ CHÍNH
                path_item = self.scene.addPath(path, border_pen, QBrush(color))
                path_item.setZValue(2) # Thẻ chính ở lớp giữa
                path_item.setFlags(path_item.flags() | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                path_item.setData(Qt.ItemDataRole.UserRole, l_id) # Lưu ID lịch khám vào Item

                # 5. Nội dung thẻ bằng HTML
                ten_dv = dict_dv.get(l_dv_id, "Khám Bệnh")
                bn_name = dict_bn.get(str(v(lich, 'benhnhan_id')), "Không rõ")
                bs_name_card = dict_bs.get(l_bs_id, "Không rõ")

                # 💎 ĐÃ SỬA: Đổi toàn bộ đơn vị px thành pt ở đây để tránh lỗi QFont
                html_content = f"""
                <div style="font-family: 'Segoe UI'; color: #FFFFFF;">
                    <b style="font-size: 10pt;">💊 {ten_dv}</b><br/>
                    <span style="font-size: 9pt; color: #E2E8F0;">👤 BN: {bn_name}</span><br/>
                    <span style="font-size: 9pt; color: #E2E8F0;">🩺 BS: {bs_name_card}</span><br/>
                    <span style="font-size: 9pt; color: #FFFFFF; font-weight: bold;">🕒 Giờ: {l_gio}</span>
                </div>
                """
                
                # Chèn text vào Scene
                text_item = QGraphicsTextItem()
                text_item.setHtml(html_content)
                text_item.setPos(x + 8, y + 5)
                text_item.setTextWidth(card_width - 15) 
                text_item.setZValue(3) # TextItem ở lớp cao nhất
                
                # Ngăn TextItem chiếm mất click của thẻ PathItem
                text_item.setAcceptedMouseButtons(Qt.MouseButton.NoButton) 
                
                self.scene.addItem(text_item)
                
            except Exception as e:
                print(f"Lỗi vẽ thẻ: {e}")
                continue

        # --- VẼ VẠCH GIỜ HIỆN TẠI ---
        now = datetime.now()
        # Vạch giờ chỉ hiển thị nếu ngày xem (target_date) trùng với ngày hôm nay
        if self.START_HOUR <= now.hour <= self.END_HOUR and target_date == now.strftime("%Y-%m-%d"):
            curr_x = self.LEFT_MARGIN + (now.hour - self.START_HOUR) * self.HOUR_WIDTH + (now.minute / 60) * self.HOUR_WIDTH
            
            # Đổi màu vạch báo giờ sang #00E5FF
            pen = QPen(QColor("#00E5FF"), 2) 
            self.scene.addLine(curr_x, 0, curr_x, self.TOP_MARGIN + len(bs_ids) * self.ROW_HEIGHT, pen)
            
            # Khối tròn đầu vạch báo giờ
            self.scene.addEllipse(curr_x - 5, 0, 10, 10, QPen(Qt.PenStyle.NoPen), QBrush(QColor("#00E5FF")))

        self.scene.setSceneRect(0, 0, self.LEFT_MARGIN + total_width + 100, self.TOP_MARGIN + len(bs_ids) * self.ROW_HEIGHT + 100)