import datetime

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
            with open(file_path, 'r', encoding='cp1251') as file:
                return file.readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        except UnicodeDecodeError:
            raise UnicodeDecodeError(f"Ошибка декодирования файла: {file_path}")

    @staticmethod
    def create_products(lines):
        products = []
        for line in lines:
            try:
                product = Product.create_from_line(line)
                products.append(product)
            except ValueError as e:
                print(f"Ошибка обработки строки: {line.strip()}\nОшибка: {e}")  # Вместо логирования выводим в консоль для тестов
        return products