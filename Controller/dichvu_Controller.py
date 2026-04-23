import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Model.connecDB import execute_query, fetch_all
from Model.dichvu_Model import DichVu

class DichVuController:
    @staticmethod
    def get_all():
        rows = fetch_all("SELECT * FROM DichVu")
        return [DichVu(r["id"], r["ten_dich_vu"], r["gia"]) for r in rows]
    @staticmethod
    def insert(values):
        # values = [ten_dich_vu, gia]
        sql = "INSERT INTO DichVu (ten_dich_vu, gia) VALUES (%s, %s)"
        return execute_query(sql, (values[0], values[1]))

    @staticmethod
    def update(id_val, values):
        # values = [ten_dich_vu, gia]
        sql = "UPDATE DichVu SET ten_dich_vu = %s, gia = %s WHERE id = %s"
        return execute_query(sql, (values[0], values[1], id_val))

    @staticmethod
    def delete(id_val):
        sql = "DELETE FROM DichVu WHERE id = %s"
        return execute_query(sql, (id_val,))

    @staticmethod
    def search(keyword):
        sql = "SELECT * FROM DichVu WHERE ten_dich_vu LIKE %s"
        rows = fetch_all(sql, (f"%{keyword}%",))
        return [DichVu(r["id"], r["ten_dich_vu"], r["gia"]) for r in rows]