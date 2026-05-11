from datetime import datetime

from PyQt6.QtCore import QDate, QDateTime, Qt
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from Controller.bacsi_Controller import BacSiController
from Controller.benhnhan_Controller import BenhNhanController
from Controller.dichvu_Controller import DichVuController
from Controller.hoadon_Controller import HoaDonController
from Controller.lichkham_Controller import LichKhamController
from Controller.phong_Controller import PhongKhamController
from Controller.taikhoan_Controller import TaiKhoanController
from Controller.thongke_Controller import ThongKeController
from Model.connecDB import fetch_one, execute_query


def tao_mau_trang_thai(text):
    status = str(text or "").strip().lower()
    if "xong" in status or "hoan" in status:
        return ("#166534", "#dcfce7")
    if "dang" in status:
        return ("#1d4ed8", "#dbeafe")
    if "cho" in status:
        return ("#a16207", "#fef3c7")
    if "huy" in status:
        return ("#b91c1c", "#fee2e2")
    return ("#475569", "#e2e8f0")


def ap_dung_mau_trang_thai_cho_bang(table, cot_trang_thai):
    for row in range(table.rowCount()):
        item = table.item(row, cot_trang_thai)
        if not item:
            continue
        fg, bg = tao_mau_trang_thai(item.text())
        item.setForeground(QColor(fg))
        item.setBackground(QColor(bg))


def fill_table(app, table, data, headers):
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
            vals = [getattr(obj, a) for a in obj.__dict__ if not a.startswith("_")]
        for c, val in enumerate(vals):
            if c < len(headers):
                table.setItem(r, c, QTableWidgetItem(str(val)))

    for idx, header in enumerate(headers):
        header_text = str(header).lower()
        if "trạng thái" in header_text or "trang thai" in header_text:
            ap_dung_mau_trang_thai_cho_bang(table, idx)
            break


def cap_nhat_dashboard_theo_quyen(app, lich_trong_ngay, so_ca_da_xong, tong_tien_hom_nay):
    tl_form = app.forms.get("TL")
    if not tl_form:
        return
    lbl1 = getattr(tl_form, "lblRevenueTitle", None)
    lbl2 = getattr(tl_form, "lblCompletedTitle", None)
    lbl3 = getattr(tl_form, "lblTotalTitle", None)
    val1 = getattr(tl_form, "lblRevenueValue", None)
    val2 = getattr(tl_form, "lblCompletedValue", None)
    val3 = getattr(tl_form, "lblTotalValue", None)
    if not all([lbl1, lbl2, lbl3, val1, val2, val3]):
        return

    role = app.current_role
    bn_all = BenhNhanController.get_all()
    bs_all = BacSiController.get_all()

    if role in ("admin", "quan_ly"):
        lbl1.setText("Tong lich hom nay")
        lbl2.setText("Da kham xong")
        lbl3.setText("Tong bac si")
        val1.setText(str(len(lich_trong_ngay)))
        val2.setText(str(so_ca_da_xong))
        val3.setText(str(len(bs_all)))
        return
    if role == "ke_toan":
        lbl1.setText("Doanh thu hom nay")
        lbl2.setText("Hoa don hom nay")
        lbl3.setText("Ca da xong")
        val1.setText(f"{tong_tien_hom_nay:,.0f} VND")
        val2.setText(str(so_ca_da_xong))
        val3.setText(str(len(lich_trong_ngay)))
        return
    if role == "bac_si":
        dang_kham = 0
        cho_kham = 0
        for lk in lich_trong_ngay:
            status = str(getattr(lk, "trang_thai", getattr(lk, "TrangThai", ""))).strip().lower()
            if "dang" in status:
                dang_kham += 1
            elif "cho" in status:
                cho_kham += 1
        lbl1.setText("Ca kham hom nay")
        lbl2.setText("Da kham xong")
        lbl3.setText("Dang/Cho kham")
        val1.setText(str(len(lich_trong_ngay)))
        val2.setText(str(so_ca_da_xong))
        val3.setText(f"{dang_kham}/{cho_kham}")
        return
    if role == "le_tan":
        lbl1.setText("Lich moi hom nay")
        lbl2.setText("Benh nhan hom nay")
        lbl3.setText("Ca cho kham")
        benh_nhan_ids = {str(getattr(lk, "benhnhan_id", "")) for lk in lich_trong_ngay}
        cho_kham = 0
        for lk in lich_trong_ngay:
            status = str(getattr(lk, "trang_thai", getattr(lk, "TrangThai", ""))).strip().lower()
            if "cho" in status:
                cho_kham += 1
        val1.setText(str(len(lich_trong_ngay)))
        val2.setText(str(len(benh_nhan_ids)))
        val3.setText(str(cho_kham))
        return

    lbl1.setText("Tong lich")
    lbl2.setText("Da xong")
    lbl3.setText("Tong benh nhan")
    val1.setText(str(len(lich_trong_ngay)))
    val2.setText(str(so_ca_da_xong))
    val3.setText(str(len(bn_all)))


def on_calendar_date_changed(app, qdate):
    app.selected_dashboard_date = qdate.toString("yyyy-MM-dd")
    lk_ui = app.forms["LK"]
    if hasattr(lk_ui, "txtLocNgayKham"):
        lk_ui.txtLocNgayKham.setText(app.selected_dashboard_date)
    hien_thi_timeline(app)


def cap_nhat_danh_dau_calendar(app):
    if not hasattr(app.formChucNang, "calendarWidget"):
        return
    calendar = app.formChucNang.calendarWidget
    dates = set()
    for lk in app.loc_lich_kham_theo_quyen(LichKhamController.get_all()):
        text = str(getattr(lk, "ngay_kham", "")).strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                dates.add(datetime.strptime(text, fmt).strftime("%Y-%m-%d"))
                break
            except ValueError:
                continue
    from PyQt6.QtGui import QTextCharFormat
    fmt = QTextCharFormat()
    fmt.setBackground(QBrush(QColor("#dbeafe")))
    fmt.setForeground(QColor("#1d4ed8"))
    for date_text in dates:
        qdate = QDate.fromString(date_text, "yyyy-MM-dd")
        if qdate.isValid():
            calendar.setDateTextFormat(qdate, fmt)


def cap_nhat_lich_kham_hom_nay(app):
    try:
        lk_all = app.loc_lich_kham_theo_quyen(LichKhamController.get_all())
        bn_all = BenhNhanController.get_all()
        hd_all = HoaDonController.get_all()
        dict_bn = {
            str(b.get("id") if isinstance(b, dict) else getattr(b, "id")):
            (b.get("ten") or b.get("TenBN") if isinstance(b, dict) else getattr(b, "ten", ""))
            for b in bn_all
        }
        now = datetime.now()
        base_date = app.selected_dashboard_date or now.strftime("%Y-%m-%d")
        today_str = base_date
        try:
            today_rev = datetime.strptime(base_date, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            today_rev = base_date

        lk_hom_nay = []
        so_ca_da_xong = 0
        for k in lk_all:
            ngay_kham = str(k.get("ngay_kham") if isinstance(k, dict) else getattr(k, "ngay_kham", "")).strip()
            if today_str in ngay_kham or today_rev in ngay_kham:
                lk_hom_nay.append(k)
                trang_thai = str(
                    k.get("trang_thai") or k.get("TrangThai", "") if isinstance(k, dict) else getattr(k, "trang_thai", "")
                ).strip().upper()
                if any(x in trang_thai for x in ["ĐÃ", "XONG", "HOÀN THÀNH"]):
                    so_ca_da_xong += 1

        tong_tien_hom_nay = 0
        for hd in hd_all:
            ngay_hd = str(
                hd.get("ngay_lap") or hd.get("ngay_thanh_toan") or hd.get("Ngay") or hd.get("ngay", "")
                if isinstance(hd, dict) else getattr(hd, "ngay_thanh_toan", getattr(hd, "ngay_lap", ""))
            ).strip()
            if today_str in ngay_hd or today_rev in ngay_hd:
                tien = hd.get("tong_tien") or hd.get("TongTien", 0) if isinstance(hd, dict) else getattr(hd, "tong_tien", 0)
                try:
                    tong_tien_hom_nay += float(tien)
                except Exception:
                    pass

        target_ui = app.forms.get("TIMELINE") if hasattr(app, "forms") and "TIMELINE" in app.forms else getattr(app, "formChucNang", None)
        if not hasattr(app, "list_lich_kham") or app.list_lich_kham is None:
            if target_ui:
                found_list = target_ui.findChild(QListWidget, "list_lich_kham")
                if found_list:
                    app.list_lich_kham = found_list
                else:
                    app.list_lich_kham = QListWidget()
                    group_box = target_ui.findChild(QGroupBox, "groupBox")
                    if group_box:
                        if not group_box.layout():
                            group_box.setLayout(QVBoxLayout())
                        group_box.layout().addWidget(app.list_lich_kham)
        if hasattr(app, "list_lich_kham") and app.list_lich_kham is not None:
            app.list_lich_kham.clear()
        else:
            return

        for k in lk_hom_nay:
            gio = str(k.get("gio_kham") if isinstance(k, dict) else getattr(k, "gio_kham", "")).strip()
            id_bn = str(k.get("benhnhan_id") if isinstance(k, dict) else getattr(k, "benhnhan_id", ""))
            trang_thai = str(k.get("trang_thai") or k.get("TrangThai", "") if isinstance(k, dict) else getattr(k, "trang_thai", "")).strip()

            container = QWidget()
            lay = QHBoxLayout(container)
            card = QFrame()
            card.setObjectName("cardLichKham")
            card_lay = QHBoxLayout(card)
            lbl_gio = QLabel(f"⏰ {gio}")
            lbl_gio.setStyleSheet("color: #00E5FF; font-weight: bold;")
            lbl_ten = QLabel(dict_bn.get(id_bn, f"BN: {id_bn}"))
            lbl_ten.setStyleSheet("color: white;")
            lbl_st = QLabel(trang_thai.upper())
            st_color = "#2e7d32" if any(x in trang_thai.upper() for x in ["ĐÃ", "XONG"]) else "#d32f2f"
            lbl_st.setStyleSheet(
                f"color: {st_color}; border: 1px solid {st_color}; border-radius: 4px; padding: 2px 5px; font-size: 9px;"
            )
            card_lay.addWidget(lbl_gio)
            card_lay.addWidget(lbl_ten, 1)
            card_lay.addWidget(lbl_st)
            lay.addWidget(card)
            item = QListWidgetItem(app.list_lich_kham)
            from PyQt6.QtCore import QSize
            item.setSizeHint(QSize(0, 55))
            app.list_lich_kham.setItemWidget(item, container)

        if target_ui:
            lbl_total = target_ui.findChild(QLabel, "lblTotalValue")
            lbl_completed = target_ui.findChild(QLabel, "lblCompletedValue")
            lbl_revenue = target_ui.findChild(QLabel, "lblRevenueValue")
            if lbl_total:
                lbl_total.setText(str(len(lk_hom_nay)))
            if lbl_completed:
                lbl_completed.setText(str(so_ca_da_xong))
            if lbl_revenue:
                lbl_revenue.setText(f"{tong_tien_hom_nay:,.0f} VNĐ")
        cap_nhat_dashboard_theo_quyen(app, lk_hom_nay, so_ca_da_xong, tong_tien_hom_nay)
    except Exception as e:
        print(f"Loi cap nhat lich kham: {e}")


def show_thongke(app):
    app.mo_tab(app.forms["TK"], app.setup_thong_ke_ui)
    app.xu_ly_tim_kiem_tk()


def setup_thong_ke_ui(app):
    if app.forms["TK"].cboxloai.count() == 0:
        app.forms["TK"].cboxloai.addItems(["Doanh thu theo dịch vụ", "Danh sách lượt khám"])
        app.forms["TK"].cboxthoigian.addItems(["Tất cả", "Tháng hiện tại", "Năm nay"])


def xu_ly_tim_kiem_tk(app):
    try:
        loai = app.forms["TK"].cboxloai.currentText()
        if loai == "Doanh thu theo dịch vụ":
            data = ThongKeController.thong_ke_doanh_thu_dich_vu()
            display = [[r.get("ten_dich_vu", ""), r.get("so_luong", ""), f"{r.get('tong_tien', 0):,.0f}"] for r in data]
            fill_table(app, app.forms["TK"].tableThongKe, display, ["Dich vu", "So luong", "Doanh thu"])
        else:
            data = ThongKeController.thong_ke_luot_kham_tong_hop()
            display = [[r.get("ngay_kham", ""), r.get("ten_bac_si", ""), r.get("ten_benh_nhan", ""), r.get("gio_kham", ""), r.get("trang_thai", "")] for r in data]
            fill_table(app, app.forms["TK"].tableThongKe, display, ["Ngay", "Bac si", "Benh nhan", "Gio", "Trang thai"])
    except Exception:
        pass


def xuat_file_thong_ke(app):
    import csv
    path = "BaoCao.csv"
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        table = app.forms["TK"].tableThongKe
        writer.writerow([table.horizontalHeaderItem(i).text() for i in range(table.columnCount())])
        for r in range(table.rowCount()):
            writer.writerow([table.item(r, c).text() for c in range(table.columnCount())])


def hien_thi_timeline(app):
    try:
        if "TL" in app.forms:
            app.formChucNang.stackedWidgetMain.setCurrentWidget(app.forms["TL"])
            app.cap_nhat_sidebar_dang_chon("TL")
        lk = app.loc_lich_kham_theo_quyen(LichKhamController.get_all())
        bn = BenhNhanController.get_all()
        bs = BacSiController.get_all()
        dv = DichVuController.get_all()
        ngay_xem = app.selected_dashboard_date or datetime.now().strftime("%Y-%m-%d")
        if hasattr(app, "timeline_drawer"):
            app.timeline_drawer.draw(lk, bn, bs, dv, ngay_xem)
        cap_nhat_danh_dau_calendar(app)
        cap_nhat_lich_kham_hom_nay(app)
    except Exception as e:
        print(f"Loi hien thi Timeline: {e}")


def mo_tab(app, form, func):
    app.formChucNang.stackedWidgetMain.setCurrentWidget(form)
    app.cap_nhat_trang_thai_nut_theo_form()
    active_key = next((key for key, current_form in app.forms.items() if current_form == form), None)
    app.cap_nhat_sidebar_dang_chon(active_key)
    if func:
        func()


def update_time(app):
    app.lblTime.setText(QDateTime.currentDateTime().toString("HH:mm:ss - dd/MM/yyyy"))


def load_data_lichkham(app):
    table = app.forms["LK"].tableLichKham
    headers = ["ID", "Bệnh Nhân", "Bác Sĩ", "Phòng Khám", "Dịch Vụ", "Ngày Khám", "Giờ Khám", "Trạng Thái", "Ca Làm", "Mô tả"]
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

    lich_kham = app.loc_lich_kham_theo_quyen(LichKhamController.get_all())
    lk_ui = app.forms["LK"]
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
        lich_kham = [lk for lk in lich_kham if ngay_filter in str(lk.ngay_kham) or chuan_hoa_ngay(lk.ngay_kham) == ngay_filter_chuan]
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
        table.setItem(row, 9, QTableWidgetItem(str(getattr(lk, "mo_ta", "") or "")))
    ap_dung_mau_trang_thai_cho_bang(table, 7)
    cap_nhat_lich_kham_hom_nay(app)


def load_data_taikhoan(app):
    fill_table(app, app.forms["TAIKHOAN"].tableTaiKhoan, TaiKhoanController.get_all(), ["ID", "Username", "Password", "Họ Tên", "Quyền"])


def dong_bo_hoa_don_theo_trang_thai(app, lichkham_id, trang_thai, ngay_thanh_toan=None):
    status = str(trang_thai or "").strip().upper()
    is_done = any(text in status for text in ("XONG", "HOAN", "HOÀN", "DA KHAM", "ĐÃ KHÁM"))
    hoa_don = fetch_one("SELECT id FROM HoaDon WHERE lichkham_id = ?", (lichkham_id,))
    if not is_done:
        if hoa_don:
            execute_query("DELETE FROM HoaDon WHERE lichkham_id = ?", (lichkham_id,))
        app.load_data_doanhthu()
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
            (tong_tien, ngay, ten_bn, lichkham_id),
        )
    else:
        HoaDonController.insert(lichkham_id, tong_tien, ngay, ten_bn)
    load_data_doanhthu(app)


def load_data_doanhthu(app):
    data = HoaDonController.get_all()
    fill_table(app, app.forms["DT"].tableDoanhThu, data, ["ID Hóa Đơn", "Mã Lịch Khám", "Tổng Tiền", "Ngày", "Tên Bệnh Nhân"])
    load_thong_ke_doanh_thu(app)


def load_thong_ke_doanh_thu(app):
    try:
        res = fetch_one("SELECT SUM(tong_tien) as Tong FROM HoaDon")
        val = res["Tong"] if res and res["Tong"] else 0
        if hasattr(app.forms["DT"], "lblTongDoanhThu"):
            app.forms["DT"].lblTongDoanhThu.setText(f"{val:,.0f} VNĐ")
    except Exception:
        pass
