from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFileDialog, QPushButton, QLineEdit, QMessageBox, QComboBox
from PyQt5.QtGui import QFont, QPixmap
from Classes.ErrorMessageBox import ErrorMessageBox
from settings import *
import ExcelAutomators.elisa_controls as em
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
       
        self.select_file_button = QPushButton('Select Raw Data File')
        self.template_file_button = QPushButton('Select Template File')
        self.elisa_button = QPushButton('Process ELISA Data')
        self.neutralization_assay_button = QPushButton("Process Neutralization Assay Data")
        select_file_destination = QPushButton('Select File Destination')
        self.logo_image = QPixmap('./Images/logo2.png')
        self.logo_label = QLabel()
        self.logo_label.setPixmap(self.logo_image.scaled(600,450))
        self.cohort_combobox = CohortSelectionComboBox()
        self.button = QPushButton("Click me to switch pages")
        self.button.clicked.connect(lambda:parent.setCurrentIndex(1 if parent.currentIndex() != 1 else 0))
        
        self.template_file_button.clicked.connect(self.select_template)
        self.select_file_button.clicked.connect(self.open_file_selector)
        self.elisa_button.clicked.connect(self.process_elisa_data)
        self.neutralization_assay_button.clicked.connect(self.process_neutralization_assay_data)
        select_file_destination.clicked.connect(self.select_file_destination)
        
        self.layout().addWidget(self.button)
        self.layout().addWidget(self.app_description)
        self.layout().addWidget(self.logo_label)
        self.layout().addWidget(self.cohort_combobox)
        self.layout().addWidget(self.select_file_button)
        self.layout().addWidget(self.template_file_button)
        self.layout().addWidget(select_file_destination)
        # self.layout().addWidget(self.elisa_button)
        self.layout().addWidget(self.neutralization_assay_button)
        
        self.template_filepath = False
        self.raw_data_filepath = False
        self.destination_filepath = False
    
    def select_template(self)->None:
        self.template_filepath = QFileDialog(filter=".csv").getOpenFileName(self, 'Select File',filter='Text Files(*.csv)')[0]
    
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
        
        if not self.template_filepath:
            ErrorMessageBox("No Template File Selected")
            return
        
        try:
            em.main(self.raw_data_filepath, self.destination_filepath)
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
                nam.main(self.raw_data_filepath, self.template_filepath, self.destination_filepath)
        else:
            try:
                selected_cohort = self.cohort_combobox.currentText().split("->")[0]
                nam.neutralization_assay_singlets(self.raw_data_filepath, self.destination_filepath, cohort=selected_cohort)
            except AttributeError:
                pass

### End of import