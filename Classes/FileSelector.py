from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QFileDialog, QPushButton, QRadioButton, QCheckBox,QLineEdit, QVBoxLayout, QGridLayout
from Classes.ErrorMessageBox import ErrorMessageBox
import pathlib
import typing

class FileSelector(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        layout = QGridLayout()
        self.raw_file = ""
        self.template = ""
        button_titles = ["Select Raw Data File", "Select Template File"]
        button_funcs = [self.select_data_file, self.select_template_file]
        for index, (title, func) in enumerate(zip(button_titles, button_funcs)):
            button = QPushButton(title)
            button.setObjectName(title)
            button.clicked.connect(func)
            if index!=0:position = index + 2
            else: position = index
            layout.addWidget(button, 0, position)
            layout.addWidget(QLabel("", objectName = f"label {index+1}"), 0, position+1)
        self.analysis_selection =AnalysisSelection(self, "AnalysisSelection")
        layout.addWidget(self.analysis_selection, 1,0, 1, layout.columnCount())
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
            analysis_type = self.analysis_selection.get_current_analysis()
            if analysis_type == "regression":
                analysis_widget = self.layout().itemAt(self.layout().count()-1).widget()
                regression_selections = analysis_widget.get_selection()
                if len(regression_selections) < 3: return []
                return [self.raw_file, self.template, *regression_selections]
            elif analysis_type == "ave+3xStdev":
                return [self.raw_file, self.template]
            else:
                return []
        else:
            ErrorMessageBox("Raw Data File or Template File Missing")
            return []
        
class AvePlusThreeStdev(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        pass


class RegressionSelection(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)        
        layout = QHBoxLayout(self)
        regressions = ["Linear", "Logarithmic", "5PL"]
        for regression in regressions: 
            layout.addWidget(QRadioButton(regression, self))
     
        layout.addWidget(QCheckBox("Make Excel?"))

        graph_title = QLineEdit()
        graph_title.setPlaceholderText("Add an optional name for the graph here")
        layout.addWidget(graph_title)
        self.setLayout(layout)
    
    def get_selection(self)->list[typing.Any]:
        try:
            regression = [child.text() for child in self.children() if isinstance(child, QRadioButton) and child.isChecked()][0]
            make_excel = self.findChild(QCheckBox)
            graph_title = self.findChild(QLineEdit)
            return [regression, make_excel.isChecked(), graph_title.text()]
        except IndexError:
            ErrorMessageBox("Regression Type Missing")
            return []
    


class AnalysisSelection(QWidget):
    def __init__(self, parent:QWidget, name:str) -> None:
        super().__init__(parent)
        layout = QHBoxLayout()
        self.setObjectName(name)
        threexstd_Button = QRadioButton("Average of Controls + 3x Stdev of Controls")
        regression_button = QRadioButton("Interpolation via Regression Model fitted to Standards")  
        threexstd_Button.clicked.connect(lambda: self.changeAnalysis("ave+3xStdev"))
        regression_button.clicked.connect(lambda: self.changeAnalysis("regression"))
        layout.addWidget(threexstd_Button)
        layout.addWidget(regression_button)
        self.analysis = None
        self.setLayout(layout)

    def changeAnalysis(self, analysis_type:str)->None:        
        parent_layout = self.parentWidget().layout()
        if self.analysis is not None: 
            parent_layout.removeWidget(parent_layout.itemAt(parent_layout.count()-1).widget())            
        if analysis_type == "regression":            
            parent_layout.addWidget(RegressionSelection(self), 2,0, 1, parent_layout.columnCount())
            self.analysis = "regression"
        elif analysis_type == "ave+3xStdev":
            parent_layout.addWidget(AvePlusThreeStdev(self), 2,0, 1, parent_layout.columnCount())
            self.analysis = "ave+3xStdev"
        return None
    
    def get_current_analysis(self)->str:
        '''Returns the current analysis selection present on the UI'''
        if self.analysis is None:
            ErrorMessageBox("Select an analysis type.")
            return ""
        return self.analysis

