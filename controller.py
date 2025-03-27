from PyQt5 import QtWidgets
from my_class import show_error

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

