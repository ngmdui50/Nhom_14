class LichKham:
    # Khai báo đủ 7 tham số
    def __init__(self, id, benhnhan_id, bacsi_id, phongkham_id, dichvu_id, ngay_kham, gio_kham, TrangThai):
        self.id = id
        self.benhnhan_id = benhnhan_id
        self.bacsi_id = bacsi_id
        self.phongkham_id = phongkham_id  # Thêm dòng này
        self.dichvu_id = dichvu_id        # Thêm dòng này
        self.ngay_kham = ngay_kham
        self.gio_kham = gio_kham
        self.trang_thai = TrangThai