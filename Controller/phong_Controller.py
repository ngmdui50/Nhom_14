import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Model.connecDB import execute_query, fetch_all
from Model.phong_Model import PhongKham

class PhongKhamController:
    @staticmethod
    def get_all():
        rows = fetch_all("SELECT * FROM PhongKham")
        return [PhongKham(r["id"], r["ten_phong"], r["so_giuong"], r["mo_ta"]) for r in rows]
    @staticmethod
    def insert(values):
        # values = [ten_phong, so_giuong, mo_ta]
        sql = "INSERT INTO PhongKham (ten_phong, so_giuong, mo_ta) VALUES (?, ?, ?)"
        return execute_query(sql, values)

    @staticmethod
    def update(id_val, values):
        # values = [ten_phong, so_giuong, mo_ta]
        sql = "UPDATE PhongKham SET ten_phong = ?, so_giuong = ?, mo_ta = ? WHERE id = ?"
        return execute_query(sql, (*values, id_val))

    @staticmethod
    def delete(id_val):
        sql = "DELETE FROM PhongKham WHERE id = ?"
        return execute_query(sql, (id_val,))

    @staticmethod
    def search(keyword):
        sql = "SELECT * FROM PhongKham WHERE ten_phong LIKE ? OR mo_ta LIKE ?"
        rows = fetch_all(sql, (f"%{keyword}%", f"%{keyword}%"))
        return [PhongKham(r["id"], r["ten_phong"], r["so_giuong"], r["mo_ta"]) for r in rows]