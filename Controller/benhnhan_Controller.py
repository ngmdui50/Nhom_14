import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Model.connecDB import fetch_all, execute_query
from Model.benhnhan_Model import BenhNhan

class BenhNhanController:

    @staticmethod
    def get_all():
        try:
            rows = fetch_all("SELECT * FROM BenhNhan")
            return [BenhNhan(r["id"], r["ten"], r["sdt"], r["dia_chi"], r["gioi_tinh"], r["ngay_sinh"]) for r in rows]
        except Exception as e:
            print(f"Lỗi lấy danh sách bệnh nhân: {e}")
            return []

    @staticmethod
    def insert(ten, sdt, dia_chi, gioi_tinh, ngay_sinh):
        try:
            query = "INSERT INTO BenhNhan (ten, sdt, dia_chi, gioi_tinh, ngay_sinh) VALUES (?, ?, ?, ?, ?)"
            execute_query(query, (ten, sdt, dia_chi, gioi_tinh, ngay_sinh))
            return True
        except Exception as e:
            print(f"Lỗi thêm bệnh nhân: {e}")
            return False

    @staticmethod
    def update(id_bn, ten, sdt, dia_chi, gioi_tinh, ngay_sinh):
        try:
            query = "UPDATE BenhNhan SET ten=?, sdt=?, dia_chi=?, gioi_tinh=?, ngay_sinh=? WHERE id=?"
            execute_query(query, (ten, sdt, dia_chi, gioi_tinh, ngay_sinh, id_bn))
            return True
        except Exception as e:
            print(f"Lỗi cập nhật bệnh nhân: {e}")
            return False

    @staticmethod
    def delete(id_bn):
        try:
            query = "DELETE FROM BenhNhan WHERE id=?"
            execute_query(query, (id_bn,))
            return True
        except Exception as e:
            print(f"Lỗi xóa bệnh nhân: {e}")
            return False

    @staticmethod
    def search(keyword):
        """Tìm kiếm bệnh nhân theo tên hoặc số điện thoại"""
        try:
            query = "SELECT * FROM BenhNhan WHERE ten LIKE ? OR sdt LIKE ?"
            params = (f"%{keyword}%", f"%{keyword}%")
            rows = fetch_all(query, params)
            return [BenhNhan(r["id"], r["ten"], r["sdt"], r["dia_chi"], r["gioi_tinh"], r["ngay_sinh"]) for r in rows]
        except Exception as e:
            print(f"Lỗi tìm kiếm: {e}")
            return []