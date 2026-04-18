import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Model.connecDB import fetch_all
from Model.dichvu_Model import DichVu

class DichVuController:
    @staticmethod
    def get_all():
        rows = fetch_all("SELECT * FROM DichVu")
        return [DichVu(r["id"], r["ten_dich_vu"], r["gia"]) for r in rows]