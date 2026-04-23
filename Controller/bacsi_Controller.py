import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Model.connecDB import fetch_all, execute_query
from Model.bacsi_Model import BacSi


class BacSiController:

    @staticmethod
    def get_all():
        rows = fetch_all("SELECT * FROM BacSi")
        return [BacSi(r["id"], r["ten"], r["gioi_tinh"], r["chuyen_khoa"]) for r in rows]

    @staticmethod
    def insert(ten, gioi_tinh, chuyen_khoa):
        query = "INSERT INTO BacSi (ten, gioi_tinh, chuyen_khoa) VALUES (?, ?, ?)"
        execute_query(query, (ten, gioi_tinh, chuyen_khoa))

    @staticmethod
    def update(id, ten, gioi_tinh, chuyen_khoa):
        query = "UPDATE BacSi SET ten=?, gioi_tinh=?, chuyen_khoa=? WHERE id=?"
        execute_query(query, (ten, gioi_tinh, chuyen_khoa, id))

    @staticmethod
    def delete(id):
        query = "DELETE FROM BacSi WHERE id=?"
        execute_query(query, (id,))

    @staticmethod
    def search(keyword):
        query = """
        SELECT * FROM BacSi
        WHERE ten LIKE ? OR chuyen_khoa LIKE ?
        """
        rows = fetch_all(query, (f"%{keyword}%", f"%{keyword}%"))
        return [BacSi(r["id"], r["ten"], r["gioi_tinh"], r["chuyen_khoa"]) for r in rows]