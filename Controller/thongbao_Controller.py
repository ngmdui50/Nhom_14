from Model.connecDB import execute_query, fetch_all, get_connection


class ThongBaoController:
    @staticmethod
    def _execute_non_strict(query, params=()):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query.replace("%s", "?"), params)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    @staticmethod
    def ensure_table():
        execute_query(
            """
            CREATE TABLE IF NOT EXISTS ThongBao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                taikhoan_id INTEGER,
                tieu_de TEXT NOT NULL,
                noi_dung TEXT NOT NULL,
                loai TEXT,
                da_doc INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

    @staticmethod
    def insert(taikhoan_id, tieu_de, noi_dung, loai="lich_kham_moi"):
        ThongBaoController.ensure_table()
        return execute_query(
            """
            INSERT INTO ThongBao (taikhoan_id, tieu_de, noi_dung, loai, da_doc)
            VALUES (?, ?, ?, ?, 0)
            """,
            (taikhoan_id, tieu_de, noi_dung, loai),
        )

    @staticmethod
    def get_chua_doc(taikhoan_id):
        ThongBaoController.ensure_table()
        return fetch_all(
            """
            SELECT id, tieu_de, noi_dung, loai, da_doc, created_at
            FROM ThongBao
            WHERE taikhoan_id = ? AND da_doc = 0
            ORDER BY id DESC
            """,
            (taikhoan_id,),
        )

    @staticmethod
    def mark_as_read(thongbao_id):
        ThongBaoController.ensure_table()
        return ThongBaoController._execute_non_strict(
            "UPDATE ThongBao SET da_doc = 1 WHERE id = ?",
            (thongbao_id,),
        )

    @staticmethod
    def mark_all_as_read(taikhoan_id):
        ThongBaoController.ensure_table()
        return ThongBaoController._execute_non_strict(
            "UPDATE ThongBao SET da_doc = 1 WHERE taikhoan_id = ?",
            (taikhoan_id,),
        )
