from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFileDialog, QPushButton, QRadioButton, QCheckBox
from PyQt5.QtGui import QFont, QPixmap
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
        self.switch_pages_button.clicked.connect(lambda:parent.setCurrentIndex(1 if parent.currentIndex() != 1 else 0))
    
    
        self.app_description = QLabel('Automates calculation of concentration of set of\nunknowns from a set of standards using Linear Regression')
        self.app_description.setFont(QFont('Helvetica', 12))
        self.vertical_layout.addWidget(self.app_description)
        
        self.logo_label = QLabel(self)
        self.logo_label.setPixmap(QPixmap('./Images/logo2.png').scaled(600,450))
        self.vertical_layout.addWidget(self.logo_label)
        
        self.linear_reg = QRadioButton("Linear Regression", self)
        self.vertical_layout.addWidget(self.linear_reg)
        
        self.log_reg = QRadioButton("Logarithmic Regression", self)
        self.vertical_layout.addWidget(self.log_reg)
        
        self.make_excel = QCheckBox("Make Excel File?", self)
        self.vertical_layout.addWidget(self.make_excel)
        
        self.select_file_button = QPushButton('Select Raw Data File')
        self.vertical_layout.addWidget(self.select_file_button)
        self.select_file_button.clicked.connect(self.select_data_file)

        self.select_template_button = QPushButton("Select Template File")
        self.vertical_layout.addWidget(self.select_template_button)
        self.select_template_button.clicked.connect(self.select_template_file)
        
        self.select_file_destination_button = QPushButton('Select File Destination')
        self.vertical_layout.addWidget(self.select_file_destination_button)
        self.select_file_destination_button.clicked.connect(self.select_destination)
        
        self.process = QPushButton("Process ELISA Data")
        self.vertical_layout.addWidget(self.process)
        self.process.clicked.connect(self.process_elisa)
        
        self.data_filepath = ""
        self.destination_filepath = ""
    
    def select_data_file(self):
        self.data_filepath = QFileDialog(filter=".txt").getOpenFileName(self, 'Select File',filter='*.txt')[0]
    
    def select_destination(self):
        self.destination_filepath = QFileDialog.getExistingDirectory(self,'Select Directory')

    def select_template_file(self):
        self.template_filepath = QFileDialog(filter=".csv").getOpenFileName(self, 'Select File',filter='*.csv')[0]
    
    def process_elisa(self):

        if not self.data_filepath: 
            ErrorMessageBox("No Data Selected")
            return
        if not self.template_filepath: 
            ErrorMessageBox("No Template Selected")
            return
        if not self.destination_filepath: 
            ErrorMessageBox("No Destination Selected")
            return

        es.main(self.data_filepath, self.template_filepath, self.destination_filepath, linear= self.linear_reg.isChecked(), logarthimic= self.log_reg.isChecked(), make_excel = self.make_excel.isChecked())
       