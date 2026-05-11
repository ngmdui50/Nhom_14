from Controller.taikhoan_Controller import TaiKhoanController


def authenticate(username, password):
    username = str(username or "").strip()
    password = str(password or "").strip()
    return next(
        (
            tk for tk in TaiKhoanController.get_all()
            if tk.username == username and tk.password == password
        ),
        None,
    )


def reset_password_via_identity(username, ho_ten, new_password):
    return TaiKhoanController.reset_password_by_identity(
        str(username or "").strip(),
        str(ho_ten or "").strip(),
        str(new_password or "").strip(),
    )
