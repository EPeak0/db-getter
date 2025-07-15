import sys

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QTextEdit, QLineEdit, \
    QCheckBox, QFileDialog, QMessageBox
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import Qt, QDateTime
from param import ParamSelector
from csv_writer import write_to_csv, write_to_csv_aligned


class UI:
    def __init__(self):
        self.callback_db = None

        # Window
        self.app = QApplication(sys.argv)
        self.window = QWidget()
        self.window.setWindowTitle("Data - Getter")

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
        self.database_svg = QSvgWidget("../../asset/database.svg")
        self.database_svg.setFixedSize(100, 175)

        self.data_flow_from_svg = QSvgWidget("../../asset/data_flow_arrow.svg")
        self.data_flow_from_svg.setFixedSize(53, 54)
        self.db_layout.addWidget(self.database_svg)
        self.db_layout.addWidget(self.data_flow_from_svg)

        # Build Setting layout
        self.topics_label = QLabel("Topics")
        self.topics_label.setAlignment(Qt.AlignLeft)

        self.topics_list = ParamSelector()

        self.start_label = QLabel("Start")
        self.start = QLineEdit("")
        self.start.setPlaceholderText("dd-MM-yyyy HH:mm:ss")

        self.end_label = QLabel("End")
        self.end = QLineEdit("")
        self.end.setPlaceholderText("dd-MM-yyyy HH:mm:ss")

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
        self.csv_svg.setFixedSize(140, 90)

        self.execute_button = QPushButton("Execute")
        self.execute_button.clicked.connect(self.on_execute_clicked)
        self.execute_button.setStyleSheet("""   
                                                QPushButton {
                                                    background-color: #2C8BF8;
                                                    color: #F5F6FF;
                                                    border: 3px solid #A2CCFC;
                                                    border-radius: 12px;
                                                    font-weight: bold;
                                                    font-size: 16px;
                                                }
                                                QPushButton:hover {
                                                    color: #FFF;
                                                }          
                                                            
                                                            
                                                """)
        self.execute_button.setFixedSize(140, 40)

        self.data_flow_to_svg = QSvgWidget("../../asset/data_flow_arrow_90.svg")
        self.data_flow_to_svg.setFixedSize(54, 53)
        self.data_flow_to_svg_parent = QVBoxLayout()
        self.data_flow_to_svg_parent.addWidget(self.data_flow_to_svg)
        self.data_flow_to_svg_parent.setAlignment(Qt.AlignHCenter)

        self.command_layout_sub = QVBoxLayout()
        self.command_layout_sub.addWidget(self.csv_svg)
        self.command_layout_sub.addWidget(self.execute_button)
        self.command_layout_sub.setAlignment(Qt.AlignVCenter)

        self.command_layout.addLayout(self.command_layout_sub)
        self.command_layout.addLayout(self.data_flow_to_svg_parent)
        self.command_layout.setAlignment(Qt.AlignBottom)

        self.window.setLayout(self.main_layout)

    # PUBLIC
    def show_window(self):
        self.window.resize(400, 400)
        self.window.show()
        sys.exit(self.app.exec_())

    # PUBLIC
    def set_db_callback(self, callback):
        self.callback_db = callback

    # PRIVATE
    def on_execute_clicked(self):
        if self.check_format():
            # Ready to request the database
            text = self.topics_list.toPlainText()
            lines = text.splitlines()
            cleaned_lines = [line.strip() for line in lines if line.strip()]
            cleaned = '\n'.join(cleaned_lines)
            try:
                data = self.callback_db(self.start.text(), self.end.text(), cleaned)
            except Exception as e:
                QMessageBox.critical(
                    self.window,
                    "Database : Error",
                    f"Database failed to connect/respond"
                )
                return

            path = self.ask_path()
            if path is not None:
                # Ready to write CSV
                if self.align_data.isChecked():
                    try :
                        write_to_csv_aligned(data, path)
                    except Exception as e:
                        QMessageBox.critical(
                            self.window,
                            "CSV : Error",
                            f"CSV failed to write"
                        )
                        return
                else:
                    try:
                        write_to_csv(data, path)
                    except Exception as e:
                        QMessageBox.critical(
                            self.window,
                            "CSV : Error",
                            f"CSV failed to write"
                        )
                        return

        else :
            # TODO Non-valid start and/or end dates
            QMessageBox.warning(
                self.window,
                "Invalid format",
                f"Invalid Start and/or End format"
            )

    # PRIVATE
    def check_format(self) -> bool:
        start_dt = QDateTime.fromString(self.start.text(), "dd-MM-yyyy HH:mm:ss")
        end_dt = QDateTime.fromString(self.end.text(), "dd-MM-yyyy HH:mm:ss")

        if start_dt.isValid() and end_dt.isValid():
            return True
        else:
            return False


    # PRIVATE
    def ask_path(self):
        file_path, _ = QFileDialog.getSaveFileName(
            parent=self.window,
            caption="Save CSV in",
            directory="",
            filter="CSV (*.csv);;Tous les fichiers (*)"
        )

        if file_path:
            return file_path
        else:
            return None
