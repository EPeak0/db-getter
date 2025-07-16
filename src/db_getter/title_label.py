from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout


class TitleLabel(QWidget) :
    def __init__(self, text) :
        super().__init__()
        self.label = QLabel(text)
        self.label.setStyleSheet("""font-weight: bold; font-size: 24px;""")
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
