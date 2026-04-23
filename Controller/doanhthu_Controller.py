from Model.connecDB import fetch_all, fetch_one, execute_query

class DoanhThuController:
    @staticmethod

    def get_all():
        # Sửa lại tên bảng (DoanhThu) và tên cột cho khớp với CSDL SQL của bạn
        sql = "SELECT id, lichkham_id, tong_tien, ngay_thanh_toan, TenBenhNhan FROM DoanhThu"
        
        try:
            result = fetch_all(sql) # Hàm này sẽ trả về list các dict hoặc object
            return result if result else []
        except Exception as e:
            print(f"Lỗi truy vấn danh sách doanh thu: {e}")
            return []
    @staticmethod
    def insert(lichkham_id, tong_tien, ngay, ten_bn):
        sql = "INSERT INTO DoanhThu (lichkham_id, tong_tien, ngay_thanh_toan, TenBenhNhan) VALUES (%s, %s, %s, %s)"
        return execute_query(sql, (lichkham_id, tong_tien, ngay, ten_bn))

    @staticmethod
    def update(id_val, tong_tien, ngay):
        sql = "UPDATE DoanhThu SET tong_tien = %s, ngay_thanh_toan = %s WHERE id = %s"
        return execute_query(sql, (tong_tien, ngay, id_val))

    @staticmethod
    def delete(id_val):
        sql = "DELETE FROM DoanhThu WHERE id = %s"
        return execute_query(sql, (id_val,))

    @staticmethod
    def search(keyword):
        sql = "SELECT * FROM DoanhThu WHERE TenBenhNhan LIKE %s OR lichkham_id LIKE %s"
        return fetch_all(sql, (f"%{keyword}%", f"%{keyword}%"))