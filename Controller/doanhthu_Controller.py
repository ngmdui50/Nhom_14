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

    def xu_ly_thanh_toan(id_lich_kham):
        sql = """
            SELECT DichVu.DonGia 
            FROM LichKham 
            JOIN DichVu ON LichKham.dichvu_id = DichVu.id 
            WHERE LichKham.id = ?
        """
        result = fetch_one(sql, (id_lich_kham,))
        
        if result:
            gia_tien = result['DonGia']
            
            # 2. Lưu vào bảng DoanhThu
            sql_insert = "INSERT INTO DoanhThu (lichkham_id, tong_tien) VALUES (?, ?)"
            execute_query(sql_insert, (id_lich_kham, gia_tien))
            return True
        return False