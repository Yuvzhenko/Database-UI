import os
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Система управління будівельною БД")
        self.geometry("1400x650")
        self.configure(bg="#f5f6fa")

        load_dotenv()

        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME')
        }

        self.main_container = tk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.sidebar = tk.Frame(self.main_container, bg="#2c3e50", width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        self.workspace = tk.Frame(self.main_container, bg="#f5f6fa")
        self.workspace.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.setup_menu()

        self.pages = {}

        for PageClass in (ProjectsPage, BuildersPage, CompaniesPage, SubdivisionsPage):
            page_name = PageClass.__name__
            frame = PageClass(parent=self.workspace, controller=self)
            self.pages[page_name] = frame
            
        self.show_page("ProjectsPage")

    def setup_menu(self):
        logo_label = tk.Label(self.sidebar, text="БУДІВНИЦТВО\nБаза Даних", 
                              font=("Arial", 14, "bold"), fg="#ecf0f1", bg="#2c3e50")
        logo_label.pack(pady=25)

        separator = tk.Frame(self.sidebar, bg="#34495e", height=2)
        separator.pack(fill=tk.X, padx=15, pady=(0, 20))

        btn_style = {
            "font": ("Arial", 11, "bold"),
            "bg": "#34495e",
            "fg": "#ecf0f1",
            "activebackground": "#1abc9c",
            "activeforeground": "white",
            "relief": tk.FLAT,
            "anchor": "w",
            "padx": 20
        }

        btn_projects = tk.Button(self.sidebar, text="Проєкти", **btn_style, command=lambda: self.show_page("ProjectsPage"))
        btn_projects.pack(fill=tk.X, padx=10, pady=5, ipady=8)

        btn_builders = tk.Button(self.sidebar, text="Будівельники", **btn_style, command=lambda: self.show_page("BuildersPage"))
        btn_builders.pack(fill=tk.X, padx=10, pady=5, ipady=8)

        btn_companies = tk.Button(self.sidebar, text="Будівельні компанії", **btn_style, command=lambda: self.show_page("CompaniesPage"))
        btn_companies.pack(fill=tk.X, padx=10, pady=5, ipady=8)

        btn_subdivisions = tk.Button(self.sidebar, text="Підрозділи", **btn_style, command=lambda: self.show_page("SubdivisionsPage"))
        btn_subdivisions.pack(fill=tk.X, padx=10, pady=5, ipady=8)

    def show_page(self, page_name):
        for frame in self.pages.values():
            frame.pack_forget()

        current_page = self.pages[page_name]
        current_page.pack(fill=tk.BOTH, expand=True)

    def get_db_connection(self):
        try:
            return mysql.connector.connect(**self.db_config)
        except Error as e:
            messagebox.showerror("Помилка з'єднання", "Не вдалося підключитися до бази данних")
            print(f'database error: {e}')
            return None

class ProjectsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f5f6fa")
        self.controller = controller

        self.setup_ui()
        self.load_companies()

    def setup_ui(self):
        title = tk.Label(self, text="Управління Будівельними Проєктами", 
                         font=("Arial", 18, "bold"), bg="#f5f6fa", fg="#2c3e50")
        title.pack(anchor="w", padx=20, pady=15)
        
        top_management_frame = tk.Frame(self, bg="#f5f6fa")
        top_management_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.action_var = tk.StringVar(value="SELECT")
        radio_frame = tk.LabelFrame(top_management_frame, text=" Оберіть операцію ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=5)
        radio_frame.grid(row=0, column=0, sticky="nw")

        tk.Radiobutton(radio_frame, text="Отримати проєкти (SELECT)", variable=self.action_var, value="SELECT", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Додати новий проєкт (INSERT)", variable=self.action_var, value="INSERT", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Оновити проєкт (UPDATE)", variable=self.action_var, value="UPDATE", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Вилучити проєкт (DELETE)", variable=self.action_var, value="DELETE", bg="white").pack(anchor="w")

        input_frame = tk.LabelFrame(self, text=" Поля запису таблиці `projects` ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        input_frame.pack(fill=tk.X, padx=20, pady=15)

        labels = ["ID", "Назва проєкту", "Дата завершення (РРРР-ММ-ДД)", "Адреса", "Вартість (грн)", "Компанія (ЄДРПОУ)"]
        self.entries = {}

        for i, label_text in enumerate(labels):
            tk.Label(input_frame, text=label_text, bg="white", font=("Arial", 9)).grid(row=0, column=i, padx=5, sticky="w")
            
            if "ЄДРПОУ" in label_text:
                self.company_cb = ttk.Combobox(input_frame, width=18, state="readonly")
                self.company_cb.grid(row=1, column=i, padx=5, pady=5)
                self.entries["company"] = self.company_cb
            else:
                entry = tk.Entry(input_frame, width=12 if i == 0 else 22)
                entry.grid(row=1, column=i, padx=5, pady=5)
                key = ["id", "name", "completion_date", "address", "price"][i]
                self.entries[key] = entry

        bottom_frame = tk.Frame(self, bg="#f5f6fa")
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        tk.Button(bottom_frame, text="Виконати\nзапит", width=14, height=3, 
                  bg="#1abc9c", fg="white", font=("Arial", 11, "bold"), 
                  relief=tk.RAISED, command=self.execute_query).pack(side=tk.LEFT, anchor="nw", pady=20, padx=(0, 20))
        tk.Button(bottom_frame, text="Очистити\nполя", width=10, height=3, 
                  bg="#95a5a6", fg="white", font=("Arial", 10, "bold"), 
                  relief=tk.RAISED, command=self.clear_entries).pack(side=tk.LEFT, anchor="nw", pady=20, padx=(0, 20))

        result_frame = tk.Frame(bottom_frame, bg="#f5f6fa")
        result_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.status_label = tk.Label(result_frame, text="", font=("Arial", 10, "bold"), bg="#f5f6fa", fg="#27ae60")
        self.status_label.pack(anchor="w", pady=(0, 5))

        columns = ("id", "name", "date", "address", "price", "company")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=10)

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Назва проєкту")
        self.tree.heading("date", text="Дата заверш.")
        self.tree.heading("address", text="Адреса")
        self.tree.heading("price", text="Ціна")
        self.tree.heading("company", text="Компанія")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("name", width=180, anchor="w")
        self.tree.column("date", width=90, anchor="center")
        self.tree.column("address", width=250, anchor="w")
        self.tree.column("price", width=80, anchor="e")
        self.tree.column("company", width=80, anchor="center")

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_y = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=scrollbar_y.set)

    def load_companies(self):
        conn = self.controller.get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT USREOU FROM construction_companies")
                companies = [row[0] for row in cursor.fetchall()]

                companies.insert(0, "") 
                
                self.company_cb['values'] = companies
            except Error as e:
                print(f"Помилка завантаження компаній: {e}")
            finally:
                cursor.close()
                conn.close()

    def execute_query(self):
        action = self.action_var.get()

        self.status_label.config(text="", fg="#27ae60")
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        conn = self.controller.get_db_connection()
        if not conn:
            return

        cursor = conn.cursor(dictionary=True)
        
        try:
            if action == "SELECT":
                query = "SELECT * FROM projects WHERE 1=1"
                params = []
                
                if self.entries['id'].get():
                    query += " AND id = %s"
                    params.append(self.entries['id'].get())
                    
                if self.entries['name'].get():
                    query += " AND name LIKE %s"
                    params.append(f"%{self.entries['name'].get()}%")
                    
                if self.entries['completion_date'].get():
                    query += " AND completion_date LIKE %s"
                    params.append(f"%{self.entries['completion_date'].get()}%")
                    
                if self.entries['address'].get():
                    query += " AND address LIKE %s"
                    params.append(f"%{self.entries['address'].get()}%")
                    
                if self.entries['price'].get():
                    query += " AND price = %s"
                    params.append(self.entries['price'].get())
                    
                if self.entries['company'].get():
                    query += " AND company = %s"
                    params.append(self.entries['company'].get())
                    
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                
                if rows:
                    for row in rows:
                        self.tree.insert("", tk.END, values=(
                            row['id'], row['name'], row['completion_date'], 
                            row['address'], row['price'], row['company']
                        ))
                    self.status_label.config(text=f"Успіх: Знайдено {len(rows)} записів.", fg="#27ae60")
                else:
                    self.status_label.config(text="Записів за вказаними критеріями не знайдено.", fg="#e67e22")

            elif action == "INSERT":
                query = """INSERT INTO projects (name, completion_date, address, price, company) 
                           VALUES (%s, %s, %s, %s, %s)"""
                params = (
                    self.entries['name'].get(),
                    self.entries['completion_date'].get(),
                    self.entries['address'].get(),
                    self.entries['price'].get() or None,
                    self.entries['company'].get()
                )
                cursor.execute(query, params)
                conn.commit()
                self.status_label.config(text=f"Успішно додано новий проєкт! ID: {cursor.lastrowid}")

            elif action == "UPDATE":
                if not self.entries['id'].get():
                    raise ValueError("Необхідно вказати ID проєкту для оновлення.")
                
                query = """UPDATE projects SET name=%s, completion_date=%s, address=%s, 
                           price=%s, company=%s WHERE id=%s"""
                params = (
                    self.entries['name'].get(),
                    self.entries['completion_date'].get(),
                    self.entries['address'].get(),
                    self.entries['price'].get() or None,
                    self.entries['company'].get(),
                    self.entries['id'].get()
                )
                cursor.execute(query, params)
                conn.commit()
                self.status_label.config(text=f"Успішно оновлено. Змінено рядків: {cursor.rowcount}")

            elif action == "DELETE":
                if not self.entries['id'].get():
                    raise ValueError("Необхідно вказати ID проєкту для видалення.")
                
                query = "DELETE FROM projects WHERE id=%s"
                cursor.execute(query, (self.entries['id'].get(),))
                conn.commit()
                self.status_label.config(text=f"Запис видалено. Вилучено рядків: {cursor.rowcount}")

        except Exception as e:
            self.status_label.config(text=f"Помилка: {e}", fg="#e74c3c")
        finally:
            cursor.close()
            conn.close()

    def clear_entries(self):
        for key, entry in self.entries.items():
            if isinstance(entry, ttk.Combobox):
                entry.set("")
            else:
                entry.delete(0, tk.END)

class BuildersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f5f6fa")
        
        title = tk.Label(self, text="Управління Персоналом", font=("Arial", 18, "bold"), bg="#f5f6fa", fg="#2c3e50")
        title.pack(anchor="w", padx=20, pady=20)
        
        content_frame = tk.LabelFrame(self, text="Панель дій для будівельників", font=("Arial", 10, "bold"), bg="white", padx=15, pady=15)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)


class CompaniesPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f5f6fa")
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        title = tk.Label(self, text="Будівельні Організації (таблиця `construction_companies`)", 
                         font=("Arial", 18, "bold"), bg="#f5f6fa", fg="#2c3e50")
        title.pack(anchor="w", padx=20, pady=15)
        
        top_management_frame = tk.Frame(self, bg="#f5f6fa")
        top_management_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.action_var = tk.StringVar(value="SELECT")
        radio_frame = tk.LabelFrame(top_management_frame, text=" Оберіть операцію ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=5)
        radio_frame.pack(side=tk.LEFT, anchor="nw")

        tk.Radiobutton(radio_frame, text="Отримати компанії (SELECT)", variable=self.action_var, value="SELECT", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Додати компанію (INSERT)", variable=self.action_var, value="INSERT", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Оновити компанію за ЄДРПОУ (UPDATE)", variable=self.action_var, value="UPDATE", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Вилучити компанію за ЄДРПОУ (DELETE)", variable=self.action_var, value="DELETE", bg="white").pack(anchor="w")

        input_frame = tk.LabelFrame(self, text=" Поля запису таблиці `construction_companies` ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        input_frame.pack(fill=tk.X, padx=20, pady=15)

        labels = ["Код ЄДРПОУ (USREOU)", "Назва компанії", "Номер ліцензії", "Юридична адреса"]
        self.entries = {}

        for i, label_text in enumerate(labels):
            tk.Label(input_frame, text=label_text, bg="white", font=("Arial", 9)).grid(row=0, column=i, padx=5, sticky="w")

            entry_width = 35 if i == 3 else 20
            entry = tk.Entry(input_frame, width=entry_width)
            entry.grid(row=1, column=i, padx=5, pady=5)
            
            key = ["usreou", "name", "license_number", "legal_address"][i]
            self.entries[key] = entry

        bottom_frame = tk.Frame(self, bg="#f5f6fa")
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        btn_frame = tk.Frame(bottom_frame, bg="#f5f6fa")
        btn_frame.pack(side=tk.LEFT, anchor="nw", pady=20, padx=(0, 20))

        tk.Button(btn_frame, text="Виконати\nзапит", width=14, height=3, 
                  bg="#1abc9c", fg="white", font=("Arial", 11, "bold"), 
                  relief=tk.RAISED, command=self.execute_query).pack(pady=(0, 10))

        tk.Button(btn_frame, text="Очистити\nполя", width=14, height=3, 
                  bg="#95a5a6", fg="white", font=("Arial", 11, "bold"), 
                  relief=tk.RAISED, command=self.clear_entries).pack()

        result_frame = tk.Frame(bottom_frame, bg="#f5f6fa")
        result_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.status_label = tk.Label(result_frame, text="", font=("Arial", 10, "bold"), bg="#f5f6fa", fg="#27ae60")
        self.status_label.pack(anchor="w", pady=(0, 5))

        columns = ("usreou", "name", "license", "address")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=10)

        self.tree.heading("usreou", text="ЄДРПОУ")
        self.tree.heading("name", text="Назва компанії")
        self.tree.heading("license", text="Ліцензія")
        self.tree.heading("address", text="Юридична адреса")

        self.tree.column("usreou", width=100, anchor="center")
        self.tree.column("name", width=150, anchor="w")
        self.tree.column("license", width=120, anchor="center")
        self.tree.column("address", width=300, anchor="w")

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_y = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=scrollbar_y.set)

    def clear_entries(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def execute_query(self):
        action = self.action_var.get()
        
        self.status_label.config(text="", fg="#27ae60")
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        conn = self.controller.get_db_connection()
        if not conn:
            return

        cursor = conn.cursor(dictionary=True)
        
        try:
            if action == "SELECT":
                query = "SELECT * FROM construction_companies WHERE 1=1"
                params = []

                if self.entries['usreou'].get():
                    query += " AND USREOU = %s"
                    params.append(self.entries['usreou'].get())
                    
                if self.entries['name'].get():
                    query += " AND name LIKE %s"
                    params.append(f"%{self.entries['name'].get()}%")
                    
                if self.entries['license_number'].get():
                    query += " AND license_number LIKE %s"
                    params.append(f"%{self.entries['license_number'].get()}%")
                    
                if self.entries['legal_address'].get():
                    query += " AND legal_address LIKE %s"
                    params.append(f"%{self.entries['legal_address'].get()}%")
                    
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                
                if rows:
                    for row in rows:
                        self.tree.insert("", tk.END, values=(
                            row['USREOU'], row['name'], 
                            row['license_number'], row['legal_address']
                        ))
                    self.status_label.config(text=f"Успіх: Знайдено {len(rows)} записів.", fg="#27ae60")
                else:
                    self.status_label.config(text="Записів за вказаними критеріями не знайдено.", fg="#e67e22")

            elif action == "INSERT":
                if not self.entries['usreou'].get():
                    raise ValueError("Помилка: Код ЄДРПОУ є обов'язковим для додавання компанії.")
                    
                query = """INSERT INTO construction_companies (USREOU, name, license_number, legal_address) 
                           VALUES (%s, %s, %s, %s)"""
                params = (
                    self.entries['usreou'].get(),
                    self.entries['name'].get() or None,
                    self.entries['license_number'].get() or None,
                    self.entries['legal_address'].get() or None
                )
                cursor.execute(query, params)
                conn.commit()
                self.status_label.config(text=f"Успішно додано компанію з ЄДРПОУ: {self.entries['usreou'].get()}")

            elif action == "UPDATE":
                if not self.entries['usreou'].get():
                    raise ValueError("Помилка: Необхідно вказати ЄДРПОУ компанії для оновлення.")
                
                query = """UPDATE construction_companies SET name=%s, license_number=%s, legal_address=%s 
                           WHERE USREOU=%s"""
                params = (
                    self.entries['name'].get() or None,
                    self.entries['license_number'].get() or None,
                    self.entries['legal_address'].get() or None,
                    self.entries['usreou'].get()
                )
                cursor.execute(query, params)
                conn.commit()
                if cursor.rowcount == 0:
                    self.status_label.config(text="Компанію з таким ЄДРПОУ не знайдено.", fg="#e67e22")
                else:
                    self.status_label.config(text=f"Успішно оновлено. Змінено рядків: {cursor.rowcount}")

            elif action == "DELETE":
                if not self.entries['usreou'].get():
                    raise ValueError("Помилка: Необхідно вказати ЄДРПОУ компанії для видалення.")
                
                query = "DELETE FROM construction_companies WHERE USREOU=%s"
                cursor.execute(query, (self.entries['usreou'].get(),))
                conn.commit()
                if cursor.rowcount == 0:
                    self.status_label.config(text="Компанію з таким ЄДРПОУ не знайдено.", fg="#e67e22")
                else:
                    self.status_label.config(text=f"Запис видалено. Вилучено рядків: {cursor.rowcount}")

        except Exception as e:
            self.status_label.config(text=f"Помилка: {e}", fg="#e74c3c")
        finally:
            cursor.close()
            conn.close()
    
class SubdivisionsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f5f6fa")
        
        title = tk.Label(self, text="Підрозділи компаній", font=("Arial", 18, "bold"), bg="#f5f6fa", fg="#2c3e50")
        title.pack(anchor="w", padx=20, pady=20)
        
        content_frame = tk.LabelFrame(self, text="Панель дій для підрозділів", font=("Arial", 10, "bold"), bg="white", padx=15, pady=15)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()