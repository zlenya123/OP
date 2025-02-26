class Product:
    def __init__(self, status, date, name, quantity):
        self.status = status
        self.date = date
        self.name = name
        self.quantity = int(quantity)

    def __str__(self):
        return f"{self.status.capitalize()} товар: {self.name}, Дата: {self.date}, Количество: {self.quantity}"

    @classmethod
    def create_from_line(cls, line):
        data = line.strip().split(";")
        if data[0] == "Cписанный товар":
            return WrittenOffProduct(*data[1:])
        elif data[0] == "Потсупивший товар":
            return IncomingProduct(*data[1:])


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
        super().__init__("Потсупивший товар", date, name, quantity)
        self.cost = float(cost)
        self.product_id = int(product_id)

    def __str__(self):
        base_info = super().__str__()
        return f"{base_info}, Стоимость: {self.cost:.2f}, ID товара: {self.product_id}"


def main():
    file_path = 'in.csv'
    written_off_products = []
    incoming_products = []

    with open(file_path, 'r', encoding='cp1251') as file:
        for line in file:
            product = Product.create_from_line(line)
            if isinstance(product, WrittenOffProduct):
                written_off_products.append(product)
            elif isinstance(product, IncomingProduct):
                incoming_products.append(product)

    print("Списанные товары:")
    for product in written_off_products:
        print(product)

    print("\nПоступившие товары:")
    for product in incoming_products:
        print(product)


if __name__ == "__main__":
    main()
