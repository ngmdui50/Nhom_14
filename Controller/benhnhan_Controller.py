import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Model.connecDB import fetch_all, execute_query
from Model.benhnhan_Model import BenhNhan

class BenhNhanController:

    @staticmethod
    def get_all():
        rows = fetch_all("SELECT * FROM BenhNhan")
        return [BenhNhan(r["id"], r["ten"], r["sdt"], r["dia_chi"], r["gioi_tinh"], r["ngay_sinh"]) for r in rows]

    @staticmethod
    def insert(ten, sdt, dia_chi, gioi_tinh, ngay_sinh):
        query = "INSERT INTO BenhNhan (ten, sdt, dia_chi, gioi_tinh, ngay_sinh) VALUES (?, ?, ?, ?, ?)"
        execute_query(query, (ten, sdt, dia_chi, gioi_tinh, ngay_sinh))

    @staticmethod
    def update(id, ten, sdt, dia_chi, gioi_tinh, ngay_sinh):
        query = "UPDATE BenhNhan SET ten=?, sdt=?, dia_chi=?, gioi_tinh=?, ngay_sinh=? WHERE id=?"
        execute_query(query, (ten, sdt, dia_chi, gioi_tinh, ngay_sinh, id))

    @staticmethod
    def delete(id):
        query = "DELETE FROM BenhNhan WHERE id=?"
        execute_query(query, (id,))

    @staticmethod
    def search(keyword):
        query = """
        SELECT * FROM BenhNhan
        WHERE ten LIKE ? OR sdt LIKE ?
        """
        # Chú ý: Trả về danh sách Object BenhNhan y hệt cách làm của Bác sĩ
        rows = fetch_all(query, (f"%{keyword}%", f"%{keyword}%"))
        return [BenhNhan(r["id"], r["ten"], r["sdt"], r["dia_chi"], r["gioi_tinh"], r["ngay_sinh"]) for r in rows]