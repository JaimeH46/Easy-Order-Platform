import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import messagebox, ttk


# Link the database
def connect_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="your_password",
            database="your_databasename"
        )
        return connection
    except Error as e:
        messagebox.showerror("Error", "Failed to connect to database: {}".format(e))
        return None


# access current number of Vendor, Products and Orders
def get_counts(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Vendor")
    vendor_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Products")
    product_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Orders")
    order_count = cursor.fetchone()[0]
    cursor.close()
    return vendor_count, product_count, order_count


# access list of Products' single price
def get_product_prices(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT P_id, Price FROM Products ORDER BY P_id")
    prices = {row[0]: row[1] for row in cursor.fetchall()}
    cursor.close()
    return prices


# update Order_history from Customer
def update_order_history(connection, c_id, o_id, action):
    cursor = connection.cursor()
    cursor.execute("SELECT Order_History FROM Customer WHERE C_id = {}".format(c_id))
    history = cursor.fetchone()[0]

    if action == "add":
        new_history = "{},{}".format(history, o_id) if history else str(o_id)
        cursor.execute("UPDATE Customer SET Order_History = '{}' WHERE C_id = {}".format(new_history, c_id))
    elif action == "delete":
        if history:
            history_list = history.split(",")
            history_list = [x for x in history_list if x != str(o_id)]
            new_history = ",".join(history_list) if history_list else "NULL"
            cursor.execute(
                "UPDATE Customer SET Order_History = {} WHERE C_id = {}".format(
                    'NULL' if new_history == 'NULL' else "'{}'".format(new_history), c_id))

    connection.commit()
    cursor.close()


# GUI main program
class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("COMP7640_Group11")
        self.root.geometry("800x600")
        self.connection = connect_db()
        self.current_window = None
        self.show_identity_selection()

    def clear_window(self):
        if self.current_window:
            self.current_window.destroy()
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_identity_selection(self):
        self.clear_window()
        tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
        self.current_window = tk.Frame(self.root, bg="#d3d3d3")
        self.current_window.pack(expand=True, fill="both")

        tk.Label(self.current_window, text="Please select your identity:", bg="#d3d3d3", font=("Arial", 12)).pack(
            pady=10)
        tk.Button(self.current_window, text="1. Administrator", command=self.show_admin_password, width=30).pack(pady=5)
        tk.Button(self.current_window, text="2. Customer", command=self.show_customer_login, width=30).pack(pady=5)
        tk.Button(self.current_window, text="3. Quit", command=self.root.quit, width=30).pack(pady=5)

# enter administrator's password
    def show_admin_password(self):
        self.clear_window()
        tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
        self.current_window = tk.Frame(self.root, bg="#d3d3d3")
        self.current_window.pack(expand=True, fill="both")

        tk.Label(self.current_window, text="Please enter your password:", bg="#d3d3d3", font=("Arial", 12)).pack(
            pady=10)
        password_entry = tk.Entry(self.current_window, show="*")
        password_entry.pack(pady=5)
        password_entry.focus_set()  #

        tk.Button(self.current_window, text="Back", command=self.show_identity_selection).pack(side="right", padx=10)

        def check_password():
            if password_entry.get() == "7640":
                self.show_admin_options()
            else:
                messagebox.showerror("Error", "Incorrect password!")

        password_entry.bind("<Return>", lambda event: check_password())
        tk.Button(self.current_window, text="Submit", command=check_password).pack(pady=5)

    def show_customer_login(self):
        self.clear_window()
        tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
        self.current_window = tk.Frame(self.root, bg="#d3d3d3")
        self.current_window.pack(expand=True, fill="both")

        tk.Label(self.current_window, text="Please enter your C_id:", bg="#d3d3d3", font=("Arial", 12)).pack(pady=10)
        c_id_entry = tk.Entry(self.current_window)
        c_id_entry.pack(pady=5)
        c_id_entry.focus_set()  #

        tk.Button(self.current_window, text="Back", command=self.show_identity_selection).pack(side="right", padx=10)

        def check_c_id():
            try:
                c_id = int(c_id_entry.get())
                cursor = self.connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM Customer WHERE C_id = {}".format(c_id))
                if cursor.fetchone()[0] == 0:
                    messagebox.showerror("Error", "Invalid C_id!")
                else:
                    self.show_customer_options(c_id)
                cursor.close()
            except ValueError:
                messagebox.showerror("Error", "C_id must be an integer!")

        c_id_entry.bind("<Return>", lambda event: check_c_id())
        tk.Button(self.current_window, text="Submit", command=check_c_id).pack(pady=5)

    def show_admin_options(self):
        self.clear_window()
        tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
        self.current_window = tk.Frame(self.root, bg="#d3d3d3")
        self.current_window.pack(expand=True, fill="both")

        tk.Label(self.current_window, text="Administrator options:", bg="#d3d3d3", font=("Arial", 12)).pack(pady=10)
        tk.Button(self.current_window, text="1. Add product", command=self.add_product, width=30).pack(pady=5)
        tk.Button(self.current_window, text="2. Delete product", command=self.delete_product, width=30).pack(pady=5)
        tk.Button(self.current_window, text="3. Add Vendor", command=self.add_vendor, width=30).pack(pady=5)
        tk.Button(self.current_window, text="4. Delete Vendor", command=self.delete_vendor, width=30).pack(pady=5)
        tk.Button(self.current_window, text="5. Order management", command=self.admin_order_management, width=30).pack(
            pady=5)
        tk.Button(self.current_window, text="6. View all customer information", command=self.view_customers,
                  width=30).pack(pady=5)
        tk.Button(self.current_window, text="7. View all Vendor information", command=self.view_vendors, width=30).pack(
            pady=5)
        tk.Button(self.current_window, text="8. View product information",
                  command=lambda: self.check_products(self.show_admin_options), width=30).pack(pady=5)
        tk.Button(self.current_window, text="9. Restore to original state", command=self.reset_to_initial,
                  width=30).pack(pady=5)
        tk.Button(self.current_window, text="Back", command=self.show_identity_selection).pack(side="right", padx=10)

    def show_customer_options(self, c_id):
        self.clear_window()
        tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
        self.current_window = tk.Frame(self.root, bg="#d3d3d3")
        self.current_window.pack(expand=True, fill="both")

        tk.Label(self.current_window, text="Customer options:", bg="#d3d3d3", font=("Arial", 12)).pack(pady=10)
        tk.Button(self.current_window, text="1. Add order", command=lambda: self.add_order("customer", c_id),
                  width=30).pack(pady=5)
        tk.Button(self.current_window, text="2. Delete order", command=lambda: self.delete_order("customer", c_id),
                  width=30).pack(pady=5)
        tk.Button(self.current_window, text="3. Modify order", command=lambda: self.modify_order(c_id), width=30).pack(
            pady=5)
        tk.Button(self.current_window, text="4. View my order", command=lambda: self.view_customer_orders(c_id),
                  width=30).pack(pady=5)
        tk.Button(self.current_window, text="5. View product information",
                  command=lambda: self.check_products(lambda: self.show_customer_options(c_id)), width=30).pack(pady=5)
        tk.Button(self.current_window, text="6. Rate Vendor", command=lambda: self.rate_vendor(c_id), width=30).pack(
            pady=5)
        tk.Button(self.current_window, text="Back", command=self.show_identity_selection).pack(side="right", padx=10)

# permission to add product to table 'Products'
    def add_product(self):
        vendor_count, _, _ = get_counts(self.connection)
        self.clear_window()
        tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
        self.current_window = tk.Frame(self.root, bg="#d3d3d3")
        self.current_window.pack(expand=True, fill="both")

        tk.Label(self.current_window,
                 text="There are currently {} Vendors, please enter new product data in the format (separated by ','):".format(vendor_count),
                 bg="#d3d3d3", font=("Arial", 12), wraplength=350).pack(pady=10)
        tk.Label(self.current_window,
                 text="P_id(int), Name(str), Price(float), Size(str), Weight(str), Category(str), {} Stock(int)".format(vendor_count),
                 bg="#d3d3d3", font=("Arial", 10)).pack(pady=5)
        data_entry = tk.Entry(self.current_window)
        data_entry.pack(pady=5)
        data_entry.focus_set()

        tk.Button(self.current_window, text="Back", command=self.show_admin_options).pack(side="right", padx=10)

# check if input are valid or not
        def submit():
            data = data_entry.get().split(",")
            if len(data) != 6 + vendor_count:
                messagebox.showerror("Error", "Incorrect number of inputs!")
                return
            try:
                p_id = int(data[0])
                name = data[1].strip()
                price = float(data[2])
                size = data[3].strip()
                weight = data[4].strip()
                category = data[5].strip()
                stocks = [int(stock) for stock in data[6:]]

                cursor = self.connection.cursor()
                insert_query = "INSERT INTO Products (P_id, Name, Price, Size, Weight, Category, {}) VALUES ({}, '{}', {}, '{}', '{}', '{}', {})".format(
                    ', '.join(['Stock{}'.format(i + 1) for i in range(vendor_count)]), p_id, name, price, size, weight, category, ', '.join(map(str, stocks)))
                cursor.execute(insert_query)
                self.connection.commit()

                new_stock_col = "Stock{}".format(p_id)
                cursor.execute("ALTER TABLE Vendor ADD COLUMN {} INT DEFAULT 0".format(new_stock_col))
                self.connection.commit()
                for i, stock in enumerate(stocks, 1):
                    cursor.execute("UPDATE Vendor SET {} = {} WHERE V_id = {}".format(new_stock_col, stock, i))
                    self.connection.commit()

                new_num_col = "Num_Product{}".format(p_id)
                cursor.execute("ALTER TABLE Order_Item ADD COLUMN {} INT DEFAULT 0".format(new_num_col))
                self.connection.commit()
                messagebox.showinfo("Success", "Product {} added successfully!".format(name))
                self.show_admin_options()
            except Error as e:
                messagebox.showerror("Error", "Operation failed: {}".format(e))
                self.connection.rollback()
            finally:
                cursor.close()

        data_entry.bind("<Return>", lambda event: submit())
        tk.Button(self.current_window, text="Submit", command=submit).pack(pady=5)

    def delete_product(self):
        self.clear_window()
        tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
        self.current_window = tk.Frame(self.root, bg="#d3d3d3")
        self.current_window.pack(expand=True, fill="both")

        tk.Label(self.current_window, text="Please enter the P_id to delete:", bg="#d3d3d3", font=("Arial", 12)).pack(
            pady=10)
        p_id_entry = tk.Entry(self.current_window)
        p_id_entry.pack(pady=5)
        p_id_entry.focus_set()

        tk.Button(self.current_window, text="Back", command=self.show_admin_options).pack(side="right", padx=10)

        def submit():
            try:
                p_id = int(p_id_entry.get())
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM Products WHERE P_id = {}".format(p_id))
                cursor.execute("ALTER TABLE Vendor DROP COLUMN Stock{}".format(p_id))
                cursor.execute("ALTER TABLE Order_Item DROP COLUMN Num_Product{}".format(p_id))
                self.connection.commit()
                messagebox.showinfo("Success", "Product with P_id = {} deleted!".format(p_id))
                self.show_admin_options()
            except Error as e:
                messagebox.showerror("Error", "Operation failed: {}".format(e))
                self.connection.rollback()
            finally:
                cursor.close()

        p_id_entry.bind("<Return>", lambda event: submit())
        tk.Button(self.current_window, text="Submit", command=submit).pack(pady=5)

# Add vendors to table 'Vendor'
    def add_vendor(self):
        _, product_count, _ = get_counts(self.connection)
        self.clear_window()
        tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
        self.current_window = tk.Frame(self.root, bg="#d3d3d3")
        self.current_window.pack(expand=True, fill="both")

        tk.Label(self.current_window,
                 text="There are currently {} products, please enter new Vendor data in the format (separated by ','):".format(product_count),
                 bg="#d3d3d3", font=("Arial", 12), wraplength=350).pack(pady=10)
        tk.Label(self.current_window,
                 text="V_id(int), Name(str), Location(str), Feedback_Score(int), {} Stock(int)".format(product_count),
                 bg="#d3d3d3", font=("Arial", 10)).pack(pady=5)
        data_entry = tk.Entry(self.current_window)
        data_entry.pack(pady=5)
        data_entry.focus_set()

        tk.Button(self.current_window, text="Back", command=self.show_admin_options).pack(side="right", padx=10)

        def submit():
            data = data_entry.get().split(",")
            if len(data) != 4 + product_count:
                messagebox.showerror("Error", "Incorrect number of inputs!")
                return
            try:
                v_id = int(data[0])
                name = data[1].strip()
                location = data[2].strip()
                feedback = int(data[3])
                stocks = [int(stock) for stock in data[4:]]

                cursor = self.connection.cursor()
                insert_query = "INSERT INTO Vendor (V_id, Name, Location, Feedback_Score, {}) VALUES ({}, '{}', '{}', {}, {})".format(
                    ', '.join(['Stock{}'.format(i + 1) for i in range(product_count)]), v_id, name, location, feedback, ', '.join(map(str, stocks)))
                cursor.execute(insert_query)
                self.connection.commit()

                new_stock_col = "Stock{}".format(v_id)
                cursor.execute("ALTER TABLE Products ADD COLUMN {} INT DEFAULT 0".format(new_stock_col))
                self.connection.commit()
                for i, stock in enumerate(stocks, 1):
                    cursor.execute("UPDATE Products SET {} = {} WHERE P_id = {}".format(new_stock_col, stock, i))
                    self.connection.commit()
                messagebox.showinfo("Success", "Vendor {} added successfully!".format(name))
                self.show_admin_options()
            except Error as e:
                messagebox.showerror("Error", "Operation failed: {}".format(e))
                self.connection.rollback()
            finally:
                cursor.close()

        data_entry.bind("<Return>", lambda event: submit())
        tk.Button(self.current_window, text="Submit", command=submit).pack(pady=5)

    def delete_vendor(self):
        self.clear_window()
        tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
        self.current_window = tk.Frame(self.root, bg="#d3d3d3")
        self.current_window.pack(expand=True, fill="both")

        tk.Label(self.current_window, text="Please enter the V_id to delete:", bg="#d3d3d3", font=("Arial", 12)).pack(
            pady=10)
        v_id_entry = tk.Entry(self.current_window)
        v_id_entry.pack(pady=5)
        v_id_entry.focus_set()

        tk.Button(self.current_window, text="Back", command=self.show_admin_options).pack(side="right", padx=10)

        def submit():
            try:
                v_id = int(v_id_entry.get())
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM Order_Item WHERE O_id IN (SELECT O_id FROM Orders WHERE V_id = {})".format(v_id))
                cursor.execute("DELETE FROM Orders WHERE V_id = {}".format(v_id))
                cursor.execute("DELETE FROM Vendor WHERE V_id = {}".format(v_id))
                cursor.execute("ALTER TABLE Products DROP COLUMN Stock{}".format(v_id))
                self.connection.commit()
                messagebox.showinfo("Success", "Vendor with V_id = {} and related orders deleted!".format(v_id))
                self.show_admin_options()
            except Error as e:
                messagebox.showerror("Error", "Operation failed: {}".format(e))
                self.connection.rollback()
            finally:
                cursor.close()

        v_id_entry.bind("<Return>", lambda event: submit())
        tk.Button(self.current_window, text="Submit", command=submit).pack(pady=5)

# Managment orders
    def admin_order_management(self):
        self.clear_window()
        tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
        self.current_window = tk.Frame(self.root, bg="#d3d3d3")
        self.current_window.pack(expand=True, fill="both")

        tk.Label(self.current_window, text="Order management options:", bg="#d3d3d3", font=("Arial", 12)).pack(pady=10)
        tk.Button(self.current_window, text="1. Add order", command=lambda: self.add_order("admin"), width=30).pack(
            pady=5)
        tk.Button(self.current_window, text="2. Delete order", command=lambda: self.delete_order("admin"),
                  width=30).pack(pady=5)
        tk.Button(self.current_window, text="3. View all orders", command=self.view_all_orders, width=30).pack(pady=5)
        tk.Button(self.current_window, text="4. View product information",
                  command=lambda: self.check_products(self.admin_order_management), width=30).pack(pady=5)
        tk.Button(self.current_window, text="Back", command=self.show_admin_options).pack(side="right", padx=10)

    def add_order(self, role, c_id=None):
        _, product_count, _ = get_counts(self.connection)
        self.clear_window()
        tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
        self.current_window = tk.Frame(self.root, bg="#d3d3d3")
        self.current_window.pack(expand=True, fill="both")

        tk.Label(self.current_window,
                 text="There are currently {} products, please enter order data (separated by ','):".format(product_count),
                 bg="#d3d3d3", font=("Arial", 12), wraplength=350).pack(pady=10)
        if role == "admin":
            tk.Label(self.current_window,
                     text="O_id(int), Shipping_status(str), C_id(int), V_id(int), {} Num_Product(int)".format(product_count),
                     bg="#d3d3d3", font=("Arial", 10)).pack(pady=5)
        else:
            tk.Label(self.current_window, text="V_id(int), {} Num_Product(int)".format(product_count), bg="#d3d3d3",
                     font=("Arial", 10)).pack(pady=5)
        data_entry = tk.Entry(self.current_window)
        data_entry.pack(pady=5)
        data_entry.focus_set()

        back_command = self.admin_order_management if role == "admin" else lambda: self.show_customer_options(c_id)
        tk.Button(self.current_window, text="Back", command=back_command).pack(side="right", padx=10)

        def submit():
            cursor = self.connection.cursor()
            prices = get_product_prices(self.connection)
            data = data_entry.get().split(",")
            if role == "admin":
                if len(data) != 4 + product_count:
                    messagebox.showerror("Error", "Incorrect number of inputs!")
                    return
                o_id = int(data[0])
                shipping_status = data[1].strip()
                order_c_id = int(data[2])
                v_id = int(data[3])
                quantities = [int(x) for x in data[4:]]
            else:
                if len(data) != 1 + product_count:
                    messagebox.showerror("Error", "Incorrect number of inputs!")
                    return
                cursor.execute("SELECT MAX(O_id) FROM Orders")
                max_o_id = cursor.fetchone()[0]
                o_id = (max_o_id or 0) + 1
                order_c_id = c_id
                v_id = int(data[0])
                quantities = [int(x) for x in data[1:]]
                shipping_status = "Awaiting"

            stock_cols = ", ".join(["Stock{}".format(i + 1) for i in range(product_count)])
            cursor.execute("SELECT {} FROM Vendor WHERE V_id = {}".format(stock_cols, v_id))
            vendor_stocks = cursor.fetchone()

            if not vendor_stocks:
                messagebox.showerror("Error", "Vendor V_id = {} does not exist!".format(v_id))
                return

            cursor.execute("SELECT Name FROM Products ORDER BY P_id")
            product_names = [row[0] for row in cursor.fetchall()]

            insufficient = []
            for i in range(product_count):
                stock = vendor_stocks[i]
                if stock < quantities[i]:
                    insufficient.append("{} remaining {}".format(product_names[i], stock))

            if insufficient:
                messagebox.showerror("Error",
                                     "Order creation failed! The Vendor has: {}, please reorder!".format(', '.join(insufficient)))
                return

            try:
                cursor.execute(
                    "INSERT INTO Orders (O_id, Shipping_status, C_id, V_id) VALUES ({}, '{}', {}, {})".format(o_id, shipping_status, order_c_id, v_id))
                total_price = sum(prices[i + 1] * quantities[i] for i in range(product_count) if i + 1 in prices)
                num_cols = ", ".join(["Num_Product{}".format(i + 1) for i in range(product_count)])
                num_vals = ", ".join(map(str, quantities))
                cursor.execute(
                    "INSERT INTO Order_Item (O_id, Total_Price, {}) VALUES ({}, {}, {})".format(num_cols, o_id, total_price, num_vals))

                for i in range(product_count):
                    cursor.execute(
                        "UPDATE Vendor SET Stock{} = Stock{} - {} WHERE V_id = {}".format(i + 1, i + 1, quantities[i], v_id))
                    cursor.execute(
                        "UPDATE Products SET Stock{} = Stock{} - {} WHERE P_id = {}".format(v_id, v_id, quantities[i], i + 1))

                self.connection.commit()
                update_order_history(self.connection, order_c_id, o_id, "add")
                messagebox.showinfo("Success", "Order {} added successfully!".format(o_id))
                back_command()
            except Error as e:
                messagebox.showerror("Error", "Operation failed: {}".format(e))
                self.connection.rollback()
            finally:
                cursor.close()

        data_entry.bind("<Return>", lambda event: submit())
        tk.Button(self.current_window, text="Submit", command=submit).pack(pady=5)

    def delete_order(self, role, c_id=None):
        self.clear_window()
        tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
        self.current_window = tk.Frame(self.root, bg="#d3d3d3")
        self.current_window.pack(expand=True, fill="both")

        tk.Label(self.current_window, text="Please enter the O_id to delete:", bg="#d3d3d3", font=("Arial", 12)).pack(
            pady=10)
        o_id_entry = tk.Entry(self.current_window)
        o_id_entry.pack(pady=5)
        o_id_entry.focus_set()

        back_command = self.admin_order_management if role == "admin" else lambda: self.show_customer_options(c_id)
        tk.Button(self.current_window, text="Back", command=back_command).pack(side="right", padx=10)

        def submit():
            cursor = self.connection.cursor()
            _, product_count, _ = get_counts(self.connection)
            try:
                o_id = int(o_id_entry.get())
                cursor.execute("SELECT C_id, Shipping_status, V_id FROM Orders WHERE O_id = {}".format(o_id))
                result = cursor.fetchone()
                if not result:
                    messagebox.showerror("Error", "Order does not exist!")
                    return
                order_c_id, _, v_id = result

                if role == "customer" and order_c_id != c_id:
                    messagebox.showerror("Error", "You can only delete your own orders!")
                    return

                num_cols = ", ".join(["Num_Product{}".format(i + 1) for i in range(product_count)])
                cursor.execute("SELECT {} FROM Order_Item WHERE O_id = {}".format(num_cols, o_id))
                quantities = list(cursor.fetchone())

                cursor.execute("DELETE FROM Order_Item WHERE O_id = {}".format(o_id))
                cursor.execute("DELETE FROM Orders WHERE O_id = {}".format(o_id))

                for i in range(product_count):
                    cursor.execute(
                        "UPDATE Vendor SET Stock{} = Stock{} + {} WHERE V_id = {}".format(i + 1, i + 1, quantities[i], v_id))
                    cursor.execute(
                        "UPDATE Products SET Stock{} = Stock{} + {} WHERE P_id = {}".format(v_id, v_id, quantities[i], i + 1))

                self.connection.commit()
                update_order_history(self.connection, order_c_id, o_id, "delete")
                messagebox.showinfo("Success", "Order {} deleted!".format(o_id))
                back_command()
            except Error as e:
                messagebox.showerror("Error", "Operation failed: {}".format(e))
                self.connection.rollback()
            finally:
                cursor.close()

        o_id_entry.bind("<Return>", lambda event: submit())
        tk.Button(self.current_window, text="Submit", command=submit).pack(pady=5)

    def modify_order(self, c_id):
        self.clear_window()
        tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
        self.current_window = tk.Frame(self.root, bg="#d3d3d3")
        self.current_window.pack(expand=True, fill="both")

        tk.Label(self.current_window, text="Please enter the O_id to modify:", bg="#d3d3d3", font=("Arial", 12)).pack(
            pady=10)
        o_id_entry = tk.Entry(self.current_window)
        o_id_entry.pack(pady=5)
        o_id_entry.focus_set()

        tk.Button(self.current_window, text="Back", command=lambda: self.show_customer_options(c_id)).pack(side="right",
                                                                                                           padx=10)
# customers can only change their own orders, and only in condition 'Awaiting'
        def submit():
            cursor = self.connection.cursor()
            _, product_count, _ = get_counts(self.connection)
            prices = get_product_prices(self.connection)
            try:
                o_id = int(o_id_entry.get())
                cursor.execute("SELECT C_id, Shipping_status FROM Orders WHERE O_id = {}".format(o_id))
                result = cursor.fetchone()
                if not result:
                    messagebox.showerror("Error", "Order does not exist!")
                    return
                order_c_id, shipping_status = result

                if order_c_id != c_id:
                    messagebox.showerror("Error", "You can only modify your own orders!")
                    return
                if shipping_status != "Awaiting":
                    messagebox.showerror("Error", "You can only modify orders with 'Awaiting' status!")
                    return

                self.clear_window()
                tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
                self.current_window = tk.Frame(self.root, bg="#d3d3d3")
                self.current_window.pack(expand=True, fill="both")

                tk.Label(self.current_window,
                         text="There are currently {} products, please enter new product quantities (separated by ','):".format(product_count),
                         bg="#d3d3d3", font=("Arial", 12), wraplength=350).pack(pady=10)
                quantities_entry = tk.Entry(self.current_window)
                quantities_entry.pack(pady=5)
                quantities_entry.focus_set()

                tk.Button(self.current_window, text="Back", command=lambda: self.show_customer_options(c_id)).pack(
                    side="right", padx=10)

                def submit_quantities():
                    quantities = [int(x) for x in quantities_entry.get().split(",")]
                    if len(quantities) != product_count:
                        messagebox.showerror("Error", "Incorrect number of inputs!")
                        return
                    try:
                        total_price = sum(
                            prices[i + 1] * quantities[i] for i in range(product_count) if i + 1 in prices)
                        update_query = "UPDATE Order_Item SET Total_Price = {}, {}".format(
                            total_price, ", ".join(["Num_Product{} = {}".format(i + 1, quantities[i]) for i in range(product_count)]))
                        cursor.execute("{} WHERE O_id = {}".format(update_query, o_id))
                        self.connection.commit()
                        messagebox.showinfo("Success", "Order {} modified!".format(o_id))
                        self.show_customer_options(c_id)
                    except Error as e:
                        messagebox.showerror("Error", "Operation failed: {}".format(e))
                        self.connection.rollback()

                quantities_entry.bind("<Return>", lambda event: submit_quantities())
                tk.Button(self.current_window, text="Submit", command=submit_quantities).pack(pady=5)
            except Error as e:
                messagebox.showerror("Error", "Operation failed: {}".format(e))
            finally:
                cursor.close()

        o_id_entry.bind("<Return>", lambda event: submit())
        tk.Button(self.current_window, text="Submit", command=submit).pack(pady=5)

    def view_all_orders(self):
        cursor = self.connection.cursor()
        _, product_count, _ = get_counts(self.connection)
        cursor.execute("SELECT * FROM Orders")
        orders = cursor.fetchall()
        cursor.execute("SELECT * FROM Order_Item")
        order_items = cursor.fetchall()
        cursor.close()

        self.clear_window()
        tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
        self.current_window = tk.Frame(self.root, bg="#d3d3d3")
        self.current_window.pack(expand=True, fill="both")

        text_area = tk.Text(self.current_window, height=20, width=80)
        text_area.pack(pady=10)
        for order, item in zip(orders, order_items):
            o_id = order[0]
            text_area.insert(tk.END, "Order {}:\n".format(o_id))
            text_area.insert(tk.END,
                             "O_id: {}, Shipping_status: {}, C_id: {}, V_id: {}, Total_Price: {}, {}".format(
                                 order[0], order[1], order[2], order[3], item[1],
                                 ", ".join(["Num_Product{}: {}".format(i + 1, item[i + 2]) for i in range(product_count)])) + "\n\n")
        text_area.config(state="disabled")

        tk.Button(self.current_window, text="Back", command=self.admin_order_management).pack(side="right", padx=10)

    def view_customer_orders(self, c_id):
        cursor = self.connection.cursor()
        _, product_count, _ = get_counts(self.connection)
        cursor.execute("SELECT * FROM Orders WHERE C_id = {}".format(c_id))
        orders = cursor.fetchall()
        cursor.execute("SELECT * FROM Order_Item WHERE O_id IN (SELECT O_id FROM Orders WHERE C_id = {})".format(c_id))
        order_items = cursor.fetchall()
        cursor.close()

        self.clear_window()
        tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
        self.current_window = tk.Frame(self.root, bg="#d3d3d3")
        self.current_window.pack(expand=True, fill="both")

        text_area = tk.Text(self.current_window, height=20, width=80)
        text_area.pack(pady=10)
        for order, item in zip(orders, order_items):
            o_id = order[0]
            text_area.insert(tk.END, "Order {}:\n".format(o_id))
            text_area.insert(tk.END,
                             "O_id: {}, Shipping_status: {}, C_id: {}, V_id: {}, Total_Price: {}, {}".format(
                                 order[0], order[1], order[2], order[3], item[1],
                                 ", ".join(["Num_Product{}: {}".format(i + 1, item[i + 2]) for i in range(product_count)])) + "\n\n")
        text_area.config(state="disabled")

        tk.Button(self.current_window, text="Back", command=lambda: self.show_customer_options(c_id)).pack(side="right",
                                                                                                           padx=10)

    def check_products(self, back_command):
        self.clear_window()
        tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
        self.current_window = tk.Frame(self.root, bg="#d3d3d3")
        self.current_window.pack(expand=True, fill="both")

        tk.Label(self.current_window, text="View product information options:", bg="#d3d3d3", font=("Arial", 12)).pack(
            pady=10)
        tk.Button(self.current_window, text="1. View all products",
                  command=lambda: self.view_all_products(back_command), width=30).pack(pady=5)
        tk.Button(self.current_window, text="2. Browse specific product",
                  command=lambda: self.browse_specific_product(back_command), width=30).pack(pady=5)
        tk.Button(self.current_window, text="3. Browse by category",
                  command=lambda: self.browse_by_category(back_command), width=30).pack(pady=5)
        tk.Button(self.current_window, text="Back", command=back_command).pack(side="right", padx=10)

    def view_all_products(self, back_command):
        cursor = self.connection.cursor()
        vendor_count, product_count, _ = get_counts(self.connection)
        cursor.execute("SELECT * FROM Products")
        products = cursor.fetchall()
        cursor.close()

        self.clear_window()
        tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
        self.current_window = tk.Frame(self.root, bg="#d3d3d3")
        self.current_window.pack(expand=True, fill="both")

        text_area = tk.Text(self.current_window, height=20, width=80)
        text_area.pack(pady=10)
        for product in products:
            p_id = product[0]
            text_area.insert(tk.END, "Product {}:\n".format(p_id))
            text_area.insert(tk.END,
                             "P_id: {}, Name: {}, Price: {}, Size: {}, Weight: {}, Category: {}, {}".format(
                                 product[0], product[1], product[2], product[3], product[4], product[5],
                                 ", ".join(["Stock{}: {}".format(i + 1, product[i + 6]) for i in range(vendor_count)])) + "\n\n")
        text_area.config(state="disabled")

        tk.Button(self.current_window, text="Back", command=lambda: self.check_products(back_command)).pack(
            side="right", padx=10)

# check products by sepcific way, name or catagories
    def browse_specific_product(self, back_command):
        cursor = self.connection.cursor()
        cursor.execute("SELECT Name FROM Products ORDER BY P_id")
        names = [row[0] for row in cursor.fetchall()]
        cursor.close()

        self.clear_window()
        tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
        self.current_window = tk.Frame(self.root, bg="#d3d3d3")
        self.current_window.pack(expand=True, fill="both")

        tk.Label(self.current_window, text="Available product names: {}".format(', '.join(names)), bg="#d3d3d3",
                 font=("Arial", 12), wraplength=350).pack(pady=10)
        tk.Label(self.current_window, text="Please enter product Name:", bg="#d3d3d3").pack(pady=5)
        name_entry = tk.Entry(self.current_window)
        name_entry.pack(pady=5)
        name_entry.focus_set()

        tk.Button(self.current_window, text="Back", command=lambda: self.check_products(back_command)).pack(
            side="right", padx=10)

        def submit():
            cursor = self.connection.cursor()
            vendor_count, _, _ = get_counts(self.connection)
            name = name_entry.get().strip()
            cursor.execute("SELECT * FROM Products WHERE Name = '{}'".format(name))
            product = cursor.fetchone()
            if product:
                self.clear_window()
                tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
                self.current_window = tk.Frame(self.root, bg="#d3d3d3")
                self.current_window.pack(expand=True, fill="both")

                text_area = tk.Text(self.current_window, height=20, width=80)
                text_area.pack(pady=10)
                p_id = product[0]
                text_area.insert(tk.END, "Product {}:\n".format(p_id))
                text_area.insert(tk.END,
                                 "P_id: {}, Name: {}, Price: {}, Size: {}, Weight: {}, Category: {}, {}".format(
                                     product[0], product[1], product[2], product[3], product[4], product[5],
                                     ", ".join(["Stock{}: {}".format(i + 1, product[i + 6]) for i in range(vendor_count)])))
                text_area.config(state="disabled")

                tk.Button(self.current_window, text="Back", command=lambda: self.check_products(back_command)).pack(
                    side="right", padx=10)
            else:
                messagebox.showerror("Error", "Product not found!")
            cursor.close()

        name_entry.bind("<Return>", lambda event: submit())
        tk.Button(self.current_window, text="Submit", command=submit).pack(pady=5)

    def browse_by_category(self, back_command):
        cursor = self.connection.cursor()
        cursor.execute("SELECT DISTINCT Category FROM Products")
        categories = [row[0] for row in cursor.fetchall()]
        cursor.close()

        self.clear_window()
        tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
        self.current_window = tk.Frame(self.root, bg="#d3d3d3")
        self.current_window.pack(expand=True, fill="both")

        tk.Label(self.current_window, text="Available product categories: {}".format(', '.join(categories)), bg="#d3d3d3",
                 font=("Arial", 12), wraplength=350).pack(pady=10)
        tk.Label(self.current_window, text="Please enter product Category:", bg="#d3d3d3").pack(pady=5)
        category_entry = tk.Entry(self.current_window)
        category_entry.pack(pady=5)
        category_entry.focus_set()

        tk.Button(self.current_window, text="Back", command=lambda: self.check_products(back_command)).pack(
            side="right", padx=10)

        def submit():
            cursor = self.connection.cursor()
            vendor_count, _, _ = get_counts(self.connection)
            category = category_entry.get().strip()
            cursor.execute("SELECT * FROM Products WHERE Category = '{}'".format(category))
            products = cursor.fetchall()
            if products:
                self.clear_window()
                tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
                self.current_window = tk.Frame(self.root, bg="#d3d3d3")
                self.current_window.pack(expand=True, fill="both")

                text_area = tk.Text(self.current_window, height=20, width=80)
                text_area.pack(pady=10)
                for product in products:
                    p_id = product[0]
                    text_area.insert(tk.END, "Product {}:\n".format(p_id))
                    text_area.insert(tk.END,
                                     "P_id: {}, Name: {}, Price: {}, Size: {}, Weight: {}, Category: {}, {}".format(
                                         product[0], product[1], product[2], product[3], product[4], product[5],
                                         ", ".join(["Stock{}: {}".format(i + 1, product[i + 6]) for i in range(vendor_count)])) + "\n\n")
                text_area.config(state="disabled")

                tk.Button(self.current_window, text="Back", command=lambda: self.check_products(back_command)).pack(
                    side="right", padx=10)
            else:
                messagebox.showerror("Error", "No products found in this category!")
            cursor.close()

        category_entry.bind("<Return>", lambda event: submit())
        tk.Button(self.current_window, text="Submit", command=submit).pack(pady=5)

    def view_customers(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM Customer")
        customers = cursor.fetchall()
        cursor.close()

        self.clear_window()
        tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
        self.current_window = tk.Frame(self.root, bg="#d3d3d3")
        self.current_window.pack(expand=True, fill="both")

        text_area = tk.Text(self.current_window, height=20, width=80)
        text_area.pack(pady=10)
        for customer in customers:
            c_id = customer[0]
            text_area.insert(tk.END, "Customer {}:\n".format(c_id))
            text_area.insert(tk.END,
                             "C_id: {}, Contact_Number: {}, Address: {}, Order_History: {}\n\n".format(
                                 customer[0], customer[1], customer[2], customer[3]))
        text_area.config(state="disabled")

        tk.Button(self.current_window, text="Back", command=self.show_admin_options).pack(side="right", padx=10)

    def view_vendors(self):
        cursor = self.connection.cursor()
        _, product_count, _ = get_counts(self.connection)
        cursor.execute("SELECT * FROM Vendor")
        vendors = cursor.fetchall()
        cursor.close()

        self.clear_window()
        tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
        self.current_window = tk.Frame(self.root, bg="#d3d3d3")
        self.current_window.pack(expand=True, fill="both")

        text_area = tk.Text(self.current_window, height=20, width=80)
        text_area.pack(pady=10)
        for vendor in vendors:
            v_id = vendor[0]
            text_area.insert(tk.END, "Vendor {}:\n".format(v_id))
            text_area.insert(tk.END,
                             "V_id: {}, Name: {}, Location: {}, Feedback_Score: {}, {}".format(
                                 vendor[0], vendor[1], vendor[2], vendor[3],
                                 ", ".join(["Stock{}: {}".format(i + 1, vendor[i + 4]) for i in range(product_count)])) + "\n\n")
        text_area.config(state="disabled")

        tk.Button(self.current_window, text="Back", command=self.show_admin_options).pack(side="right", padx=10)

    def rate_vendor(self, c_id):
        cursor = self.connection.cursor()
        _, product_count, _ = get_counts(self.connection)
        cursor.execute("SELECT * FROM Orders WHERE C_id = {}".format(c_id))
        orders = cursor.fetchall()
        cursor.execute("SELECT * FROM Order_Item WHERE O_id IN (SELECT O_id FROM Orders WHERE C_id = {})".format(c_id))
        order_items = cursor.fetchall()

        self.clear_window()
        tk.Label(self.root, text="COMP7640_Group11", bg="black", fg="white", font=("Arial", 12)).pack(fill="x")
        self.current_window = tk.Frame(self.root, bg="#d3d3d3")
        self.current_window.pack(expand=True, fill="both")

        text_area = tk.Text(self.current_window, height=5, width=50)
        text_area.pack(pady=10)
        for order, item in zip(orders, order_items):
            o_id = order[0]
            text_area.insert(tk.END, "Order {}:\n".format(o_id))
            text_area.insert(tk.END,
                             "O_id: {}, Shipping_status: {}, C_id: {}, V_id: {}, Total_Price: {}, {}".format(
                                 order[0], order[1], order[2], order[3], item[1],
                                 ", ".join(["Num_Product{}: {}".format(i + 1, item[i + 2]) for i in range(product_count)])) + "\n\n")
        text_area.config(state="disabled")

        tk.Label(self.current_window, text="Please select an O_id to rate:", bg="#d3d3d3").pack(pady=5)
        o_id_entry = tk.Entry(self.current_window)
        o_id_entry.pack(pady=5)
        o_id_entry.focus_set()

        tk.Label(self.current_window, text="Please enter rating (0-100):", bg="#d3d3d3").pack(pady=5)
        score_entry = tk.Entry(self.current_window)
        score_entry.pack(pady=5)

        tk.Button(self.current_window, text="Back", command=lambda: self.show_customer_options(c_id)).pack(side="right",
                                                                                                           padx=10)

        def submit():
            try:
                o_id = int(o_id_entry.get())
                score = int(score_entry.get())
                if not (0 <= score <= 100):
                    messagebox.showerror("Error", "Rating must be between 0 and 100!")
                    return

                cursor.execute("SELECT V_id FROM Orders WHERE O_id = {} AND C_id = {}".format(o_id, c_id))
                result = cursor.fetchone()
                if not result:
                    messagebox.showerror("Error", "Invalid O_id or not your order!")
                    return
                v_id = result[0]

                cursor.execute("SELECT Feedback_Score FROM Vendor WHERE V_id = {}".format(v_id))
                current_score = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM Orders WHERE V_id = {}".format(v_id))
                order_count = cursor.fetchone()[0]
                new_score = (current_score * (order_count - 1) + score) / order_count if current_score else score
                cursor.execute("UPDATE Vendor SET Feedback_Score = {} WHERE V_id = {}".format(new_score, v_id))
                self.connection.commit()
                messagebox.showinfo("Success", "Vendor V_id = {} rating updated to {:.2f}!".format(v_id, new_score))
                self.show_customer_options(c_id)
            except Error as e:
                messagebox.showerror("Error", "Operation failed: {}".format(e))
                self.connection.rollback()
            finally:
                cursor.close()

        o_id_entry.bind("<Return>", lambda event: submit())
        tk.Button(self.current_window, text="Submit", command=submit).pack(pady=5)

# this is initialized figures in database, you can change it or return back to it
    def reset_to_initial(self):
        cursor = self.connection.cursor()
        cursor.execute("DROP TABLE Order_Item, Orders, Customer, Products, Vendor")

        cursor.execute("""
            CREATE TABLE Vendor (
                V_id INT PRIMARY KEY,
                Name VARCHAR(100),
                Location VARCHAR(100),
                Feedback_Score INT,
                Stock1 INT,
                Stock2 INT,
                Stock3 INT,
                Stock4 INT,
                Stock5 INT
            );
        """)
        cursor.execute("""
            CREATE TABLE Products (
                P_id INT PRIMARY KEY,
                Name VARCHAR(100),
                Price FLOAT,
                Size VARCHAR(100),
                Weight VARCHAR(100),
                Category VARCHAR(100),
                Stock1 INT,
                Stock2 INT,
                Stock3 INT
            );
        """)
        cursor.execute("""
            CREATE TABLE Customer (
                C_id INT PRIMARY KEY,
                Contact_Number INT,
                Address VARCHAR(100),
                Order_History VARCHAR(1000)
            );
        """)
        cursor.execute("""
            CREATE TABLE `Orders` (
                O_id INT PRIMARY KEY,
                Shipping_status VARCHAR(100),
                C_id INT,
                V_id INT,
                FOREIGN KEY (C_id) REFERENCES Customer(C_id),
                FOREIGN KEY (V_id) REFERENCES Vendor(V_id)
            );
        """)
        cursor.execute("""
            CREATE TABLE Order_Item (
                O_id INT PRIMARY KEY,
                Total_Price FLOAT,
                Num_Product1 INT,
                Num_Product2 INT,
                Num_Product3 INT,
                Num_Product4 INT,
                Num_Product5 INT,
                FOREIGN KEY (O_id) REFERENCES `Orders`(O_id)
            );
        """)

        cursor.execute("""
            INSERT INTO Customer VALUES 
            (1, 43225655, 'Hong Kong Island', NULL),
            (2, 76872341, 'KowLoon City', NULL),
            (3, 82295616, 'Hong Kong Island', NULL),
            (4, 54888219, 'Singapore', NULL);
        """)
        cursor.execute("""
            INSERT INTO Vendor VALUES 
            (1, 'A', 'China', NULL, 100, 150, 100, 300, 200),
            (2, 'B', 'Japan', NULL, 80, 200, 200, 120, 180),
            (3, 'C', 'Singapore', NULL, 50, 300, 100, 150, 150);
        """)
        cursor.execute("""
            INSERT INTO Products VALUES 
            (1, 'Refrigerator', 3300.0, 'Large', '30kg', 'Furniture', 100, 80, 50),
            (2, 'TV', 5000.0, 'Large', '20kg', 'Furniture', 150, 200, 300),
            (3, 'CCTV', 270.0, 'Small', '0.2kg', 'Electronic products', 100, 200, 100),
            (4, 'Table', 1000.0, 'Medium', "10kg", 'Furniture', 300, 120, 150),
            (5, 'DVD', 600.0, 'Small', '2kg', 'Electronic products', 200, 180, 150);
        """)
        cursor.execute("""
            INSERT INTO Orders VALUES
            (1, 'Signed', 2, 1),
            (2, 'Shipping', 1, 3),
            (3, 'Awaiting', 3, 1),
            (4, 'Signed', 4, 2);
        """)
        cursor.execute("""
            INSERT INTO Order_Item VALUES
            (1, 118700.0, 20, 10, 10, 0, 0),
            (2, 31200.0, 5, 0, 10, 0, 20),
            (3, 47070.0, 0, 7, 21, 4, 4),
            (4, 82900.0, 6, 11, 30, 0, 0);
        """)

        self.connection.commit()
        cursor.close()
        messagebox.showinfo("Success", "Restored to initial state!")
        self.show_admin_options()


if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()