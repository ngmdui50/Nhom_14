import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Model.connecDB import execute_query, fetch_all
from Model.lichkham_Model import LichKham 

class LichKhamController:
    @staticmethod
    def get_all():
        rows = fetch_all("SELECT * FROM LichKham")
        # Truyền ĐẦY ĐỦ trường vào Model theo đúng thứ tự trong CSDL
        return [LichKham(
            r["id"],
            r["benhnhan_id"],
            r["bacsi_id"],
            r["phongkham_id"],  
            r["dichvu_id"],     
            r["ngay_kham"],
            r["gio_kham"],
            r["TrangThai"],
            r["calam_id"]
        ) for r in rows]

    @staticmethod
    def insert(values):
        # Đã SỬA LỖI: Thêm đủ 8 dấu %s cho 8 trường dữ liệu tương ứng
        sql = """
            INSERT INTO LichKham (benhnhan_id, bacsi_id, phongkham_id, dichvu_id, ngay_kham, gio_kham, TrangThai, calam_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        return execute_query(sql, values)

    @staticmethod
    def update(id_val, values):
        sql = """
            UPDATE LichKham 
            SET benhnhan_id=%s, bacsi_id=%s, phongkham_id=%s, dichvu_id=%s, ngay_kham=%s, gio_kham=%s, TrangThai=%s, calam_id=%s
            WHERE id=%s
        """
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

    @staticmethod
    def update_tu_form_chi_tiet(id_val, ngay, gio, trangthai):
        # Hàm này thiết kế riêng cho việc sửa nhanh trên Form Timeline
        sql = """
            UPDATE LichKham 
            SET ngay_kham=%s, gio_kham=%s, TrangThai=%s 
            WHERE id=%s
        """
        return execute_query(sql, (ngay, gio, trangthai, id_val))

    # ================= CÁC HÀM GỢI Ý THÔNG MINH =================
    
    @staticmethod
    def get_benhnhan_goi_y():
        # Đã cập nhật: Lấy TOÀN BỘ bệnh nhân thay vì chỉ lấy người chưa có lịch
        return fetch_all("SELECT id, ten FROM BenhNhan")

    @staticmethod
    def get_dichvu_goi_y():
        # Lấy tất cả dịch vụ và chuyên khoa tương ứng
        return fetch_all("SELECT id, ten_dich_vu, chuyen_khoa FROM DichVu")

    @staticmethod
    def get_bacsi_theo_loc(chuyen_khoa, calam_id):
        # Lọc bác sĩ theo chuyên khoa của dịch vụ VÀ ca làm việc
        sql = "SELECT id, ten FROM BacSi_Moi WHERE chuyen_khoa = %s AND calam_id = %s"
        return fetch_all(sql, (chuyen_khoa, calam_id))

    @staticmethod
    def get_all_bacsi_goi_y():
        # Đã thêm mới: Lấy toàn bộ bác sĩ (dùng để hiển thị tất cả nếu khoa/ca đó bị trống)
        return fetch_all("SELECT id, ten FROM BacSi_Moi")

    @staticmethod
    def get_bacsi_theo_chuyen_khoa(chuyen_khoa):
        return fetch_all("SELECT id, ten FROM BacSi_Moi WHERE chuyen_khoa = %s", (chuyen_khoa,))
    @staticmethod
    def get_phongkham_goi_y():
        # Lấy danh sách phòng khám để hiển thị lên ComboBox
        return fetch_all("SELECT id, ten_phong FROM PhongKham")
