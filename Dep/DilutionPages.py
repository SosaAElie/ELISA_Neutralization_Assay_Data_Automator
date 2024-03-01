from PyQt5.QtWidgets import QWidget, QLineEdit, QVBoxLayout

class InconsistentDilution(QWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent, objectName = "InconsistentDilution")
        self.setLayout(QVBoxLayout())

        for num in range(1,7):
            self.layout().addWidget(QLineEdit())
            self.layout().itemAt(num-1).widget().setPlaceholderText(f"Enter the concentration: {num} (Numeric Value):")
        
        self.units = QLineEdit()
        self.units.setPlaceholderText("Enter the units of the standards, i.e. ug/mL")

        self.layout().addWidget(self.units)

    def get_input(self)->tuple[list[str], str]:
        '''Returns a list of strings of numbers the concentration as strings that were passed in by the user in the QLineEdit inputs'''
        return [self.layout().itemAt(num).widget().text() for num in range(6)], self.units.text()
        
class ConsistentDilution(QWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent, objectName = "ConsistentDilution")
        self.setLayout(QVBoxLayout())

        self.starting_concentration = QLineEdit()
        self.starting_concentration.setPlaceholderText("Entering the starting concentration (number only)")
        self.layout().addWidget(self.starting_concentration)
        
        self.units = QLineEdit()
        self.units.setPlaceholderText("Enter the units")
        self.layout().addWidget(self.units)
        
        self.dilution_factor = QLineEdit()
        self.dilution_factor.setPlaceholderText("Enter the dilution factor, i.e 2,5,10")
        self.layout().addWidget(self.dilution_factor)
        
        self.dilutions = QLineEdit()
        self.dilutions.setPlaceholderText("Enter the number of times the standards were diluted")
        self.layout().addWidget(self.dilutions)
    
    def get_input(self)->tuple[str]:
        '''Returns a tuple of 4 strings from user input: starting_concentration, units, dilution_factor, times_diluted'''
        return (self.starting_concentration.text(), self.units.text(), self.dilution_factor.text(), self.dilutions.text())