from datetime import datetime

from Controller.benhnhan_Controller import BenhNhanController


def normalize_date_input(text):
    value = str(text or "").strip()
    if not value:
        return ""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    raise ValueError("Ngay thang khong hop le. Dung yyyy-mm-dd hoac dd/mm/yyyy.")


def normalize_phone(text):
    value = "".join(ch for ch in str(text or "").strip() if ch.isdigit())
    if value and (len(value) < 9 or len(value) > 11):
        raise ValueError("So dien thoai phai tu 9 den 11 chu so.")
    return value


def validate_patient_input(ten, sdt, ngay_sinh):
    ten = str(ten or "").strip()
    if not ten:
        raise ValueError("Ten benh nhan khong duoc de trong.")
    return ten, normalize_phone(sdt), normalize_date_input(ngay_sinh) if str(ngay_sinh or "").strip() else ""


def update_patient(id_bn, ten, sdt, dia_chi, gioi_tinh, ngay_sinh, tien_su_benh="", di_ung="", ghi_chu_y_khoa=""):
    ten, sdt, ngay_sinh = validate_patient_input(ten, sdt, ngay_sinh)
    return BenhNhanController.update(
        id_bn, ten, sdt, str(dia_chi or "").strip(), str(gioi_tinh or "").strip(), ngay_sinh,
        tien_su_benh, di_ung, ghi_chu_y_khoa
    )
