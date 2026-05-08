import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Model.connecDB import fetch_all, execute_query
from Model.bacsi_Model import BacSi


class BacSiController:
    @staticmethod
    def _to_model(rows):
        return [
            BacSi(
                r["id"],
                r["ten"],
                r["gioi_tinh"],
                r["chuyen_khoa"],
                r.get("calam_id", "")
            )
            for r in rows
        ]

    @staticmethod
    def get_all():
        rows = fetch_all("""
            SELECT
                bs.id,
                bs.ten,
                bs.gioi_tinh,
                bs.chuyen_khoa,
                COALESCE(GROUP_CONCAT(bcl.calam_id), '') AS calam_id
            FROM BacSi_Moi bs
            LEFT JOIN BacSi_CaLam bcl ON bcl.bacsi_id = bs.id
            GROUP BY bs.id, bs.ten, bs.gioi_tinh, bs.chuyen_khoa
        """)
        return BacSiController._to_model(rows)

    @staticmethod
    def insert(ten, gioi_tinh, chuyen_khoa, ca_lam=None):
        query = "INSERT INTO BacSi_Moi (ten, gioi_tinh, chuyen_khoa) VALUES (?, ?, ?)"
        execute_query(query, (ten, gioi_tinh, chuyen_khoa))
        row = fetch_all("SELECT id FROM BacSi_Moi ORDER BY id DESC LIMIT 1")
        if not row:
            return

        bacsi_id = row[0]["id"]
        ca_ids = [ca_lam] if ca_lam else [ca["id"] for ca in fetch_all("SELECT id FROM CaLam")]
        for ca_id in ca_ids:
            execute_query(
                "INSERT OR IGNORE INTO BacSi_CaLam (bacsi_id, calam_id) VALUES (?, ?)",
                (bacsi_id, ca_id)
            )

    @staticmethod
    def update(id, ten, gioi_tinh, chuyen_khoa, ca_lam=None):
        query = "UPDATE BacSi_Moi SET ten=?, gioi_tinh=?, chuyen_khoa=? WHERE id=?"
        execute_query(query, (ten, gioi_tinh, chuyen_khoa, id))
        if ca_lam:
            execute_query("DELETE FROM BacSi_CaLam WHERE bacsi_id=?", (id,))
            execute_query(
                "INSERT OR IGNORE INTO BacSi_CaLam (bacsi_id, calam_id) VALUES (?, ?)",
                (id, ca_lam)
            )

    @staticmethod
    def delete(id):
        execute_query("DELETE FROM BacSi_CaLam WHERE bacsi_id=?", (id,))
        query = "DELETE FROM BacSi_Moi WHERE id=?"
        execute_query(query, (id,))

    @staticmethod
    def search(keyword):
        query = """
            SELECT
                bs.id,
                bs.ten,
                bs.gioi_tinh,
                bs.chuyen_khoa,
                COALESCE(GROUP_CONCAT(bcl.calam_id), '') AS calam_id
            FROM BacSi_Moi bs
            LEFT JOIN BacSi_CaLam bcl ON bcl.bacsi_id = bs.id
            WHERE bs.ten LIKE ? OR bs.chuyen_khoa LIKE ? OR bcl.calam_id LIKE ?
            GROUP BY bs.id, bs.ten, bs.gioi_tinh, bs.chuyen_khoa
        """
        rows = fetch_all(query, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        return BacSiController._to_model(rows)
