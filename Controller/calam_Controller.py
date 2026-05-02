from Model.connecDB import execute_query, fetch_all
from Model.calam_Model import CaLam  # Nhớ import Model

class CaLamController:
    @staticmethod
    def get_all():
        # Lấy dữ liệu với tên cột chuẩn từ DB
        rows = fetch_all("SELECT id, ten_ca, gio_bat_dau, gio_ket_thuc FROM CaLam")
        
        # Đổ vào Model
        return [CaLam(
            r["id"], 
            r["ten_ca"], 
            r["gio_bat_dau"], 
            r["gio_ket_thuc"]
        ) for r in rows]

    # Cập nhật luôn các hàm Insert/Update cho đúng tên cột nhé:
    @staticmethod
    def insert(ten, bat_dau, ket_thuc):
        sql = "INSERT INTO CaLam (ten_ca, gio_bat_dau, gio_ket_thuc) VALUES (%s, %s, %s)"
        return execute_query(sql, (ten, bat_dau, ket_thuc))

    @staticmethod
    def update(id_val, ten, bat_dau, ket_thuc):
        sql = "UPDATE CaLam SET ten_ca=%s, gio_bat_dau=%s, gio_ket_thuc=%s WHERE id=%s"
        return execute_query(sql, (ten, bat_dau, ket_thuc, id_val))

    @staticmethod
    def delete(id_val):
        return execute_query("DELETE FROM CaLam WHERE id = %s", (id_val,))