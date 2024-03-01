from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFileDialog, QPushButton
from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QPixmap
from Classes.ErrorMessageBox import ErrorMessageBox
from Classes.FileSelector import FileSelector
import ExcelAutomators.elisa_standards as es
import asyncio

class ElisaStandardsPage(QWidget):
    def __init__(self,parent):
        super().__init__(parent)

        self.file_selectors:list[FileSelector] = []

        self.vertical_layout = QVBoxLayout()
        self.setLayout(self.vertical_layout)
        
        self.switch_pages_button = QPushButton("Click me to switch pages")
        self.vertical_layout.addWidget(self.switch_pages_button)
        self.switch_pages_button.clicked.connect(lambda:parent.setCurrentIndex(1 if parent.currentIndex() != 1 else 0))
    
        
        self.app_description = QLabel('Interpolates Concentration of Unknowns From a Set of Known Standards')
        self.app_description.setFont(QFont('Helvetica', 12))
        self.vertical_layout.addWidget(self.app_description, alignment=QtCore.Qt.AlignCenter)
        
        width = round(self.window().width()*1.25)
        height = round(self.window().height()*1.25)

        logo = QLabel(self)
        logo.setPixmap(QPixmap('./Images/logo2.png').scaled(width, height))
        self.vertical_layout.addWidget(logo, alignment=QtCore.Qt.AlignCenter)
        
        
        file_selector = FileSelector(self)
        self.vertical_layout.addWidget(file_selector)
        self.file_selectors.append(file_selector)
        
        self.add_button = QPushButton("Add", self, clicked = self.add_file_selectors)
        self.vertical_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Remove", self, clicked = self.remove_file_selector)
        self.vertical_layout.addWidget(self.remove_button)


        self.select_file_destination_button = QPushButton('Select File Destination')
        self.vertical_layout.addWidget(self.select_file_destination_button)
        self.select_file_destination_button.clicked.connect(self.select_destination)
        
       
        self.process = QPushButton("Process Data")
        self.vertical_layout.addWidget(self.process)
        self.process.clicked.connect(lambda:asyncio.run(self.process_elisa()))
        self.destination_filepath = ""

    def select_destination(self):
        self.destination_filepath = QFileDialog.getExistingDirectory(self,'Select Directory')
    
    def add_file_selectors(self)->None:
        index = self.layout().indexOf(self.file_selectors[-1])+1
        file_selector = FileSelector(self)
        self.vertical_layout.insertWidget(index,file_selector)
        self.file_selectors.append(file_selector)

    def remove_file_selector(self)->None:
        if len(self.file_selectors) > 1:
            self.vertical_layout.removeWidget(self.file_selectors.pop())
        
    async def process_elisa(self):

        if not self.destination_filepath: 
            ErrorMessageBox("No Destination Selected")
            return
        
        selected_files = [file_selector.get_selection() for file_selector in self.file_selectors]
        coroutines = []
        for selected in selected_files:
            if len(selected) == 0: return
            else: 
                raw, template, regression, excel, title = selected
                coroutines.append(es.main(raw, template, self.destination_filepath, regression, excel, title))
        await asyncio.gather(*coroutines)
       