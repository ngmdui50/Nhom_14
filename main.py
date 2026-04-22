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
from Controller.taikhoan_Controller import TaiKhoanController
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
