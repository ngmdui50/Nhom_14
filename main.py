import sys
import os
from datetime import datetime
from PyQt6 import uic
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMessageBox
import re

from PyQt6.QtWidgets import (
    QApplication, QInputDialog, QMainWindow, QMessageBox,
    QVBoxLayout, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import QTimer, QDateTime, pyqtSignal, Qt

from Model.connecDB import fetch_one
<<<<<<< HEAD
from Controller.taikhoan_Controller import TaiKhoanController
=======
from Model.benhnhan_Model import BenhNhan

>>>>>>> 6c7d68a (fix UI conflict)
# ================= IMPORT HELPER & CONTROLLER =================
try:
    from Helper.TimelineHelper import TimelineDrawer
    from Controller.benhnhan_Controller import BenhNhanController
    from Controller.bacsi_Controller import BacSiController
    from Controller.dichvu_Controller import DichVuController
    from Controller.phong_Controller import PhongKhamController
    from Controller.lichkham_Controller import LichKhamController
    from Controller.doanhthu_Controller import DoanhThuController # <-- THÊM IMPORT CONTROLLER DOANH THU
    from Controller.thongke_Controller import ThongKeController
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
        self.apply_style()

    def apply_style(self):
        """Hàm nạp file QSS với đường dẫn tuyệt đối"""
        try:
            # Lấy đường dẫn tệp style.qss nằm cùng thư mục với file python này
            current_dir = os.path.dirname(os.path.abspath(__file__))
            qss_file = os.path.join(current_dir, "style.qss")
            
            with open(qss_file, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Lỗi khi nạp file CSS: {e}")
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
            "TAIKHOAN": uic.loadUi("View/FormTaiKhoan.ui"),
        }

        for form in self.forms.values():
            self.formChucNang.stackedWidgetMain.addWidget(form)

<<<<<<< HEAD
        
=======
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

>>>>>>> 6c7d68a (fix UI conflict)
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
        self.actionT_i_Kho_n.triggered.connect(lambda: self.mo_tab(self.forms["TAIKHOAN"], self.load_data_taikhoan))
        self.actionTh_ng_k.triggered.connect(lambda: self.mo_tab(self.forms["TK"], None))
        self.actionTh_ng_k_l_t_kh_m.triggered.connect(lambda: self.mo_tab(self.forms["TKLK"], None))
        self.actionDxuat.triggered.connect(self.dang_xuat)
        # Kết nối các nút chức năng chính
        self.btnThem.clicked.connect(self.xu_ly_them)
        self.btnSua.clicked.connect(self.xu_ly_sua)
        self.btnXoa.clicked.connect(self.xu_ly_xoa)
        self.btnTimKiem.clicked.connect(self.xu_ly_tim_kiem)

        # Sự kiện click vào dòng trong bảng Bác sĩ để hiển thị lên form nhập liệu
        self.forms["BS"].tableBacSi.itemClicked.connect(self.do_du_lieu_bacsi_len_form)

# Kết nối sự kiện click vào bảng Bệnh nhân để hiển thị dữ liệu lên form nhập liệu
        self.forms["BN"].tableBenhNhan.itemClicked.connect(self.do_du_lieu_benhnhan_len_form)
        self.forms["DV"].tableDichVu.itemClicked.connect(self.do_du_lieu_dichvu_len_form)
        self.forms["DT"].tableDoanhThu.itemClicked.connect(self.do_du_lieu_doanhthu_len_form)
        self.forms["LK"].tableLichKham.itemClicked.connect(self.do_du_lieu_lichkham_len_form)
        self.forms["PK"].tablePhong.itemClicked.connect(self.do_du_lieu_phong_len_form)
        self.forms["TK"].btnthongke.clicked.connect(self.xu_ly_tim_kiem_tk)
        self.forms["TK"].btnxuatfile.clicked.connect(self.xu_ly_them_tk) # Xuất file coi như là 'thêm' báo cáo
    
    def get_active_form(self):
        return self.formChucNang.stackedWidgetMain.currentWidget()
    def xu_ly_them(self):
        active_form = self.formChucNang.stackedWidgetMain.currentWidget()
        if active_form == self.forms["BS"]:
            self.xu_ly_them_bs() # Code thêm bác sĩ cũ của bạn để vào hàm này
        elif active_form == self.forms["BN"]:
            self.xu_ly_them_bn()
        elif active_form == self.forms["DV"]: self.xu_ly_them_dv() # Thêm dòng này
        elif active_form == self.forms["DT"]: self.xu_ly_them_dt()
        elif active_form == self.forms["LK"]: self.xu_ly_them_lk()
        elif active_form == self.forms["PK"]: self.xu_ly_them_phong()
        elif active_form == self.forms["TK"]: self.xu_ly_them_tk()
        
    def xu_ly_sua(self):
        active_form = self.formChucNang.stackedWidgetMain.currentWidget()
        if active_form == self.forms["BS"]:
            self.xu_ly_sua_bs()
        elif active_form == self.forms["BN"]:
            self.xu_ly_sua_bn()
        elif active_form == self.forms["DV"]: self.xu_ly_sua_dv() # Thêm dòng này
        elif active_form == self.forms["DT"]: self.xu_ly_sua_dt()
        elif active_form == self.forms["LK"]: self.xu_ly_sua_lk()
        elif active_form == self.forms["PK"]: self.xu_ly_sua_phong()
        elif active_form == self.forms["TK"]: self.xu_ly_sua_tk()
    
    def xu_ly_xoa(self):
        active_form = self.formChucNang.stackedWidgetMain.currentWidget()
        if active_form == self.forms["BS"]:
            self.xu_ly_xoa_bs()
        elif active_form == self.forms["BN"]:
            self.xu_ly_xoa_bn()
        elif active_form == self.forms["DV"]: self.xu_ly_xoa_dv() # Thêm dòng này
        elif active_form == self.forms["DT"]: self.xu_ly_xoa_dt()
        elif active_form == self.forms["LK"]: self.xu_ly_xoa_lk()
        elif active_form == self.forms["PK"]: self.xu_ly_xoa_phong()
        elif active_form == self.forms["TK"]: self.xu_ly_xoa_tk()
    
    def xu_ly_tim_kiem(self):
        active_form = self.get_active_form()
        if active_form == self.forms["BS"]:
            self.xu_ly_tim_kiem_bs()
        elif active_form == self.forms["BN"]:
            self.xu_ly_tim_kiem_bn()
        elif active_form == self.forms["DV"]: self.xu_ly_tim_kiem_dv() # Thêm dòng này
        elif active_form == self.forms["DT"]: self.xu_ly_tim_kiem_dt()
        elif active_form == self.forms["LK"]: self.xu_ly_tim_kiem_lk()
        elif active_form == self.forms["PK"]: self.xu_ly_tim_kiem_phong()
        elif active_form == self.forms["TK"]: self.xu_ly_tim_kiem_tk()
    def show_thongke(self):
        self.formChucNang.stackedWidgetMain.setCurrentWidget(self.forms["TK"])
        self.setup_thong_ke_ui() # Load lại các combobox
        self.xu_ly_tim_kiem_tk() # Tự động chạy thống kê mặc định
    
    # ================= LOGIC TIMELINE =================
    def hien_thi_timeline(self):
        self.formChucNang.stackedWidgetMain.setCurrentWidget(self.forms["TL"])
        self.ve_timeline()
    def do_du_lieu_bacsi_len_form(self):
        table = self.forms["BS"].tableBacSi
        current_row = table.currentRow()
        if current_row < 0:
            return

        # Đổ dữ liệu vào các QLineEdit [cite: 36, 37, 38]
        self.forms["BS"].txtIDBS.setText(table.item(current_row, 0).text())
        self.forms["BS"].txtTenBS.setText(table.item(current_row, 1).text())
        self.forms["BS"].txtGioiTinhBS.setText(table.item(current_row, 2).text())
        self.forms["BS"].txtChuyenKhoa.setText(table.item(current_row, 3).text())
    def xu_ly_them(self):
        active_form = self.formChucNang.stackedWidgetMain.currentWidget()
        
        if active_form == self.forms["BS"]:
            ten = self.forms["BS"].txtTenBS.text()
            gioi_tinh = self.forms["BS"].txtGioiTinhBS.text()
            chuyen_khoa = self.forms["BS"].txtChuyenKhoa.text()

            if not ten:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên bác sĩ!")
                return

            BacSiController.insert(ten, gioi_tinh, chuyen_khoa)
            QMessageBox.information(self, "Thông báo", "Thêm bác sĩ thành công!")
            self.load_data_bacsi() # Refresh bảng
    def xu_ly_sua(self):
        active_form = self.formChucNang.stackedWidgetMain.currentWidget()
        
        if active_form == self.forms["BS"]:
            id_bs = self.forms["BS"].txtIDBS.text()
            if not id_bs:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn bác sĩ cần sửa!")
                return
            
            ten = self.forms["BS"].txtTenBS.text()
            gioi_tinh = self.forms["BS"].txtGioiTinhBS.text()
            chuyen_khoa = self.forms["BS"].txtChuyenKhoa.text()

            BacSiController.update(id_bs, ten, gioi_tinh, chuyen_khoa)
            QMessageBox.information(self, "Thông báo", "Cập nhật thành công!")
            self.load_data_bacsi()
    def xu_ly_xoa(self):
        active_form = self.formChucNang.stackedWidgetMain.currentWidget()
        
        if active_form == self.forms["BS"]:
            id_bs = self.forms["BS"].txtIDBS.text()
            if not id_bs:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn bác sĩ cần xóa!")
                return

            confirm = QMessageBox.question(self, "Xác nhận", f"Bạn có chắc muốn xóa bác sĩ ID: {id_bs}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if confirm == QMessageBox.StandardButton.Yes:
                BacSiController.delete(id_bs)
                self.load_data_bacsi()
                # Xóa sạch form sau khi xóa
                self.forms["BS"].txtIDBS.clear()
                self.forms["BS"].txtTenBS.clear()
    def xu_ly_tim_kiem(self):
        active_form = self.formChucNang.stackedWidgetMain.currentWidget()
        
        if active_form == self.forms["BS"]:
            keyword, ok = QInputDialog.getText(self, "Tìm kiếm", "Nhập tên hoặc chuyên khoa bác sĩ:")
            
            if ok and keyword:
                results = BacSiController.search(keyword)
                self.fill_table(self.forms["BS"].tableBacSi, results,
                                ["ID", "Họ Tên", "Giới Tính", "Chuyên Khoa"])
            elif ok and not keyword:
                self.load_data_bacsi() # Nếu để trống thì load lại toàn bộ
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
# --- LOGIC CHI TIẾT CHO BỆNH NHÂN ---
    def do_du_lieu_benhnhan_len_form(self):
        try:
            table = self.forms["BN"].tableBenhNhan
            row = table.currentRow()
            if row < 0: return

            # Hàm lấy text an toàn, nếu ô rỗng thì trả về "" tránh crash
            def get_text(col):
                item = table.item(row, col)
                return item.text() if item is not None else ""

            # Đổ dữ liệu lên giao diện
            self.forms["BN"].txtIDBN.setText(get_text(0))
            self.forms["BN"].txtTenBN.setText(get_text(1))
            self.forms["BN"].txtSDT.setText(get_text(2))
            self.forms["BN"].txtDiaChi.setText(get_text(3))
            self.forms["BN"].txtGioiTinh.setText(get_text(4))
            self.forms["BN"].txtNgaySinh.setText(get_text(5))
        except Exception as e:
            print(f"Lỗi khi chọn bệnh nhân: {e}")

    def xu_ly_them(self):
        # Kiểm tra widget đang hiển thị trong stackedWidgetMain
        current_form = self.stackedWidgetMain.currentWidget()
        if current_form == self.forms["BS"]:
            self.xu_ly_them_bs()
        elif current_form == self.forms["BN"]:
            self.xu_ly_them_bn()
    def xu_ly_sua_bn(self):
        try:
            # 1. Lấy dữ liệu từ các ô nhập liệu trên giao diện (.strip() để xóa khoảng trắng thừa)
            id_bn = self.forms["BN"].txtIDBN.text().strip()
            ten = self.forms["BN"].txtTenBN.text().strip()
            sdt = self.forms["BN"].txtSDT.text().strip()
            dia_chi = self.forms["BN"].txtDiaChi.text().strip()
            gioi_tinh = self.forms["BN"].txtGioiTinh.text().strip()
            ngay_sinh = self.forms["BN"].txtNgaySinh.text().strip()

            # 2. Kiểm tra xem người dùng đã chọn bệnh nhân chưa (ID có trống không)
            if not id_bn:
                QMessageBox.warning(self, "Thông báo", "Vui lòng click chọn một bệnh nhân từ bảng trước khi sửa!")
                return
            
            # Kiểm tra tên không được để trống
            if not ten:
                QMessageBox.warning(self, "Cảnh báo", "Tên bệnh nhân không được để trống!")
                return

            # 3. Gọi Controller để cập nhật vào Database
            # Nhớ ép kiểu ID sang int để tránh lỗi khi đẩy vào Database
            BenhNhanController.update(int(id_bn), ten, sdt, dia_chi, gioi_tinh, ngay_sinh)

            # 4. Hiển thị thông báo thành công
            QMessageBox.information(self, "Thành công", f"Đã cập nhật thông tin bệnh nhân:\n{ten}")

            # 5. Tải lại bảng dữ liệu để hiển thị thông tin mới nhất
            self.load_data_benhnhan()

        except ValueError:
            QMessageBox.critical(self, "Lỗi dữ liệu", "Mã bệnh nhân (ID) không hợp lệ. Vui lòng kiểm tra lại!")
        except Exception as e:
            # Nếu có lỗi (như sai tên bảng, lỗi SQL...), app sẽ hiện thông báo này thay vì bị văng code
            QMessageBox.critical(self, "Lỗi hệ thống", f"Không thể sửa thông tin bệnh nhân.\nChi tiết lỗi: {str(e)}")
    def xu_ly_xoa(self):
        current_form = self.stackedWidgetMain.currentWidget()
        if current_form == self.forms["BS"]:
            self.xu_ly_xoa_bs()
        elif current_form == self.forms["BN"]:
            self.xu_ly_xoa_bn()

    def xu_ly_tim_kiem(self):
        current_form = self.stackedWidgetMain.currentWidget()
        if current_form == self.forms["BS"]:
            self.xu_ly_tim_kiem_bs()
        elif current_form == self.forms["BN"]:
            self.xu_ly_tim_kiem_bn()
        
    # ================= LOGIC DỊCH VỤ =================

    def do_du_lieu_dichvu_len_form(self):
        """Đổ dữ liệu từ bảng lên các ô nhập liệu khi click vào dòng"""
        table = self.forms["DV"].tableDichVu
        row = table.currentRow()
        if row < 0: return

        self.forms["DV"].txtIDDichVu.setText(table.item(row, 0).text())
        self.forms["DV"].txtTenDichVu.setText(table.item(row, 1).text())
        self.forms["DV"].txtGiaTien.setText(table.item(row, 2).text())

    def xu_ly_them_dv(self):
        ten = self.forms["DV"].txtTenDichVu.text().strip()
        gia = self.forms["DV"].txtGiaTien.text().strip()

        if not ten or not gia:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ tên và giá dịch vụ!")
            return

        try:
            DichVuController.insert([ten, float(gia)])
            QMessageBox.information(self, "Thông báo", f"Thêm dịch vụ '{ten}' thành công!")
            self.load_data_dichvu() # Refresh bảng
            self.lam_moi_form_dv()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể thêm dịch vụ: {e}")

    def xu_ly_sua_dv(self):
        id_dv = self.forms["DV"].txtIDDichVu.text()
        ten = self.forms["DV"].txtTenDichVu.text().strip()
        gia = self.forms["DV"].txtGiaTien.text().strip()

        if not id_dv:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn dịch vụ từ bảng để sửa!")
            return

        try:
            DichVuController.update(id_dv, [ten, float(gia)])
            QMessageBox.information(self, "Thông báo", "Cập nhật dịch vụ thành công!")
            self.load_data_dichvu()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi cập nhật: {e}")

    def xu_ly_xoa_dv(self):
        id_dv = self.forms["DV"].txtIDDichVu.text()
        if not id_dv:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn dịch vụ cần xóa!")
            return

        confirm = QMessageBox.question(self, "Xác nhận", f"Bạn có chắc muốn xóa dịch vụ ID: {id_dv}?", 
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            DichVuController.delete(id_dv)
            self.load_data_dichvu()
            self.lam_moi_form_dv()

    def xu_ly_tim_kiem_dv(self):
        keyword, ok = QInputDialog.getText(self, "Tìm kiếm dịch vụ", "Nhập tên dịch vụ cần tìm:")
        if ok and keyword.strip():
            results = DichVuController.search(keyword.strip())
            self.fill_table(self.forms["DV"].tableDichVu, results, ["ID", "Tên Dịch Vụ", "Đơn Giá"])
        elif ok and not keyword.strip():
            self.load_data_dichvu()

    def lam_moi_form_dv(self):
        """Xóa trắng các ô nhập liệu dịch vụ"""
        self.forms["DV"].txtIDDichVu.clear()
        self.forms["DV"].txtTenDichVu.clear()
        self.forms["DV"].txtGiaTien.clear()
    
    def do_du_lieu_lichkham_len_form(self):
        table = self.forms["LK"].tableLichKham
        row = table.currentRow()
        if row < 0: return

        # Đổ dữ liệu vào các ô nhập liệu (theo tên object trong FormLichKham.ui)
        self.forms["LK"].txtIDLich.setText(table.item(row, 0).text())
        self.forms["LK"].txtIDBN_Lich.setText(table.item(row, 1).text())
        self.forms["LK"].txtIDBS_Lich.setText(table.item(row, 2).text())
        self.forms["LK"].txtNgayKham.setText(table.item(row, 3).text())
        self.forms["LK"].txtGioKham.setText(table.item(row, 4).text())
        
        # Cập nhật ComboBox trạng thái
        trang_thai = table.item(row, 5).text()
        index = self.forms["LK"].comboBoxTrangThai.findText(trang_thai)
        if index >= 0: self.forms["LK"].comboBoxTrangThai.setCurrentIndex(index)

    def xu_ly_them_lk(self):
        id_bn = self.forms["LK"].txtIDBN_Lich.text().strip()
        id_bs = self.forms["LK"].txtIDBS_Lich.text().strip()
        ngay = self.forms["LK"].txtNgayKham.text().strip()
        gio = self.forms["LK"].txtGioKham.text().strip()
        trang_thai = self.forms["LK"].comboBoxTrangThai.currentText()

        if not id_bn or not id_bs:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập ID Bệnh nhân và Bác sĩ!")
            return

        try:
            # Lưu ý: Controller của bạn cần nhận list [id_bn, id_bs, ngay, gio, trang_thai]
            LichKhamController.insert([id_bn, id_bs, ngay, gio, trang_thai])
            QMessageBox.information(self, "Thành công", "Đã thêm lịch khám mới!")
            self.load_data_lichkham()
            self.lam_moi_form_lk()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể thêm: {e}")

    def xu_ly_sua_lk(self):
        id_lk = self.forms["LK"].txtIDLich.text()
        if not id_lk:
            QMessageBox.warning(self, "Lỗi", "Hãy chọn một lịch khám để sửa!")
            return

        values = [
            self.forms["LK"].txtIDBN_Lich.text(),
            self.forms["LK"].txtIDBS_Lich.text(),
            self.forms["LK"].txtNgayKham.text(),
            self.forms["LK"].txtGioKham.text(),
            self.forms["LK"].comboBoxTrangThai.currentText()
        ]

        if LichKhamController.update(id_lk, values):
            QMessageBox.information(self, "Thông báo", "Cập nhật thành công!")
            self.load_data_lichkham()

    def xu_ly_xoa_lk(self):
        id_lk = self.forms["LK"].txtIDLich.text()
        if not id_lk: return

        ret = QMessageBox.question(self, "Xác nhận", f"Xóa lịch khám ID {id_lk}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if ret == QMessageBox.StandardButton.Yes:
            LichKhamController.delete(id_lk)
            self.load_data_lichkham()
            self.lam_moi_form_lk()

    def xu_ly_tim_kiem_lk(self):
        keyword, ok = QInputDialog.getText(self, "Tìm kiếm", "Nhập ID BN hoặc ID BS:")
        if ok and keyword:
            results = LichKhamController.search(keyword)
            # Tương tự load_data, chuyển kết quả search thành list để fill_table
            display_data = [[r["id"], r["benhnhan_id"], r["bacsi_id"], r["ngay_kham"], r["gio_kham"], r["TrangThai"]] for r in results]
            self.fill_table(self.forms["LK"].tableLichKham, display_data, ["ID", "Mã BN", "Mã BS", "Ngày Khám", "Giờ Khám", "Trạng Thái"])

    def lam_moi_form_lk(self):
        self.forms["LK"].txtIDLich.clear()
        self.forms["LK"].txtIDBN_Lich.clear()
        self.forms["LK"].txtIDBS_Lich.clear()
        self.forms["LK"].txtNgayKham.clear()
        self.forms["LK"].txtGioKham.clear()

    # ================= LOGIC THỐNG KÊ =================

    def xu_ly_tim_kiem_tk(self):
        """Đây là chức năng chính: Chạy Thống kê"""
        loai = self.forms["TK"].cboxloai.currentText()
        
        if loai == "Doanh thu theo dịch vụ":
            data = ThongKeController.thong_ke_doanh_thu_dich_vu()
            headers = ["Tên Dịch Vụ", "Số Lượng", "Tổng Doanh Thu"]
            # Chuyển dict thành list để fill_table
            display_data = [[r['ten_dich_vu'], r['so_luong'], f"{r['tong_tien']:,.0f}"] for r in data]
            self.fill_table(self.forms["TK"].tableThongKe, display_data, headers)
            
        elif loai == "Danh sách lượt khám":
            data = ThongKeController.thong_ke_luot_kham_theo_ngay()
            headers = ["Ngày Khám", "Bác Sĩ", "Bệnh Nhân", "Giờ Khám"]
            display_data = [[r['ngay_kham'], r['ten_bac_si'], r['ten_benh_nhan'], r['gio_kham']] for r in data]
            self.fill_table(self.forms["TK"].tableThongKe, display_data, headers)

    def xu_ly_them_tk(self):
        """Quy ước: Thêm = Xuất bản ghi báo cáo ra file Excel/CSV"""
        import csv
        path = "BaoCao_ThongKe.csv"
        try:
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                # Lấy header và dữ liệu từ tableThongKe để lưu
                table = self.forms["TK"].tableThongKe
                headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
                writer.writerow(headers)
                
                for row in range(table.rowCount()):
                    row_data = [table.item(row, col).text() for col in range(table.columnCount())]
                    writer.writerow(row_data)
            
            QMessageBox.information(self, "Thành công", f"Đã xuất báo cáo ra file: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xuất file: {e}")

    def xu_ly_xoa_tk(self):
        """Quy ước: Xóa = Dọn dẹp bảng hiển thị"""
        self.forms["TK"].tableThongKe.setRowCount(0)

    def xu_ly_sua_tk(self):
        """Quy ước: Sửa = Thay đổi bộ lọc và chạy lại (Refresh)"""
        self.xu_ly_tim_kiem_tk()
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
    
    def do_du_lieu_doanhthu_len_form(self):
        table = self.forms["DT"].tableDoanhThu
        row = table.currentRow()
        if row < 0: return
        
        # Đổ dữ liệu vào các QLineEdit tương ứng trong FormDoanhThu.ui
        self.forms["DT"].txtIDDoanhThu.setText(table.item(row, 0).text())
        self.forms["DT"].txtIDLichKham.setText(table.item(row, 1).text())
        self.forms["DT"].txtTongTien.setText(table.item(row, 2).text())
        self.forms["DT"].txtNgayThanhToan.setText(table.item(row, 3).text())

    def xu_ly_them_dt(self):
        # Lưu ý: Doanh thu thường tự động tạo, nhưng nếu bạn muốn thêm tay:
        id_lk, ok1 = QInputDialog.getText(self, "Thêm", "Nhập Mã Lịch Khám:")
        tien, ok2 = QInputDialog.getDouble(self, "Thêm", "Nhập số tiền:", 0, 0, 1000000000, 0)
        if ok1 and ok2:
            DoanhThuController.insert(id_lk, tien, datetime.now().strftime("%Y-%m-%d"), "Khách vãng lai")
            self.load_data_doanhthu()

    def xu_ly_sua_dt(self):
        id_dt = self.forms["DT"].txtIDDoanhThu.text()
        if not id_dt:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn hóa đơn cần sửa!")
            return
        
        moi_tien = self.forms["DT"].txtTongTien.text()
        moi_ngay = self.forms["DT"].txtNgayThanhToan.text()
        
        DoanhThuController.update(id_dt, moi_tien, moi_ngay)
        QMessageBox.information(self, "Thông báo", "Cập nhật thành công!")
        self.load_data_doanhthu()

    def xu_ly_xoa_dt(self):
        id_dt = self.forms["DT"].txtIDDoanhThu.text()
        if not id_dt:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn hóa đơn cần xóa!")
            return
            
        confirm = QMessageBox.question(self, "Xác nhận", f"Xóa hóa đơn {id_dt}?",  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            DoanhThuController.delete(id_dt)
            self.load_data_doanhthu()

    def xu_ly_tim_kiem_dt(self):
        keyword, ok = QInputDialog.getText(self, "Tìm kiếm", "Nhập tên BN hoặc Mã LK:")
        if ok and keyword:
            results = DoanhThuController.search(keyword)
            self.fill_table(self.forms["DT"].tableDoanhThu, results, ["ID", "Mã LK", "Tiền", "Ngày", "Tên BN"])

    def do_du_lieu_phong_len_form(self):
        """Đổ dữ liệu từ bảng lên các ô nhập liệu"""
        table = self.forms["PK"].tablePhong
        row = table.currentRow()
        if row < 0: return

        self.forms["PK"].txtIDPhong.setText(table.item(row, 0).text())
        self.forms["PK"].txtTenPhong.setText(table.item(row, 1).text())
        self.forms["PK"].txtSoGiuong.setText(table.item(row, 2).text())
        self.forms["PK"].txtMoTa.setText(table.item(row, 3).text())

    def xu_ly_them_phong(self):
        ten = self.forms["PK"].txtTenPhong.text().strip()
        so_giuong = self.forms["PK"].txtSoGiuong.text().strip()
        mo_ta = self.forms["PK"].txtMoTa.text().strip()

        if not ten or not so_giuong:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên phòng và số giường!")
            return

        try:
            PhongKhamController.insert([ten, int(so_giuong), mo_ta])
            QMessageBox.information(self, "Thông báo", "Thêm phòng thành công!")
            self.load_data_phong()
            self.lam_moi_form_phong()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể thêm: {e}")

    def xu_ly_sua_phong(self):
        id_phong = self.forms["PK"].txtIDPhong.text()
        if not id_phong:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn phòng cần sửa từ bảng!")
            return

        ten = self.forms["PK"].txtTenPhong.text()
        so_giuong = self.forms["PK"].txtSoGiuong.text()
        mo_ta = self.forms["PK"].txtMoTa.text()

        if PhongKhamController.update(id_phong, [ten, int(so_giuong), mo_ta]):
            QMessageBox.information(self, "Thông báo", "Cập nhật thành công!")
            self.load_data_phong()

    def xu_ly_xoa_phong(self):
        id_phong = self.forms["PK"].txtIDPhong.text()
        if not id_phong: return

        confirm = QMessageBox.question(self, "Xác nhận", f"Xóa phòng ID {id_phong}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            PhongKhamController.delete(id_phong)
            self.load_data_phong()
            self.lam_moi_form_phong()

    def xu_ly_tim_kiem_phong(self):
        keyword, ok = QInputDialog.getText(self, "Tìm kiếm", "Nhập tên phòng cần tìm:")
        if ok and keyword.strip():
            results = PhongKhamController.search(keyword.strip())
            # Convert kết quả search thành list để fill_table
            display_data = [[r["id"], r["ten_phong"], r["so_giuong"], r["mo_ta"]] for r in results]
            self.fill_table(self.forms["PK"].tablePhong, display_data, ["ID", "Tên Phòng", "Số Giường", "Mô Tả"])
        elif ok:
            self.load_data_phong()

    def lam_moi_form_phong(self):
        self.forms["PK"].txtIDPhong.clear()
        self.forms["PK"].txtTenPhong.clear()
        self.forms["PK"].txtSoGiuong.clear()
        self.forms["PK"].txtMoTa.clear()
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
    def load_data_taikhoan(self):
        """Hàm lấy dữ liệu từ DB và đổ lên tableTaiKhoan"""
        try:
            headers = ["ID", "Username", "Password", "Họ Tên", "Quyền"]
            data = TaiKhoanController.get_all()
            
            # Đổ dữ liệu vào tableTaiKhoan nằm trong form TAIKHOAN
            self.fill_table(self.forms["TAIKHOAN"].tableTaiKhoan, data, headers)
        except Exception as e:
            print(f"Lỗi load dữ liệu bảng tài khoản: {e}")
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

    def setup_thong_ke_ui(self):
        # Thiết lập các loại thống kê
        self.forms["TK"].cboxloai.addItems([
            "Doanh thu theo dịch vụ", 
            "Danh sách lượt khám"
        ])
        # Thiết lập mốc thời gian (ví dụ đơn giản)
        self.forms["TK"].cboxthoigian.addItems(["Tất cả", "Tháng hiện tại", "Năm nay"])

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

class DangKyApp:
    def __init__(self):
        self.ui = uic.loadUi("Giaodienchinh.ui")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DangKyApp()
    window.ui.show()
    sys.exit(app.exec())
