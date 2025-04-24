import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
import sqlite3

class LoginWindow:
    def _init_(self, master):
        self.master = master
        self.master.title("Login")
        self.master.geometry("300x150")

        self.label_username = tk.Label(master, text="Username:")
        self.label_username.pack()

        self.entry_username = tk.Entry(master)
        self.entry_username.pack()

        self.label_password = tk.Label(master, text="Password:")
        self.label_password.pack()

        self.entry_password = tk.Entry(master, show="*")
        self.entry_password.pack()

        self.button_login = tk.Button(master, text="Login", command=self.login)
        self.button_login.pack()

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        # Replace this with your authentication logic
        if username == "admin" and password == "password":
            self.master.destroy()
            root = tk.Tk()
            app = EmployeeManagementApp(root)
            root.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

class EmployeeManagementApp:
    def _init_(self, master):
        self.master = master
        self.master.title("Employee Management System")
        self.master.geometry("600x400")
        self.create_database_connection()
        self.create_table()

        self.tree = ttk.Treeview(master, columns=("ID", "Name", "Salary"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Salary", text="Salary")
        self.tree.pack(pady=20)

        add_button = tk.Button(master, text="Add Employee", command=self.add_employee, bg="sky blue", fg="black")
        add_button.pack(side=tk.LEFT, padx=10)

        remove_button = tk.Button(master, text="Remove Employee", command=self.remove_employee, bg="orange", fg="black")
        remove_button.pack(side=tk.LEFT, padx=10)

        search_button = tk.Button(master, text="Search Employee", command=self.search_employee, bg="light green", fg="black")
        search_button.pack(side=tk.LEFT, padx=10)

        update_button = tk.Button(master, text="Update Salary", command=self.update_salary, bg="yellow", fg="black")
        update_button.pack(side=tk.LEFT, padx=10)

        # Initialize the treeview with existing data
        self.update_treeview()

    def create_database_connection(self):
        try:
            self.conn = sqlite3.connect("employee.db")
            self.cur = self.conn.cursor()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error connecting to database: {e}")
            self.master.destroy()

    def create_table(self):
        try:
            self.cur.execute("""CREATE TABLE IF NOT EXISTS employees (
                                id INTEGER PRIMARY KEY,
                                name TEXT,
                                salary REAL
                            )""")
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error creating table: {e}")
            self.master.destroy()

        # If the table exists but the 'id' column is missing, recreate the table
        self.cur.execute("PRAGMA table_info(employees)")
        columns = self.cur.fetchall()
        if not any(column[1] == 'id' for column in columns):
            self.cur.execute("DROP TABLE IF EXISTS employees")
            self.create_table()

    def add_employee(self):
        id = simpledialog.askinteger("Add Employee", "Enter employee ID:")
        if id is None:
            return
        elif self.employee_exists(id):
            messagebox.showwarning("Duplicate ID", "This ID already exists. Please enter a unique ID.")
            return

        name = simpledialog.askstring("Add Employee", "Enter employee name:")
        if name is None:
            return

        salary = simpledialog.askfloat("Add Employee", "Enter employee salary:")
        if salary is None:
            return

        self.cur.execute("INSERT INTO employees (id, name, salary) VALUES (?, ?, ?)", (id, name, salary))
        self.conn.commit()
        self.tree.insert("", "end", values=(id, name, salary))

    def remove_employee(self):
        id = simpledialog.askinteger("Remove Employee", "Enter employee ID:")
        if id is None:
            return
        self.cur.execute("DELETE FROM employees WHERE id = ?", (id,))
        if self.cur.rowcount == 1:
            self.conn.commit()
            self.update_treeview()
        else:
            messagebox.showwarning("Not Found", "Employee ID not found.")

    def search_employee(self):
        id = simpledialog.askinteger("Search Employee", "Enter employee ID:")
        if id is None:
            return
        self.cur.execute("SELECT * FROM employees WHERE id = ?", (id,))
        employee = self.cur.fetchone()
        if employee:
            messagebox.showinfo("Employee Found", f"ID: {employee[0]}\nName: {employee[1]}\nSalary: {employee[2]}")
        else:
            messagebox.showwarning("Not Found", "Employee ID not found.")

    def update_salary(self):
        id = simpledialog.askinteger("Update Salary", "Enter employee ID:")
        if id is None:
            return
        salary = simpledialog.askfloat("Update Salary", "Enter new salary:")
        if salary is not None:
            self.cur.execute("UPDATE employees SET salary = ? WHERE id = ?", (salary, id))
            if self.cur.rowcount == 1:
                self.conn.commit()
                self.update_treeview()
            else:
                messagebox.showwarning("Not Found", "Employee ID not found.")

    def employee_exists(self, id):
        self.cur.execute("SELECT COUNT(*) FROM employees WHERE id = ?", (id,))
        return self.cur.fetchone()[0] > 0

    def update_treeview(self):
        self.tree.delete(*self.tree.get_children())
        self.cur.execute("SELECT * FROM employees")
        for employee in self.cur.fetchall():
            self.tree.insert("", "end", values=employee)

    def _del_(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if _name_ == "_main_":
    root = tk.Tk()
    login_window = LoginWindow(root)
    root.mainloop()
