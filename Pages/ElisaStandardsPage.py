from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFileDialog, QPushButton, QLineEdit, QRadioButton
from PyQt5.QtGui import QFont, QPixmap
from Classes.ErrorMessageBox import ErrorMessageBox
import ExcelAutomators.elisa_standards as es
from settings import *

class ElisaStandardsPage(QWidget):
    def __init__(self,parent):
        super().__init__(parent)
        
        self.setLayout(QVBoxLayout())
        self.app_description = QLabel('Automates calculation of concentration of set of\n unknowns from a set of standards using Linear Regression')
        self.app_description.setFont(QFont('Helvetica', 12))
        self.starting_sample_num = QLineEdit()
        self.starting_sample_num.setPlaceholderText('Enter first sample number here')
        self.last_sample_num = QLineEdit()
        self.last_sample_num.setPlaceholderText('Enter the last sample number here')
        self.exclude_nums = QLineEdit()
        self.exclude_nums.setPlaceholderText("Enter the samples you don't want to include in the range here. i.e 111-117,113")
        
        self.starting_concentration = QLineEdit()
        self.starting_concentration.setPlaceholderText("Entering the starting concentration (number only)")
        self.units = QLineEdit()
        self.units.setPlaceholderText("Enter the units of the starting concentration")
        self.dilution_factor = QLineEdit()
        self.dilution_factor.setPlaceholderText("Enter the dilution factor, i.e 2,5,10")
        self.dilutions = QLineEdit()
        self.dilutions.setPlaceholderText("Enter the number of times the standards were diluted")
        
        
        self.select_file_button = QPushButton('Select Raw Data File')
        self.select_file_destination_button = QPushButton('Select File Destination')
        self.switch_pages_button = QPushButton("Click me to switch pages")
        self.process = QPushButton("Process ELISA Data")
        
        self.duplicates = QRadioButton("Duplicates")
        self.triplcates = QRadioButton("Triplicates")
        self.logo_image = QPixmap('./Images/logo2.png')
        self.logo_label = QLabel()
        self.logo_label.setPixmap(self.logo_image.scaled(600,450))
        
        
        self.switch_pages_button.clicked.connect(lambda:parent.setCurrentIndex(1 if parent.currentIndex() != 1 else 0))
        self.select_file_button.clicked.connect(self.open_file_selector)
        self.select_file_destination_button.clicked.connect(self.select_file_destination)
        self.process.clicked.connect(self.process_elisa)
        
        self.layout().addWidget(self.switch_pages_button)
        self.layout().addWidget(self.app_description)
        self.layout().addWidget(self.logo_label)
        self.layout().addWidget(self.starting_sample_num)
        self.layout().addWidget(self.last_sample_num)
        self.layout().addWidget(self.exclude_nums)
        self.layout().addWidget(self.starting_concentration)
        self.layout().addWidget(self.units)
        self.layout().addWidget(self.dilution_factor)
        self.layout().addWidget(self.dilutions)
        
        
        self.layout().addWidget(self.duplicates)
        self.layout().addWidget(self.triplcates)
        self.layout().addWidget(self.select_file_button)
        self.layout().addWidget(self.select_file_destination_button)
        self.layout().addWidget(self.process)
        
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
        #print(self.starting_sample_num.text(), self.last_sample_num.text(), self.exclude_nums.text())
        samples = self.sample_cohort(self.starting_sample_num.text(), self.last_sample_num.text(), self.exclude_nums.text().split(","))
        starting_conc = self.starting_concentration.text()
        units = self.units.text()
        dilution_factor = self.dilution_factor.text()
        dilutions = self.dilutions.text()
        replicates = "2" if self.duplicates.isChecked() else "3"
        #print(self.raw_data_filepath, self.destination_filepath, samples, starting_conc, units, dilution_factor, dilutions,replicates)
        es.main(self.raw_data_filepath, self.destination_filepath, samples, starting_conc, units, dilution_factor, dilutions,replicates)
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

        
        