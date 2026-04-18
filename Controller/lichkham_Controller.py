import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Model.connecDB import fetch_all
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
