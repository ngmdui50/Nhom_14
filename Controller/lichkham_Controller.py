import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Model.connecDB import execute_query, fetch_all
# Lưu ý: Chỉnh lại đường dẫn import Model nếu file này là Controller
from Model.lichkham_Model import LichKham 

class LichKhamController:
    @staticmethod
    def get_all():
        rows = fetch_all("SELECT * FROM LichKham")
        # Truyền ĐẦY ĐỦ 7 trường vào Model theo đúng thứ tự trong CSDL
        return [LichKham(
            r["id"],
            r["benhnhan_id"],
            r["bacsi_id"],
            r["phongkham_id"],  # Bổ sung cột Phòng Khám
            r["dichvu_id"],     # Bổ sung cột Dịch Vụ
            r["ngay_kham"],
            r["gio_kham"],
            r["TrangThai"]
        ) for r in rows]
    @staticmethod
    def insert(values):
        # values: [id_bn, id_bs, ngay, gio, trang_thai] 
        # Lưu ý: Bạn cần bổ sung ID Phòng và ID Dịch vụ nếu DB yêu cầu NOT NULL
        sql = "INSERT INTO LichKham (benhnhan_id, bacsi_id, ngay_kham, gio_kham, TrangThai) VALUES (?, ?, ?, ?, ?)"
        return execute_query(sql, values)

    @staticmethod
    def update(id_val, values):
        sql = "UPDATE LichKham SET benhnhan_id=?, bacsi_id=?, ngay_kham=?, gio_kham=?, TrangThai=? WHERE id=?"
        return execute_query(sql, (*values, id_val))

    @staticmethod
    def delete(id_val):
        sql = "DELETE FROM LichKham WHERE id = ?"
        return execute_query(sql, (id_val,))

    @staticmethod
    def search(keyword):
        # Tìm kiếm theo ID Bệnh nhân hoặc ID Bác sĩ (hoặc tên nếu bạn join bảng)
        sql = "SELECT * FROM LichKham WHERE benhnhan_id LIKE %s OR bacsi_id LIKE %s"
        return fetch_all(sql, (f"%{keyword}%", f"%{keyword}%"))