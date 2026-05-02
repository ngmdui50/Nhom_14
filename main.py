import sys
import os
from datetime import datetime
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication, QInputDialog, QMainWindow, QMessageBox,
    QVBoxLayout, QTableWidgetItem, QHeaderView, QAbstractItemView, QLineEdit,
    QListWidget, QListWidgetItem, QHBoxLayout, QLabel, QPushButton, QComboBox, QTableWidget
)
# main.py
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QHeaderView,
                             QDialog, QGraphicsItem) # Thêm QDialog và QGraphicsItem
from PyQt6.QtCore import Qt, QTimer, QDate, QTime # Thêm QDate, QTime
from PyQt6.uic import loadUi # Đảm bảo đã có loadUi

from PyQt6.QtGui import QColor, QBrush # Thêm thư viện tô màu
from PyQt6.QtCore import QTimer, QDateTime, pyqtSignal, Qt
from Helper.TimelineHelper import TimelineDrawer
from Controller.calam_Controller import CaLamController

# ================= 1. VÁ LỖI DATABASE TRƯỚC KHI IMPORT CONTROLLER =================
try:
    from Model import connecDB
    
    def _robust_execute(query, params=()):
        conn = connecDB.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query.replace("%s", "?"), params)
            conn.commit()
            if query.strip().upper().startswith(("DELETE", "UPDATE")) and cursor.rowcount == 0:
                raise Exception("Không tìm thấy dữ liệu để thao tác. Có thể ID không đúng!")
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            raise e  
        finally:
            conn.close()
            
    connecDB.execute_query = _robust_execute

    _orig_fetchall = connecDB.fetch_all
    def _patched_fetchall(query, params=()):
        return _orig_fetchall(query.replace("%s", "?"), params)
    connecDB.fetch_all = _patched_fetchall

    _orig_fetchone = connecDB.fetch_one
    def _patched_fetchone(query, params=()):
        return _orig_fetchone(query.replace("%s", "?"), params)
    connecDB.fetch_one = _patched_fetchone
except Exception as e:
    print(f"Lỗi Patch SQLite: {e}")


# ================= 2. IMPORT HELPER & CONTROLLER =================
from Model.connecDB import fetch_one, execute_query
from Controller.taikhoan_Controller import TaiKhoanController
try:
    from Helper.TimelineHelper import TimelineDrawer
    from Controller.benhnhan_Controller import BenhNhanController
    from Controller.bacsi_Controller import BacSiController
    from Controller.dichvu_Controller import DichVuController
    from Controller.phong_Controller import PhongKhamController
    from Controller.lichkham_Controller import LichKhamController
    from Controller.hoadon_Controller import HoaDonController
    from Controller.thongke_Controller import ThongKeController
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from Helper.TimelineHelper import TimelineDrawer

# ================= LOGIN WINDOW =================
class LoginApp(QMainWindow):
    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        try:
            uic.loadUi("View/dangnhap.ui", self)
            self.btndangnhap.clicked.connect(self.check_login)
        except Exception as e:
            print(f"Lỗi load form Đăng nhập: {e}")

    def check_login(self):
        self.login_successful.emit()
        self.close()
class DialogChiTietLichKham(QDialog):
    def __init__(self, parent=None, lich_id=None):
        super().__init__(parent)
        self.main_app = parent # Tham chiếu đến MainApp
        self.lich_id = lich_id
        self.is_edit_mode = False
        self.init_ui()

    def init_ui(self):
        # 1. Load file UI
        loadUi("View/FormChiTietLichKham.ui", self)
        
        # 2. Khởi tạo dữ liệu trạng thái cho ComboBox (Cột trang_thai)
        self.cbtrang_thai.clear()
        self.cbtrang_thai.addItems(["Chờ Khám", "Đang Khám", "Đã Xong", "Hủy Lịch"])
        
        # 3. Kết nối sự kiện nút bấm
        self.btnEdit.clicked.connect(self.bat_che_do_sua)
        self.btnSave.clicked.connect(self.luu_thong_tin_sua)
        self.btnClose.clicked.connect(self.close)
        
        # 4. Load dữ liệu
        self.load_data()
        self.set_che_do_chiren(True) # Mặc định chỉ đọc

    def load_data(self):
        if not self.lich_id: return
        
        # 💎 HÀM HỖ TRỢ: Tự động trích xuất dữ liệu dù nó là Object hay Dictionary
        def val(item, *keys):
            if isinstance(item, dict):
                for k in keys:
                    if k in item and item[k] is not None: return item[k]
            else:
                for k in keys:
                    if hasattr(item, k) and getattr(item, k) is not None: return getattr(item, k)
            return ""

        try:
            # 1. Lấy dữ liệu Lịch khám
            lk_data = LichKhamController.get_all()
            
            l = None
            for x in lk_data:
                # Dùng hàm val() để lấy ID an toàn
                x_id = str(val(x, 'id', 'ID')).strip()
                if x_id == str(self.lich_id).strip():
                    l = x
                    break
                    
            if not l: 
                raise Exception(f"Không tìm thấy lịch khám có ID là '{self.lich_id}'")

            # 2. Tạo từ điển map ID -> Tên
            # Hàm val() sẽ tự dò tìm nếu bạn đặt tên biến là ho_ten, ten, hay ten_benh_nhan...
            dict_bn = {str(val(bn, 'id', 'ID')): str(val(bn, 'ho_ten', 'ten', 'ten_benh_nhan')) for bn in BenhNhanController.get_all()}
            dict_bs = {str(val(bs, 'id', 'ID')): str(val(bs, 'ho_ten', 'ten', 'ten_bac_si')) for bs in BacSiController.get_all()}
            dict_dv = {str(val(dv, 'id', 'ID')): str(val(dv, 'ten_dich_vu', 'ten_dv', 'ten')) for dv in DichVuController.get_all()}

            # 3. Đổ dữ liệu lên giao diện
            self.txtid.setText(str(val(l, 'id', 'ID')))
            self.txtbenhnhan.setText(dict_bn.get(str(val(l, 'benh_nhan_id', 'benhnhan_id')), "Không rõ"))
            self.txtbacsi.setText(dict_bs.get(str(val(l, 'bac_si_id', 'bacsi_id')), "Không rõ"))
            self.txtdichvu.setText(dict_dv.get(str(val(l, 'dich_vu_id', 'dichvu_id')), "Không rõ"))
            
            # Xử lý Ngày
            ngay_str = str(val(l, 'ngay_kham'))
            q_date = QDate.fromString(ngay_str, "yyyy-MM-dd") 
            if not q_date.isValid():
                q_date = QDate.fromString(ngay_str, "dd/MM/yyyy") 
            if q_date.isValid():
                self.datekham.setDate(q_date)

            # Xử lý Giờ (Cắt phần giây đi nếu CSDL lưu là 08:30:00)
            gio_str = str(val(l, 'gio_kham'))
            if len(gio_str) > 5:
                gio_str = gio_str[:5] 
                
            q_time = QTime.fromString(gio_str, "HH:mm")
            if q_time.isValid():
                self.timekham.setTime(q_time)
            
            # Xử lý Trạng thái (ComboBox)
            trang_thai = str(val(l, 'trang_thai', 'TrangThai', 'trangthai'))
            index = self.cbtrang_thai.findText(trang_thai)
            if index >= 0:
                self.cbtrang_thai.setCurrentIndex(index)
            
            
        except NameError as ne:
            QMessageBox.critical(self, "Thiếu Controller", f"Bạn chưa Import Controller: {str(ne)}")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi lấy dữ liệu", f"Chi tiết lỗi: {str(e)}")
            self.close()  
    def set_che_do_chiren(self, is_read_only):
        # Các trường chỉ đọc cố định
        self.txtid.setReadOnly(True)
        self.txtbenhnhan.setReadOnly(True)
        
        # Các trường có thể sửa khi is_read_only = False
        self.txtbacsi.setReadOnly(is_read_only)
        self.txtdichvu.setReadOnly(is_read_only)
        self.datekham.setReadOnly(is_read_only)
        self.timekham.setReadOnly(is_read_only)
        
        # ComboBox không có read-only, dùng setEnabled
        self.cbtrang_thai.setEnabled(not is_read_only) 
        
        # Quản lý nút
        self.btnEdit.setVisible(is_read_only)
        self.btnSave.setVisible(not is_read_only)
        self.btnClose.setVisible(is_read_only) # Hiện nút đóng khi chỉ xem

    def bat_che_do_sua(self):
        self.is_edit_mode = True
        self.set_che_do_chiren(False)
        self.btnEdit.setVisible(False)
        self.btnSave.setVisible(True)

    def luu_thong_tin_sua(self):
        try:
            # 1. Lấy dữ liệu mới từ Form (Bỏ qua ghi chú vì DB không có cột này)
            ngay_new = self.datekham.date().toString("yyyy-MM-dd")
            gio_new = self.timekham.time().toString("HH:mm")
            tt_new = self.cbtrang_thai.currentText()

            # 2. Hỏi xác nhận
            xac_nhan = QMessageBox.question(
                None, "Xác nhận", "Bạn có chắc chắn muốn lưu thông tin đã sửa?", 
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if xac_nhan == QMessageBox.StandardButton.Yes:
                # 💎 3. Gọi đúng hàm update dành riêng cho Form Chi Tiết
                LichKhamController.update_tu_form_chi_tiet(self.lich_id, ngay_new, gio_new, tt_new)
                
                QMessageBox.information(None, "Thành công", "Đã cập nhật thông tin lịch khám thành công!")
                
                # 4. Vẽ lại Timeline ở MainApp để cập nhật ngay lập tức
                if hasattr(self, 'main_app') and self.main_app:
                    self.main_app.dong_bo_hoa_don_theo_trang_thai(self.lich_id, tt_new, ngay_new)
                    self.main_app.hien_thi_timeline() 
                    
                self.close()

        except NameError as ne:
             QMessageBox.critical(None, "Lỗi Import", f"Chưa nhận diện được Controller. Lỗi: {str(ne)}")
        except Exception as e:
            QMessageBox.critical(None, "Lỗi khi lưu", f"Có lỗi xảy ra: {str(e)}") 
# --- LỚP ĐIỀU KHIỂN FORM THÊM BỆNH NHÂN RIÊNG ---
class ThemBenhNhanWindow(QDialog):
    def __init__(self, parent_main):
        super().__init__(parent_main)
        try:
            ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "View", "FormThemBenhNhan.ui")
            uic.loadUi(ui_path, self)
            self.parent_main = parent_main
            self.btnLuuBN.clicked.connect(self.xu_ly_luu)
        except Exception as e:
            print(f"Không thể load file FormThemBenhNhan.ui: {e}")

    def xu_ly_luu(self):
        ten = self.txtTenBN.text().strip()
        if not ten:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên bệnh nhân!")
            return

        # Lấy dữ liệu từ các ô nhập
        gioi_tinh = self.cboGioiTinh.currentText()
        ngay_sinh = self.txtNgaySinh.text().strip()
        sdt = self.txtSDT.text().strip()
        dia_chi = self.txtDiaChi.text().strip()

        try:
            from Controller.benhnhan_Controller import BenhNhanController
            
            # SỬA TẠI ĐÂY: Truyền đúng thứ tự và truyền rời từng biến (không dùng ngoặc tròn bao quanh data)
            BenhNhanController.insert(ten, sdt, dia_chi, gioi_tinh, ngay_sinh)
            
            QMessageBox.information(self, "Thành công", f"Đã thêm bệnh nhân: {ten}")
            
            # Cập nhật lại danh sách ở màn hình chính
            if hasattr(self.parent_main, 'load_data_benhnhan'):
                self.parent_main.load_data_benhnhan()
            if hasattr(self.parent_main, 'setup_goi_y_lich_kham'):
                self.parent_main.setup_goi_y_lich_kham()
            
            self.accept() # Đóng form
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu: {e}")
            
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        self.timeline_drawer = TimelineDrawer(self.forms["TL"].graphicsViewTimeline)
        self.connect_events()
        
        QTimer.singleShot(100, self.hien_thi_timeline)
        if self.timeline_drawer and self.timeline_drawer.scene:
            self.timeline_drawer.scene.selectionChanged.connect(self.mo_form_chi_tiet_tu_timeline)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.apply_style()
        # Thêm dòng này vào cuối hàm __init__
        self.setup_goi_y_lich_kham()
        self.setup_bo_loc_lich_kham()
        self.setup_lich_su_benh_nhan()
        
    def apply_style(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            qss_file = os.path.join(current_dir, "style.qss")
            if os.path.exists(qss_file):
                with open(qss_file, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
            elif os.path.exists("View/style.qss"):
                with open("View/style.qss", "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
        except Exception as e:
            pass

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
            "TAIKHOAN": uic.loadUi("View/FormTaiKhoan.ui"),
            "CL": uic.loadUi("View/FormCaLam.ui"),
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
            btn.clicked.connect(lambda _, f=form, fn=func: self.mo_tab(f, fn))

        self.actionProfile.triggered.connect(lambda: self.mo_tab(self.forms["PROFILE"], None))
        self.actionT_i_Kho_n.triggered.connect(lambda: self.mo_tab(self.forms["TAIKHOAN"], self.load_data_taikhoan))
        self.actionTh_ng_k.triggered.connect(self.show_thongke)
        self.actionDxuat.triggered.connect(self.dang_xuat)
        if "TK" in self.forms:
            # Gắn dữ liệu cho cboxloai
            self.forms["TK"].cboxloai.clear()
            self.forms["TK"].cboxloai.addItems(["Lượt Khám Tổng Hợp", "Doanh Thu Dịch Vụ"])
            
            # Gắn dữ liệu cho cboxthoigian
            self.forms["TK"].cboxthoigian.clear()
            self.forms["TK"].cboxthoigian.addItems(["Tất cả thời gian"])
            for i in range(1, 13):
                self.forms["TK"].cboxthoigian.addItem(f"Tháng {i}")
            
            # Kết nối nút bấm
            self.forms["TK"].btnthongke.clicked.connect(self.thuc_hien_thong_ke)
        if hasattr(self, 'timeline_drawer') and self.timeline_drawer.scene:
            self.timeline_drawer.scene.selectionChanged.connect(self.mo_form_chi_tiet_tu_timeline)

        self.btnThem.clicked.connect(self.xu_ly_them)
        self.btnSua.clicked.connect(self.xu_ly_sua)
        self.btnXoa.clicked.connect(self.xu_ly_xoa)
        self.btnTimKiem.clicked.connect(self.xu_ly_tim_kiem)
        self.btnxoaDL.clicked.connect(self.xoa_du_lieu_dang_hien_thi)
        self.btnCaLam.clicked.connect(lambda: self.mo_tab(self.forms["CL"], self.load_data_calam))      
        self.forms["CL"].tableCaLam.itemClicked.connect(self.do_du_lieu_calam_len_form)
        self.forms["BS"].tableBacSi.itemClicked.connect(self.do_du_lieu_bacsi_len_form)
        self.forms["BN"].tableBenhNhan.itemClicked.connect(self.do_du_lieu_benhnhan_len_form)
        self.forms["DV"].tableDichVu.itemClicked.connect(self.do_du_lieu_dichvu_len_form)
        self.forms["DT"].tableDoanhThu.itemClicked.connect(self.do_du_lieu_doanhthu_len_form)
        self.forms["LK"].tableLichKham.itemClicked.connect(self.do_du_lieu_lichkham_len_form)
        self.forms["PK"].tablePhong.itemClicked.connect(self.do_du_lieu_phong_len_form)
        self.forms["TK"].btnthongke.clicked.connect(self.xu_ly_tim_kiem_tk)
        self.forms["TK"].btnxuatfile.clicked.connect(self.xu_ly_them_tk)

    def get_active_form(self):
        return self.formChucNang.stackedWidgetMain.currentWidget()

    def xoa_du_lieu_dang_hien_thi(self):
        active = self.get_active_form()
        if active:
            self.clear_form_inputs(active)

    def setup_bo_loc_lich_kham(self):
        lk_ui = self.forms["LK"]
        if hasattr(lk_ui, "txtLocNgayKham"):
            return

        layout = lk_ui.groupList.layout()
        filter_bar = QHBoxLayout()

        lk_ui.txtLocNgayKham = QLineEdit()
        lk_ui.txtLocNgayKham.setObjectName("txtLocNgayKham")
        lk_ui.txtLocNgayKham.setPlaceholderText("Loc ngay kham: yyyy-mm-dd hoac dd/mm/yyyy")

        lk_ui.cboLocTrangThai = QComboBox()
        lk_ui.cboLocTrangThai.setObjectName("cboLocTrangThai")
        lk_ui.cboLocTrangThai.addItems(["Tat ca trang thai", "Chờ Khám", "Đang Khám", "Đã Xong", "Đã Hủy"])

        btn_hom_nay = QPushButton("Hom nay")
        btn_tat_ca = QPushButton("Tat ca")

        filter_bar.addWidget(QLabel("Loc:"))
        filter_bar.addWidget(lk_ui.txtLocNgayKham, 2)
        filter_bar.addWidget(lk_ui.cboLocTrangThai, 1)
        filter_bar.addWidget(btn_hom_nay)
        filter_bar.addWidget(btn_tat_ca)
        layout.insertLayout(0, filter_bar)

        lk_ui.txtLocNgayKham.textChanged.connect(lambda *_: self.load_data_lichkham())
        lk_ui.cboLocTrangThai.currentIndexChanged.connect(lambda *_: self.load_data_lichkham())
        btn_hom_nay.clicked.connect(lambda: lk_ui.txtLocNgayKham.setText(datetime.now().strftime("%Y-%m-%d")))
        btn_tat_ca.clicked.connect(lambda: (lk_ui.txtLocNgayKham.clear(), lk_ui.cboLocTrangThai.setCurrentIndex(0)))

    def setup_lich_su_benh_nhan(self):
        bn_ui = self.forms["BN"]
        if hasattr(bn_ui, "btnLichSuKham"):
            return

        bn_ui.btnLichSuKham = QPushButton("Xem lich su kham")
        layout = bn_ui.groupEdit.layout()
        if layout:
            row = layout.rowCount() if hasattr(layout, "rowCount") else 0
            layout.addWidget(bn_ui.btnLichSuKham, row, 0, 1, 2)
        bn_ui.btnLichSuKham.clicked.connect(self.hien_thi_lich_su_benh_nhan)
    

    def mo_form_them_benh_nhan_nhanh(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QComboBox, QPushButton, QLabel, QMessageBox
        from PyQt6.QtGui import QFont
        dialog = QDialog(self)
        dialog.setWindowTitle("Nhập Bệnh Nhân Mới")
        dialog.resize(350, 280)
        
        # Ép Font để chống lỗi QFont (-1)
        font_chuan = QFont("Arial", 10)
        dialog.setFont(font_chuan)

        layout = QVBoxLayout(dialog)

        # 2. Tạo các ô nhập liệu
        txt_ten = QLineEdit(dialog)
        txt_ten.setPlaceholderText("Họ và Tên (*)")
        
        cbo_gioitinh = QComboBox(dialog)
        cbo_gioitinh.addItems(["Nam", "Nữ"])
        
        txt_ngaysinh = QLineEdit(dialog)
        txt_ngaysinh.setPlaceholderText("Ngày sinh (dd/mm/yyyy)")
        
        txt_sdt = QLineEdit(dialog)
        txt_sdt.setPlaceholderText("Số điện thoại")
        
        txt_diachi = QLineEdit(dialog)
        txt_diachi.setPlaceholderText("Địa chỉ")

        btn_luu = QPushButton("Lưu và Chọn ngay", dialog)
        btn_luu.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; font-size: 10pt;")

        # Đưa các ô vào cửa sổ
        layout.addWidget(QLabel("<b>Vui lòng nhập thông tin bệnh nhân:</b>"))
        layout.addWidget(txt_ten)
        layout.addWidget(cbo_gioitinh)
        layout.addWidget(txt_ngaysinh)
        layout.addWidget(txt_sdt)
        layout.addWidget(txt_diachi)
        layout.addWidget(btn_luu)
        layout.addStretch()

        # 3. Hàm xử lý khi bấm nút Lưu 
        # SỬA LỖI TẠI ĐÂY: Thêm tham số checked=False để PyQt6 không bị crash
        def thuc_hien_luu(checked=False):
            ten = txt_ten.text().strip()
            
            if not ten:
                QMessageBox.warning(dialog, "Lỗi", "Vui lòng nhập Họ Tên!")
                return
            
            gioi_tinh = cbo_gioitinh.currentText()
            ngay_sinh = txt_ngaysinh.text().strip()
            sdt = txt_sdt.text().strip()
            dia_chi = txt_diachi.text().strip()
            
            try:
                from Controller.benhnhan_Controller import BenhNhanController
                
                # Gọi hàm insert
                success = BenhNhanController.insert(ten, sdt, dia_chi, gioi_tinh, ngay_sinh)
                
                if success is False:
                    QMessageBox.warning(dialog, "Lỗi", "Không thể lưu vào Cơ sở dữ liệu! Vui lòng kiểm tra lại.")
                    return

                QMessageBox.information(dialog, "Thành công", "Đã thêm bệnh nhân vào hệ thống!")
                
                dialog.accept() # Tắt form
                
                # Tải lại CSDL bảng bệnh nhân và reset ComboBox
                if hasattr(self, 'load_data_benhnhan'):
                    self.load_data_benhnhan()
                    
                if hasattr(self, 'setup_goi_y_lich_kham'):
                    self.setup_goi_y_lich_kham()
                
                # Chọn bệnh nhân vừa mới thêm
                if "LK" in getattr(self, "forms", {}) and hasattr(self.forms["LK"], 'cboBN_Lich'):
                    combo_bn = self.forms["LK"].cboBN_Lich
                    if combo_bn.count() > 0:
                        combo_bn.setCurrentIndex(combo_bn.count() - 1)
                
            except Exception as e:
                # Nếu có lỗi ngầm, nó sẽ hiển thị thẳng lên màn hình chứ không im lặng nữa
                QMessageBox.critical(dialog, "Lỗi hệ thống", f"Báo cáo lỗi: {e}")

        btn_luu.clicked.connect(thuc_hien_luu)
        
        # 4. Hiển thị form
        result = dialog.exec()
        if result == 0: 
            if "LK" in getattr(self, "forms", {}) and hasattr(self.forms["LK"], 'cboBN_Lich'):
                combo_bn = self.forms["LK"].cboBN_Lich
                if combo_bn.count() > 1:
                    combo_bn.setCurrentIndex(1)
                else:
                    combo_bn.setCurrentIndex(-1)
       
    def setup_goi_y_lich_kham(self):
        lk_ui = self.forms["LK"]
        
        # 1. Gợi ý Bệnh nhân
        lk_ui.cboBN_Lich.blockSignals(True)
        lk_ui.cboBN_Lich.clear()
        lk_ui.cboBN_Lich.addItem("-- Chon Benh Nhan --", None)
        lk_ui.cboBN_Lich.addItem("[+] Thêm Bệnh Nhân Mới...", "NEW")
        try:
            for bn in BenhNhanController.get_all():
                lk_ui.cboBN_Lich.addItem(f"{bn.id} - {bn.ten}", bn.id)
        except: pass
        lk_ui.cboBN_Lich.blockSignals(False)

        # Kết nối sự kiện chọn BN mới
        try: lk_ui.cboBN_Lich.activated.disconnect()
        except: pass
        lk_ui.cboBN_Lich.activated.connect(self.xu_ly_chon_benh_nhan)

        # 2. Gợi ý Phòng Khám (Sửa lỗi không hiện phòng)
        lk_ui.cboPK_Lich.clear()
        try:
            # Lưu ý: Bạn cần thêm hàm get_phongkham_goi_y trong LichKhamController
            list_phong = LichKhamController.get_phongkham_goi_y()
            for p in list_phong:
                lk_ui.cboPK_Lich.addItem(p['ten_phong'], p['id'])
        except: pass

        # 3. Gợi ý Dịch vụ
        lk_ui.cboDV_Lich.clear()
        self.dv_specialty_map = {}
        try:
            list_dv = LichKhamController.get_dichvu_goi_y()
            for dv in list_dv:
                lk_ui.cboDV_Lich.addItem(dv['ten_dich_vu'], dv['id'])
                self.dv_specialty_map[dv['id']] = dv['chuyen_khoa']
        except: pass

        lk_ui.cboCaLamLich.blockSignals(True)
        current_ca = lk_ui.cboCaLamLich.currentData() or lk_ui.cboCaLamLich.currentText().split(" - ")[0]
        lk_ui.cboCaLamLich.clear()
        lk_ui.cboCaLamLich.addItem("1 - Ca Sáng", "1")
        lk_ui.cboCaLamLich.addItem("2 - Ca Chiều", "2")
        lk_ui.cboCaLamLich.addItem("3 - Ca Tối", "3")
        idx_ca = lk_ui.cboCaLamLich.findData(str(current_ca))
        lk_ui.cboCaLamLich.setCurrentIndex(idx_ca if idx_ca >= 0 else 0)
        lk_ui.cboCaLamLich.blockSignals(False)

        # Kết nối lọc bác sĩ tự động
        try: lk_ui.cboDV_Lich.currentIndexChanged.disconnect()
        except: pass
        try: lk_ui.cboCaLamLich.currentIndexChanged.disconnect()
        except: pass
        lk_ui.cboDV_Lich.currentIndexChanged.connect(self.loc_bac_si_thong_minh)
        lk_ui.cboCaLamLich.currentIndexChanged.connect(self.loc_bac_si_thong_minh)
        
        self.loc_bac_si_thong_minh()

    def xu_ly_chon_benh_nhan(self, *args):
        combo_bn = self.forms["LK"].cboBN_Lich
        if combo_bn.currentData() == "NEW":
            popup = ThemBenhNhanWindow(self)
            if popup.exec():
                # Nếu thêm thành công, chọn BN cuối cùng (người vừa thêm)
                combo_bn.setCurrentIndex(combo_bn.count() - 1)
            elif combo_bn.count() > 0:
                combo_bn.setCurrentIndex(0)

    def loc_bac_si_thong_minh(self, *args):
        lk_ui = self.forms["LK"]
        dv_id = lk_ui.cboDV_Lich.currentData()
        chuyen_khoa = self.dv_specialty_map.get(dv_id)
        ca_id = lk_ui.cboCaLamLich.currentData()
        if ca_id is None:
            ca_text = lk_ui.cboCaLamLich.currentText()
            ca_id = ca_text.split(" - ")[0] if " - " in ca_text else "1"

        lk_ui.cboBS_Lich.clear()
        try:
            list_bs = []
            if chuyen_khoa:
                list_bs = LichKhamController.get_bacsi_theo_loc(chuyen_khoa, ca_id)
            
            if not list_bs and chuyen_khoa:
                lk_ui.cboBS_Lich.addItem("Khong co BS dung ca - hien cung chuyen khoa", None)
                list_bs = LichKhamController.get_bacsi_theo_chuyen_khoa(chuyen_khoa)
            elif not list_bs:
                lk_ui.cboBS_Lich.addItem("Chua chon dich vu - hien tat ca BS", None)
                list_bs = LichKhamController.get_all_bacsi_goi_y()

            for bs in list_bs:
                lk_ui.cboBS_Lich.addItem(f"{bs['id']} - {bs['ten']}", bs['id'])
        except: pass
    def on_table_click_lichkham(self):
        curr = self.forms["LK"].tableLichKham.currentRow()
        if curr < 0: return
        
        obj = self.data_cache["LK"][curr]
        lk_ui = self.forms["LK"]

        lk_ui.txtIDLich.setText(str(obj.id))
        
        # Set ComboBox Bệnh nhân, Dịch vụ, Ca làm
        lk_ui.cboBN_Lich.setCurrentIndex(lk_ui.cboBN_Lich.findData(obj.benhnhan_id))
        lk_ui.cboDV_Lich.setCurrentIndex(lk_ui.cboDV_Lich.findData(obj.dichvu_id))
        for i in range(lk_ui.cboCaLamLich.count()):
            if lk_ui.cboCaLamLich.itemText(i).startswith(str(obj.calam_id)):
                lk_ui.cboCaLamLich.setCurrentIndex(i)
                break
        
        # Set ComboBox Bác Sĩ (đợi 100ms để hàm lọc BS chạy xong)
        QTimer.singleShot(100, lambda: lk_ui.cboBS_Lich.setCurrentIndex(lk_ui.cboBS_Lich.findData(obj.bacsi_id)))

        lk_ui.txtNgayKham.setText(obj.ngay_kham)
        lk_ui.txtGioKham.setText(obj.gio_kham)
        lk_ui.comboBoxTrangThai.setCurrentText(obj.TrangThai)

    def luu_lich_kham(self):
        lk_ui = self.forms["LK"]
        
        id_bn = lk_ui.cboBN_Lich.currentData()
        id_bs = lk_ui.cboBS_Lich.currentData()
        id_dv = lk_ui.cboDV_Lich.currentData()
        ca_id = lk_ui.cboCaLamLich.currentData() or lk_ui.cboCaLamLich.currentText().split(" - ")[0]

        if not id_bn or not id_bs or not id_dv:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn đầy đủ Bệnh nhân, Dịch vụ và Bác sĩ!")
            return

        values = (
            id_bn, id_bs, 1, id_dv, 
            lk_ui.txtNgayKham.text(), lk_ui.txtGioKham.text(), 
            lk_ui.comboBoxTrangThai.currentText(), ca_id
        )

        try:
            idx = lk_ui.txtIDLich.text()
            if not idx:
                LichKhamController.insert(values)
            else:
                LichKhamController.update(int(idx), values)
            
            self.load_data_lichkham()
            self.lam_moi_lich_kham()
            QMessageBox.information(self, "Thành công", "Đã lưu thông tin lịch khám!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu: {e}")

    def lam_moi_lich_kham(self):
        lk_ui = self.forms["LK"]
        lk_ui.txtIDLich.clear()
        lk_ui.txtNgayKham.setText(datetime.now().strftime("%d/%m/%Y"))
        lk_ui.txtGioKham.setText(datetime.now().strftime("%H:%M"))
        # Gọi lại hàm setup để reset form về trạng thái gợi ý ban đầu
        self.setup_goi_y_lich_kham()

    def mo_form_chi_tiet_tu_timeline(self):
        try:
        # 1. Lấy danh sách item đang được chọn trên Scene
            selected_items = self.timeline_drawer.scene.selectedItems()
            if not selected_items: return

        # 2. Lấy item đầu tiên (thẻ PathItem chính)
            card_item = selected_items[0]

        # 3. Lấy ID lịch khám được lưu trong setData
            l_id = card_item.data(Qt.ItemDataRole.UserRole)

            if l_id:
            # 4. Mở Form Chi Tiết (PopUp)
                dialog = DialogChiTietLichKham(parent=self, lich_id=l_id)
                dialog.exec() # Mở ở chế độ Modal

        # 5. Bỏ chọn trên Scene để tránh mở lại form khi click lần sau
            self.timeline_drawer.scene.clearSelection() 

        except Exception as e:
            print(f"Lỗi khi mở form chi tiết: {e}")
        self.timeline_drawer.scene.clearSelection() # Reset selection
    def thuc_hien_thong_ke(self):
        try:
            # 1. Lấy dữ liệu người dùng chọn
            loai_tk = self.forms["TK"].cboxloai.currentText()
            thoi_gian = self.forms["TK"].cboxthoigian.currentText()
            
            # 2. Xử lý khoảng thời gian (Mặc định lấy năm hiện tại)
            thang = None
            nam = datetime.now().year
            
            if "Tháng" in thoi_gian:
                # Cắt lấy số tháng (ví dụ "Tháng 5" -> "5")
                thang = thoi_gian.replace("Tháng ", "").strip()
            
            # 3. Lấy dữ liệu theo Loại thống kê
            if loai_tk == "Doanh Thu Dịch Vụ":
                data = ThongKeController.thong_ke_doanh_thu_dich_vu(thang, nam)
                headers = ["Tên Dịch Vụ", "Số Lượt Khám", "Tổng Doanh Thu"]
            else:
                data = ThongKeController.thong_ke_luot_kham_tong_hop(thang, nam)
                headers = ["Ngày Khám", "Tên Bác Sĩ", "Tên Bệnh Nhân", "Giờ Khám", "Trạng Thái"]
                
            # 4. Đổ vào tableThongKe
            if hasattr(self.forms["TK"], "tableThongKe"):
                self.fill_table(self.forms["TK"].tableThongKe, data, headers)
            
            # Thông báo nếu trống
            if not data:
                QMessageBox.information(self, "Thông báo", "Không tìm thấy dữ liệu cho khoảng thời gian này.")
                
        except Exception as e:
            print(f"Lỗi thống kê: {e}")
            QMessageBox.critical(self, "Lỗi", f"Có lỗi xảy ra khi lấy thống kê: {str(e)}")
    # ================= HÀM XÓA TRẮNG & ÉP KIỂU =================
    def clear_form_inputs(self, form_widget):
        for line_edit in form_widget.findChildren(QLineEdit):
            line_edit.clear()

    def parse_id(self, id_str):
        return int(id_str) if str(id_str).strip().isdigit() else id_str

    def lay_id_tu_item(self, item):
        if not item:
            return None
        data = item.data(Qt.ItemDataRole.UserRole)
        if data is not None:
            return data
        return self.parse_id(item.text().split(" - ", 1)[0].strip())

    def la_trung_lich_bac_si(self, bacsi_id, ngay_kham, gio_kham, ca_lam, lich_bo_qua=None):
        def chuan_hoa_ngay(value):
            text = str(value).strip()
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
                try:
                    return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
                except ValueError:
                    pass
            return text

        ngay_moi = chuan_hoa_ngay(ngay_kham)
        for lich in LichKhamController.get_all():
            if lich_bo_qua and str(lich.id) == str(lich_bo_qua):
                continue
            if str(lich.bacsi_id) != str(bacsi_id):
                continue
            if chuan_hoa_ngay(lich.ngay_kham) != ngay_moi:
                continue
            gio_moi = str(gio_kham).strip()
            gio_cu = str(lich.gio_kham).strip()
            trung_gio = bool(gio_moi) and gio_cu == gio_moi
            trung_ca = not gio_moi and str(lich.ca_lam).strip() == str(ca_lam).strip()
            if trung_gio or trung_ca:
                QMessageBox.warning(
                    self,
                    "Trung lich bac si",
                    f"Bac si nay da co lich kham ngay {ngay_kham}, ca {ca_lam}, gio {lich.gio_kham}."
                )
                return True
        return False

    # ================= HÀM ĐỔ DỮ LIỆU LÊN "LỊCH KHÁM SẮP TỚI" =================
    def cap_nhat_lich_kham_hom_nay(self):
        """Bản fix: Giữ giao diện Card + Tính tiền theo ngày hóa đơn + Chống lỗi mất list_lich_kham"""
        from datetime import datetime
        from PyQt6.QtWidgets import QLabel, QListWidgetItem, QWidget, QHBoxLayout, QFrame, QListWidget, QVBoxLayout, QGroupBox
        from PyQt6.QtCore import QSize

        try:
            lk_all = LichKhamController.get_all()
            bn_all = BenhNhanController.get_all()
            hd_all = HoaDonController.get_all() 
            
            dict_bn = {str(b.get('id') if isinstance(b, dict) else getattr(b, 'id')): 
                       (b.get('ten') or b.get('TenBN') if isinstance(b, dict) else getattr(b, 'ten', ''))
                       for b in bn_all}

            now = datetime.now()
            today_str = now.strftime("%Y-%m-%d")
            today_rev = now.strftime("%d/%m/%Y")
            
            lk_hom_nay = []
            so_ca_da_xong = 0 

            # 1. Lọc lịch khám & Đếm số ca xong
            for k in lk_all:
                ngay_kham = str(k.get('ngay_kham') if isinstance(k, dict) else getattr(k, 'ngay_kham', '')).strip()
                if today_str in ngay_kham or today_rev in ngay_kham:
                    lk_hom_nay.append(k)
                    trang_thai = str(k.get('trang_thai') or k.get('TrangThai', '') if isinstance(k, dict) else getattr(k, 'trang_thai', '')).strip().upper()
                    if any(x in trang_thai for x in ["ĐÃ", "XONG", "HOÀN THÀNH"]):
                        so_ca_da_xong += 1

            # 2. TÍNH TIỀN THEO NGÀY (KHÔI PHỤC CÁCH CŨ)
            tong_tien_hom_nay = 0
            for hd in hd_all:
                # Lấy ngày của hóa đơn (Bao gồm cả các trường hợp tên cột khác nhau)
                ngay_hd = str(hd.get('ngay_lap') or hd.get('ngay_thanh_toan') or hd.get('Ngay') or hd.get('ngay', '') if isinstance(hd, dict) else getattr(hd, 'ngay_thanh_toan', getattr(hd, 'ngay_lap', ''))).strip()
                if today_str in ngay_hd or today_rev in ngay_hd:
                    tien = hd.get('tong_tien') or hd.get('TongTien', 0) if isinstance(hd, dict) else getattr(hd, 'tong_tien', 0)
                    try:
                        tong_tien_hom_nay += float(tien)
                    except: pass

            # 3. FIX LỖI: TÌM HOẶC KHỞI TẠO LIST WIDGET TRƯỚC KHI DÙNG
            target_ui = self.forms.get("TIMELINE") if hasattr(self, 'forms') and "TIMELINE" in self.forms else getattr(self, 'formChucNang', None)
            
            if not hasattr(self, 'list_lich_kham') or self.list_lich_kham is None:
                if target_ui:
                    # Thử tìm widget list_lich_kham trong file UI
                    found_list = target_ui.findChild(QListWidget, "list_lich_kham")
                    if found_list:
                        self.list_lich_kham = found_list
                    else:
                        # Nếu file UI không có, tự động tạo mới và gắn vào groupBox
                        self.list_lich_kham = QListWidget()
                        group_box = target_ui.findChild(QGroupBox, "groupBox")
                        if group_box:
                            if not group_box.layout():
                                group_box.setLayout(QVBoxLayout())
                            group_box.layout().addWidget(self.list_lich_kham)

            # Đảm bảo list_lich_kham đã tồn tại mới xóa và thêm item
            if hasattr(self, 'list_lich_kham') and self.list_lich_kham is not None:
                self.list_lich_kham.clear()
            else:
                print("⚠️ Cảnh báo: Không thể khởi tạo danh sách lịch khám.")
                return

            # 4. HIỂN THỊ DANH SÁCH (Dạng Card đẹp)
            for k in lk_hom_nay:
                gio = str(k.get('gio_kham') if isinstance(k, dict) else getattr(k, 'gio_kham', '')).strip()
                id_bn = str(k.get('benhnhan_id') if isinstance(k, dict) else getattr(k, 'benhnhan_id', ''))
                trang_thai = str(k.get('trang_thai') or k.get('TrangThai', '') if isinstance(k, dict) else getattr(k, 'trang_thai', '')).strip()
                
                container = QWidget(); lay = QHBoxLayout(container)
                card = QFrame(); card.setObjectName("cardLichKham")
                card_lay = QHBoxLayout(card)
                lbl_gio = QLabel(f"⏰ {gio}"); lbl_gio.setStyleSheet("color: #00E5FF; font-weight: bold;")
                lbl_ten = QLabel(dict_bn.get(id_bn, f"BN: {id_bn}")); lbl_ten.setStyleSheet("color: white;")
                lbl_st = QLabel(trang_thai.upper())
                st_color = "#2e7d32" if any(x in trang_thai.upper() for x in ["ĐÃ", "XONG"]) else "#d32f2f"
                lbl_st.setStyleSheet(f"color: {st_color}; border: 1px solid {st_color}; border-radius: 4px; padding: 2px 5px; font-size: 9px;")
                card_lay.addWidget(lbl_gio); card_lay.addWidget(lbl_ten, 1); card_lay.addWidget(lbl_st)
                lay.addWidget(card)
                item = QListWidgetItem(self.list_lich_kham); item.setSizeHint(QSize(0, 55))
                self.list_lich_kham.setItemWidget(item, container)

            # 5. CẬP NHẬT UI
            if target_ui:
                lbl_total = target_ui.findChild(QLabel, "lblTotalValue")
                lbl_completed = target_ui.findChild(QLabel, "lblCompletedValue")
                lbl_revenue = target_ui.findChild(QLabel, "lblRevenueValue")
                if lbl_total: lbl_total.setText(str(len(lk_hom_nay)))
                if lbl_completed: lbl_completed.setText(str(so_ca_da_xong))
                if lbl_revenue: lbl_revenue.setText(f"{tong_tien_hom_nay:,.0f} VNĐ")

        except Exception as e:
            print(f"Lỗi cập nhật lịch khám: {e}")
    def xu_ly_them(self):
        self.chay_hanh_dong_form("them")
    

    def xu_ly_sua(self):
        self.chay_hanh_dong_form("sua")

    def xu_ly_xoa(self):
        self.chay_hanh_dong_form("xoa")

    def xu_ly_tim_kiem(self):
        self.chay_hanh_dong_form("tim_kiem")

    def chay_hanh_dong_form(self, action):
        active = self.get_active_form()
        active_key = next((key for key, form in self.forms.items() if active == form), None)
        action_names = ("them", "sua", "xoa", "tim_kiem")
        routes = {
            "BS": (self.xu_ly_them_bs, self.xu_ly_sua_bs, self.xu_ly_xoa_bs, self.xu_ly_tim_kiem_bs),
            "BN": (self.xu_ly_them_bn, self.xu_ly_sua_bn, self.xu_ly_xoa_bn, self.xu_ly_tim_kiem_bn),
            "DV": (self.xu_ly_them_dv, self.xu_ly_sua_dv, self.xu_ly_xoa_dv, self.xu_ly_tim_kiem_dv),
            "DT": (self.xu_ly_them_dt, self.xu_ly_sua_dt, self.xu_ly_xoa_dt, self.xu_ly_tim_kiem_dt),
            "LK": (self.xu_ly_them_lk, self.xu_ly_sua_lk, self.xu_ly_xoa_lk, self.xu_ly_tim_kiem_lk),
            "PK": (self.xu_ly_them_phong, self.xu_ly_sua_phong, self.xu_ly_xoa_phong, self.xu_ly_tim_kiem_phong),
            "TK": (self.xu_ly_them_tk, self.xu_ly_sua_tk, None, None),
        }
        handler = dict(zip(action_names, routes.get(active_key, ()))).get(action)
        if handler:
            handler()

    # ================= LOGIC BÁC SĨ =================
    def do_du_lieu_bacsi_len_form(self):
        row = self.forms["BS"].tableBacSi.currentRow()
        if row >= 0:
            self.forms["BS"].txtIDBS.setText(self.forms["BS"].tableBacSi.item(row, 0).text())
            self.forms["BS"].txtTenBS.setText(self.forms["BS"].tableBacSi.item(row, 1).text())
            self.forms["BS"].txtGioiTinhBS.setText(self.forms["BS"].tableBacSi.item(row, 2).text())
            self.forms["BS"].txtChuyenKhoa.setText(self.forms["BS"].tableBacSi.item(row, 3).text())

    def xu_ly_them_bs(self):
        f = self.forms["BS"]
        ten = f.txtTenBS.text().strip()
        if not ten: 
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập tên Bác sĩ!")
            return
        BacSiController.insert(ten, f.txtGioiTinhBS.text(), f.txtChuyenKhoa.text())
        QMessageBox.information(self, "Thành công", "Đã thêm Bác sĩ mới!")
        self.load_data_bacsi()
        self.clear_form_inputs(f)

    def xu_ly_sua_bs(self):
        f = self.forms["BS"]
        id_bs = f.txtIDBS.text()
        if not id_bs:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn Bác sĩ cần sửa!")
            return
        BacSiController.update(self.parse_id(id_bs), f.txtTenBS.text(), f.txtGioiTinhBS.text(), f.txtChuyenKhoa.text())
        QMessageBox.information(self, "Thành công", "Cập nhật thông tin Bác sĩ thành công!")
        self.load_data_bacsi()
        self.clear_form_inputs(f)

    def xu_ly_xoa_bs(self):
        f = self.forms["BS"]
        id_bs = f.txtIDBS.text()
        if not id_bs:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn Bác sĩ cần xóa!")
            return
        
        _id = self.parse_id(id_bs)
        if QMessageBox.question(self, "Xác nhận", "Xóa bác sĩ này?") == QMessageBox.StandardButton.Yes:
            try:
                BacSiController.delete(_id)
                QMessageBox.information(self, "Thành công", "Đã xóa Bác sĩ!")
                self.load_data_bacsi()
                self.clear_form_inputs(f)
            except Exception as e:
                err_msg = str(e).upper()
                if "FOREIGN KEY" in err_msg or "CONSTRAINT" in err_msg:
                    reply = QMessageBox.question(self, "Cảnh báo", 
                                                 "Bác sĩ này đang có Lịch khám. Bạn có muốn XÓA SẠCH toàn bộ Lịch khám và Hóa đơn của bác sĩ này không?", 
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.Yes:
                        try:
                            # Đổi DoanhThu -> HoaDon
                            execute_query("DELETE FROM HoaDon WHERE lichkham_id IN (SELECT id FROM LichKham WHERE bacsi_id = ?)", (_id,))
                            execute_query("DELETE FROM LichKham WHERE bacsi_id = ?", (_id,))
                            BacSiController.delete(_id)
                            QMessageBox.information(self, "Thành công", "Đã xóa sạch Bác sĩ và các dữ liệu liên quan!")
                            self.load_data_bacsi()
                            self.clear_form_inputs(f)
                        except Exception as ex:
                            QMessageBox.critical(self, "Lỗi", f"Không thể xóa tự động.\nChi tiết: {ex}")
                else:
                    QMessageBox.critical(self, "Lỗi", f"Không thể xóa bác sĩ này.\nChi tiết: {e}")

    def xu_ly_tim_kiem_bs(self):
        keyword, ok = QInputDialog.getText(self, "Tìm kiếm", "Nhập tên bác sĩ:")
        if ok and keyword:
            res = BacSiController.search(keyword)
            self.fill_table(self.forms["BS"].tableBacSi, res, ["ID", "Họ Tên", "Giới Tính", "Chuyên Khoa"])

    # ================= LOGIC BỆNH NHÂN =================
    def do_du_lieu_benhnhan_len_form(self):
        row = self.forms["BN"].tableBenhNhan.currentRow()
        if row >= 0:
            self.forms["BN"].txtIDBN.setText(self.forms["BN"].tableBenhNhan.item(row, 0).text())
            self.forms["BN"].txtTenBN.setText(self.forms["BN"].tableBenhNhan.item(row, 1).text())
            self.forms["BN"].txtSDT.setText(self.forms["BN"].tableBenhNhan.item(row, 2).text())
            self.forms["BN"].txtDiaChi.setText(self.forms["BN"].tableBenhNhan.item(row, 3).text())
            self.forms["BN"].txtGioiTinh.setText(self.forms["BN"].tableBenhNhan.item(row, 4).text())
            self.forms["BN"].txtNgaySinh.setText(self.forms["BN"].tableBenhNhan.item(row, 5).text())

    def hien_thi_lich_su_benh_nhan(self):
        bn_ui = self.forms["BN"]
        benhnhan_id = bn_ui.txtIDBN.text().strip()
        ten_bn = bn_ui.txtTenBN.text().strip()
        if not benhnhan_id:
            QMessageBox.warning(self, "Thong bao", "Vui long chon benh nhan can xem lich su kham!")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Lich su kham - {ten_bn or benhnhan_id}")
        dialog.resize(900, 420)
        layout = QVBoxLayout(dialog)
        table = QTableWidget(dialog)
        layout.addWidget(table)

        bac_si = BacSiController.get_all()
        dich_vu = DichVuController.get_all()
        phong_kham = PhongKhamController.get_all()

        def ten_theo_id(items, item_id, attr_name):
            for item in items:
                if str(getattr(item, "id", "")) == str(item_id):
                    return str(getattr(item, attr_name, ""))
            return ""

        rows = [lk for lk in LichKhamController.get_all() if str(lk.benhnhan_id) == str(benhnhan_id)]
        headers = ["ID", "Ngay Kham", "Gio", "Bac Si", "Dich Vu", "Phong", "Trang Thai", "Ca"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(0)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        for row, lk in enumerate(rows):
            table.insertRow(row)
            values = [
                lk.id,
                lk.ngay_kham,
                lk.gio_kham,
                f"{lk.bacsi_id} - {ten_theo_id(bac_si, lk.bacsi_id, 'ten')}",
                f"{lk.dichvu_id} - {ten_theo_id(dich_vu, lk.dichvu_id, 'ten_dich_vu')}",
                f"{lk.phongkham_id} - {ten_theo_id(phong_kham, lk.phongkham_id, 'ten_phong')}",
                lk.trang_thai,
                lk.ca_lam,
            ]
            for col, value in enumerate(values):
                table.setItem(row, col, QTableWidgetItem(str(value)))

        if not rows:
            QMessageBox.information(self, "Thong bao", "Benh nhan nay chua co lich su kham.")
            return
        dialog.exec()

    def xu_ly_them_bn(self):
        ThemBenhNhanWindow(self).exec()

    def xu_ly_sua_bn(self):
        f = self.forms["BN"]
        id_bn = f.txtIDBN.text()
        if not id_bn:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn Bệnh nhân cần sửa!")
            return
        BenhNhanController.update(self.parse_id(id_bn), f.txtTenBN.text(), f.txtSDT.text(), f.txtDiaChi.text(), f.txtGioiTinh.text(), f.txtNgaySinh.text())
        QMessageBox.information(self, "Thành công", "Cập nhật thông tái Bệnh nhân thành công!")
        self.load_data_benhnhan()
        self.clear_form_inputs(f)

    def xu_ly_xoa_bn(self):
        f = self.forms["BN"]
        id_bn = f.txtIDBN.text()
        if not id_bn:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn Bệnh nhân cần xóa!")
            return
        
        _id = self.parse_id(id_bn)
        if QMessageBox.question(self, "Xác nhận", "Xóa bệnh nhân này?") == QMessageBox.StandardButton.Yes:
            try:
                BenhNhanController.delete(_id)
                QMessageBox.information(self, "Thành công", "Đã xóa Bệnh nhân!")
                self.load_data_benhnhan()
                self.clear_form_inputs(f)
            except Exception as e:
                err_msg = str(e).upper()
                if "FOREIGN KEY" in err_msg or "CONSTRAINT" in err_msg:
                    reply = QMessageBox.question(self, "Cảnh báo", 
                                                 "Bệnh nhân này đang có Lịch khám và Hóa đơn. Bạn có chắc chắn muốn xóa sạch không?", 
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.Yes:
                        try:
                            # Đổi DoanhThu -> HoaDon
                            execute_query("DELETE FROM HoaDon WHERE lichkham_id IN (SELECT id FROM LichKham WHERE benhnhan_id = ?)", (_id,))
                            execute_query("DELETE FROM LichKham WHERE benhnhan_id = ?", (_id,))
                            BenhNhanController.delete(_id)
                            QMessageBox.information(self, "Thành công", "Đã xóa Bệnh nhân và toàn bộ lịch sử khám!")
                            self.load_data_benhnhan()
                            self.clear_form_inputs(f)
                        except Exception as ex:
                            QMessageBox.critical(self, "Lỗi", f"Không thể xóa tự động.\nChi tiết: {ex}")
                else:
                    QMessageBox.critical(self, "Lỗi", f"Không thể xóa bệnh nhân này.\nChi tiết: {e}")

    def xu_ly_tim_kiem_bn(self):
        keyword, ok = QInputDialog.getText(self, "Tìm kiếm", "Nhập tên/SĐT:")
        if ok and keyword:
            res = BenhNhanController.search(keyword)
            self.fill_table(self.forms["BN"].tableBenhNhan, res, ["ID", "Tên", "SĐT", "Địa chỉ", "GT", "Ngày sinh"])
    def load_data_calam(self):
        data = CaLamController.get_all()
        self.forms["CL"].tableCaLam.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Đổ dữ liệu vào bảng tableCaLam
        table = self.forms["CL"].tableCaLam
        table.setRowCount(0)
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["ID", "Tên Ca", "Bắt Đầu", "Kết Thúc"])
        
        for i, row in enumerate(data):
            table.insertRow(i)
            # Truy cập bằng dấu chấm (.) thay vì ['...']
            table.setItem(i, 0, QTableWidgetItem(str(row.id)))
            table.setItem(i, 1, QTableWidgetItem(str(row.ten_ca)))
            table.setItem(i, 2, QTableWidgetItem(str(row.gio_bat_dau)))
            table.setItem(i, 3, QTableWidgetItem(str(row.gio_ket_thuc)))

    def do_du_lieu_calam_len_form(self):
        row = self.forms["CL"].tableCaLam.currentRow()
        if row >= 0:
            f = self.forms["CL"]
            f.txtIDCa.setText(f.tableCaLam.item(row, 0).text())
            f.txtTenCa.setText(f.tableCaLam.item(row, 1).text())
            f.txtGioBD.setText(f.tableCaLam.item(row, 2).text())
            f.txtGioKT.setText(f.tableCaLam.item(row, 3).text())

    # --- NẾU BẠN CÓ HÀM XỬ LÝ THÊM/SỬA/XÓA RIÊNG THÌ THÊM VÀO ---
    def xu_ly_them_ca_lam(self):
        f = self.forms["CL"]
        ten = f.txtTenCa.text().strip()
        bd = f.txtGioBD.text().strip()
        kt = f.txtGioKT.text().strip()
        
        if not ten or not bd or not kt:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin ca làm!")
            return
            
        if CaLamController.insert(ten, bd, kt):
            QMessageBox.information(self, "Thành công", "Đã thêm ca làm!")
            self.load_data_calam()

    def xu_ly_sua_ca_lam(self):
        f = self.forms["CL"]
        id_ca = f.txtIDCa.text()
        if not id_ca:
            return
            
        ten = f.txtTenCa.text().strip()
        bd = f.txtGioBD.text().strip()
        kt = f.txtGioKT.text().strip()
        
        if CaLamController.update(int(id_ca), ten, bd, kt):
            QMessageBox.information(self, "Thành công", "Đã cập nhật ca làm!")
            self.load_data_calam()
    # ================= LOGIC DỊCH VỤ =================
    def do_du_lieu_dichvu_len_form(self):
        row = self.forms["DV"].tableDichVu.currentRow()
        if row >= 0:
            self.forms["DV"].txtIDDichVu.setText(self.forms["DV"].tableDichVu.item(row, 0).text())
            self.forms["DV"].txtTenDichVu.setText(self.forms["DV"].tableDichVu.item(row, 1).text())
            self.forms["DV"].txtGiaTien.setText(self.forms["DV"].tableDichVu.item(row, 2).text())
            self.forms["DV"].txtChuyenKhoa.setText(self.forms["DV"].tableDichVu.item(row, 3).text())


    def xu_ly_them_dv(self):
        f = self.forms["DV"]
        try:
            ten = f.txtTenDichVu.text().strip()
            gia = float(f.txtGiaTien.text().strip() or 0)
            if not ten:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập Tên dịch vụ!")
                return
            DichVuController.insert([ten, gia])
            QMessageBox.information(self, "Thành công", "Đã thêm Dịch vụ mới!")
            self.load_data_dichvu()
            self.clear_form_inputs(f)
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Giá tiền phải là số!")

    def xu_ly_sua_dv(self):
        f = self.forms["DV"]
        id_dv = f.txtIDDichVu.text()
        if not id_dv:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn Dịch vụ cần sửa!")
            return
        try:
            gia = float(f.txtGiaTien.text().strip() or 0)
            DichVuController.update(self.parse_id(id_dv), [f.txtTenDichVu.text(), gia])
            QMessageBox.information(self, "Thành công", "Cập nhật Dịch vụ thành công!")
            self.load_data_dichvu()
            self.clear_form_inputs(f)
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Giá tiền phải là số!")

    def xu_ly_xoa_dv(self):
        f = self.forms["DV"]
        id_dv = f.txtIDDichVu.text()
        if not id_dv:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn Dịch vụ cần xóa!")
            return
        
        _id = self.parse_id(id_dv)
        if QMessageBox.question(self, "Xác nhận", "Xóa dịch vụ này?") == QMessageBox.StandardButton.Yes:
            try:
                DichVuController.delete(_id)
                QMessageBox.information(self, "Thành công", "Đã xóa Dịch vụ!")
                self.load_data_dichvu()
                self.clear_form_inputs(f)
            except Exception as e:
                err_msg = str(e).upper()
                if "FOREIGN KEY" in err_msg or "CONSTRAINT" in err_msg:
                    reply = QMessageBox.question(self, "Cảnh báo", 
                                                 "Dịch vụ này đang có Lịch khám sử dụng. Xóa dịch vụ sẽ xóa luôn Lịch khám và Hóa đơn của dịch vụ này.\nBạn có dám xóa?", 
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.Yes:
                        try:
                            execute_query("DELETE FROM HoaDon WHERE lichkham_id IN (SELECT id FROM LichKham WHERE dichvu_id = ?)", (_id,))
                            execute_query("DELETE FROM LichKham WHERE dichvu_id = ?", (_id,))
                            DichVuController.delete(_id)
                            QMessageBox.information(self, "Thành công", "Đã xóa sạch!")
                            self.load_data_dichvu()
                            self.clear_form_inputs(f)
                        except Exception as ex:
                            QMessageBox.critical(self, "Lỗi", f"Không thể xóa tự động.\nChi tiết: {ex}")
                else:
                    QMessageBox.critical(self, "Lỗi", f"Không thể xóa dịch vụ này.\nChi tiết: {e}")
            
    def xu_ly_tim_kiem_dv(self):
        kw, ok = QInputDialog.getText(self, "Tìm", "Tên dịch vụ:")
        if ok and kw:
            res = DichVuController.search(kw)
            self.fill_table(self.forms["DV"].tableDichVu, res, ["ID", "Tên Dịch Vụ", "Đơn Giá"])

    # ================= LOGIC LỊCH KHÁM =================
    def do_du_lieu_lichkham_len_form(self):
        row = self.forms["LK"].tableLichKham.currentRow()
        if row >= 0:
            f = self.forms["LK"]
            
            # Gán ID, Ngày, Giờ
            f.txtIDLich.setText(f.tableLichKham.item(row, 0).text())
            f.txtNgayKham.setText(f.tableLichKham.item(row, 5).text())
            f.txtGioKham.setText(f.tableLichKham.item(row, 6).text())
            
            # Gán Trạng Thái
            status = f.tableLichKham.item(row, 7).text()
            idx = f.comboBoxTrangThai.findText(status)
            if idx >= 0:
                f.comboBoxTrangThai.setCurrentIndex(idx)

            # Chọn Bệnh Nhân (Cột 1)
            try:
                id_bn = self.lay_id_tu_item(f.tableLichKham.item(row, 1))
                f.cboBN_Lich.setCurrentIndex(f.cboBN_Lich.findData(id_bn))
            except: pass

            # Chọn Phòng Khám (Cột 3) - PHẦN VỪA BỔ SUNG
            try:
                id_phong = self.lay_id_tu_item(f.tableLichKham.item(row, 3))
                f.cboPK_Lich.setCurrentIndex(f.cboPK_Lich.findData(id_phong))
            except: pass

            # Chọn Dịch Vụ (Cột 4)
            try:
                id_dv = self.lay_id_tu_item(f.tableLichKham.item(row, 4))
                f.cboDV_Lich.setCurrentIndex(f.cboDV_Lich.findData(id_dv))
            except: pass

            # Chọn Ca Làm (Cột 8)
            try:
                ca_lam = f.tableLichKham.item(row, 8).text()
                for i in range(f.cboCaLamLich.count()):
                    if f.cboCaLamLich.itemText(i).startswith(ca_lam):
                        f.cboCaLamLich.setCurrentIndex(i)
                        break
            except: pass

            # Chọn Bác Sĩ (Đợi 100ms để Dịch vụ & Ca làm kịp lọc Bác sĩ xong)
            try:
                id_bs = self.lay_id_tu_item(f.tableLichKham.item(row, 2))
                QTimer.singleShot(100, lambda: f.cboBS_Lich.setCurrentIndex(f.cboBS_Lich.findData(id_bs)))
            except: pass
    def xu_ly_them_lk(self):
        f = self.forms["LK"]
        
        # Lấy dữ liệu ID ẩn từ các ComboBox
        id_bn = f.cboBN_Lich.currentData()
        id_bs = f.cboBS_Lich.currentData()
        id_dv = f.cboDV_Lich.currentData()
        
        ca_id = f.cboCaLamLich.currentData() or f.cboCaLamLich.currentText().split(" - ")[0]

        if id_bn == "NEW" or not id_bn or not id_bs or not id_dv:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn đầy đủ Bệnh nhân, Dịch vụ và Bác sĩ!")
            return

        if self.la_trung_lich_bac_si(id_bs, f.txtNgayKham.text(), f.txtGioKham.text(), ca_id):
            return

        # Bệnh nhân, Bác sĩ, Phòng khám (1), Dịch vụ, Ngày, Giờ, Trạng thái, Ca làm
        values = (
            id_bn, id_bs, 1, id_dv,
            f.txtNgayKham.text(), f.txtGioKham.text(), 
            f.comboBoxTrangThai.currentText(), ca_id
        )

        try:
            LichKhamController.insert(values)
            self.load_data_lichkham()
            QMessageBox.information(self, "Thành công", "Đã thêm lịch khám!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể thêm: {e}")
    def xu_ly_sua_lk(self):
        f = self.forms["LK"]
        idx = f.txtIDLich.text()
        
        if not idx:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng click chọn một lịch khám trên bảng để sửa!")
            return

        id_bn = f.cboBN_Lich.currentData()
        id_bs = f.cboBS_Lich.currentData()
        id_dv = f.cboDV_Lich.currentData()
        
        ca_id = f.cboCaLamLich.currentData() or f.cboCaLamLich.currentText().split(" - ")[0]

        if id_bn == "NEW" or not id_bn or not id_bs or not id_dv:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn đầy đủ Bệnh nhân, Dịch vụ và Bác sĩ!")
            return

        if self.la_trung_lich_bac_si(id_bs, f.txtNgayKham.text(), f.txtGioKham.text(), ca_id, idx):
            return

        values = (
            id_bn, id_bs, 1, id_dv, 
            f.txtNgayKham.text(), f.txtGioKham.text(), 
            f.comboBoxTrangThai.currentText(), ca_id
        )

        try:
            LichKhamController.update(int(idx), values)
            self.dong_bo_hoa_don_theo_trang_thai(idx, f.comboBoxTrangThai.currentText(), f.txtNgayKham.text())
            self.load_data_lichkham()
            QMessageBox.information(self, "Thành công", "Đã cập nhật lịch khám!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật: {e}")
    def xu_ly_xoa_lk(self):
        f = self.forms["LK"]
        id_lk = f.txtIDLich.text()
        if not id_lk:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn Lịch khám cần xóa!")
            return
        
        _id = self.parse_id(id_lk)
        if QMessageBox.question(self, "Xác nhận", "Xóa lịch khám này?") == QMessageBox.StandardButton.Yes:
            try:
                LichKhamController.delete(_id)
                QMessageBox.information(self, "Thành công", "Đã xóa Lịch khám!")
                self.load_data_lichkham()
                self.clear_form_inputs(f)
            except Exception as e:
                err_msg = str(e).upper()
                if "FOREIGN KEY" in err_msg or "CONSTRAINT" in err_msg:
                    reply = QMessageBox.question(self, "Cảnh báo", 
                                                 "Lịch khám này đã có Hóa đơn. Bạn có muốn xóa luôn Hóa đơn đi kèm không?", 
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.Yes:
                        try:
                            # Đổi DoanhThu -> HoaDon
                            execute_query("DELETE FROM HoaDon WHERE lichkham_id = ?", (_id,))
                            LichKhamController.delete(_id)
                            QMessageBox.information(self, "Thành công", "Đã xóa sạch Lịch khám và Hóa đơn!")
                            self.load_data_lichkham()
                            self.load_data_doanhthu()
                            self.clear_form_inputs(f)
                        except Exception as ex:
                            QMessageBox.critical(self, "Lỗi", f"Không thể xóa tự động.\nChi tiết: {ex}")
                else:
                    QMessageBox.critical(self, "Lỗi", f"Không thể xóa Lịch khám.\nChi tiết: {e}")
            
    def xu_ly_tim_kiem_lk(self):
        kw, ok = QInputDialog.getText(self, "Tìm", "Nhập mã BN hoặc BS:")
        if ok and kw:
            res = LichKhamController.search(kw)
            self.fill_table(self.forms["LK"].tableLichKham, res, ["ID", "Mã BN", "Mã BS", "Ngày Khám", "Giờ Khám", "Trạng Thái"])

    # ================= LOGIC DOANH THU =================
    def do_du_lieu_doanhthu_len_form(self):
        row = self.forms["DT"].tableDoanhThu.currentRow()
        if row >= 0:
            self.forms["DT"].txtIDDoanhThu.setText(self.forms["DT"].tableDoanhThu.item(row, 0).text())
            self.forms["DT"].txtIDLichKham.setText(self.forms["DT"].tableDoanhThu.item(row, 1).text())
            self.forms["DT"].txtTongTien.setText(self.forms["DT"].tableDoanhThu.item(row, 2).text())
            self.forms["DT"].txtNgayThanhToan.setText(self.forms["DT"].tableDoanhThu.item(row, 3).text())


    def xu_ly_them_dt(self):
        try:
            lichkham_id = self.forms["DT"].txtIDLichKham.text().strip()
            ngay = self.forms["DT"].txtNgayThanhToan.text().strip() 
            
            # 💎 THÊM LOGIC TỰ ĐỘNG ĐIỀN NGÀY HIỆN TẠI
            if not ngay:
                # Lấy ngày hôm nay theo định dạng Năm-Tháng-Ngày (chuẩn CSDL)
                from datetime import datetime
                ngay = datetime.now().strftime("%Y-%m-%d")
                
                # Điền ngược lại vào ô textbox để giao diện hiển thị cho người dùng thấy
                self.forms["DT"].txtNgayThanhToan.setText(ngay)
                
            if not lichkham_id:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập Mã Lịch Khám!")
                return

            # 2. Gọi hàm tự động lấy Tên và Tiền từ Database
            thong_tin = HoaDonController.get_thong_tin_tu_lich_kham(lichkham_id)
            
            if not thong_tin:
                QMessageBox.warning(self, "Lỗi", f"Không tìm thấy dữ liệu cho Lịch Khám ID: {lichkham_id}!")
                return
                
            # Trích xuất dữ liệu
            ten_bn = thong_tin.get('TenBenhNhan', 'Không rõ')
            tong_tien = thong_tin.get('TongTien', 0)

            # 3. Tiến hành Insert vào bảng HoaDon
            HoaDonController.insert(lichkham_id, tong_tien, ngay, ten_bn)
            
            QMessageBox.information(
                self, "Thành công", 
                f"Đã tạo hóa đơn tự động!\n- Bệnh nhân: {ten_bn}\n- Tổng tiền: {tong_tien:,.0f} VNĐ"
            )
            
            # 4. Tải lại bảng dữ liệu và xóa ô nhập liệu cũ để sẵn sàng cho hóa đơn tiếp theo
            self.load_data_doanhthu()
            self.forms["DT"].txtIDLichKham.clear()
            self.forms["DT"].txtNgayThanhToan.clear()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Có lỗi xảy ra khi thêm: {str(e)}")
    def xu_ly_sua_dt(self):
        f = self.forms["DT"]
        id_dt = f.txtIDDoanhThu.text()
        if not id_dt:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn Hóa đơn cần sửa!")
            return
        try:
            tien = float(f.txtTongTien.text().strip() or 0)
            HoaDonController.update(self.parse_id(id_dt), tien, f.txtNgayThanhToan.text())
            QMessageBox.information(self, "Thành công", "Cập nhật hóa đơn thành công!")
            self.load_data_doanhthu()
            self.clear_form_inputs(f)
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Số tiền không hợp lệ!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Có lỗi xảy ra: {e}")

    def xu_ly_xoa_dt(self):
        f = self.forms["DT"]
        id_dt = f.txtIDDoanhThu.text()
        if not id_dt:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn Hóa đơn cần xóa!")
            return
        
        _id = self.parse_id(id_dt)
        if QMessageBox.question(self, "Xác nhận", "Xóa hóa đơn này?") == QMessageBox.StandardButton.Yes:
            try:
                HoaDonController.delete(_id)
                QMessageBox.information(self, "Thành công", "Đã xóa Hóa đơn!")
                self.load_data_doanhthu()
                self.clear_form_inputs(f)
            except Exception as e:
                QMessageBox.critical(self, "Lỗi Hệ Thống", f"Không thể xóa hóa đơn.\nChi tiết: {e}")
            
    def xu_ly_tim_kiem_dt(self):
        kw, ok = QInputDialog.getText(self, "Tìm", "Mã Lịch Khám:")
        if ok and kw:
            res = HoaDonController.search(kw)
            self.fill_table(self.forms["DT"].tableDoanhThu, res, ["ID Hóa Đơn", "Mã LK", "Tổng Tiền", "Ngày", "Tên Bệnh Nhân"])

    # ================= LOGIC PHÒNG =================
    def do_du_lieu_phong_len_form(self):
        row = self.forms["PK"].tablePhong.currentRow()
        if row >= 0:
            self.forms["PK"].txtIDPhong.setText(self.forms["PK"].tablePhong.item(row, 0).text())
            self.forms["PK"].txtTenPhong.setText(self.forms["PK"].tablePhong.item(row, 1).text())
            self.forms["PK"].txtSoGiuong.setText(self.forms["PK"].tablePhong.item(row, 2).text())
            self.forms["PK"].txtMoTa.setText(self.forms["PK"].tablePhong.item(row, 3).text())

    def xu_ly_them_phong(self):
        f = self.forms["PK"]
        try:
            sg = int(f.txtSoGiuong.text().strip() or 0)
            if not f.txtTenPhong.text():
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập tên Phòng!")
                return
            PhongKhamController.insert([f.txtTenPhong.text(), sg, f.txtMoTa.text()])
            QMessageBox.information(self, "Thành công", "Đã thêm Phòng mới!")
            self.load_data_phongkham()
            self.clear_form_inputs(f)
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Số giường phải là số nguyên!")

    def xu_ly_sua_phong(self):
        f = self.forms["PK"]
        id_p = f.txtIDPhong.text()
        if not id_p:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn Phòng cần sửa!")
            return
        try:
            sg = int(f.txtSoGiuong.text().strip() or 0)
            PhongKhamController.update(self.parse_id(id_p), [f.txtTenPhong.text(), sg, f.txtMoTa.text()])
            QMessageBox.information(self, "Thành công", "Cập nhật Phòng thành công!")
            self.load_data_phongkham()
            self.clear_form_inputs(f)
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Số giường phải là số nguyên!")

    def xu_ly_xoa_phong(self):
        f = self.forms["PK"]
        id_p = f.txtIDPhong.text()
        if not id_p:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn Phòng cần xóa!")
            return
        
        _id = self.parse_id(id_p)
        if QMessageBox.question(self, "Xác nhận", "Xóa phòng này?") == QMessageBox.StandardButton.Yes:
            try:
                PhongKhamController.delete(_id)
                QMessageBox.information(self, "Thành công", "Đã xóa Phòng!")
                self.load_data_phongkham()
                self.clear_form_inputs(f)
            except Exception as e:
                err_msg = str(e).upper()
                if "FOREIGN KEY" in err_msg or "CONSTRAINT" in err_msg:
                    reply = QMessageBox.question(self, "Cảnh báo", 
                                                 "Phòng này đang có Lịch khám. Bạn có dám xóa sập Phòng khám và toàn bộ Lịch khám, Hóa đơn của nó không?", 
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.Yes:
                        try:
                            execute_query("DELETE FROM HoaDon WHERE lichkham_id IN (SELECT id FROM LichKham WHERE phongkham_id = ?)", (_id,))
                            execute_query("DELETE FROM LichKham WHERE phongkham_id = ?", (_id,))
                            PhongKhamController.delete(_id)
                            QMessageBox.information(self, "Thành công", "Đã đập bỏ Phòng và dữ liệu liên quan!")
                            self.load_data_phongkham()
                            self.clear_form_inputs(f)
                        except Exception as ex:
                            QMessageBox.critical(self, "Lỗi", f"Không thể xóa tự động.\nChi tiết: {ex}")
                else:
                    QMessageBox.critical(self, "Lỗi", f"Không thể xóa phòng.\nChi tiết: {e}")
            
    def xu_ly_tim_kiem_phong(self):
        kw, ok = QInputDialog.getText(self, "Tìm", "Tên phòng:")
        if ok and kw:
            res = PhongKhamController.search(kw)
            self.fill_table(self.forms["PK"].tablePhong, res, ["ID", "Tên Phòng", "Số Giường", "Mô Tả"])

    # ================= KHÔI PHỤC LOGIC THỐNG KÊ GỐC =================
    def show_thongke(self):
        self.mo_tab(self.forms["TK"], self.setup_thong_ke_ui)
        self.xu_ly_tim_kiem_tk()

    def setup_thong_ke_ui(self):
        if self.forms["TK"].cboxloai.count() == 0:
            self.forms["TK"].cboxloai.addItems(["Doanh thu theo dịch vụ", "Danh sách lượt khám"])
            self.forms["TK"].cboxthoigian.addItems(["Tất cả", "Tháng hiện tại", "Năm nay"])

    def xu_ly_tim_kiem_tk(self):
        try:
            loai = self.forms["TK"].cboxloai.currentText()
            if loai == "Doanh thu theo dịch vụ":
                data = ThongKeController.thong_ke_doanh_thu_dich_vu()
                display = [[r.get('ten_dich_vu', ''), r.get('so_luong', ''), f"{r.get('tong_tien', 0):,.0f}"] for r in data]
                self.fill_table(self.forms["TK"].tableThongKe, display, ["Dịch Vụ", "Số Lượng", "Doanh Thu"])
            else:
                data = ThongKeController.thong_ke_luot_kham_tong_hop()
                display = [
                    [
                        r.get('ngay_kham', ''),
                        r.get('ten_bac_si', ''),
                        r.get('ten_benh_nhan', ''),
                        r.get('gio_kham', ''),
                        r.get('trang_thai', '')
                    ]
                    for r in data
                ]
                self.fill_table(self.forms["TK"].tableThongKe, display, ["Ngày", "Bác Sĩ", "Bệnh Nhân", "Giờ", "Trạng Thái"])
        except Exception as e:
            pass 

    def xu_ly_them_tk(self):
        import csv
        path = "BaoCao.csv"
        try:
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                table = self.forms["TK"].tableThongKe
                writer.writerow([table.horizontalHeaderItem(i).text() for i in range(table.columnCount())])
                for r in range(table.rowCount()):
                    writer.writerow([table.item(r, c).text() for c in range(table.columnCount())])
            QMessageBox.information(self, "Thông báo", f"Đã xuất file: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def xu_ly_sua_tk(self): 
        self.xu_ly_tim_kiem_tk()

    # ================= LOGIC TIMELINE =================
    def hien_thi_timeline(self):

        try:
            # 1. Chuyển sang tab Timeline trên giao diện
            if "TL" in self.forms:
                self.formChucNang.stackedWidgetMain.setCurrentWidget(self.forms["TL"])
            
            # 2. Lấy toàn bộ dữ liệu từ Database
            lk = LichKhamController.get_all()
            bn = BenhNhanController.get_all()
            bs = BacSiController.get_all()
            dv = DichVuController.get_all()

            # 3. Định nghĩa ngày cần xem (Ngày hiện tại)
            ngay_xem = datetime.now().strftime("%Y-%m-%d")

            # 4. Giao toàn bộ việc vẽ và lọc cho TimelineHelper (gọi đủ 5 tham số)
            if hasattr(self, 'timeline_drawer'):
                self.timeline_drawer.draw(lk, bn, bs, dv, ngay_xem)

            # 5. Tính toán để hiển thị Tổng số lịch khám hôm nay (lblTotalValue)
            # Khai báo các định dạng ngày để phòng ngừa DB lưu lộn xộn
            today_formats = [
                datetime.now().strftime("%Y-%m-%d"),
                datetime.now().strftime("%d/%m/%Y"),
                datetime.now().strftime("%d-%m-%Y"),
                datetime.now().strftime("%Y/%m/%d")
            ]
            so_lich_hom_nay = 0
            for k in lk:
                ngay = str(k.get('ngay_kham', '') if isinstance(k, dict) else getattr(k, 'ngay_kham', '')).strip()
                if any(t in ngay for t in today_formats):
                    so_lich_hom_nay += 1

            if "TL" in self.forms and hasattr(self.forms["TL"], "lblTotalValue"):
                self.forms["TL"].lblTotalValue.setText(str(so_lich_hom_nay))
            
            # 6. Cập nhật GroupBox Lịch khám sắp tới ở màn hình chính
            self.cap_nhat_lich_kham_hom_nay()
                
        except Exception as e:
            print(f"Lỗi hiển thị Timeline: {e}")

    # ================= HÀM BỔ TRỢ & ĐỔ DỮ LIỆU CHUNG =================
    def mo_tab(self, form, func):
        self.formChucNang.stackedWidgetMain.setCurrentWidget(form)
        if func: func()

    def update_time(self):
        self.lblTime.setText(QDateTime.currentDateTime().toString("HH:mm:ss - dd/MM/yyyy"))

    def fill_table(self, table, data, headers):
        if not data:
            table.setRowCount(0)
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            return

        table.setRowCount(0)
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        for r, obj in enumerate(data):
            table.insertRow(r)
            if isinstance(obj, dict):
                vals = list(obj.values())
            elif isinstance(obj, list):
                vals = obj
            else:
                vals = [getattr(obj, a) for a in obj.__dict__ if not a.startswith('_')]
            
            for c, val in enumerate(vals):
                if c < len(headers):
                    table.setItem(r, c, QTableWidgetItem(str(val)))

    def load_data_benhnhan(self):
        self.fill_table(self.forms["BN"].tableBenhNhan, BenhNhanController.get_all(), ["ID", "Tên", "SĐT", "Địa chỉ", "GT", "Ngày sinh"])

    def load_data_bacsi(self):
        self.fill_table(self.forms["BS"].tableBacSi, BacSiController.get_all(), ["ID", "Họ Tên", "Giới Tính", "Chuyên Khoa", "Ca Làm"])

    def load_data_dichvu(self):
        self.fill_table(self.forms["DV"].tableDichVu, DichVuController.get_all(), ["ID", "Tên Dịch Vụ", "Đơn Giá", "Chuyên Khoa"])

    def load_data_phongkham(self):
        self.fill_table(self.forms["PK"].tablePhong, PhongKhamController.get_all(), ["ID", "Tên Phòng", "Số Giường", "Mô tả"])

    def load_data_lichkham(self):
        table = self.forms["LK"].tableLichKham
        headers = ["ID", "Bệnh Nhân", "Bác Sĩ", "Phòng Khám", "Dịch Vụ", "Ngày Khám", "Giờ Khám", "Trạng Thái", "Ca Làm"]
        table.setRowCount(0)
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        def ten_theo_id(items, item_id, attr_name):
            for item in items:
                if str(getattr(item, "id", "")) == str(item_id):
                    return str(getattr(item, attr_name, ""))
            return ""

        def item_ma_ten(item_id, name):
            text = f"{item_id} - {name}" if name else str(item_id)
            table_item = QTableWidgetItem(text)
            table_item.setData(Qt.ItemDataRole.UserRole, item_id)
            return table_item

        lich_kham = LichKhamController.get_all()
        lk_ui = self.forms["LK"]
        loc_ngay = getattr(lk_ui, "txtLocNgayKham", None)
        loc_trang_thai = getattr(lk_ui, "cboLocTrangThai", None)
        ngay_filter = loc_ngay.text().strip() if loc_ngay else ""
        trang_thai_filter = loc_trang_thai.currentText().strip() if loc_trang_thai else "Tat ca trang thai"

        if ngay_filter:
            def chuan_hoa_ngay(value):
                text = str(value).strip()
                for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
                    try:
                        return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
                    except ValueError:
                        pass
                return text

            ngay_filter_chuan = chuan_hoa_ngay(ngay_filter)
            lich_kham = [
                lk for lk in lich_kham
                if ngay_filter in str(lk.ngay_kham) or chuan_hoa_ngay(lk.ngay_kham) == ngay_filter_chuan
            ]
        if trang_thai_filter and trang_thai_filter != "Tat ca trang thai":
            lich_kham = [lk for lk in lich_kham if str(lk.trang_thai).strip() == trang_thai_filter]

        benh_nhan = BenhNhanController.get_all()
        bac_si = BacSiController.get_all()
        dich_vu = DichVuController.get_all()
        phong_kham = PhongKhamController.get_all()

        for row, lk in enumerate(lich_kham):
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(str(lk.id)))
            table.setItem(row, 1, item_ma_ten(lk.benhnhan_id, ten_theo_id(benh_nhan, lk.benhnhan_id, "ten")))
            table.setItem(row, 2, item_ma_ten(lk.bacsi_id, ten_theo_id(bac_si, lk.bacsi_id, "ten")))
            table.setItem(row, 3, item_ma_ten(lk.phongkham_id, ten_theo_id(phong_kham, lk.phongkham_id, "ten_phong")))
            table.setItem(row, 4, item_ma_ten(lk.dichvu_id, ten_theo_id(dich_vu, lk.dichvu_id, "ten_dich_vu")))
            table.setItem(row, 5, QTableWidgetItem(str(lk.ngay_kham)))
            table.setItem(row, 6, QTableWidgetItem(str(lk.gio_kham)))
            table.setItem(row, 7, QTableWidgetItem(str(lk.trang_thai)))
            table.setItem(row, 8, QTableWidgetItem(str(lk.ca_lam)))
        # Update groupBox bên phải khi lịch khám thay đổi
        self.cap_nhat_lich_kham_hom_nay()

    def load_data_taikhoan(self):
        self.fill_table(self.forms["TAIKHOAN"].tableTaiKhoan, TaiKhoanController.get_all(), ["ID", "Username", "Password", "Họ Tên", "Quyền"])

    def dong_bo_hoa_don_theo_trang_thai(self, lichkham_id, trang_thai, ngay_thanh_toan=None):
        status = str(trang_thai or "").strip().upper()
        is_done = any(text in status for text in ("XONG", "HOAN", "HOÀN", "DA KHAM", "ĐÃ KHÁM"))

        hoa_don = fetch_one("SELECT id FROM HoaDon WHERE lichkham_id = ?", (lichkham_id,))

        if not is_done:
            if hoa_don:
                execute_query("DELETE FROM HoaDon WHERE lichkham_id = ?", (lichkham_id,))
            self.load_data_doanhthu()
            return

        thong_tin = HoaDonController.get_thong_tin_tu_lich_kham(lichkham_id)
        if not thong_tin:
            return

        ten_bn = thong_tin.get("TenBenhNhan", "")
        tong_tien = thong_tin.get("TongTien", 0) or 0
        ngay = ngay_thanh_toan or datetime.now().strftime("%Y-%m-%d")
        if hoa_don:
            execute_query(
                "UPDATE HoaDon SET tong_tien = ?, ngay_thanh_toan = ?, TenBenhNhan = ? WHERE lichkham_id = ?",
                (tong_tien, ngay, ten_bn, lichkham_id)
            )
        else:
            HoaDonController.insert(lichkham_id, tong_tien, ngay, ten_bn)

        self.load_data_doanhthu()

    def load_data_doanhthu(self):
        data = HoaDonController.get_all()
        self.fill_table(self.forms["DT"].tableDoanhThu, data, ["ID Hóa Đơn", "Mã Lịch Khám", "Tổng Tiền", "Ngày", "Tên Bệnh Nhân"])
        self.load_thong_ke_doanh_thu()

    def load_thong_ke_doanh_thu(self):
        try:
            res = fetch_one("SELECT SUM(tong_tien) as Tong FROM HoaDon")
            val = res['Tong'] if res and res['Tong'] else 0
            if hasattr(self.forms["DT"], "lblTongDoanhThu"):
                self.forms["DT"].lblTongDoanhThu.setText(f"{val:,.0f} VNĐ")
        except Exception as e:
            pass

    def dang_xuat(self):
        if QMessageBox.question(self, 'Xác nhận', 'Bạn muốn đăng xuất?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.close()

# ================= RUN APP =================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginApp()
    main_win = MainApp()
    
    login.login_successful.connect(main_win.show)
    login.show()
    
    sys.exit(app.exec())
