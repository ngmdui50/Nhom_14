import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Model.connecDB import fetch_all
from Model.phong_Model import PhongKham

class PhongKhamController:
    @staticmethod
    def get_all():
        rows = fetch_all("SELECT * FROM PhongKham")
        return [PhongKham(r["id"], r["ten_phong"], r["so_giuong"], r["mo_ta"]) for r in rows]