import json
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QTextEdit, QPushButton, QInputDialog, QMessageBox
)

PARAMS_FILE = "params.json"

class ParamSelector(QWidget):
    def __init__(self):
        super().__init__()

        # Interface
        self.combo = QComboBox()
        self.combo.currentIndexChanged.connect(self.on_selection_change)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("param1=...\nparam2=...")

        # Boutons
        self.add_btn = QPushButton("Ajouter")
        self.edit_btn = QPushButton("Modifier")
        self.delete_btn = QPushButton("Supprimer")

        self.add_btn.clicked.connect(self.add_param_set)
        self.edit_btn.clicked.connect(self.save_current_param_set)
        self.delete_btn.clicked.connect(self.delete_param_set)

        # Layouts
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.combo)
        layout.addWidget(self.text_edit)
        layout.addLayout(button_layout)

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
                "Défaut": "param1=10\nparam2=20\nparam3=30"
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
            name = self.combo.currentText()
            self.text_edit.setPlainText(self.param_sets.get(name, ""))
        self.update_ui_state()

    def update_ui_state(self):
        has_items = self.combo.count() > 0
        self.text_edit.setEnabled(has_items)
        self.edit_btn.setEnabled(has_items)
        self.delete_btn.setEnabled(has_items)

    def add_param_set(self):
        name, ok = QInputDialog.getText(self, "Nouveau paramètre", "Nom de la configuration :")
        if ok and name:
            if name in self.param_sets:
                QMessageBox.warning(self, "Erreur", "Ce nom existe déjà.")
                return
            self.param_sets[name] = ""
            self.save_params()
            self.update_combobox()
            self.combo.setCurrentText(name)

    def save_current_param_set(self):
        name = self.combo.currentText()
        if not name:
            return
        self.param_sets[name] = self.text_edit.toPlainText()
        self.save_params()
        QMessageBox.information(self, "Sauvegardé", f"Configuration '{name}' mise à jour.")

    def delete_param_set(self):
        name = self.combo.currentText()
        if not name:
            return
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Supprimer la configuration '{name}' ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.param_sets.pop(name, None)
            self.save_params()
            self.update_combobox()