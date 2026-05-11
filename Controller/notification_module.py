from Controller.benhnhan_Controller import BenhNhanController
from Controller.taikhoan_Controller import TaiKhoanController
from Controller.thongbao_Controller import ThongBaoController
from Model.connecDB import fetch_one


def find_account_for_doctor(bacsi_id):
    try:
        row = fetch_one("SELECT ten FROM BacSi_Moi WHERE id = ?", (bacsi_id,))
        if not row:
            return None
        ten_bs = str(row.get("ten", "")).strip().lower()
        for tk in TaiKhoanController.get_all():
            if str(getattr(tk, "ho_ten", "") or "").strip().lower() == ten_bs:
                return tk
    except Exception:
        return None
    return None


def create_new_schedule_notification(bacsi_id, benhnhan_id, ngay_kham, gio_kham):
    tai_khoan_bs = find_account_for_doctor(bacsi_id)
    if not tai_khoan_bs:
        return

    benh_nhan = next(
        (bn for bn in BenhNhanController.get_all() if str(getattr(bn, "id", "")) == str(benhnhan_id)),
        None,
    )
    ten_bn = str(getattr(benh_nhan, "ten", "") or benhnhan_id)
    ThongBaoController.insert(
        getattr(tai_khoan_bs, "id", None),
        "Ban co lich kham moi",
        f"Benh nhan {ten_bn} duoc dat lich vao {gio_kham} ngay {ngay_kham}.",
    )


def get_unread_notifications(taikhoan_id):
    return ThongBaoController.get_chua_doc(taikhoan_id)


def mark_all_notifications_read(taikhoan_id):
    return ThongBaoController.mark_all_as_read(taikhoan_id)


def mark_notification_read(thongbao_id):
    return ThongBaoController.mark_as_read(thongbao_id)
