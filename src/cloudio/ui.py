import sys

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QTextEdit, QLineEdit, \
    QCheckBox, QFileDialog, QMessageBox, QSizePolicy
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import Qt, QDateTime
from param import ParamSelector
from csv_writer import write_to_csv, write_to_csv_aligned
from title_label import TitleLabel


class UI:
    def __init__(self):
        self.callback_db = None

        # Window
        self.app = QApplication(sys.argv)
        self.window = QWidget()
        self.window.setWindowTitle("Data - Getter")

        # Main layout
        main_layout = QHBoxLayout()

        # DB
        db_layout = QVBoxLayout()
        db_widget = self.draw_db_widget()
        db_layout.addWidget(db_widget, alignment=Qt.AlignVCenter)
        db_layout.setAlignment(Qt.AlignVCenter)
        db_layout.setStretchFactor(db_widget, 1)

        # Settings layout
        self.settings_layout = QVBoxLayout()

        # Command layout
        command_layout = QVBoxLayout()
        command_widget = self.draw_command_widget()
        command_layout.addWidget(command_widget, alignment=Qt.AlignVCenter)
        command_layout.setAlignment(Qt.AlignVCenter)
        command_layout.setStretchFactor(command_widget, 1)

        # Put DB, Settings and Command layout in the main layout
        main_layout.addLayout(db_layout)
        main_layout.addLayout(self.settings_layout)
        main_layout.addLayout(command_layout)

        # Build Setting layout
        self.topics_label = TitleLabel("Topics")

        self.topics_list = ParamSelector()

        start_label = QLabel("Start")
        self.start = QLineEdit("")
        self.start.setPlaceholderText("dd-MM-yyyy HH:mm:ss")

        end_label = QLabel("End")
        self.end = QLineEdit("")
        self.end.setPlaceholderText("dd-MM-yyyy HH:mm:ss")

        self.align_data = QCheckBox("Align data")

        sub_group_topics_settings_layout = QVBoxLayout()
        sub_group_topics_settings_layout.addWidget(self.topics_label)
        sub_group_topics_settings_layout.addWidget(self.topics_list)

        sub_group_times_settings_layout = QHBoxLayout()
        sub_group_start_settings_layout = QVBoxLayout()
        sub_group_end_settings_layout = QVBoxLayout()

        sub_group_times_settings_layout.addLayout(sub_group_start_settings_layout)
        sub_group_times_settings_layout.addLayout(sub_group_end_settings_layout)
        sub_group_start_settings_layout.addWidget(start_label)
        sub_group_start_settings_layout.addWidget(self.start)
        sub_group_end_settings_layout.addWidget(end_label)
        sub_group_end_settings_layout.addWidget(self.end)

        sub_group_times_settings_layout_parent = QVBoxLayout()
        sub_group_times_settings_layout_parent.addLayout(sub_group_times_settings_layout)
        sub_group_times_settings_layout_parent.addWidget(self.align_data)

        times_settings_widget = QWidget()
        times_settings_widget.setLayout(sub_group_times_settings_layout_parent)

        time_title = TitleLabel("Times")
        times_settings_layout = QVBoxLayout()
        times_settings_layout.addWidget(time_title)
        times_settings_layout.addWidget(times_settings_widget)

        self.settings_layout.addLayout(sub_group_topics_settings_layout)
        self.settings_layout.addLayout(times_settings_layout)

        self.window.setLayout(main_layout)

    # PUBLIC
    def show_window(self):
        self.window.resize(1000, 580)
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
            topics = [line for line in text.splitlines() if line.strip()]

            try:
                data = self.callback_db(self.start.text(), self.end.text(), topics)
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

    # PRIVATE
    def draw_db_widget(self) -> QWidget:
        db_layout = QVBoxLayout()

        # Build DB layout
        database_svg = QSvgWidget("../../asset/database.svg")
        database_svg.setFixedSize(100, 175)

        data_flow_from_svg = QSvgWidget("../../asset/data_flow_arrow.svg")
        data_flow_from_svg.setFixedSize(53, 54)
        data_flow_to_svg_parent = QVBoxLayout()
        data_flow_to_svg_parent.addWidget(data_flow_from_svg)
        data_flow_to_svg_parent.setAlignment(Qt.AlignHCenter)

        db_layout.addWidget(database_svg)
        db_layout.addLayout(data_flow_to_svg_parent)
        db_layout.addStretch(1)
        db_layout.setAlignment(Qt.AlignVCenter)

        widget = QWidget()
        widget.setLayout(db_layout)
        return widget

    # PRIVATE
    def draw_command_widget(self) -> QWidget:
        command_layout = QVBoxLayout()

        # Build Command layout
        csv_svg = QSvgWidget("../../asset/csv_icon.svg")
        csv_svg.setFixedSize(140, 90)

        execute_button = QPushButton("Execute")
        execute_button.clicked.connect(self.on_execute_clicked)
        execute_button.setStyleSheet("""   
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
        execute_button.setFixedSize(140, 40)

        data_flow_to_svg = QSvgWidget("../../asset/data_flow_arrow_90.svg")
        data_flow_to_svg.setFixedSize(54, 53)
        data_flow_to_svg_parent = QVBoxLayout()
        data_flow_to_svg_parent.addWidget(data_flow_to_svg)
        data_flow_to_svg_parent.setAlignment(Qt.AlignHCenter)

        command_layout.addWidget(csv_svg)
        command_layout.addWidget(execute_button)
        command_layout.addLayout(data_flow_to_svg_parent)
        command_layout.addStretch(1)
        command_layout.setAlignment(Qt.AlignVCenter)

        widget = QWidget()
        widget.setLayout(command_layout)
        return widget
