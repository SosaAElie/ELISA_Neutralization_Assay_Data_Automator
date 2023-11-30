import typing
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QLineEdit, QVBoxLayout

class InconsistentDilution(QWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        
        for num in range(1,7):
            self.layout().addWidget(QLineEdit())
            self.layout().itemAt(num-1).widget().setPlaceholderText(f"Enter the concentration {num} (Numeric Value):")
        
        self.units = QLineEdit()
        self.units.setPlaceholderText("Enter the units of the standards, i.e. ug/mL")
        self.layout().addWidget(self.units)
        
        
class ConsistentDilution(QWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.starting_concentration = QLineEdit()
        self.starting_concentration.setPlaceholderText("Entering the starting concentration (number only)")
        self.units = QLineEdit()
        self.units.setPlaceholderText("Enter the units of the starting concentration")
        self.dilution_factor = QLineEdit()
        self.dilution_factor.setPlaceholderText("Enter the dilution factor, i.e 2,5,10")
        self.dilutions = QLineEdit()
        self.dilutions.setPlaceholderText("Enter the number of times the standards were diluted")
        self.layout().addWidget(self.starting_concentration)
        self.layout().addWidget(self.units)
        self.layout().addWidget(self.dilution_factor)
        self.layout().addWidget(self.dilutions)
     