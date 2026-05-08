import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Model.benhnhan_Model import BenhNhan
from Model.connecDB import execute_query, fetch_all


class BenhNhanController:
    @staticmethod
    def _to_model(row):
        return BenhNhan(
            row["id"],
            row["ten"],
            row["sdt"],
            row["dia_chi"],
            row["gioi_tinh"],
            row["ngay_sinh"],
            row.get("tien_su_benh", ""),
            row.get("di_ung", ""),
            row.get("ghi_chu_y_khoa", ""),
        )

    @staticmethod
    def get_all():
        try:
            return [BenhNhanController._to_model(r) for r in fetch_all("SELECT * FROM BenhNhan")]
        except Exception as e:
            print(f"Loi lay danh sach benh nhan: {e}")
            return []

    @staticmethod
    def insert(ten, sdt, dia_chi, gioi_tinh, ngay_sinh, tien_su_benh="", di_ung="", ghi_chu_y_khoa=""):
        try:
            query = """
                INSERT INTO BenhNhan
                (ten, sdt, dia_chi, gioi_tinh, ngay_sinh, tien_su_benh, di_ung, ghi_chu_y_khoa)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            execute_query(query, (ten, sdt, dia_chi, gioi_tinh, ngay_sinh, tien_su_benh, di_ung, ghi_chu_y_khoa))
            return True
        except Exception as e:
            print(f"Loi them benh nhan: {e}")
            return False

    @staticmethod
    def update(id_bn, ten, sdt, dia_chi, gioi_tinh, ngay_sinh, tien_su_benh="", di_ung="", ghi_chu_y_khoa=""):
        try:
            query = """
                UPDATE BenhNhan
                SET ten=?, sdt=?, dia_chi=?, gioi_tinh=?, ngay_sinh=?, tien_su_benh=?, di_ung=?, ghi_chu_y_khoa=?
                WHERE id=?
            """
            execute_query(
                query,
                (ten, sdt, dia_chi, gioi_tinh, ngay_sinh, tien_su_benh, di_ung, ghi_chu_y_khoa, id_bn),
            )
            return True
        except Exception as e:
            print(f"Loi cap nhat benh nhan: {e}")
            return False

    @staticmethod
    def delete(id_bn):
        try:
            execute_query("DELETE FROM BenhNhan WHERE id=?", (id_bn,))
            return True
        except Exception as e:
            print(f"Loi xoa benh nhan: {e}")
            return False

    @staticmethod
    def search(keyword):
        try:
            rows = fetch_all(
                "SELECT * FROM BenhNhan WHERE ten LIKE ? OR sdt LIKE ?",
                (f"%{keyword}%", f"%{keyword}%"),
            )
            return [BenhNhanController._to_model(r) for r in rows]
        except Exception as e:
            print(f"Loi tim kiem benh nhan: {e}")
            return []
