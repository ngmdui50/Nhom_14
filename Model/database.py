import sqlite3

def create_tables():
    conn = sqlite3.connect("CSDLBTL.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # ===== BẢNG BỆNH NHÂN =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS BenhNhan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ten TEXT NOT NULL,
            sdt TEXT,
            dia_chi TEXT,
            gioi_tinh TEXT,
            ngay_sinh TEXT
        )
    """)

    # ===== BẢNG BÁC SĨ =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS BacSi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ten TEXT NOT NULL,
            gioi_tinh TEXT,
            chuyen_khoa TEXT
        )
    """)

    # ===== BẢNG DỊCH VỤ =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS DichVu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ten_dich_vu TEXT NOT NULL,
            gia REAL
        )
    """)

    # ===== BẢNG PHÒNG KHÁM =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS PhongKham (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ten_phong TEXT NOT NULL,
            so_giuong INTEGER,
            mo_ta TEXT
        )
    """)

    # ===== BẢNG LỊCH KHÁM =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS LichKham (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            benhnhan_id INTEGER,
            bacsi_id INTEGER,
            phongkham_id INTEGER,
            dichvu_id INTEGER,
            ngay_kham TEXT,
            gio_kham TEXT,

            FOREIGN KEY (benhnhan_id) REFERENCES BenhNhan(id) ON DELETE CASCADE,
            FOREIGN KEY (bacsi_id) REFERENCES BacSi(id) ON DELETE CASCADE,
            FOREIGN KEY (phongkham_id) REFERENCES PhongKham(id) ON DELETE CASCADE,
            FOREIGN KEY (dichvu_id) REFERENCES DichVu(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


    print(" Đã tạo đầy đủ các bảng!")
def insert_sample_data():
    conn = sqlite3.connect("CSDLBTL.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # ===== XÓA DỮ LIỆU CŨ (tránh trùng) =====
    cursor.execute("DELETE FROM LichKham")
    cursor.execute("DELETE FROM BenhNhan")
    cursor.execute("DELETE FROM BacSi")
    cursor.execute("DELETE FROM DichVu")
    cursor.execute("DELETE FROM PhongKham")

    # ===== BỆNH NHÂN (10) =====
    benhnhan = [
        ("Nguyễn Văn An","0123","Hà Nội","Nam","2000-01-01"),
        ("Trần Thị Bích","0124","Hải Phòng","Nữ","1999-02-02"),
        ("Lê Văn Cường","0125","Đà Nẵng","Nam","1998-03-03"),
        ("Phạm Thị Dung","0126","Huế","Nữ","1997-04-04"),
        ("Hoàng Văn Tuân","0127","HCM","Nam","1996-05-05"),
        ("Nguyễn Thị Nha","0128","Cần Thơ","Nữ","1995-06-06"),
        ("Trần Văn Gay","0129","Nghệ An","Nam","1994-07-07"),
        ("Lê Thị Hường","0130","Quảng Ninh","Nữ","1993-08-08"),
        ("Phạm Văn Tài","0131","Bắc Ninh","Nam","1992-09-09"),
        ("Hoàng Thị Hải","0132","Nam Định","Nữ","1991-10-10")
    ]

    cursor.executemany("""
        INSERT INTO BenhNhan (ten,sdt,dia_chi,gioi_tinh,ngay_sinh)
        VALUES (?,?,?,?,?)
    """, benhnhan)

    # ===== BÁC SĨ (10) =====
    bacsi = [
        ("BS Phạm Văn Minh","Nam","Tim mạch"),
        ("BS Nguyễn Thị Lan","Nữ","Nhi"),
        ("BS Nguyễn Văn Hùng","Nam","Da liễu"),
        ("BS Nguyễn Thị Hoa","Nữ","Tai mũi họng"),
        ("BS Lê Mai Nam","Nam","Ngoại"),
        ("BS Nguyễn Thị Mai","Nữ","Sản"),
        ("BS Hoàng Văn Long","Nam","Nội"),
        ("BS Trần Kiều Trang","Nữ","Mắt"),
        ("BS Phạm Minh Tuấn","Nam","Thần kinh"),
        ("BS Nguyễn Thị Hạnh","Nữ","Xương khớp")
    ]

    cursor.executemany("""
        INSERT INTO BacSi (ten,gioi_tinh,chuyen_khoa)
        VALUES (?,?,?)
    """, bacsi)

    # ===== DỊCH VỤ (10) =====
    dichvu = [
        ("Khám tổng quát",200000),
        ("Khám tim",300000),
        ("Khám da",250000),
        ("Khám tai mũi họng",220000),
        ("Khám mắt",210000),
        ("Siêu âm",150000),
        ("Xét nghiệm máu",180000),
        ("Chụp X-quang",200000),
        ("Khám thần kinh",320000),
        ("Khám xương khớp",280000)
    ]

    cursor.executemany("""
        INSERT INTO DichVu (ten_dich_vu,gia)
        VALUES (?,?)
    """, dichvu)

    # ===== PHÒNG KHÁM (10) =====
    phong = [
        ("Phòng 101",5,"Tầng 1"),
        ("Phòng 102",4,"Tầng 1"),
        ("Phòng 201",6,"Tầng 2"),
        ("Phòng 202",5,"Tầng 2"),
        ("Phòng 301",3,"Tầng 3"),
        ("Phòng 302",4,"Tầng 3"),
        ("Phòng 401",6,"Tầng 4"),
        ("Phòng 402",5,"Tầng 4"),
        ("Phòng 501",2,"Tầng 5"),
        ("Phòng 502",3,"Tầng 5")
    ]

    cursor.executemany("""
        INSERT INTO PhongKham (ten_phong,so_giuong,mo_ta)
        VALUES (?,?,?)
    """, phong)

    # ===== LỊCH KHÁM (10) =====
    lich = [
        (1,1,1,1,"2026-04-15","08:00"),
        (2,2,2,2,"2026-04-15","09:00"),
        (3,3,3,3,"2026-04-15","10:00"),
        (4,4,4,4,"2026-04-16","08:00"),
        (5,5,5,5,"2026-04-16","09:00"),
        (6,6,6,6,"2026-04-16","10:00"),
        (7,7,7,7,"2026-04-17","08:00"),
        (8,8,8,8,"2026-04-17","09:00"),
        (9,9,9,9,"2026-04-17","10:00"),
        (10,10,10,10,"2026-04-18","08:00")
    ]

    cursor.executemany("""
        INSERT INTO LichKham (benhnhan_id,bacsi_id,phongkham_id,dichvu_id,ngay_kham,gio_kham)
        VALUES (?,?,?,?,?,?)
    """, lich)

    conn.commit()
    conn.close()

    print(" Đã thêm dữ liệu mẫu (mỗi bảng ≥ 10 dòng)")
if __name__ == "__main__":
    create_tables()
    insert_sample_data()