import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Model.connecDB import fetch_all, execute_query
from Model.bacsi_Model import BacSi


class BacSiController:

    @staticmethod
    def get_all():
        rows = fetch_all("SELECT * FROM BacSi_Moi")
        return [
            BacSi(r["id"], r["ten"], r["gioi_tinh"], r["chuyen_khoa"], r["calam_id"])
            for r in rows
        ]

    @staticmethod
    def insert(ten, gioi_tinh, chuyen_khoa, ca_lam):
        query = "INSERT INTO BacSi_Moi (ten, gioi_tinh, chuyen_khoa, calam_id) VALUES (?, ?, ?, ?)"
        execute_query(query, (ten, gioi_tinh, chuyen_khoa, ca_lam))

    @staticmethod
    def update(id, ten, gioi_tinh, chuyen_khoa, ca_lam):
        query = "UPDATE BacSi_Moi SET ten=?, gioi_tinh=?, chuyen_khoa=?, calam_id=? WHERE id=?"
        execute_query(query, (ten, gioi_tinh, chuyen_khoa, ca_lam, id))

    @staticmethod
    def delete(id):
        query = "DELETE FROM BacSi_Moi WHERE id=?"
        execute_query(query, (id,))

    @staticmethod
    def search(keyword):
        query = """
        SELECT * FROM BacSi_Moi
        WHERE ten LIKE ? OR chuyen_khoa LIKE ? OR calam_id LIKE ?
        """
        rows = fetch_all(query, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        return [
            BacSi(r["id"], r["ten"], r["gioi_tinh"], r["chuyen_khoa"], r["calam_id"])
            for r in rows
        ]