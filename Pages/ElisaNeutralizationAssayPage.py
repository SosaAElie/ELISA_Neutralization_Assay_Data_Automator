from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFileDialog, QPushButton, QLineEdit, QMessageBox, QComboBox
from PyQt5.QtGui import QFont, QPixmap
from Classes.ErrorMessageBox import ErrorMessageBox
from settings import *
import ExcelAutomators.elisa_main as em
import ExcelAutomators.neutralization_assay_main as nam
import sqlite3

class CohortSelectionComboBox(QComboBox):

    def __init__(self):
        super().__init__()
        self.query_sqlite3_db()
        
    def query_sqlite3_db(self):
        self.addItem("")
        table_prefix = "cohort"
        cur = sqlite3.connect("Databases/NeutralizationAssayDB.sqlite").cursor()
        for num in range(1,24):
            cur.execute(f"SELECT label FROM {table_prefix}{num} WHERE label NOT LIKE 'MIR%'")
            data = cur.fetchall()
            first_sample = data[0][0]
            last_sample = data[-1][0]
            self.addItem(f"{table_prefix}{num}-> Sample Numbers({first_sample} - {last_sample})")
            

class ElisaNeutralizationAssayPage(QWidget):
    def __init__(self,parent):
        super().__init__(parent)
        
        self.setLayout(QVBoxLayout())
        self.app_description = QLabel('Takes in the text data from the Plate Reader\n and returns an Excel and a Prism file')
        self.app_description.setFont(QFont('Helvetica', 12))
        self.start_sample_column = QLineEdit()
        self.start_sample_column.setPlaceholderText('Set start column for samples, default is "1" ')
        self.start_control_column = QLineEdit()
        self.start_control_column.setPlaceholderText('Set start column for controls, default is "9" ')
        self.starting_sample_num = QLineEdit()
        self.starting_sample_num.setPlaceholderText('Enter first sample number here')
        self.last_sample_num = QLineEdit()
        self.last_sample_num.setPlaceholderText('Enter the last sample number here')
        self.exclude_nums = QLineEdit()
        self.exclude_nums.setPlaceholderText("Enter the samples you don't want to include in the range here. i.e 111-117,113")
        self.starting_control_num = QLineEdit()
        self.starting_control_num.setPlaceholderText('Enter the first control here i.e MIR013')
        self.last_control_num = QLineEdit()
        self.last_control_num.setPlaceholderText('Enter the last control here i.e MIR027')
        self.excluded_controls = QLineEdit()
        self.excluded_controls.setPlaceholderText('Enter any excluded controls here i.e MIR015-MIR018,MIR001')
        self.select_file_button = QPushButton('Select Raw Data File')
        self.elisa_button = QPushButton('Process ELISA Data')
        self.neutralization_assay_button = QPushButton("Process Neutralization Assay Data")
        select_file_destination = QPushButton('Select File Destination')
        self.logo_image = QPixmap('./Images/logo2.png')
        self.logo_label = QLabel()
        self.logo_label.setPixmap(self.logo_image.scaled(600,450))
        self.cohort_combobox = CohortSelectionComboBox()
        self.button = QPushButton("Click me to switch pages")
        self.button.clicked.connect(lambda:parent.setCurrentIndex(1 if parent.currentIndex() != 1 else 0))
        
        self.select_file_button.clicked.connect(self.open_file_selector)
        self.elisa_button.clicked.connect(self.process_elisa_data)
        self.neutralization_assay_button.clicked.connect(self.process_neutralization_assay_data)
        select_file_destination.clicked.connect(self.select_file_destination)
        
        self.layout().addWidget(self.button)
        self.layout().addWidget(self.app_description)
        self.layout().addWidget(self.logo_label)
        self.layout().addWidget(self.cohort_combobox)
        self.layout().addWidget(self.starting_sample_num)
        self.layout().addWidget(self.last_sample_num)
        self.layout().addWidget(self.exclude_nums)
        self.layout().addWidget(self.starting_control_num)
        self.layout().addWidget(self.last_control_num)
        self.layout().addWidget(self.excluded_controls)
        self.layout().addWidget(self.start_sample_column)
        self.layout().addWidget(self.start_control_column)
        self.layout().addWidget(self.select_file_button)
        self.layout().addWidget(select_file_destination)
        self.layout().addWidget(self.elisa_button)
        self.layout().addWidget(self.neutralization_assay_button)
        
        self.raw_data_filepath = False
        self.destination_filepath = False
        
        # self.show()
    
    def open_file_selector(self):
        self.raw_data_filepath = QFileDialog(filter=TEXT_EXT).getOpenFileName(self, 'Select File',filter='Text Files(*.txt)')[0]
    
    def select_file_destination(self):
        self.destination_filepath = QFileDialog.getExistingDirectory(self,'Select Directory')
    
    def process_elisa_data(self):
        if not self.raw_data_filepath:
            ErrorMessageBox('No File Selected')
            return
        
        if not self.destination_filepath:
            ErrorMessageBox('No Folder Selected')
            return
        
        try:
            sample_cohort = self.sample_cohort(self.starting_sample_num.text(), self.last_sample_num.text(), self.exclude_nums.text().split(','))
            control_cohort = self.control_cohort(self.starting_control_num.text(),self.last_control_num.text(),self.excluded_controls.text().split(','))
            em.main(self.raw_data_filepath, self.destination_filepath, sample_cohort, control_cohort)
        except AttributeError:
            pass
    
    def process_neutralization_assay_data(self):
        if not self.raw_data_filepath:
            ErrorMessageBox('No File Selected')
            return
        
        if not self.destination_filepath:
            ErrorMessageBox('No Folder Selected')
            return
        
        if not self.cohort_combobox.currentIndex():
            try:
                sample_cohort = self.sample_cohort(self.starting_sample_num.text(), self.last_sample_num.text(), self.exclude_nums.text().split(','))
                control_cohort = self.control_cohort(self.starting_control_num.text(),self.last_control_num.text(),self.excluded_controls.text().split(','))
                nam.neutralization_assay_singlets(self.raw_data_filepath, self.destination_filepath, None, sample_cohort, control_cohort)
            except AttributeError:
                print("Error")
                pass
        else:
            try:
                selected_cohort = self.cohort_combobox.currentText().split("->")[0]
                nam.neutralization_assay_singlets(self.raw_data_filepath, self.destination_filepath, cohort=selected_cohort)
            except AttributeError:
                pass

### Imported from elisa_main.py

    def sample_cohort(self, first:str, last:str, excluded:list[str])->list[int]:
        '''Creates a list of Samples, makes the assumption that the entire string can be coverted into an integer'''
        return [num for num in range(int(first), int(last)+1) if num not in self.format_excluded_samples(excluded)]

    def control_cohort(self, first:str, last:str, excluded:list[str])->list[str]:
        '''Creates a list of Samples, makes the assumption that first 3 characters are not convertible into an integer'''
        control_format = lambda x: f"0{x}"if x < 10 else x
        control_prefix = first[:4]
        start = int(first[3:])
        end = int(last[3:])+1
        return [f'{control_prefix}{control_format(num)}' for num in range(start, end) if num not in self.format_excluded_controls(excluded)]

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

    def format_excluded_controls(self, excluded:list[str])->list[int]:
        '''Assumes the first 3 characters in the string cannot be converted to an integer, returns same as format_exlcuded_samples'''
        if excluded[0] == '': return []
        to_extend = []
        to_remove = []
        no_sep = []
        to_exclude = [*excluded]
        
        for item in to_exclude:
            if "-" in item:
                splitted = item.split("-")
                start = int(splitted[0][3:])
                end = int(splitted[-1][3:])+1
                to_extend.extend(range(start, end))
                to_remove.append(item)
            else:
                to_remove.append(item)
                no_sep.append(item)
        
        for _ in to_remove:to_exclude.remove(_)
        to_exclude.extend([int(item[3:]) for item in no_sep])
        to_exclude.extend(to_extend)
        
        return to_exclude

### End of import