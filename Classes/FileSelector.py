from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QFileDialog, QPushButton, QRadioButton, QCheckBox,QLineEdit, QGridLayout
from Classes.ErrorMessageBox import ErrorMessageBox
import pathlib
import typing

class FileSelector(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        layout = QGridLayout()
        self.raw_filepath:pathlib.Path|None = None
        self.template_filepath:pathlib.Path|None = None
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
        self.analysis_selection = AnalysisSelection(self, "AnalysisSelection")
        layout.addWidget(self.analysis_selection, 1,0, 1, layout.columnCount())
        self.setLayout(layout)

    def select_data_file(self)->None:
        '''Gets raw data filepath, sets the text of the label to the stem of the filepath, sets the text of the xlsx QLineEdit instance to the filepath stem'''
        self.raw_filepath = pathlib.Path(QFileDialog(filter=".txt").getOpenFileName(self, 'Select File',filter='*.txt')[0])
        self.set_label_text(self.raw_filepath, "label 1")
        analysis_widget = self.analysis_selection.get_analysis_widget()
        if analysis_widget is None: return None
        analysis_widget.set_xlsx_filename(self.raw_filepath.stem)

    def select_template_file(self)->None:        
        self.template_filepath = pathlib.Path(QFileDialog(filter=".csv").getOpenFileName(self, 'Select File',filter='*.csv')[0])
        self.set_label_text(self.template_filepath, "label 2")
        return None
    
    def set_label_text(self, filepath:pathlib.Path, label_name:str)->None:
        '''Sets the name of the label identified by the object name to the stem of the Path object'''
        if filepath.exists():            
            self.findChild(QLabel, label_name).setText(filepath.name)            
        else:
            self.findChild(QLabel, label_name).setText("")
            
    def get_selection(self)->dict[str, list[str|bool|pathlib.Path]]:
        '''Gets the user inputed values from the UI and returns it as a list'''
        default = {
            "analysis":"",
            "data":[],
        }

        if self.raw_filepath == None or self.template_filepath == None: 
            ErrorMessageBox("Raw Data File or Template File Missing")
            return default
            
        if not self.raw_filepath.is_file() or not self.template_filepath.is_file(): 
            ErrorMessageBox("Raw Data File or Template File Missing")
            return default
        print(self.raw_filepath, self.template_filepath)
        analysis_type = self.analysis_selection.get_current_analysis()
        analysis_widget = self.analysis_selection.get_analysis_widget()
        selections = analysis_widget.get_selection()
        if analysis_type is None or analysis_widget is None or len(selections) == 0: return default
        return {
            "analysis":analysis_type,
            "data":[self.raw_filepath, self.template_filepath, *selections]
            }
        
        

class UserEditableFields(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("user_editable_fields")
        layout = QHBoxLayout(self)
        layout.addWidget(QCheckBox(parent=self, text="Make Excel?"))
        
        graph_title = QLineEdit(parent=self)
        graph_title.setObjectName("graph_title")
        graph_title.setPlaceholderText("Add an optional name for the graph here")

        xlsx_filename = QLineEdit(parent=self)
        xlsx_filename.setObjectName("xlsx_filename")
        xlsx_filename.setPlaceholderText("Name Excel File or Leave Empty to Use Default Data Filename Instead")

        raw_data_filename = self.__get_parent_raw_data_file__()
        xlsx_filename.setText(raw_data_filename)


        layout.addWidget(graph_title)
        layout.addWidget(xlsx_filename)

    def get_selection(self)->list[str|bool]:
        make_excel = self.findChild(QCheckBox)
        graph_title = self.findChild(QLineEdit, "graph_title")
        xlsx_filename = self.findChild(QLineEdit, "xlsx_filename")
        return [make_excel.isChecked(), graph_title.text(), xlsx_filename.text()]
        
    def set_xlsx_filename(self, name:str)->None:
        '''Sets the name of the xlsx attribute to the string passed in'''
        xlsx_filename = self.findChild(QLineEdit, "xlsx_filename")        
        xlsx_filename.setText(name)
        return None
    
    def __get_parent_raw_data_file__(self)->str:
        '''Checks the great-grandparent for the raw_filepath Path attribute, returns the stem or an empty string if it does not exist'''
        great_grandparent = self.parent().parent().parent()
        if filename := great_grandparent.raw_filepath:
            return filename.stem
        return ""
    

        
class AvePlusThreeStdev(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)        
        layout.addWidget(UserEditableFields(self))
        self.setLayout(layout)

    def get_selection(self)->list[typing.Any]:
        return self.findChild(UserEditableFields).get_selection()        
        
    def set_xlsx_filename(self, name:str)->None:
        '''Sets the name of the xlsx attribute to the string passed in'''
        xlsx_filename = self.findChild(QLineEdit, "xlsx_filename")        
        xlsx_filename.setText(name)


class RegressionSelection(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)        
        layout = QHBoxLayout(self)
        regressions = ["Linear", "Logarithmic", "5PL"]
        for regression in regressions: layout.addWidget(QRadioButton(regression, self))
        layout.addWidget(UserEditableFields(self))
        self.setLayout(layout)
    
    def get_selection(self)->list[typing.Any]:
        try:
            regression = [child.text() for child in self.children() if isinstance(child, QRadioButton) and child.isChecked()][0]            
            return [regression, *self.findChild(UserEditableFields).get_selection()]
        except IndexError:
            ErrorMessageBox("Regression Type Missing")
            return []
        
    def set_xlsx_filename(self, name:str)->None:
        '''Sets the name of the xlsx attribute to the string passed in'''
        xlsx_filename = self.findChild(QLineEdit, "xlsx_filename")        
        xlsx_filename.setText(name)
        



class AnalysisSelection(QWidget):
    def __init__(self, parent:QWidget, name:str) -> None:
        super().__init__(parent)
        self.analysis = None
        layout = QHBoxLayout()
        self.setObjectName(name)
        threexstd_Button = QRadioButton("Average of Controls + 3x Stdev of Controls")
        regression_button = QRadioButton("Interpolation via Regression Model fitted to Standards")  
        threexstd_Button.clicked.connect(lambda: self.changeAnalysis("ave+3xStdev"))
        regression_button.clicked.connect(lambda: self.changeAnalysis("regression"))
        layout.addWidget(threexstd_Button)
        layout.addWidget(regression_button)
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
    
    def get_analysis_widget(self)->RegressionSelection|AvePlusThreeStdev|None:
        '''Returns the current analysis widget selected or None if no radiobutton is selected'''
        parent_layout = self.parentWidget().layout() 
        if self.analysis is None: return None
        return parent_layout.itemAt(parent_layout.count()-1).widget()

