import sys
from PyQt5 import QtWidgets
from my_class import ProductApp
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ProductApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
