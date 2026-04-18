class DoanhThu:
    def __init__(self, id, lichkham_id, tong_tien, ngay_thanh_toan, TenBenhNhan):
        self.id = id
        self.lichkham_id = lichkham_id
        self.tong_tien = tong_tien
        self.ngay_thanh_toan = ngay_thanh_toan
        self.TenBenhNhan = TenBenhNhan

    def get_formatted_money(self):
        """Hàm hỗ trợ hiển thị tiền đẹp: 1,000,000 VNĐ"""
        return f"{self.tong_tien:,.0f} VNĐ"