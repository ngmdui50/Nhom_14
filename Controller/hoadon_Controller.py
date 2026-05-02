from Model.connecDB import fetch_all, fetch_one, execute_query

class HoaDonController:
    @staticmethod
    def get_all():
        # Đảm bảo các cột này KHỚP Y HỆT trong SQL của bạn
        sql = "SELECT id, lichkham_id, tong_tien, ngay_thanh_toan, TenBenhNhan FROM HoaDon"
        try:
            result = fetch_all(sql)
            return result if result else []
        except Exception as e:
            print(f"Lỗi truy vấn danh sách doanh thu: {e}")
            return []

    @staticmethod
    def insert(lichkham_id, tong_tien, ngay, ten_bn):
        # Nếu cột tự tăng (AUTO_INCREMENT), không cần chèn id
        sql = "INSERT INTO HoaDon (lichkham_id, tong_tien, ngay_thanh_toan, TenBenhNhan) VALUES (%s, %s, %s, %s)"
        return execute_query(sql, (lichkham_id, tong_tien, ngay, ten_bn))

    @staticmethod
    def update(id_val, tong_tien, ngay):
        # Kiểm tra xem tên cột 'id' có đúng không
        sql = "UPDATE HoaDon SET tong_tien = %s, ngay_thanh_toan = %s WHERE id = %s"
        return execute_query(sql, (tong_tien, ngay, int(id_val))) # ÉP KIỂU INT

    @staticmethod
    def delete(id_val):
        # LƯU Ý: Đổi chữ 'id' thành tên cột khóa chính thực tế trong DB của bạn nếu nó khác
        sql = "DELETE FROM HoaDon WHERE id = %s"
        # Ép kiểu int(id_val) để đảm bảo SQL hiểu đây là số
        return execute_query(sql, (int(id_val),)) 

    @staticmethod
    def search(keyword):
        sql = "SELECT * FROM HoaDon WHERE TenBenhNhan LIKE %s OR lichkham_id LIKE %s"
        return fetch_all(sql, (f"%{keyword}%", f"%{keyword}%"))
    @staticmethod
    def get_thong_tin_tu_lich_kham(lichkham_id):
        # Kết nối 3 bảng để lấy Tên Bệnh Nhân và Giá Tiền Dịch Vụ
        # LƯU Ý: Hãy sửa 'ho_ten' và 'gia_tien' thành tên cột đúng trong CSDL của bạn
        sql = """
            SELECT 
                BN.ten AS TenBenhNhan, 
                DV.gia AS TongTien
            FROM LichKham LK
            JOIN BenhNhan BN ON LK.benhnhan_id = BN.id
            JOIN DichVu DV ON LK.dichvu_id = DV.id
            WHERE LK.id = %s
        """
        try:
            return fetch_one(sql, (lichkham_id,))
        except Exception as e:
            print(f"Lỗi truy vấn thông tin lịch khám: {e}")
            return None