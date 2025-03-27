import datetime
import logging
from PyQt5 import QtWidgets

def generate_log_filename():
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    return f'app_{timestamp}.log'

log_filename = generate_log_filename()

logging.basicConfig(level=logging.ERROR, filename=log_filename, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

def show_error(message):
    error_dialog = QtWidgets.QMessageBox()
    error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
    error_dialog.setWindowTitle('Ошибка')
    error_dialog.setText(message)
    error_dialog.exec_()