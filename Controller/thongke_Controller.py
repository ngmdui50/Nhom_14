from Model.connecDB import fetch_all
from datetime import datetime

class ThongKeController:
    @staticmethod
    def thong_ke_doanh_thu_dich_vu(thang=None, nam=None):
        sql = """
            SELECT dv.ten_dich_vu, COUNT(lk.id) as so_luong, SUM(dv.gia) as tong_tien
            FROM LichKham lk
            JOIN DichVu dv ON lk.dichvu_id = dv.id
        """
        params = ()
        # Nếu người dùng chọn lọc theo tháng cụ thể
        if thang and nam:
            sql += " WHERE strftime('%m', lk.ngay_kham) = %s AND strftime('%Y', lk.ngay_kham) = %s "
            params = (str(thang).zfill(2), str(nam))
            
        sql += " GROUP BY dv.ten_dich_vu"
        return fetch_all(sql, params)

    @staticmethod
    def thong_ke_luot_kham_tong_hop(thang=None, nam=None):
        sql = """
            SELECT
                lk.ngay_kham,
                bs.ten AS ten_bac_si,
                bn.ten AS ten_benh_nhan,
                lk.gio_kham,
                lk.TrangThai AS trang_thai
            FROM LichKham lk
            JOIN BacSi bs ON lk.bacsi_id = bs.id
            JOIN BenhNhan bn ON lk.benhnhan_id = bn.id
        """
        params = ()
        # Nếu người dùng chọn lọc theo tháng cụ thể
        if thang and nam:
            sql += " WHERE strftime('%m', lk.ngay_kham) = %s AND strftime('%Y', lk.ngay_kham) = %s "
            params = (str(thang).zfill(2), str(nam))
            
        sql += " ORDER BY lk.ngay_kham DESC"
        return fetch_all(sql, params)
