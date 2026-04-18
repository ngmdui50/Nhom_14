from Model.connecDB import fetch_all, execute_query
from Model.benhnhan_Model import BenhNhan

class BenhNhanController:
    @staticmethod
    def get_all():
        """Lấy toàn bộ danh sách bệnh nhân từ database"""
        rows = fetch_all("SELECT * FROM BenhNhan")
        return [
            BenhNhan(
                r["id"], 
                r["ten"], 
                r["sdt"], 
                r["dia_chi"], 
                r["gioi_tinh"], 
                r["ngay_sinh"]
            )
            for r in rows
        ]

    @staticmethod
    def insert(bn: BenhNhan):
        """Thêm bệnh nhân mới (chuẩn bị cho chức năng Thêm)"""
        execute_query("""
            INSERT INTO BenhNhan (ten, sdt, dia_chi, gioi_tinh, ngay_sinh)
            VALUES (?, ?, ?, ?, ?)
        """, (bn.ten, bn.sdt, bn.dia_chi, bn.gioi_tinh, bn.ngay_sinh))