from datetime import datetime

from Model.connecDB import fetch_all


class BacSiScheduleController:
    @staticmethod
    def get_bacsi_theo_lich_tuan(chuyen_khoa, calam_id, ngay_kham=None):
        thu_trong_tuan = None
        text = str(ngay_kham or "").strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                thu_trong_tuan = datetime.strptime(text, fmt).weekday()
                break
            except ValueError:
                continue
        if thu_trong_tuan is None:
            return []

        return fetch_all(
            """
            SELECT DISTINCT bs.id, bs.ten
            FROM BacSi_Moi bs
            JOIN BacSi_CaLam blt ON blt.bacsi_id = bs.id
            WHERE bs.chuyen_khoa = ?
              AND blt.calam_id = ?
              AND blt.thu_trong_tuan = ?
            """,
            (chuyen_khoa, calam_id, thu_trong_tuan),
        )
