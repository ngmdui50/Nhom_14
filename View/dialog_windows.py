import os

from PyQt6 import uic
from PyQt6.QtCore import QDate, QTime, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
)

from Controller.auth_module import authenticate, reset_password_via_identity
from Controller.bacsi_Controller import BacSiController
from Controller.benhnhan_Controller import BenhNhanController
from Controller.dichvu_Controller import DichVuController
from Controller.lichkham_Controller import LichKhamController

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIEW_DIR = os.path.join(BASE_DIR, "View")


def build_ui_path(filename):
    return os.path.join(VIEW_DIR, filename)


class LoginApp(QMainWindow):
    login_successful = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        try:
            uic.loadUi(build_ui_path("dangnhap.ui"), self)
            self.setFixedSize(self.size())
            self.txtpassword.setEchoMode(QLineEdit.EchoMode.Password)
            self.btndangnhap.clicked.connect(self.check_login)
            self.btnthoat.clicked.connect(self.close)
            logo_path = os.path.join(BASE_DIR, "logo.png")
            if hasattr(self, "lblLogo") and os.path.exists(logo_path):
                self.lblLogo.setPixmap(QPixmap(logo_path))
            if hasattr(self, "labelForgot"):
                self.labelForgot.clicked.connect(self.quen_mat_khau)
            self.txtusername.setFocus()
        except Exception as e:
            print(f"Lỗi load form Đăng nhập: {e}")

    def quen_mat_khau(self):
        username, ok = QInputDialog.getText(self, "Quên mật khẩu", "Nhập username:")
        if not ok or not username.strip():
            return
        ho_ten, ok = QInputDialog.getText(self, "Xác minh", "Nhập họ tên đúng với tài khoản:")
        if not ok or not ho_ten.strip():
            return
        new_password, ok = QInputDialog.getText(self, "Đặt mật khẩu mới", "Nhập mật khẩu mới:")
        if not ok or not new_password.strip():
            return
        confirm_password, ok = QInputDialog.getText(self, "Xác nhận", "Nhập lại mật khẩu mới:")
        if not ok or not confirm_password.strip():
            return
        if new_password != confirm_password:
            QMessageBox.warning(self, "Thông báo", "Xác nhận mật khẩu không khớp.")
            return
        try:
            reset_password_via_identity(username.strip(), ho_ten.strip(), new_password.strip())
            QMessageBox.information(self, "Thành công", "Đã đặt lại mật khẩu. Hãy đăng nhập lại.")
        except ValueError as ve:
            QMessageBox.warning(self, "Thông báo", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def check_login(self):
        username = self.txtusername.text().strip()
        password = self.txtpassword.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
            return

        try:
            user = authenticate(username, password)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi hệ thống", f"Không thể xử lý đăng nhập: {e}")
            return

        if not user:
            QMessageBox.warning(self, "Lỗi đăng nhập", "Tên đăng nhập hoặc mật khẩu không đúng!")
            return

        ten_hien_thi = str(getattr(user, "ho_ten", "") or getattr(user, "username", "") or username)
        QMessageBox.information(self, "Thành công", f"Đăng nhập thành công. Xin chào {ten_hien_thi}!")
        self.login_successful.emit(user)
        self.close()


class DialogChiTietLichKham(QDialog):
    def __init__(self, parent=None, lich_id=None):
        super().__init__(parent)
        self.main_app = parent
        self.lich_id = lich_id
        self.is_edit_mode = False
        self.init_ui()

    def init_ui(self):
        uic.loadUi(build_ui_path("FormChiTietLichKham.ui"), self)
        self.cbtrang_thai.clear()
        self.cbtrang_thai.addItems(["Chờ Khám", "Đang Khám", "Đã Xong", "Hủy Lịch"])
        self.btnEdit.clicked.connect(self.bat_che_do_sua)
        self.btnSave.clicked.connect(self.luu_thong_tin_sua)
        self.btnClose.clicked.connect(self.close)
        self.load_data()
        self.set_che_do_chiren(True)

    def load_data(self):
        if not self.lich_id:
            return

        def val(item, *keys):
            if isinstance(item, dict):
                for k in keys:
                    if k in item and item[k] is not None:
                        return item[k]
            else:
                for k in keys:
                    if hasattr(item, k) and getattr(item, k) is not None:
                        return getattr(item, k)
            return ""

        try:
            lk_data = LichKhamController.get_all()
            l = None
            for x in lk_data:
                if str(val(x, "id", "ID")).strip() == str(self.lich_id).strip():
                    l = x
                    break
            if not l:
                raise Exception(f"Không tìm thấy lịch khám có ID {self.lich_id}")
            self.lich_hien_tai = l

            dict_bn = {str(val(bn, "id", "ID")): str(val(bn, "ho_ten", "ten", "ten_benh_nhan")) for bn in BenhNhanController.get_all()}
            dict_bs = {str(val(bs, "id", "ID")): str(val(bs, "ho_ten", "ten", "ten_bac_si")) for bs in BacSiController.get_all()}
            dict_dv = {str(val(dv, "id", "ID")): str(val(dv, "ten_dich_vu", "ten_dv", "ten")) for dv in DichVuController.get_all()}

            self.txtid.setText(str(val(l, "id", "ID")))
            self.txtbenhnhan.setText(dict_bn.get(str(val(l, "benh_nhan_id", "benhnhan_id")), "Không rõ"))
            self.txtbacsi.setText(dict_bs.get(str(val(l, "bac_si_id", "bacsi_id")), "Không rõ"))
            self.txtdichvu.setText(dict_dv.get(str(val(l, "dich_vu_id", "dichvu_id")), "Không rõ"))

            ngay_str = str(val(l, "ngay_kham"))
            q_date = QDate.fromString(ngay_str, "yyyy-MM-dd")
            if not q_date.isValid():
                q_date = QDate.fromString(ngay_str, "dd/MM/yyyy")
            if q_date.isValid():
                self.datekham.setDate(q_date)

            gio_str = str(val(l, "gio_kham"))
            if len(gio_str) > 5:
                gio_str = gio_str[:5]
            q_time = QTime.fromString(gio_str, "HH:mm")
            if q_time.isValid():
                self.timekham.setTime(q_time)

            trang_thai = str(val(l, "trang_thai", "TrangThai", "trangthai"))
            index = self.cbtrang_thai.findText(trang_thai)
            if index >= 0:
                self.cbtrang_thai.setCurrentIndex(index)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi lấy dữ liệu", str(e))
            self.close()

    def set_che_do_chiren(self, is_read_only):
        self.txtid.setReadOnly(True)
        self.txtbenhnhan.setReadOnly(True)
        self.txtbacsi.setReadOnly(is_read_only)
        self.txtdichvu.setReadOnly(is_read_only)
        self.datekham.setReadOnly(is_read_only)
        self.timekham.setReadOnly(is_read_only)
        self.cbtrang_thai.setEnabled(not is_read_only)
        self.btnEdit.setVisible(is_read_only)
        self.btnSave.setVisible(not is_read_only)
        self.btnClose.setVisible(is_read_only)

    def bat_che_do_sua(self):
        self.is_edit_mode = True
        self.set_che_do_chiren(False)

    def luu_thong_tin_sua(self):
        try:
            ngay_new = self.datekham.date().toString("yyyy-MM-dd")
            gio_new = self.timekham.time().toString("HH:mm")
            tt_new = self.cbtrang_thai.currentText()
            tt_old = str(getattr(self.lich_hien_tai, "trang_thai", getattr(self.lich_hien_tai, "TrangThai", "")))
            mo_ta_new = None
            if tt_new != tt_old and "Đã Xong" in tt_new:
                mo_ta_new, ok = QInputDialog.getMultiLineText(
                    self,
                    "Mô tả chuyển trạng thái",
                    f"Nhập mô tả/lý do chuyển trạng thái từ '{tt_old}' sang '{tt_new}':",
                    str(getattr(self.lich_hien_tai, "mo_ta", "") or ""),
                )
                if not ok:
                    return
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Question)
            msg_box.setWindowTitle("Xác nhận")
            msg_box.setText("Bạn có chắc chắn muốn lưu thông tin đã sửa?")
            btn_yes = msg_box.addButton("Có", QMessageBox.ButtonRole.YesRole)
            msg_box.addButton("Không", QMessageBox.ButtonRole.NoRole)
            msg_box.exec()

            if msg_box.clickedButton() != btn_yes:
                return

            updated_rows = LichKhamController.update_tu_form_chi_tiet(
                self.lich_id, ngay_new, gio_new, tt_new, mo_ta_new
            )
            if updated_rows == 0:
                raise ValueError("Không tìm thấy lịch khám để cập nhật.")

            QMessageBox.information(self, "Thành công", "Đã cập nhật thông tin lịch khám thành công!")
            self.accept()
            if hasattr(self, "main_app") and self.main_app:
                QTimer.singleShot(
                    0,
                    lambda: (
                        self.main_app.dong_bo_hoa_don_theo_trang_thai(self.lich_id, tt_new, ngay_new),
                        self.main_app.hien_thi_timeline(),
                    ),
                )
        except Exception as e:
            QMessageBox.critical(self, "Lỗi khi lưu", str(e))


class ThemBenhNhanWindow(QDialog):
    def __init__(self, parent_main, preset_name=""):
        super().__init__(parent_main)
        try:
            uic.loadUi(build_ui_path("FormThemBenhNhan.ui"), self)
            self.parent_main = parent_main
            self.preset_name = str(preset_name or "").strip()
            if self.preset_name and hasattr(self, "txtTenBN"):
                self.txtTenBN.setText(self.preset_name)
                self.txtTenBN.selectAll()
            self.btnLuuBN.clicked.connect(self.xu_ly_luu)
        except Exception as e:
            print(f"Không thể load file FormThemBenhNhan.ui: {e}")

    def xu_ly_luu(self):
        ten = self.txtTenBN.text().strip()
        if not ten:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên bệnh nhân!")
            return
        gioi_tinh = self.cboGioiTinh.currentText()
        ngay_sinh = self.txtNgaySinh.text().strip()
        sdt = self.txtSDT.text().strip()
        dia_chi = self.txtDiaChi.text().strip()
        try:
            BenhNhanController.insert(ten, sdt, dia_chi, gioi_tinh, ngay_sinh)
            QMessageBox.information(self, "Thành công", f"Đã thêm bệnh nhân: {ten}")
            self.created_patient_id = None
            try:
                from Model.connecDB import fetch_one
                row = fetch_one(
                    "SELECT id FROM BenhNhan ORDER BY id DESC LIMIT 1"
                )
                if row:
                    self.created_patient_id = row.get("id")
            except Exception:
                pass
            if hasattr(self.parent_main, "load_data_benhnhan"):
                self.parent_main.load_data_benhnhan()
            if hasattr(self.parent_main, "setup_goi_y_lich_kham"):
                self.parent_main.setup_goi_y_lich_kham()
            if hasattr(self.parent_main, "chon_benh_nhan_vua_them"):
                self.parent_main.chon_benh_nhan_vua_them(ten, sdt, ngay_sinh)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu: {e}")


class ToastNotification(QDialog):
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(320, 96)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        card = QFrame(self)
        card.setObjectName("toastCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 12, 14, 12)
        card_layout.setSpacing(4)
        lbl_title = QLabel(title, card)
        lbl_title.setObjectName("toastTitle")
        lbl_msg = QLabel(message, card)
        lbl_msg.setObjectName("toastMessage")
        lbl_msg.setWordWrap(True)
        card_layout.addWidget(lbl_title)
        card_layout.addWidget(lbl_msg)
        layout.addWidget(card)
        QTimer.singleShot(4200, self.close)
