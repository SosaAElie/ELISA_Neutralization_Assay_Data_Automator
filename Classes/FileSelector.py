from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QFileDialog, QPushButton, QRadioButton, QCheckBox,QLineEdit
from Classes.ErrorMessageBox import ErrorMessageBox
import pathlib
import typing

class FileSelector(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        layout = QHBoxLayout()
        self.raw_file = ""
        self.template = ""
        button_titles = ["Select Raw Data File", "Select Template File"]
        button_funcs = [self.select_data_file, self.select_template_file]
        for index, (title, func) in enumerate(zip(button_titles, button_funcs)):
            button = QPushButton(title)
            button.clicked.connect(func)
            layout.addWidget(button)
            layout.addWidget(QLabel("", objectName = f"label {index+1}"))

        regressions = ["Linear", "Logarithmic", "5PL"]
        for regression in regressions: 
            layout.addWidget(QRadioButton(regression))
     
        layout.addWidget(QCheckBox("Make Excel?"))

        graph_title = QLineEdit()
        graph_title.setPlaceholderText("Add an optional name for the graph here")
        layout.addWidget(graph_title)

        self.setLayout(layout)

    def select_data_file(self)->None:
        self.raw_file = QFileDialog(filter=".txt").getOpenFileName(self, 'Select File',filter='*.txt')[0]
        self.set_label_text(self.raw_file, "label 1")

    def select_template_file(self)->None:
        self.template = QFileDialog(filter=".csv").getOpenFileName(self, 'Select File',filter='*.csv')[0]
        self.set_label_text(self.template, "label 2")
    
    def set_label_text(self, filepath:str, label_name:str)->None:
        if filepath != "":
            filename = pathlib.Path(filepath).name
            self.findChild(QLabel, label_name).setText(filename)
        else:
            self.findChild(QLabel, label_name).setText("")
    
    def get_selection(self)->list[typing.Any]:

        if not self.raw_file == "" and not self.template == "":
            try:
                regression = [child.text() for child in self.children() if isinstance(child, QRadioButton) and child.isChecked()][0]
                make_excel = self.findChild(QCheckBox)
                graph_title = self.findChild(QLineEdit)
                return [self.raw_file, self.template, regression, make_excel.isChecked(), graph_title.text()]
            except IndexError:
                ErrorMessageBox("Regression Type Missing")
                return []
        else:
            ErrorMessageBox("Raw Data File or Template File Missing")
            return []
        