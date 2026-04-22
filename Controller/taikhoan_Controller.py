from Model.connecDB import fetch_all
from Model.taikhoan_Model import TaiKhoan

class TaiKhoanController:
    @staticmethod
    def get_all():
        sql = "SELECT id, username, password, ho_ten, quyen FROM TaiKhoan"
        rows = fetch_all(sql)
        
        danh_sach_tk = []
        if rows:
            for row in rows:
                tk = TaiKhoan(
                    id=row.get('id'),
                    username=row.get('username'),
                    password=row.get('password'),
                    ho_ten=row.get('ho_ten'),
                    quyen=row.get('quyen')
                )
                danh_sach_tk.append(tk)
        return danh_sach_tk