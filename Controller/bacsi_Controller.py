import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Model.connecDB import fetch_all, execute_query
from Model.bacsi_Model import BacSi


class BacSiController:
    WEEKDAY_LABELS = {
        0: "T2",
        1: "T3",
        2: "T4",
        3: "T5",
        4: "T6",
        5: "T7",
        6: "CN",
    }

    @staticmethod
    def ensure_weekly_schedule_table():
        table_rows = fetch_all(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='BacSi_CaLam'"
        )
        if not table_rows:
            execute_query(
                """
                CREATE TABLE IF NOT EXISTS BacSi_CaLam (
                    bacsi_id INTEGER NOT NULL,
                    thu_trong_tuan INTEGER NOT NULL DEFAULT -1,
                    calam_id INTEGER NOT NULL,
                    PRIMARY KEY (bacsi_id, thu_trong_tuan, calam_id),
                    FOREIGN KEY (bacsi_id) REFERENCES BacSi_Moi(id) ON DELETE CASCADE,
                    FOREIGN KEY (calam_id) REFERENCES CaLam(id) ON DELETE CASCADE
                )
                """
            )
            return

        columns = fetch_all("PRAGMA table_info(BacSi_CaLam)")
        has_weekday = any(str(col.get("name", "")) == "thu_trong_tuan" for col in columns)
        if not has_weekday:
            execute_query(
                """
                CREATE TABLE IF NOT EXISTS BacSi_CaLam_new (
                    bacsi_id INTEGER NOT NULL,
                    thu_trong_tuan INTEGER NOT NULL DEFAULT -1,
                    calam_id INTEGER NOT NULL,
                    PRIMARY KEY (bacsi_id, thu_trong_tuan, calam_id),
                    FOREIGN KEY (bacsi_id) REFERENCES BacSi_Moi(id) ON DELETE CASCADE,
                    FOREIGN KEY (calam_id) REFERENCES CaLam(id) ON DELETE CASCADE
                )
                """
            )
            execute_query(
                """
                INSERT OR IGNORE INTO BacSi_CaLam_new (bacsi_id, thu_trong_tuan, calam_id)
                SELECT bacsi_id, -1, calam_id
                FROM BacSi_CaLam
                """
            )
            legacy_weekly_table = fetch_all(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='BacSi_LichTuan'"
            )
            if legacy_weekly_table:
                execute_query(
                    """
                    INSERT OR IGNORE INTO BacSi_CaLam_new (bacsi_id, thu_trong_tuan, calam_id)
                    SELECT bacsi_id, thu_trong_tuan, calam_id
                    FROM BacSi_LichTuan
                    """
                )
            execute_query("DROP TABLE BacSi_CaLam")
            execute_query("ALTER TABLE BacSi_CaLam_new RENAME TO BacSi_CaLam")

        legacy_weekly_table = fetch_all(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='BacSi_LichTuan'"
        )
        if legacy_weekly_table:
            execute_query("DROP TABLE BacSi_LichTuan")

    @staticmethod
    def _to_model(rows):
        return [
            BacSi(
                r["id"],
                r["ten"],
                r["gioi_tinh"],
                r["chuyen_khoa"],
                r.get("lich_tuan_hien_thi", r.get("calam_id", ""))
            )
            for r in rows
        ]

    @staticmethod
    def _normalize_schedule_map(schedule_map):
        normalized = {}
        for thu, ca_id in (schedule_map or {}).items():
            if ca_id in (None, "", "None"):
                continue
            normalized[int(thu)] = int(ca_id)
        return normalized

    @staticmethod
    def get_legacy_ca_ids(bacsi_id):
        BacSiController.ensure_weekly_schedule_table()
        rows = fetch_all(
            """
            SELECT DISTINCT calam_id
            FROM BacSi_CaLam
            WHERE bacsi_id = ? AND thu_trong_tuan = -1
            ORDER BY calam_id
            """,
            (bacsi_id,),
        )
        return [int(r["calam_id"]) for r in rows if r.get("calam_id") is not None]

    @staticmethod
    def get_schedule_map(bacsi_id):
        BacSiController.ensure_weekly_schedule_table()
        rows = fetch_all(
            """
            SELECT thu_trong_tuan, MIN(calam_id) AS calam_id
            FROM BacSi_CaLam
            WHERE bacsi_id = ?
              AND thu_trong_tuan >= 0
            GROUP BY thu_trong_tuan
            ORDER BY thu_trong_tuan
            """,
            (bacsi_id,),
        )
        return {
            int(r["thu_trong_tuan"]): int(r["calam_id"])
            for r in rows
            if r.get("thu_trong_tuan") is not None and r.get("calam_id") is not None
        }

    @staticmethod
    def get_full_schedule_map(bacsi_id):
        schedule_map = BacSiController.get_schedule_map(bacsi_id)
        if schedule_map:
            return schedule_map

        legacy_ids = BacSiController.get_legacy_ca_ids(bacsi_id)
        if not legacy_ids:
            return {}

        full_schedule = {}
        for thu in range(7):
            full_schedule[thu] = legacy_ids[thu % len(legacy_ids)]
        return full_schedule

    @staticmethod
    def save_weekly_schedule(bacsi_id, schedule_map):
        BacSiController.ensure_weekly_schedule_table()
        execute_query("DELETE FROM BacSi_CaLam WHERE bacsi_id = ?", (bacsi_id,))
        normalized = BacSiController._normalize_schedule_map(schedule_map)
        for thu, ca_id in normalized.items():
            execute_query(
                "INSERT OR REPLACE INTO BacSi_CaLam (bacsi_id, thu_trong_tuan, calam_id) VALUES (?, ?, ?)",
                (bacsi_id, thu, ca_id),
            )
        return normalized

    @staticmethod
    def format_schedule_display(schedule_map=None, legacy_ca_ids=None):
        schedule_map = BacSiController._normalize_schedule_map(schedule_map)
        legacy_ca_ids = [int(ca) for ca in (legacy_ca_ids or []) if str(ca).strip()]
        if schedule_map:
            parts = []
            for thu in range(7):
                if thu not in schedule_map:
                    continue
                parts.append(f"{BacSiController.WEEKDAY_LABELS.get(thu, thu)}: Ca {schedule_map[thu]}")
            return " | ".join(parts)
        if legacy_ca_ids:
            if len(legacy_ca_ids) == 1:
                return f"Mac dinh tat ca ngay: Ca {legacy_ca_ids[0]}"
            return "Mac dinh: " + ", ".join(f"Ca {ca}" for ca in legacy_ca_ids)
        return "Chua xep lich"

    @staticmethod
    def get_all():
        BacSiController.ensure_weekly_schedule_table()
        rows = fetch_all("""
            SELECT
                bs.id,
                bs.ten,
                bs.gioi_tinh,
                bs.chuyen_khoa,
                COALESCE(GROUP_CONCAT(bcl.calam_id), '') AS calam_id
            FROM BacSi_Moi bs
            LEFT JOIN BacSi_CaLam bcl ON bcl.bacsi_id = bs.id
            GROUP BY bs.id, bs.ten, bs.gioi_tinh, bs.chuyen_khoa
        """)
        for r in rows:
            legacy_ids = [int(x) for x in str(r.get("calam_id", "") or "").split(",") if str(x).strip().isdigit()]
            r["lich_tuan_hien_thi"] = BacSiController.format_schedule_display(
                BacSiController.get_schedule_map(r["id"]),
                legacy_ids,
            )
        return BacSiController._to_model(rows)

    @staticmethod
    def insert(ten, gioi_tinh, chuyen_khoa, ca_lam=None, schedule_map=None):
        BacSiController.ensure_weekly_schedule_table()
        query = "INSERT INTO BacSi_Moi (ten, gioi_tinh, chuyen_khoa) VALUES (?, ?, ?)"
        execute_query(query, (ten, gioi_tinh, chuyen_khoa))
        row = fetch_all("SELECT id FROM BacSi_Moi ORDER BY id DESC LIMIT 1")
        if not row:
            return

        bacsi_id = row[0]["id"]
        normalized_schedule = BacSiController.save_weekly_schedule(bacsi_id, schedule_map)
        if not normalized_schedule:
            ca_ids = [ca_lam] if ca_lam else [ca["id"] for ca in fetch_all("SELECT id FROM CaLam")]
            for ca_id in ca_ids:
                execute_query(
                    "INSERT OR IGNORE INTO BacSi_CaLam (bacsi_id, thu_trong_tuan, calam_id) VALUES (?, ?, ?)",
                    (bacsi_id, -1, ca_id)
                )
        return bacsi_id

    @staticmethod
    def update(id, ten, gioi_tinh, chuyen_khoa, ca_lam=None, schedule_map=None):
        BacSiController.ensure_weekly_schedule_table()
        query = "UPDATE BacSi_Moi SET ten=?, gioi_tinh=?, chuyen_khoa=? WHERE id=?"
        execute_query(query, (ten, gioi_tinh, chuyen_khoa, id))
        normalized_schedule = BacSiController.save_weekly_schedule(id, schedule_map)
        if not normalized_schedule and ca_lam:
            execute_query("DELETE FROM BacSi_CaLam WHERE bacsi_id=?", (id,))
            ca_ids = [ca_lam]
            for ca_id in ca_ids:
                execute_query(
                    "INSERT OR IGNORE INTO BacSi_CaLam (bacsi_id, thu_trong_tuan, calam_id) VALUES (?, ?, ?)",
                    (id, -1, ca_id)
                )

    @staticmethod
    def delete(id):
        BacSiController.ensure_weekly_schedule_table()
        execute_query("DELETE FROM BacSi_CaLam WHERE bacsi_id=?", (id,))
        query = "DELETE FROM BacSi_Moi WHERE id=?"
        execute_query(query, (id,))

    @staticmethod
    def search(keyword):
        BacSiController.ensure_weekly_schedule_table()
        query = """
            SELECT
                bs.id,
                bs.ten,
                bs.gioi_tinh,
                bs.chuyen_khoa,
                COALESCE(GROUP_CONCAT(bcl.calam_id), '') AS calam_id
            FROM BacSi_Moi bs
            LEFT JOIN BacSi_CaLam bcl ON bcl.bacsi_id = bs.id
            WHERE bs.ten LIKE ? OR bs.chuyen_khoa LIKE ? OR bcl.calam_id LIKE ?
            GROUP BY bs.id, bs.ten, bs.gioi_tinh, bs.chuyen_khoa
        """
        rows = fetch_all(query, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        for r in rows:
            legacy_ids = [int(x) for x in str(r.get("calam_id", "") or "").split(",") if str(x).strip().isdigit()]
            r["lich_tuan_hien_thi"] = BacSiController.format_schedule_display(
                BacSiController.get_schedule_map(r["id"]),
                legacy_ids,
            )
        return BacSiController._to_model(rows)
