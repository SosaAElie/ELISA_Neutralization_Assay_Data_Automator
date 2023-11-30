from PyQt5.QtWidgets import QComboBox, QWidget, QLabel
from Pages.DilutionPages import ConsistentDilution, InconsistentDilution

class SelectDilutionType(QComboBox):
    def __init__(self, parent: QWidget | None = ...) -> None:
        super().__init__(parent)

        self.addItem("Consistent Dilutions")
        self.addItem("Inconsistent Dilutions")
        self.inconsistent_label = QLabel("Inconsistent Dilutions", parent)
        self.consistent_label = QLabel("Consistent Dilutions", parent)
        self.consistent = ConsistentDilution(parent)
        self.inconsistent = InconsistentDilution(parent)
        self.currentTextChanged.connect(self.change_dilution_page)
        self.consistent_label.hide()
        self.inconsistent_label.hide()
        self.consistent.hide()
        self.inconsistent.hide()
        parent.layout().addWidget(self.consistent_label)
        parent.layout().addWidget(self.consistent)
        parent.layout().addWidget(self.inconsistent_label)
        parent.layout().addWidget(self.inconsistent)
        
    def change_dilution_page(self, current_selection)->None:
        '''When the user selects a different option in the combobox, this function will activate removing the current dilution'''
        if current_selection == "Consistent Dilutions":
            self.consistent_label.show()
            self.consistent.show()
            self.inconsistent.hide()
            self.inconsistent_label.hide()
        elif current_selection == "Inconsistent Dilutions":
            self.inconsistent_label.show()
            self.inconsistent.show()
            self.consistent.hide()
            self.consistent_label.hide()
        self.repaint()