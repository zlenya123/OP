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

class Product:
    def __init__(self, status, date, name, quantity):
        self.status = status
        self.date = date
        self.name = name
        self.quantity = int(quantity)

    def __str__(self):
        return f"{self.status} товар: {self.name}, Дата: {self.date}, Количество: {self.quantity}"

    @staticmethod
    def create_from_line(line):
        data = line.strip().split(";")
        if len(data) < 6:
            raise ValueError("Недостаточно данных в строке.")
        
        status, date, name, quantity, extra, product_id = data

        try:
            datetime.datetime.strptime(date, '%d.%m.%Y')
        except ValueError:
            raise ValueError(f"Некорректная дата: {date}")

        if status == "Списанный товар":
            return WrittenOffProduct(date, name, quantity, extra, product_id)
        elif status == "Поступивший товар":
            return IncomingProduct(date, name, quantity, extra, product_id)
        else:
            raise ValueError(f"Неизвестный статус товара: {status}")

class WrittenOffProduct(Product):
    def __init__(self, date, name, quantity, reason, product_id):
        super().__init__("Списанный товар", date, name, quantity)
        self.reason = reason
        self.product_id = int(product_id)

class IncomingProduct(Product):
    def __init__(self, date, name, quantity, cost, product_id):
        super().__init__("Поступивший товар", date, name, quantity)
        self.cost = float(cost)
        self.product_id = int(product_id)

class ProductManager:
    @staticmethod
    def read_file(file_path):
        try:
            with open(file_path, 'r') as file:
                return file.readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл не найден: {file_path}")

    @staticmethod
    def create_products(lines):
        products = []
        for line in lines:
            try:
                product = Product.create_from_line(line)
                products.append(product)
            except ValueError as e:
                logging.error(f"Ошибка обработки строки: {line.strip()}\nОшибка: {e}")
                show_error(f"Ошибка обработки строки: {line.strip()}\nОшибка: {e}")
        return products

class AddProductDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Добавить товар')
        self.setGeometry(200, 200, 400, 300)
        layout = QtWidgets.QFormLayout()

        self.date_edit = QtWidgets.QLineEdit(datetime.datetime.now().strftime('%d.%m.%Y'))
        self.name_edit = QtWidgets.QLineEdit()
        self.quantity_edit = QtWidgets.QSpinBox()
        self.quantity_edit.setMaximum(10000)

        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(['Поступивший товар', 'Списанный товар'])

        self.extra_edit = QtWidgets.QLineEdit()
        self.id_edit = QtWidgets.QSpinBox()
        self.id_edit.setMaximum(100000)

        layout.addRow('Дата (дд.мм.гггг):', self.date_edit)
        layout.addRow('Наименование:', self.name_edit)
        layout.addRow('Количество:', self.quantity_edit)
        layout.addRow('Тип товара:', self.type_combo)
        layout.addRow('Стоимость/Причина:', self.extra_edit)
        layout.addRow('ID:', self.id_edit)

        self.add_button = QtWidgets.QPushButton('Добавить')
        self.add_button.clicked.connect(self.validate_and_accept)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def validate_and_accept(self):
        date = self.date_edit.text()
        try:
            datetime.datetime.strptime(date, '%d.%m.%Y')
        except:
            show_error('Некорректный формат даты. Используйте дд.мм.гггг.')
            return
        self.accept()

    def get_product_data(self):
        product_type = self.type_combo.currentText()
        date = self.date_edit.text()
        name = self.name_edit.text()
        quantity = self.quantity_edit.value()
        extra = self.extra_edit.text()
        product_id = self.id_edit.value()

        if product_type == 'Поступивший товар':
            try:
                cost = float(extra)
                return IncomingProduct(date, name, quantity, cost, product_id)
            except ValueError:
                show_error('Стоимость должна быть числом.')
                return
        else:
            return WrittenOffProduct(date, name, quantity, extra, product_id)

class TableManager:
    def __init__(self, table_widget):
        self.table_widget = table_widget
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels(['Статус', 'Дата', 'Наименование', 'Количество', 'Дополнительно', 'ID'])

    def populate_table(self, products):
        self.table_widget.setRowCount(0)
        for product in products:
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)
            self.table_widget.setItem(row_position, 0, QtWidgets.QTableWidgetItem(product.status))
            self.table_widget.setItem(row_position, 1, QtWidgets.QTableWidgetItem(product.date))
            self.table_widget.setItem(row_position, 2, QtWidgets.QTableWidgetItem(product.name))
            self.table_widget.setItem(row_position, 3, QtWidgets.QTableWidgetItem(str(product.quantity)))
            extra_info = str(getattr(product, 'reason', getattr(product, 'cost', '')))
            self.table_widget.setItem(row_position, 4, QtWidgets.QTableWidgetItem(extra_info))
            self.table_widget.setItem(row_position, 5, QtWidgets.QTableWidgetItem(str(product.product_id)))

    def remove_row(self, row):
        self.table_widget.removeRow(row)

class FileLoader:
    def __init__(self, product_manager):
        self.product_manager = product_manager

    def load_file(self, file_path):
        lines = self.product_manager.read_file(file_path)
        return self.product_manager.create_products(lines)

class ProductController:
    def __init__(self, products, table_manager, file_loader):
        self.products = products
        self.table_manager = table_manager
        self.file_loader = file_loader

    def add_product(self, product):
        if product:
            self.products.append(product)
            self.table_manager.populate_table(self.products)

    def delete_selected(self, selected_rows):
        for row in sorted(selected_rows, reverse=True):
            del self.products[row]
            self.table_manager.remove_row(row)

    def load_products_from_file(self, file_path):
        try:
            self.products = self.file_loader.load_file(file_path)
            self.table_manager.populate_table(self.products)
        except Exception as e:
            show_error(f"Ошибка загрузки файла: {e}")

class ProductApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.products = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Обработка данных о товарах')
        self.setGeometry(100, 100, 700, 400)

        layout = QtWidgets.QVBoxLayout()
        self.table = QtWidgets.QTableWidget()
        self.table_manager = TableManager(self.table)
        layout.addWidget(self.table)

        button_layout = QtWidgets.QHBoxLayout()

        self.load_button = QtWidgets.QPushButton('Загрузить файл')
        self.load_button.clicked.connect(self.select_file)
        button_layout.addWidget(self.load_button)

        self.add_button = QtWidgets.QPushButton('Добавить товар')
        self.add_button.clicked.connect(self.add_product)
        button_layout.addWidget(self.add_button)

        self.delete_button = QtWidgets.QPushButton('Удалить выбранное')
        self.delete_button.clicked.connect(self.delete_selected)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.product_manager = ProductManager()
        self.file_loader = FileLoader(self.product_manager)
        self.product_controller = ProductController(self.products, self.table_manager, self.file_loader)

    def select_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Открыть файл', '', 'CSV файлы (*.csv);;Все файлы (*)')
        if file_path:
            self.product_controller.load_products_from_file(file_path)

    def add_product(self):
        dialog = AddProductDialog()
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            product = dialog.get_product_data()
            self.product_controller.add_product(product)

    def delete_selected(self):
        selected_rows = set(index.row() for index in self.table.selectedIndexes())
        self.product_controller.delete_selected(selected_rows)