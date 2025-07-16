import json
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QTextEdit, QPushButton, QInputDialog, QMessageBox
)
from persistent_config import get_persistent_config_path

PARAMS_FILE = get_persistent_config_path("params.json")

class ParamSelector(QWidget):
    def __init__(self):
        super().__init__()

        self.current_text = ""

        # Interface
        self.combo = QComboBox()
        self.combo.currentIndexChanged.connect(self.on_selection_change)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("topic 1\ntopic 2\ntopic 3\n...")
        self.text_edit.textChanged.connect(self.on_text_changed)

        # Boutons
        self.add_btn = QPushButton("Add")
        self.edit_btn = QPushButton("Save")
        self.delete_btn = QPushButton("Delete")

        self.add_btn.setFixedSize(64,30)
        self.edit_btn.setFixedSize(64,30)
        self.delete_btn.setFixedSize(64,30)

        self.add_btn.clicked.connect(self.add_param_set)
        self.edit_btn.clicked.connect(self.save_current_param_set)
        self.delete_btn.clicked.connect(self.delete_param_set)

        # Layouts
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)

        combo_layout = QHBoxLayout()
        combo_layout.addWidget(self.combo)
        combo_layout.addLayout(button_layout)

        layout = QVBoxLayout()
        layout.addLayout(combo_layout)
        layout.addWidget(self.text_edit)

        self.setLayout(layout)

        # Charger les données
        self.param_sets = {}
        self.load_params()
        self.update_combobox()

    def toPlainText(self):
        return self.text_edit.toPlainText()

    def load_params(self):
        if os.path.exists(PARAMS_FILE):
            with open(PARAMS_FILE, 'r', encoding='utf-8') as f:
                self.param_sets = json.load(f)
        else:
            self.param_sets = {
                "Default": "topic1\ntopic2\ntopic3\n..."
            }
            self.save_params()

    def save_params(self):
        with open(PARAMS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.param_sets, f, indent=4, ensure_ascii=False)

    def update_combobox(self):
        self.combo.blockSignals(True)
        self.combo.clear()
        self.combo.addItems(self.param_sets.keys())
        self.combo.blockSignals(False)
        self.on_selection_change(self.combo.currentIndex())
        self.update_ui_state()

    def on_selection_change(self, index):
        if index >= 0:
            name = self.combo.currentText().replace(" *", "")
            self.current_text = self.param_sets.get(name, "")
            self.text_edit.blockSignals(True)
            self.text_edit.setPlainText(self.current_text)
            self.text_edit.blockSignals(False)
        self.update_ui_state()

    def on_text_changed(self):
        current_name = self.combo.currentText().replace(" *", "")
        current_text = self.text_edit.toPlainText()

        modified = (current_text != self.param_sets.get(current_name, ""))

        if modified and not self.combo.currentText().endswith(" *"):
            self.combo.setItemText(self.combo.currentIndex(), current_name + " *")
        elif not modified and self.combo.currentText().endswith(" *"):
            self.combo.setItemText(self.combo.currentIndex(), current_name)

        self.edit_btn.setEnabled(modified)

    def update_ui_state(self):
        has_items = self.combo.count() > 0
        self.text_edit.setEnabled(has_items)
        self.delete_btn.setEnabled(has_items)

        if has_items:
            current_name = self.combo.currentText().replace(" *", "")
            modified = self.text_edit.toPlainText() != self.param_sets.get(current_name, "")
            self.edit_btn.setEnabled(modified)
        else:
            self.edit_btn.setEnabled(False)

    def add_param_set(self):
        name, ok = QInputDialog.getText(self, "New topic list", "List name")
        if ok and name:
            if name in self.param_sets:
                QMessageBox.warning(self, "Error", "Name is already used")
                return
            self.param_sets[name] = ""
            self.save_params()
            self.update_combobox()
            self.combo.setCurrentText(name)

    def save_current_param_set(self):
        name = self.combo.currentText().replace(" *", "")
        if not name:
            return
        self.param_sets[name] = self.text_edit.toPlainText()
        self.save_params()
        self.current_text = self.param_sets[name]
        self.combo.setItemText(self.combo.currentIndex(), name)
        self.edit_btn.setEnabled(False)
        QMessageBox.information(self, "Saved", f"'{name}' saved")

    def delete_param_set(self):
        name = self.combo.currentText()
        if not name:
            return
        reply = QMessageBox.question(
            self, "Delete",
            f"Delete '{name}' ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.param_sets.pop(name, None)
            self.save_params()
            self.update_combobox()