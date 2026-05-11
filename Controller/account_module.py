from Controller.taikhoan_Controller import TaiKhoanController


def validate_account_input(username, password, ho_ten, quyen):
    username = str(username or "").strip()
    password = str(password or "").strip()
    ho_ten = str(ho_ten or "").strip()
    quyen = str(quyen or "").strip()
    if not username or not password or not ho_ten or not quyen:
        raise ValueError("Vui long nhap day du thong tin tai khoan.")
    return username, password, ho_ten, quyen


def create_account(username, password, ho_ten, quyen):
    username, password, ho_ten, quyen = validate_account_input(username, password, ho_ten, quyen)
    if TaiKhoanController.find_by_username(username):
        raise ValueError("Username da ton tai.")
    TaiKhoanController.insert(username, password, ho_ten, quyen)


def update_account(id_tk, username, password, ho_ten, quyen):
    username, password, ho_ten, quyen = validate_account_input(username, password, ho_ten, quyen)
    tk = TaiKhoanController.find_by_username(username)
    if tk and str(getattr(tk, "id", "")) != str(id_tk):
        raise ValueError("Username da ton tai.")
    TaiKhoanController.update(id_tk, username, password, ho_ten, quyen)


def change_profile_password(id_tk, old_password, new_password, confirm_password):
    old_password = str(old_password or "").strip()
    new_password = str(new_password or "").strip()
    confirm_password = str(confirm_password or "").strip()
    if not old_password or not new_password or not confirm_password:
        raise ValueError("Vui long nhap day du thong tin doi mat khau.")
    if new_password != confirm_password:
        raise ValueError("Xac nhan mat khau moi khong khop.")
    TaiKhoanController.change_password(id_tk, old_password, new_password)
