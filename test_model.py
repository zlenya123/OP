import unittest
from my_model import Product, WrittenOffProduct, IncomingProduct, ProductManager

class TestProduct(unittest.TestCase):
    def test_create_from_line_written_off(self):
        line = "Списанный товар;01.01.2023;Товар A;10;Причина;123"
        product = Product.create_from_line(line)
        self.assertIsInstance(product, WrittenOffProduct)
        self.assertEqual(product.status, "Списанный товар")
        self.assertEqual(product.date, "01.01.2023")
        self.assertEqual(product.name, "Товар A")
        self.assertEqual(product.quantity, 10)
        self.assertEqual(product.reason, "Причина")
        self.assertEqual(product.product_id, 123)

    def test_create_from_line_incoming(self):
        line = "Поступивший товар;02.02.2023;Товар B;20;100.50;456"
        product = Product.create_from_line(line)
        self.assertIsInstance(product, IncomingProduct)
        self.assertEqual(product.status, "Поступивший товар")
        self.assertEqual(product.date, "02.02.2023")
        self.assertEqual(product.name, "Товар B")
        self.assertEqual(product.quantity, 20)
        self.assertEqual(product.cost, 100.50)
        self.assertEqual(product.product_id, 456)

    def test_create_from_line_invalid_status(self):
        line = "Новый товар;01.01.2023;Товар A;10;Причина;123"
        with self.assertRaises(ValueError) as context:
            Product.create_from_line(line)
        self.assertEqual(str(context.exception), "Неизвестный статус товара: Новый товар")

    def test_create_from_line_insufficient_data(self):
        line = "Списанный товар;01.01.2023;Товар A;10;Причина"
        with self.assertRaises(ValueError) as context:
            Product.create_from_line(line)
        self.assertEqual(str(context.exception), "Недостаточно данных в строке.")

    def test_create_from_line_invalid_date(self):
        line = "Списанный товар;32.01.2023;Товар A;10;Причина;123"
        with self.assertRaises(ValueError) as context:
            Product.create_from_line(line)
        self.assertEqual(str(context.exception), "Некорректная дата: 32.01.2023")

    def test_create_products_valid(self):
        lines = [
            "Списанный товар;01.01.2023;Товар A;10;Причина;123",
            "Поступивший товар;02.02.2023;Товар B;20;100.50;456"
        ]
        products = ProductManager.create_products(lines)
        self.assertEqual(len(products), 2)
        self.assertIsInstance(products[0], WrittenOffProduct)
        self.assertIsInstance(products[1], IncomingProduct)

    def test_create_products_invalid(self):
        lines = [
            "Списанный товар;01.01.2023;Товар A;10;Причина;123",
            "Новый товар;02.02.2023;Товар B;20;100.50;456",  # Неверный статус
            "Списанный товар;32.01.2023;Товар C;15;Причина;789"  # Неверная дата
        ]
        products = ProductManager.create_products(lines)
        self.assertEqual(len(products), 1)  # Только первый продукт будет добавлен

if __name__ == '__main__':
    unittest.main()