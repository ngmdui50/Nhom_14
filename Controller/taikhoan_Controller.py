from Model.connecDB import execute_query, fetch_all, fetch_one
from Model.taikhoan_Model import TaiKhoan


class TaiKhoanController:
    @staticmethod
    def _to_model(row):
        return TaiKhoan(
            id=row.get("id"),
            username=row.get("username"),
            password=row.get("password"),
            ho_ten=row.get("ho_ten"),
            quyen=row.get("quyen"),
        )

    @staticmethod
    def get_all():
        rows = fetch_all("SELECT id, username, password, ho_ten, quyen FROM TaiKhoan ORDER BY id")
        return [TaiKhoanController._to_model(row) for row in rows]

    @staticmethod
    def insert(username, password, ho_ten, quyen):
        return execute_query(
            "INSERT INTO TaiKhoan (username, password, ho_ten, quyen) VALUES (?, ?, ?, ?)",
            (username, password, ho_ten, quyen),
        )

    @staticmethod
    def update(id_tk, username, password, ho_ten, quyen):
        return execute_query(
            "UPDATE TaiKhoan SET username = ?, password = ?, ho_ten = ?, quyen = ? WHERE id = ?",
            (username, password, ho_ten, quyen, id_tk),
        )

    @staticmethod
    def find_by_username(username):
        row = fetch_one("SELECT id, username, password, ho_ten, quyen FROM TaiKhoan WHERE username = ?", (username,))
        return TaiKhoanController._to_model(row) if row else None

    @staticmethod
    def change_password(id_tk, old_password, new_password):
        row = fetch_one("SELECT password FROM TaiKhoan WHERE id = ?", (id_tk,))
        if not row or str(row.get("password", "")) != str(old_password):
            raise ValueError("Mat khau hien tai khong dung.")
        return execute_query("UPDATE TaiKhoan SET password = ? WHERE id = ?", (new_password, id_tk))

    @staticmethod
    def reset_password_by_identity(username, ho_ten, new_password):
        row = fetch_one(
            "SELECT id FROM TaiKhoan WHERE username = ? AND LOWER(ho_ten) = LOWER(?)",
            (username, ho_ten),
        )
        if not row:
            raise ValueError("Khong tim thay tai khoan phu hop voi username va ho ten.")
        return execute_query("UPDATE TaiKhoan SET password = ? WHERE id = ?", (new_password, row.get("id")))
