import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Model.connecDB import execute_query, fetch_all
from Model.dichvu_Model import DichVu

class DichVuController:
    @staticmethod
    def get_all():
        rows = fetch_all("SELECT * FROM DichVu")
        return [DichVu(r["id"], r["ten_dich_vu"], r["gia"], r["chuyen_khoa"]) for r in rows]
    @staticmethod
    def insert(values):
        chuyen_khoa = values[2] if len(values) > 2 else ""
        sql = "INSERT INTO DichVu (ten_dich_vu, gia, chuyen_khoa) VALUES (%s, %s, %s)"
        return execute_query(sql, (values[0], values[1], chuyen_khoa))

    @staticmethod
    def update(id_val, values):
        chuyen_khoa = values[2] if len(values) > 2 else ""
        sql = "UPDATE DichVu SET ten_dich_vu = %s, gia = %s, chuyen_khoa=%s WHERE id = %s"
        return execute_query(sql, (values[0], values[1], chuyen_khoa, id_val))

    @staticmethod
    def delete(id_val):
        sql = "DELETE FROM DichVu WHERE id = %s"
        return execute_query(sql, (id_val,))

    @staticmethod
    def search(keyword):
        sql = "SELECT * FROM DichVu WHERE ten_dich_vu LIKE %s OR chuyen_khoa LIKE %s"
        rows = fetch_all(sql, (f"%{keyword}%", f"%{keyword}%"))
        return [DichVu(r["id"], r["ten_dich_vu"], r["gia"], r["chuyen_khoa"]) for r in rows]
