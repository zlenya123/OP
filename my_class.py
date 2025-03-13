import datetime
from PyQt5 import QtWidgets

def read_file(file_path):
    with open(file_path, 'r', encoding='cp1251') as file:
        return file.readlines()


def create_products(lines):
    products = []
    for line in lines:
        try:
            product = Product.create_from_line(line)
            if product:
                products.append(product)
        except (ValueError, IndexError) as e:
            show_error(f"Ошибка обработки строки: {line.strip()}\nОшибка: {e}")
    return products



def show_error(message):
    error_dialog = QtWidgets.QMessageBox()
    error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
    error_dialog.setWindowTitle('Ошибка')
    error_dialog.setText(message)
    error_dialog.exec_()


def validate_date(date_str):
    try:
        datetime.datetime.strptime(date_str, '%d.%m.%Y')
        return True
    except ValueError:
        return False

class Product:
    def __init__(self, status, date, name, quantity):
        self.status = status
        self.date = date
        self.name = name
        self.quantity = int(quantity)

    def __str__(self):
        return f"{self.status.capitalize()} товар: {self.name}, Дата: {self.date}, Количество: {self.quantity}"

    @staticmethod
    def create_from_line(line):
        data = line.strip().split(";")
        if len(data) < 6:
            raise ValueError("Недостаточно данных в строке.")

        status = data[0]
        date = data[1]
        if not validate_date(date):
            raise ValueError(f"Некорректная дата: {date}")

        if status == "Списанный товар":
            _, date, name, quantity, reason, product_id = data
            if not quantity.isdigit() or not product_id.isdigit():
                raise ValueError("Количество и ID должны быть числами.")
            return WrittenOffProduct(date, name, quantity, reason, product_id)

        elif status == "Поступивший товар":
            _, date, name, quantity, cost, product_id = data
            try:
                float(cost)
            except ValueError:
                raise ValueError("Стоимость должна быть числом.")
            if not quantity.isdigit() or not product_id.isdigit():
                raise ValueError("Количество и ID должны быть числами.")
            return IncomingProduct(date, name, quantity, cost, product_id)

        else:
            raise ValueError(f"Неизвестный статус товара: {status}")



class WrittenOffProduct(Product):
    def __init__(self, date, name, quantity, reason, product_id):
        super().__init__("Списанный товар", date, name, quantity)
        self.reason = reason
        self.product_id = int(product_id)

    def __str__(self):
        base_info = super().__str__()
        return f"{base_info}, Причина списания: {self.reason}, ID товара: {self.product_id}"


class IncomingProduct(Product):
    def __init__(self, date, name, quantity, cost, product_id):
        super().__init__("Поступивший товар", date, name, quantity)
        self.cost = float(cost)
        self.product_id = int(product_id)

    def __str__(self):
        base_info = super().__str__()
        return f"{base_info}, Стоимость: {self.cost:.2f}, ID товара: {self.product_id}"

class AddProductDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Добавить товар')
        self.setGeometry(200, 200, 400, 300)
        self.init_ui()

    def init_ui(self):
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
        if not validate_date(date):
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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Статус', 'Дата', 'Наименование', 'Количество', 'Дополнительно', 'ID'])
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
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

    def select_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Открыть файл', '', 'CSV файлы (*.csv);;Все файлы (*)')
        if file_path:
            lines = read_file(file_path)
            self.products = create_products(lines)
            self.populate_table()
    

    def populate_table(self):
        self.table.setRowCount(0)
        for product in self.products:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QtWidgets.QTableWidgetItem(product.status))
            self.table.setItem(row_position, 1, QtWidgets.QTableWidgetItem(product.date))
            self.table.setItem(row_position, 2, QtWidgets.QTableWidgetItem(product.name))
            self.table.setItem(row_position, 3, QtWidgets.QTableWidgetItem(str(product.quantity)))
            extra_info = str(getattr(product, 'reason', getattr(product, 'cost', '')))
            self.table.setItem(row_position, 4, QtWidgets.QTableWidgetItem(extra_info))
            self.table.setItem(row_position, 5, QtWidgets.QTableWidgetItem(str(product.product_id)))

    def add_product(self):
        dialog = AddProductDialog()
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            product = dialog.get_product_data()
            if product:
                self.products.append(product)
                self.populate_table()

    def delete_selected(self):
        selected_rows = set(index.row() for index in self.table.selectedIndexes())
        for row in selected_rows:
            del self.products[row]
            self.table.removeRow(row)