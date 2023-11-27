from PyQt5.QtWidgets import QMessageBox
class ErrorMessageBox(QMessageBox):
    def __init__(self, message:str):
        '''Creates an instance of an error pop up with the text passed as the argument'''
        super().__init__()
        self.setIcon(QMessageBox.Critical)
        self.setText(message)
        self.setWindowTitle('Error')
        self.exec_()