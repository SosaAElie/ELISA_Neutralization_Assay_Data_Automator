from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFileDialog, QPushButton, QLineEdit, QRadioButton, QComboBox
from PyQt5.QtGui import QFont, QPixmap
from Classes.ComboBox import SelectDilutionType
from Classes.ErrorMessageBox import ErrorMessageBox
import ExcelAutomators.elisa_standards as es
from settings import *

class ElisaStandardsPage(QWidget):
    def __init__(self,parent):
        super().__init__(parent)
        self.vertical_layout = QVBoxLayout()
        self.setLayout(self.vertical_layout)
        
        self.switch_pages_button = QPushButton("Click me to switch pages")
        self.vertical_layout.addWidget(self.switch_pages_button)
    
    
        self.app_description = QLabel('Automates calculation of concentration of set of\nunknowns from a set of standards using Linear Regression')
        self.app_description.setFont(QFont('Helvetica', 12))
        self.vertical_layout.addWidget(self.app_description)
        
        self.logo_image = QPixmap('./Images/logo2.png')
        self.logo_label = QLabel(self)
        self.logo_label.setPixmap(self.logo_image.scaled(600,450))
        self.vertical_layout.addWidget(self.logo_label)
        
        self.prefix = QLineEdit()
        self.prefix.setPlaceholderText("Enter the prefix of the sample if there is one, i.e 'MIR', 'iSpecimen', 'Pharmacy Recruits', etc.")
        self.vertical_layout.addWidget(self.prefix)
        
        self.starting_sample_num = QLineEdit()
        self.starting_sample_num.setPlaceholderText('Enter first sample number here')
        self.vertical_layout.addWidget(self.starting_sample_num)
        
        
        self.last_sample_num = QLineEdit()
        self.last_sample_num.setPlaceholderText('Enter the last sample number here')
        self.vertical_layout.addWidget(self.last_sample_num)
        
        self.exclude_nums = QLineEdit()
        self.exclude_nums.setPlaceholderText("Enter the samples you don't want to include in the range here. i.e 111-117,113")
        self.vertical_layout.addWidget(self.exclude_nums)
        
        self.dilution_combobox = SelectDilutionType(self)
        self.vertical_layout.addWidget(self.dilution_combobox)
        
        self.duplicates = QRadioButton("Duplicates")
        self.vertical_layout.addWidget(self.duplicates)
        
        self.triplcates = QRadioButton("Triplicates")
        self.vertical_layout.addWidget(self.triplcates)
        
        self.select_file_button = QPushButton('Select Raw Data File')
        self.vertical_layout.addWidget(self.select_file_button)
        
        
        self.select_file_destination_button = QPushButton('Select File Destination')
        self.vertical_layout.addWidget(self.select_file_destination_button)
        
        
        self.process = QPushButton("Process ELISA Data")
        self.vertical_layout.addWidget(self.process)
        
        
        self.switch_pages_button.clicked.connect(lambda:parent.setCurrentIndex(1 if parent.currentIndex() != 1 else 0))
        self.select_file_button.clicked.connect(self.open_file_selector)
        self.select_file_destination_button.clicked.connect(self.select_file_destination)
        self.process.clicked.connect(self.process_elisa)
        
        self.raw_data_filepath = False
        self.destination_filepath = False
    
    def open_file_selector(self):
        self.raw_data_filepath = QFileDialog(filter=TEXT_EXT).getOpenFileName(self, 'Select File',filter='Text Files(*.txt)')[0]
    
    def select_file_destination(self):
        self.destination_filepath = QFileDialog.getExistingDirectory(self,'Select Directory')
    
    def process_elisa(self):
        if not self.raw_data_filepath: 
            ErrorMessageBox("No File Selected")
            return
        if not self.destination_filepath: 
            ErrorMessageBox("No Destination Selected")
            return
        prefix = self.prefix.text()
        samples = self.sample_cohort(self.starting_sample_num.text(), self.last_sample_num.text(), self.exclude_nums.text().split(","))
        starting_conc = self.starting_concentration.text()
        units = self.units.text()
        dilution_factor = self.dilution_factor.text()
        dilutions = self.dilutions.text()
        replicates = "2" if self.duplicates.isChecked() else "3"
        es.main(self.raw_data_filepath, self.destination_filepath, samples, starting_conc, units, dilution_factor, dilutions,replicates, prefix=prefix)
### Imported from elisa_main.py

    def sample_cohort(self, first:str, last:str, excluded:list[str])->list[int]:
        '''Creates a list of Samples, makes the assumption that the entire string can be coverted into an integer'''
        return [num for num in range(int(first), int(last)+1) if num not in self.format_excluded_samples(excluded)]

    def format_excluded_samples(self, excluded:list[str])->list[int]:
        '''Returns a new list of excluded numbers'''
        if excluded[0] == '': return []
        to_extend = []
        to_remove = []
        to_exclude = [*excluded]
        
        for item in to_exclude:
            if "-" in item:
                splitted = item.split("-")
                start = int(splitted[0])
                end = int(splitted[-1])+1
                to_extend.extend(range(start, end))
                to_remove.append(item)
        
        for _ in to_remove: to_exclude.remove(_)
        to_exclude.extend(to_extend)
        return [int(num) for num in to_exclude]

    def remove_prefix():
        pass
        