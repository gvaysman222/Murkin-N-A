import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem, QComboBox


class WarehouseApp(QWidget):
    def __init__(self):
        super().__init__()

        self.conn = sqlite3.connect('warehouse.db')
        self.cursor = self.conn.cursor()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                supplier TEXT NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                product_id INTEGER,
                quantity INTEGER NOT NULL,
                order_date DATE NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS deliveries (
                id INTEGER PRIMARY KEY,
                order_id INTEGER,
                delivery_date DATE NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders (id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS supplier_products (
                id INTEGER PRIMARY KEY,
                supplier_id INTEGER,
                name TEXT NOT NULL,
                FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
            )
        ''')

        self.conn.commit()

        self.init_ui()

        self.setStyleSheet("""
            QWidget {
                background-color: #F5F5DC; /* Beige */
                color: #333333;
            }

            QTabWidget::pane {
                background-color: #F5F5DC;
            }

            QTabBar {
                background-color: #DEB887; /* BurlyWood */
            }

            QTabBar::tab:selected, QTabBar::tab:hover {
                background-color: #FFE4C4; /* Bisque */
            }

            QLabel {
                color: #8B4513; /* SaddleBrown */
            }

            QLineEdit, QComboBox {
                background-color: #FFF8DC; /* Cornsilk */
                selection-background-color: #FFD700; /* Gold */
            }

            QPushButton {
                background-color: #DEB887;
                border: 1px solid #8B4513;
                padding: 5px;
                min-width: 80px;
            }

            QPushButton:hover {
                background-color: #D2B48C; /* Tan */
            }

            QTableWidget {
                background-color: #FFF8DC;
                alternate-background-color: #FAEBD7; /* AntiqueWhite */
                gridline-color: #8B4513;
            }

            QTableWidget::item:selected {
                background-color: #FFD700;
            }
        """)

    def init_ui(self):
        self.tab_widget = QTabWidget()

        self.tab_products = QWidget()
        self.init_products_tab()
        self.tab_widget.addTab(self.tab_products, "Товары")

        self.tab_orders = QWidget()
        self.init_orders_tab()
        self.tab_widget.addTab(self.tab_orders, "Заказы")

        self.tab_deliveries = QWidget()
        self.init_deliveries_tab()
        self.tab_widget.addTab(self.tab_deliveries, "Поставки")

        self.tab_suppliers = QWidget()
        self.init_suppliers_tab()
        self.tab_widget.addTab(self.tab_suppliers, "Поставщики")

        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

        self.setGeometry(100, 100, 600, 400)
        self.setWindowTitle("Автоматизация работы склада Муркин Н.А")

    def init_products_tab(self):
        v_layout = QVBoxLayout()

        label_instruction = QLabel("Добавить новый товар:")
        v_layout.addWidget(label_instruction)

        label_name = QLabel("Название товара:")
        self.entry_name = QLineEdit()
        v_layout.addWidget(label_name)
        v_layout.addWidget(self.entry_name)

        label_quantity = QLabel("Количество товара:")
        self.entry_quantity = QLineEdit()
        v_layout.addWidget(label_quantity)
        v_layout.addWidget(self.entry_quantity)

        label_supplier = QLabel("Поставщик товара:")
        self.entry_supplier = QLineEdit()
        v_layout.addWidget(label_supplier)
        v_layout.addWidget(self.entry_supplier)

        button_add_product = QPushButton("Добавить товар")
        button_add_product.clicked.connect(self.add_product)
        v_layout.addWidget(button_add_product)

        label_remove_product = QLabel("Удалить выделенные товары:")
        v_layout.addWidget(label_remove_product)

        button_remove_product = QPushButton("Удалить товары")
        button_remove_product.clicked.connect(self.remove_selected_products)
        v_layout.addWidget(button_remove_product)

        self.table_products = QTableWidget()
        self.table_products.setColumnCount(4)
        self.table_products.setHorizontalHeaderLabels(["ID", "Название", "Количество", "Поставщик"])
        v_layout.addWidget(self.table_products)

        self.display_products()

        self.tab_products.setLayout(v_layout)

    def init_orders_tab(self):
        v_layout = QVBoxLayout()

        label_instruction = QLabel("Оформить новый заказ:")
        v_layout.addWidget(label_instruction)

        label_product_id = QLabel("ID товара для заказа:")
        self.entry_product_id = QLineEdit()
        v_layout.addWidget(label_product_id)
        v_layout.addWidget(self.entry_product_id)

        label_order_quantity = QLabel("Количество товара для заказа:")
        self.entry_order_quantity = QLineEdit()
        v_layout.addWidget(label_order_quantity)
        v_layout.addWidget(self.entry_order_quantity)

        button_place_order = QPushButton("Оформить заказ")
        button_place_order.clicked.connect(self.place_order)
        v_layout.addWidget(button_place_order)

        label_remove_order = QLabel("Удалить выделенные заказы:")
        v_layout.addWidget(label_remove_order)

        button_remove_order = QPushButton("Удалить заказы")
        button_remove_order.clicked.connect(self.remove_selected_orders)
        v_layout.addWidget(button_remove_order)

        self.table_orders = QTableWidget()
        self.table_orders.setColumnCount(5)
        self.table_orders.setHorizontalHeaderLabels(["ID", "ID товара", "Название товара", "Количество", "Дата заказа"])
        v_layout.addWidget(self.table_orders)

        self.display_orders()

        self.tab_orders.setLayout(v_layout)

    def init_deliveries_tab(self):
        v_layout = QVBoxLayout()

        label_display_deliveries = QLabel("Информация о поставках:")
        v_layout.addWidget(label_display_deliveries)

        self.table_deliveries = QTableWidget()
        self.table_deliveries.setColumnCount(3)
        self.table_deliveries.setHorizontalHeaderLabels(["ID", "ID заказа", "Дата поставки"])
        v_layout.addWidget(self.table_deliveries)

        self.display_deliveries()

        self.tab_deliveries.setLayout(v_layout)

    def add_product(self):
        name = self.entry_name.text()
        quantity = self.entry_quantity.text()
        supplier = self.entry_supplier.text()

        self.cursor.execute('INSERT INTO products (name, quantity, supplier) VALUES (?, ?, ?)', (name, quantity, supplier))
        self.conn.commit()
        self.display_products()

    def remove_selected_products(self):
        selected_rows = set()
        for item in self.table_products.selectedItems():
            selected_rows.add(item.row())

        selected_ids = [self.table_products.item(row, 0).text() for row in selected_rows]

        for product_id in selected_ids:
            try:
                self.cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
                self.conn.commit()
            except sqlite3.Error as e:
                print("Ошибка удаления товара:", e)

        self.display_products()

    def place_order(self):
        product_id = self.entry_product_id.text()
        quantity = self.entry_order_quantity.text()

        self.cursor.execute('INSERT INTO orders (product_id, quantity, order_date) VALUES (?, ?, ?)',
                            (product_id, quantity, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.conn.commit()
        self.display_orders()

    def remove_selected_orders(self):
        selected_rows = set()
        for item in self.table_orders.selectedItems():
            selected_rows.add(item.row())

        selected_ids = [self.table_orders.item(row, 0).text() for row in selected_rows]

        for order_id in selected_ids:
            try:
                self.cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
                self.conn.commit()
            except sqlite3.Error as e:
                print("Ошибка удаления заказа:", e)

        self.display_orders()

    def display_products(self):
        self.cursor.execute('SELECT * FROM products')
        products = self.cursor.fetchall()

        self.table_products.setRowCount(0)
        for row_number, product in enumerate(products):
            self.table_products.insertRow(row_number)
            for column_number, data in enumerate(product):
                item = QTableWidgetItem(str(data))
                self.table_products.setItem(row_number, column_number, item)

    def display_orders(self):
        self.cursor.execute('''
            SELECT orders.id, orders.product_id, products.name, orders.quantity, orders.order_date
            FROM orders
            JOIN products ON orders.product_id = products.id
        ''')
        orders = self.cursor.fetchall()

        self.table_orders.setRowCount(0)
        for row_number, order in enumerate(orders):
            self.table_orders.insertRow(row_number)
            for column_number, data in enumerate(order):
                item = QTableWidgetItem(str(data))
                self.table_orders.setItem(row_number, column_number, item)

    def display_deliveries(self):
        self.cursor.execute('SELECT * FROM deliveries')
        deliveries = self.cursor.fetchall()

        self.table_deliveries.setRowCount(0)
        for row_number, delivery in enumerate(deliveries):
            self.table_deliveries.insertRow(row_number)
            for column_number, data in enumerate(delivery):
                item = QTableWidgetItem(str(data))
                self.table_deliveries.setItem(row_number, column_number, item)

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

    def init_suppliers_tab(self):
        v_layout = QVBoxLayout()

        label_add_supplier = QLabel("Добавить нового поставщика:")
        v_layout.addWidget(label_add_supplier)

        label_supplier_name = QLabel("Имя поставщика:")
        self.entry_supplier_name = QLineEdit()
        v_layout.addWidget(label_supplier_name)
        v_layout.addWidget(self.entry_supplier_name)

        button_add_supplier = QPushButton("Добавить поставщика")
        button_add_supplier.clicked.connect(self.add_supplier)
        v_layout.addWidget(button_add_supplier)

        label_supplier_products = QLabel("Товары поставщика:")
        v_layout.addWidget(label_supplier_products)

        self.combo_suppliers = QComboBox()
        self.combo_suppliers.currentIndexChanged.connect(self.display_supplier_products)
        v_layout.addWidget(self.combo_suppliers)

        self.table_supplier_products = QTableWidget()
        self.table_supplier_products.setColumnCount(2)  # 2 колонки: id, name
        self.table_supplier_products.setHorizontalHeaderLabels(["ID", "Название"])
        v_layout.addWidget(self.table_supplier_products)

        button_order_product = QPushButton("Заказать товар")
        button_order_product.clicked.connect(self.order_product)
        v_layout.addWidget(button_order_product)

        self.display_suppliers()
        self.display_supplier_products()

        self.tab_suppliers.setLayout(v_layout)

    def add_supplier(self):
        supplier_name = self.entry_supplier_name.text()

        self.cursor.execute('INSERT OR IGNORE INTO suppliers (name) VALUES (?)', (supplier_name,))
        self.conn.commit()
        self.display_suppliers()

    def display_suppliers(self):
        self.cursor.execute('SELECT * FROM suppliers')
        suppliers = self.cursor.fetchall()

        self.combo_suppliers.clear()
        for supplier in suppliers:
            self.combo_suppliers.addItem(supplier[1])

    def display_supplier_products(self):
        current_supplier = self.combo_suppliers.currentText()

        self.cursor.execute('''
            SELECT id, name
            FROM supplier_products
            WHERE supplier_id = (SELECT id FROM suppliers WHERE name = ?)
        ''', (current_supplier,))
        products = self.cursor.fetchall()

        self.table_supplier_products.setRowCount(0)
        for row_number, product in enumerate(products):
            self.table_supplier_products.insertRow(row_number)
            for column_number, data in enumerate(product):
                item = QTableWidgetItem(str(data))
                self.table_supplier_products.setItem(row_number, column_number, item)

    def order_product(self):
        current_supplier = self.combo_suppliers.currentText()
        product_id = self.table_supplier_products.item(self.table_supplier_products.currentRow(), 0).text()
        quantity = 1

        self.cursor.execute('INSERT INTO orders (product_id, quantity, order_date) VALUES (?, ?, ?)',
                            (product_id, quantity, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.conn.commit()

        self.display_orders()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    warehouse_app = WarehouseApp()
    warehouse_app.show()
    sys.exit(app.exec_())





