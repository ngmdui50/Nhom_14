from Model.connecDB import fetch_all

class ThongKeController:
    @staticmethod
    def thong_ke_doanh_thu_dich_vu():
        # Thống kê tổng tiền theo từng loại dịch vụ
        sql = """
            SELECT dv.ten_dich_vu, COUNT(lk.id) as so_luong, SUM(dv.gia) as tong_tien
            FROM LichKham lk
            JOIN DichVu dv ON lk.dichvu_id = dv.id
            GROUP BY dv.ten_dich_vu
        """
        return fetch_all(sql)

    @staticmethod
    def thong_ke_luot_kham_theo_ngay():
        # Thống kê số ca khám của mỗi bác sĩ
        sql = """
            SELECT lk.ngay_kham, bs.ten_bac_si, bn.ten_benh_nhan, lk.gio_kham
            FROM LichKham lk
            JOIN BacSi bs ON lk.bacsi_id = bs.id
            JOIN BenhNhan bn ON lk.benhnhan_id = bn.id
            ORDER BY lk.ngay_kham DESC
        """
        return fetch_all(sql)
    @staticmethod
    def thong_ke_theo_thang(thang, nam):
        """Lọc dữ liệu thống kê theo tháng cụ thể"""
        sql = """
            SELECT lk.ngay_kham, bs.ten_bac_si, bn.ten_benh_nhan, lk.TrangThai
            FROM LichKham lk
            JOIN BacSi bs ON lk.bacsi_id = bs.id
            JOIN BenhNhan bn ON lk.benhnhan_id = bn.id
            WHERE MONTH(lk.ngay_kham) = %s AND YEAR(lk.ngay_kham) = %s
        """
        return fetch_all(sql, (thang, nam))