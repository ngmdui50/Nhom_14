from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget


def update_action_button_state(app, active_key):
    actions = app.lay_quyen_form(active_key)
    app.btnThem.setEnabled("them" in actions)
    app.btnSua.setEnabled("sua" in actions)
    app.btnXoa.setEnabled("xoa" in actions)
    app.btnTimKiem.setEnabled("tim_kiem" in actions)
    app.btnxoaDL.setEnabled(bool(actions - {"tim_kiem"}))
    update_sidebar_active(app, active_key)
    if hasattr(app, "lblTopbarHint"):
        app.lblTopbarHint.setText(app.ten_khu_vuc(active_key))


def update_sidebar_active(app, active_key):
    button_map = {
        "TL": app.btntrangchu,
        "BS": app.btnBacSi,
        "BN": app.btnBenhNhan,
        "LK": app.btnLichKham,
        "DV": app.btnDichVu,
        "PK": app.btnPhongKham,
        "DT": app.btnDoanhThu,
        "CL": app.btnCaLam,
    }
    for key, btn in button_map.items():
        btn.setProperty("navActive", key == active_key)
        btn.style().unpolish(btn)
        btn.style().polish(btn)


def extend_patient_form(app):
    bn_ui = app.forms["BN"]
    bn_ui.groupEdit.setMaximumHeight(260)


def rebuild_sidebar(app):
    for child in app.frame.findChildren(QWidget):
        if child is app.frame:
            continue
        if child in {
            app.btntrangchu, app.btnBacSi, app.btnBenhNhan, app.btnLichKham,
            app.btnDichVu, app.btnPhongKham, app.btnDoanhThu, app.btnCaLam,
            app.btnSua, app.btnXoa, app.btnTimKiem, app.btnThem, app.btnxoaDL
        }:
            continue
        child.hide()

    old_layout = app.frame.layout()
    if old_layout:
        while old_layout.count():
            item = old_layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget:
                widget.setParent(None)
            elif child_layout:
                while child_layout.count():
                    child_item = child_layout.takeAt(0)
                    child_widget = child_item.widget()
                    if child_widget:
                        child_widget.setParent(None)
        old_layout.deleteLater()

    main_layout = QVBoxLayout(app.frame)
    main_layout.setContentsMargins(12, 12, 12, 12)
    main_layout.setSpacing(12)

    nav_card = QFrame(app.frame)
    nav_card.setObjectName("sidebarNavCard")
    nav_layout = QVBoxLayout(nav_card)
    nav_layout.setContentsMargins(10, 6, 10, 10)
    nav_layout.setSpacing(10)
    nav_title = QLabel("Dieu huong", nav_card)
    nav_title.setObjectName("sidebarSectionTitle")
    nav_layout.addWidget(nav_title)

    for btn in (
        app.btntrangchu, app.btnBacSi, app.btnBenhNhan, app.btnLichKham,
        app.btnDichVu, app.btnPhongKham, app.btnDoanhThu, app.btnCaLam,
    ):
        btn.setParent(nav_card)
        btn.setMinimumHeight(40)
        nav_layout.addWidget(btn)
    nav_layout.addStretch(0)
    nav_card.setMaximumHeight(430)

    action_card = QFrame(app.frame)
    action_card.setObjectName("sidebarActionCard")
    action_layout = QVBoxLayout(action_card)
    action_layout.setContentsMargins(10, 10, 10, 10)
    action_layout.setSpacing(8)
    action_title = QLabel("Thao tac", action_card)
    action_title.setObjectName("sidebarSectionTitle")
    action_layout.addWidget(action_title)

    for btn in (app.btnSua, app.btnXoa, app.btnTimKiem, app.btnxoaDL, app.btnThem):
        btn.setParent(action_card)
        btn.setMinimumHeight(34)
        action_layout.addWidget(btn)
    action_layout.addStretch(0)

    main_layout.addWidget(nav_card, 0)
    main_layout.addWidget(action_card, 0)
    main_layout.addStretch(1)


def rebuild_topbar(app):
    app.lblTime.setParent(app.centralwidget)
    app.label.setParent(app.centralwidget)

    header_container = QWidget(app.centralwidget)
    header_container.setObjectName("headerContainer")
    header_container.setGeometry(10, 6, 1470, 48)

    header_layout = QHBoxLayout(header_container)
    header_layout.setContentsMargins(0, 0, 0, 0)
    header_layout.setSpacing(14)

    app.label.setParent(header_container)
    app.label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    app.label.setWordWrap(False)
    header_layout.addWidget(app.label, 1)

    header_wrap = QWidget(header_container)
    header_wrap.setObjectName("topBarWrap")
    header_wrap.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
    header_layout.addWidget(header_wrap, 0)

    topbar_layout = QHBoxLayout(header_wrap)
    topbar_layout.setContentsMargins(12, 6, 12, 6)
    topbar_layout.setSpacing(10)

    app.lblCurrentRole = QLabel(header_wrap)
    app.lblCurrentRole.setObjectName("lblCurrentRole")
    app.lblCurrentUser = QLabel(header_wrap)
    app.lblCurrentUser.setObjectName("lblCurrentUser")
    app.lblTopbarHint = QLabel(header_wrap)
    app.lblTopbarHint.setObjectName("lblTopbarHint")

    app.btnNotification = QPushButton(header_wrap)
    app.btnNotification.setObjectName("btnNotification")
    app.btnNotification.setText("Thong bao")
    app.btnNotification.clicked.connect(app.mo_danh_sach_thong_bao)

    app.btnBackup = QPushButton(header_wrap)
    app.btnBackup.setObjectName("btnBackup")
    app.btnBackup.setText("Backup")
    app.btnBackup.clicked.connect(app.backup_database)

    app.btnRestore = QPushButton(header_wrap)
    app.btnRestore.setObjectName("btnRestore")
    app.btnRestore.setText("Restore")
    app.btnRestore.clicked.connect(app.restore_database)

    topbar_layout.addWidget(app.lblTopbarHint)
    topbar_layout.addWidget(app.btnBackup)
    topbar_layout.addWidget(app.btnRestore)
    topbar_layout.addWidget(app.btnNotification)
    topbar_layout.addWidget(app.lblCurrentRole)
    topbar_layout.addWidget(app.lblCurrentUser)
    topbar_layout.addWidget(app.lblTime)
