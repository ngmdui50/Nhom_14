import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Model.connecDB import fetch_all
from Model.bacsi_Model import BacSi

class BacSiController:
    @staticmethod
    def get_all():
        rows = fetch_all("SELECT * FROM BacSi")
        return [BacSi(r["id"], r["ten"], r["gioi_tinh"], r["chuyen_khoa"]) for r in rows]