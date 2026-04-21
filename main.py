import sys
import os
from datetime import datetime
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox,
    QVBoxLayout, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import QTimer, QDateTime, pyqtSignal, Qt

from Model.connecDB import fetch_one

# ================= IMPORT HELPER & CONTROLLER =================
try:
    from Helper.TimelineHelper import TimelineDrawer
    from Controller.benhnhan_Controller import BenhNhanController
    from Controller.bacsi_Controller import BacSiController
    from Controller.dichvu_Controller import DichVuController
    from Controller.phong_Controller import PhongKhamController
    from Controller.lichkham_Controller import LichKhamController
    from Controller.doanhthu_Controller import DoanhThuController # <-- THÊM IMPORT CONTROLLER DOANH THU
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from Helper.TimelineHelper import TimelineDrawer

# ================= LOGIN WINDOW =================
class LoginApp(QMainWindow):
    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        uic.loadUi("View/dangnhap.ui", self)
        self.btndangnhap.clicked.connect(self.check_login)

    def check_login(self):
        if self.txtusername.text() == "" and self.txtpassword.text() == "":
            self.login_successful.emit()
            self.close()
        else:
            QMessageBox.warning(self, "Lỗi", "Sai tài khoản hoặc mật khẩu!")

# ================= MAIN WINDOW =================
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Khởi tạo Drawer xử lý vẽ Timeline
        self.timeline_drawer = TimelineDrawer(self.forms["TL"].graphicsViewTimeline)
        
        self.connect_events()
        self.hien_thi_timeline() 

        # Timer cập nhật đồng hồ hệ thống
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def init_ui(self):
        uic.loadUi("View/Giaodienchinh.ui", self)
        self.formChucNang = uic.loadUi("View/GiaodienChucnang.ui")

        layout = QVBoxLayout(self.groupTrangChu)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.formChucNang)

        self.forms = {
            "TL": uic.loadUi("View/Timeline.ui"),
            "BN": uic.loadUi("View/FormBenhNhan.ui"),
            "BS": uic.loadUi("View/FormBacSi.ui"),
            "DV": uic.loadUi("View/FormDichVU.ui"),
            "PK": uic.loadUi("View/FormPhong.ui"),
            "LK": uic.loadUi("View/FormLichKham.ui"),
            "PROFILE": uic.loadUi("View/formThongTinTK.ui"), 
            "TK": uic.loadUi("View/formThongKe.ui"),
            "DT": uic.loadUi("View/FormDoanhThu.ui"),
            "TKLK": uic.loadUi("View/formThongKeLichKham.ui"),
        }

        for form in self.forms.values():
            self.formChucNang.stackedWidgetMain.addWidget(form)

        self.setStyleSheet("""
            /* ================================================= */
            /* 1. MÀU NỀN TỔNG THỂ & SCROLLBAR (MACOS STYLE)     */
            /* ================================================= */
            QMainWindow {
                background-color: #0B0E14; /* Deep Midnight Blue */
                font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
                color: #E2E8F0;
            }

            QFrame#frame { background-color: transparent; border: none; }

            /* Thanh cuộn siêu mượt và hiện đại */
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #2A3143;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: #4B5563; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }

            /* ================================================= */
            /* 2. CÁC KHỐI CHỨC NĂNG (CARD DESIGN)               */
            /* ================================================= */
            QGroupBox {
                background-color: #151A27;
                border: 1px solid #1E2538;
                border-radius: 14px;
                margin-top: 25px;
                padding-top: -2px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 6px 24px;
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7380E8, stop:1 #00E5FF);
                color: #000000;
                border-radius: 12px;
                font-size: 13px;
                font-weight: 900;
                text-transform: uppercase;
                letter-spacing: 1.5px;
            }

            QGroupBox#groupTrangChu {
                background-color: #151A27;
                border-radius: 14px;
                border: 1px solid #1E2538;
                margin-top: 20px;
            }
            QGroupBox#groupTrangChu::title { background-color: transparent; }

            /* ================================================= */
            /* 3. MENU BÊN TRÁI (NEON HOVER EFFECT)              */
            /* ================================================= */
            QPushButton {
                background-color: transparent;
                color: #94A3B8;
                border: none;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 14px;
                font-weight: 600;
                text-align: left;
                border-left: 3px solid transparent; /* Dành chỗ cho viền active */
            }
            
            QPushButton:hover {
                background-color: rgba(115, 128, 232, 0.1);
                color: #FFFFFF;
                border-left: 3px solid #7380E8; /* Viền sáng lên bên trái */
                padding-left: 20px; /* Chữ trượt mượt mà sang phải */
            }
            
            QPushButton:pressed {
                background-color: rgba(0, 229, 255, 0.2);
                color: #00E5FF;
                border-left: 3px solid #00E5FF;
            }
            
            /* Nút Trang chủ làm nổi bật hẳn lên */
            QPushButton#btntrangchu {
                background-color: rgba(0, 229, 255, 0.05);
                color: #00E5FF;
                border-left: 3px solid transparent;
            }
            QPushButton#btntrangchu:hover {
                background-color: rgba(0, 229, 255, 0.15);
                color: #FFFFFF;
                border-left: 3px solid #00E5FF;
                padding-left: 20px;
            }

            /* ================================================= */
            /* 4. BẢNG DỮ LIỆU (PREMIUM DATA TABLE)              */
            /* ================================================= */
            QTableWidget {
                background-color: transparent;
                color: #E2E8F0;
                border: none;
                gridline-color: transparent; /* Xóa lưới dọc ngang */
                font-size: 13px;
                outline: none; /* Bỏ viền khi click */
            }
            
            /* Chỉnh từng ô trong bảng */
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #1E2538; /* Chỉ để lại dòng kẻ ngang mờ */
            }
            
            /* Khi chọn 1 dòng */
            QTableWidget::item:selected {
                background-color: rgba(0, 229, 255, 0.15);
                color: #00E5FF;
                font-weight: bold;
            }
            
            /* Tiêu đề bảng */
            QHeaderView::section {
                background-color: #0F131D;
                color: #94A3B8;
                border: none;
                border-bottom: 2px solid #2A3143;
                padding: 10px;
                font-weight: 800;
                text-transform: uppercase;
                font-size: 11px;
                letter-spacing: 1px;
            }

            /* ================================================= */
            /* 5. TEXT & NHẬP LIỆU (ĐÃ FIX LỖI MẤT KHUNG & ID)   */
            /* ================================================= */
            
            /* Chữ mô tả, tiêu đề nhỏ (Mặc định trắng sáng cho các form) */
            QLabel {
                font-size: 13px;
                color: #FFFFFF;
                background: transparent;
            }
            
            /* BẢO VỆ TIÊU ĐỀ CHÍNH - LÀM MÀU RIÊNG CHO NÓ */
            QLabel#label {
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7380E8, stop:1 #00E5FF);
                font-size: 26px;
                font-weight: 900;
                padding-left: 10px;
                letter-spacing: 0.5px;
                font-family: 'Segoe UI Black', 'Arial Black', sans-serif;
            }

            /* Fix triệt để nếu ở dưới Form bạn lỡ đặt tên ObjectName cũng là 'label' */
            /* (Ép nó trở lại bình thường, không lấy Gradient) */
            QStackedWidget QLabel#label {
                color: #FFFFFF;
                font-size: 13px;
                font-weight: normal;
                padding-left: 0px;
                letter-spacing: 0px;
            }

            /* BẢO VỆ ĐỒNG HỒ */
            QLabel#lblTime {
                color: #00E5FF;
                font-size: 15px;
                font-weight: 900;
                background-color: rgba(0, 229, 255, 0.05);
                border-radius: 15px;
                border: 1px solid rgba(0, 229, 255, 0.2);
                padding: 6px 18px;
                letter-spacing: 1px;
            }
            
            /* KHUNG NHẬP LIỆU ĐÃ ĐƯỢC LÀM SÁNG LÊN */
            QLineEdit, QComboBox, QDateEdit, QTimeEdit, QSpinBox, QTextEdit {
                font-size: 14px;
                padding: 8px 12px;
                border: 1.5px solid #4B5563; /* Viền xám sáng hơn nhiều để tạo khung rõ ràng */
                border-radius: 8px;
                background-color: #1E2538; /* Nền sáng hơn nền card để ô nhập nổi lên */
                color: #FFFFFF;
            }
            
            /* Hiệu ứng phát sáng rực rỡ khi click vào để gõ chữ */
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus, QSpinBox:focus, QTextEdit:focus {
                border: 2px solid #00E5FF; /* Khung neon xanh hiện lên */
                background-color: #151A27;
            }
            
            /* Chỉnh nút mũi tên của ComboBox và Ngày tháng */
            QComboBox::drop-down, QDateEdit::drop-down, QTimeEdit::drop-down {
                border: none;
                width: 30px;
            }
            
            /* Ẩn dấu chấm bi (Size Grip) thừa ở góc phải dưới cùng */
            QSizeGrip {
                width: 0px;
                height: 0px;
                background: transparent;
            }

            /* ================================================= */
            /* 6. MENU BAR (QMenuBar & QMenu) Ở TRÊN CÙNG        */
            /* ================================================= */
            
            QMenuBar {
                background-color: #0F131D;
                color: #94A3B8;
                border-bottom: 1px solid #1E2538;
                font-size: 13px;
                font-weight: bold;
            }
            
            QMenuBar::item {
                spacing: 3px;
                padding: 6px 12px;
                background: transparent;
                border-radius: 4px;
                margin-top: 2px;
                margin-bottom: 2px;
            }
            
            QMenuBar::item:selected {
                background: rgba(0, 229, 255, 0.15);
                color: #00E5FF;
            }
            
            QMenuBar::item:pressed {
                background: rgba(0, 229, 255, 0.3);
            }
            
            QMenu {
                background-color: #151A27;
                color: #E2E8F0;
                border: 1px solid #2A3143;
                border-radius: 6px;
                padding: 5px;
            }
            
            QMenu::item {
                padding: 8px 30px 8px 20px;
                border-radius: 4px;
                font-size: 13px;
            }
            
            QMenu::item:selected {
                background-color: rgba(115, 128, 232, 0.2);
                color: #00E5FF;
                font-weight: bold;
            }
            
            QMenu::separator {
                height: 1px;
                background: #2A3143;
                margin: 4px 10px;
            }
            
            /* ================================================= */
            /* 7. KHUNG TIMELINE CHỐNG TRẮNG MẮT                 */
            /* ================================================= */
            QGraphicsView {
                background-color: #0B0E14; /* Ép màu nền tối đồng bộ */
                border: none; /* Xóa viền trắng */
                outline: none; /* Xóa nét đứt khi click chuột vào */
            }

            /* Khử nền của trang chứa Timeline nếu có */
            QWidget#pageTimeline, QWidget#Timeline {
                background-color: #0B0E14;
            }

            /* ================================================= */
            /* 8. CÁC Ô THỐNG KÊ DƯỚI CÙNG (DASHBOARD CARDS)     */
            /* ================================================= */
            /* Áp dụng chung cho các QFrame đóng vai trò là Card thống kê */
            QFrame {
                background-color: transparent;
            }

            /* Nếu bạn dùng QFrame cho các ô thống kê, hãy đổi màu cho nó nổi bật */
            QFrame#frameThongKe1, QFrame#frameThongKe2, QFrame#frameThongKe3, QFrame#frameThongKe4,
            QFrame#frame_2, QFrame#frame_3, QFrame#frame_4 /* Thay bằng đúng ID frame của bạn */ {
                background-color: #121824; /* Nền card sáng hơn nền app một chút */
                border: 1px solid #1E2538;
                border-radius: 12px;
            }

            /* Hiệu ứng phát sáng nhẹ khi hover chuột vào ô thống kê */
            QFrame#frameThongKe1:hover, QFrame#frameThongKe2:hover, QFrame#frameThongKe3:hover, QFrame#frameThongKe4:hover,
            QFrame#frame_2:hover, QFrame#frame_3:hover, QFrame#frame_4:hover {
                border: 1px solid #00E5FF;
                background-color: rgba(0, 229, 255, 0.05);
            }

            /* Label số lượng lớn (VD: Số 15, Số 20...) trong ô thống kê */
            QLabel#lblTotalValue, QLabel#lblTongBN, QLabel#lblTongBS {
                color: #00E5FF;
                font-size: 28px;
                font-weight: 900;
                background: transparent;
                border: none;
            }
        """)

    def connect_events(self):
        self.btntrangchu.clicked.connect(self.hien_thi_timeline)

        mapping = [
            (self.btnBenhNhan, self.forms["BN"], self.load_data_benhnhan),
            (self.btnBacSi, self.forms["BS"], self.load_data_bacsi),
            (self.btnDichVu, self.forms["DV"], self.load_data_dichvu),
            (self.btnPhongKham, self.forms["PK"], self.load_data_phongkham),
            (self.btnLichKham, self.forms["LK"], self.load_data_lichkham),
            (self.btnDoanhThu, self.forms["DT"], self.load_data_doanhthu),
        ]

        for btn, form, func in mapping:
            # Dùng form.objectName() thay cho f trực tiếp trong lambda nếu form là chuỗi, 
            # nhưng ở đây bạn đang lưu object form vào dict, nên logic của bạn đã đúng.
            btn.clicked.connect(lambda _, f=form, fn=func: self.mo_tab(f, fn))

        # Menu trên cùng
        self.actionProfile.triggered.connect(lambda: self.mo_tab(self.forms["PROFILE"], None))
        self.actionTh_ng_k.triggered.connect(lambda: self.mo_tab(self.forms["TK"], None))
        self.actionTh_ng_k_l_t_kh_m.triggered.connect(lambda: self.mo_tab(self.forms["TKLK"], None))
        self.actionDxuat.triggered.connect(self.dang_xuat)

    # ================= LOGIC TIMELINE =================
    def hien_thi_timeline(self):
        self.formChucNang.stackedWidgetMain.setCurrentWidget(self.forms["TL"])
        self.ve_timeline()

    def ve_timeline(self):
        try:
            lk = LichKhamController.get_all()
            bn = BenhNhanController.get_all()
            bs = BacSiController.get_all()
            dv = DichVuController.get_all()
            self.timeline_drawer.draw(lk, bn, bs, dv)
            if hasattr(self.forms["TL"], "lblTotalValue"):
                self.forms["TL"].lblTotalValue.setText(str(len(lk)))
        except Exception as e:
            print(f"Lỗi vẽ Timeline: {e}")

    # ================= HÀM HỖ TRỢ CHUNG =================
    def mo_tab(self, form, func):
        self.formChucNang.stackedWidgetMain.setCurrentWidget(form)
        if func:
            func()

    def update_time(self):
        self.lblTime.setText(QDateTime.currentDateTime().toString("HH:mm:ss"))

    def fill_table(self, table, data, headers):
        """Đổ dữ liệu cơ bản cho các bảng khác"""
        table.setRowCount(0)
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        for r, obj in enumerate(data):
            table.insertRow(r)
            vals = list(obj.values()) if isinstance(obj, dict) else [
                getattr(obj, a) for a in obj.__dict__ if not a.startswith('_')
            ]
            for c, val in enumerate(vals):
                table.setItem(r, c, QTableWidgetItem(str(val)))

    # ================= LOAD DỮ LIỆU CÁC BẢNG =================
    def load_data_benhnhan(self):
        self.fill_table(self.forms["BN"].tableBenhNhan, BenhNhanController.get_all(),
                        ["ID", "Tên", "SĐT", "Địa chỉ", "GT", "Ngày sinh"])

    def load_data_bacsi(self):
        self.fill_table(self.forms["BS"].tableBacSi, BacSiController.get_all(),
                        ["ID", "Họ Tên", "Giới Tính", "Chuyên Khoa"])

    def load_data_lichkham(self):
        """Hàm riêng cho Lịch khám để xử lý màu sắc Trạng thái"""
        headers = ["ID", "BN ID", "BS ID", "Phòng ID", "Dịch Vụ ID", "Ngày Khám", "Giờ Khám", "Trạng Thái"]
        data = LichKhamController.get_all()
        table = self.forms["LK"].tableLichKham
        
        table.setRowCount(0)
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for r, obj in enumerate(data):
            table.insertRow(r)
            # Lấy đúng thuộc tính từ Model (đảm bảo Model có self.trang_thai)
            vals = [obj.id, obj.benhnhan_id, obj.bacsi_id, obj.phongkham_id, 
                    obj.dichvu_id, obj.ngay_kham, obj.gio_kham, obj.trang_thai]
            
            for c, val in enumerate(vals):
                item = QTableWidgetItem(str(val))
                # Highlight cột Trạng Thái (index 7)
                if c == 7:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if val == "Chờ khám": item.setForeground(Qt.GlobalColor.yellow)
                    elif val == "Đã khám": item.setForeground(Qt.GlobalColor.green)
                    elif val == "Đã hủy": item.setForeground(Qt.GlobalColor.red)
                table.setItem(r, c, item)

    def load_data_dichvu(self):
        self.fill_table(self.forms["DV"].tableDichVu, DichVuController.get_all(),
                        ["ID", "Tên Dịch Vụ", "Đơn Giá"])

    def load_data_phongkham(self):
        self.fill_table(self.forms["PK"].tablePhong, PhongKhamController.get_all(),
                        ["ID", "Tên Phòng", "Số Giường", "Mô tả"])

    def load_data_doanhthu(self):
        """Hàm load dữ liệu bảng doanh thu và gọi tính tổng tiền"""
        headers = ["ID Hóa Đơn", "Mã Lịch Khám", "Tổng Tiền (VNĐ)", "Ngày Thanh Toán", "Tên Bệnh Nhân"]
        try:
            data = DoanhThuController.get_all()
            # Trỏ về form DT (FormDoanhThu) thay vì form TK cũ
            if hasattr(self.forms["DT"], "tableDoanhThu"):
                self.fill_table(self.forms["DT"].tableDoanhThu, data, headers)
        except Exception as e:
            print(f"Lỗi load dữ liệu bảng doanh thu: {e}")
            
        # Gọi luôn hàm cập nhật tổng doanh thu ở label
        self.load_thong_ke_doanh_thu()

    def load_thong_ke_doanh_thu(self):
        try:
            # Truy vấn tổng tiền từ bảng Doanh thu
            sql = "SELECT SUM(tong_tien) as Tong FROM DoanhThu"
            result = fetch_one(sql) 
            
            tong_tien = result['Tong'] if result and result['Tong'] else 0
            
            # Đẩy lên nhãn hiển thị (Chú ý: nếu trong FormDoanhThu.ui bạn có tạo label lblTongDoanhThu thì hàm này mới chạy)
            if hasattr(self.forms["DT"], "lblTongDoanhThu"):
                self.forms["DT"].lblTongDoanhThu.setText(f"{tong_tien:,.0f} VNĐ")
        except Exception as e:
            print(f"Lỗi tính tổng doanh thu: {e}")

    def dang_xuat(self):
        if QMessageBox.question(self, 'Xác nhận', 'Bạn muốn đăng xuất?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.close()

# ================= RUN APP =================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginApp()
    main_win = MainApp()
    login.login_successful.connect(main_win.show)
    login.show()
    sys.exit(app.exec())
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMessageBox
import sys
import re
class DangKyApp:
    def __init__(self):
        self.ui = uic.loadUi("Giaodienchinh.ui")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DangKyApp()
    window.ui.show()
    sys.exit(app.exec())
