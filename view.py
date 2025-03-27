from PyQt5 import QtWidgets
import datetime
from my_class import show_error
from controller import TableManager, FileLoader, ProductController
from model import Product, WrittenOffProduct, IncomingProduct, ProductManager

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
            ProductManager.write_file(self.products)

    def delete_selected(self):
        selected_rows = set(index.row() for index in self.table.selectedIndexes())
        self.product_controller.delete_selected(selected_rows)