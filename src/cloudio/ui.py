import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QTextEdit, QLineEdit, \
    QCheckBox, QFileDialog
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import Qt

class UI:
    def __init__(self):
        # Window
        self.app = QApplication(sys.argv)
        self.window = QWidget()
        self.window.setWindowTitle("Data - Getter")
        self.window.setStyleSheet("background-color: #fff;")

        # Main layout
        self.main_layout = QHBoxLayout()

        # DB layout
        self.db_layout = QVBoxLayout()

        # Settings layout
        self.settings_layout = QVBoxLayout()

        # Command layout
        self.command_layout = QVBoxLayout()

        # Put DB, Settings and Command layout in the main layout
        self.main_layout.addLayout(self.db_layout)
        self.main_layout.addLayout(self.settings_layout)
        self.main_layout.addLayout(self.command_layout)

        # Build DB layout
        self.database_name = QLabel("Database")
        self.database_name.setAlignment(Qt.AlignLeft)

        self.database_svg = QSvgWidget("../../asset/database.svg")
        self.database_svg.setFixedSize(200, 350)

        self.data_flow_from_svg = QSvgWidget("../../asset/data_flow_arrow.svg")
        self.data_flow_from_svg.setFixedSize(53, 54)

        self.sub_group_db_layout = QHBoxLayout()
        self.sub_group_db_layout.addWidget(self.database_name)
        self.sub_group_db_layout.addWidget(self.database_svg)

        self.db_layout.addLayout(self.sub_group_db_layout)
        self.db_layout.addWidget(self.data_flow_from_svg)

        # Build Setting layout
        self.topics_label = QLabel("Topics")
        self.topics_label.setAlignment(Qt.AlignLeft)

        self.topics_list = QTextEdit()

        self.start_label = QLabel("Start")
        self.start = QLineEdit()

        self.end_label = QLabel("End")
        self.end = QLineEdit()

        self.align_data = QCheckBox("Align data")
        self.align_data_label = QLabel("Align data")

        self.sub_group_topics_settings_layout = QVBoxLayout()
        self.sub_group_times_settings_layout = QHBoxLayout()
        self.sub_group_start_settings_layout = QVBoxLayout()
        self.sub_group_end_settings_layout = QVBoxLayout()
        self.sub_group_align_data_settings_layout = QHBoxLayout()

        self.sub_group_topics_settings_layout.addWidget(self.topics_label)
        self.sub_group_topics_settings_layout.addWidget(self.topics_list)

        self.sub_group_times_settings_layout.addLayout(self.sub_group_start_settings_layout)
        self.sub_group_times_settings_layout.addLayout(self.sub_group_end_settings_layout)
        self.sub_group_start_settings_layout.addWidget(self.start_label)
        self.sub_group_start_settings_layout.addWidget(self.start)
        self.sub_group_end_settings_layout.addWidget(self.end_label)
        self.sub_group_end_settings_layout.addWidget(self.end)

        self.sub_group_align_data_settings_layout.addWidget(self.align_data)
        self.sub_group_align_data_settings_layout.addWidget(self.align_data_label)

        self.settings_layout.addLayout(self.sub_group_topics_settings_layout)
        self.settings_layout.addLayout(self.sub_group_times_settings_layout)
        self.settings_layout.addLayout(self.sub_group_align_data_settings_layout)

        # Build Command layout
        self.csv_svg = QSvgWidget("../../asset/csv_icon.svg")
        self.csv_svg.setFixedSize(90, 130)

        self.execute_button = QPushButton("Execute")
        self.execute_button.clicked.connect(self.on_execute_clicked)

        self.data_flow_to_svg = QSvgWidget("../../asset/data_flow_arrow_90.svg")
        self.data_flow_to_svg.setFixedSize(54, 53)

        self.command_layout.addWidget(self.csv_svg)
        self.command_layout.addWidget(self.execute_button)
        self.command_layout.addWidget(self.data_flow_to_svg)

        """
        # Texte
        self.label = QLabel("Bienvenue dans l'application PyQt")
        self.label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.label)

        # Image SVG
        self.svg = QSvgWidget("../../asset/database.svg")
        #self.svg.setFixedSize(200, 350)
        self.main_layout.addWidget(self.svg, alignment=Qt.AlignCenter)

        # Bouton
        self.button = QPushButton("Clique-moi")
        self.button.setStyleSheet("""
        #    QPushButton {
        #        background-color: #3498db;
        #        color: white;
        #        font-size: 16px;
        #        padding: 10px 20px;
        #        border-radius: 10px;
        #    }
        #    QPushButton:hover {
        #        background-color: #2980b9;
        #    }
        """)
        self.button.clicked.connect(self.on_button_clicked)
        self.main_layout.addWidget(self.button, alignment=Qt.AlignCenter)
        """
        self.window.setLayout(self.main_layout)
        self.window.resize(400, 400)
        self.window.show()

        sys.exit(self.app.exec_())

    def on_execute_clicked(self):
        path = self.ask_path()

        if path is not None:


    def ask_path(self):
        file_path, _ = QFileDialog.getSaveFileName(
            parent=self.window,
            caption="Save SVG in",
            directory="",
            filter="CSV (*.csv);;Tous les fichiers (*)"
        )

        if file_path:
            return file_path
        else:
            return None
