from my_class import Product, WrittenOffProduct, IncomingProduct

def main():
    file_path = 'examples/in.csv'
    products = []

    with open(file_path, 'r', encoding='cp1251') as file:
        for line in file:
            products.append(Product.create_from_line(line))

    for product in products:
        print(product)


if __name__ == "__main__":
    main()
