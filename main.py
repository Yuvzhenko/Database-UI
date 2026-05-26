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

        for PageClass in (ProjectsPage, BuildersPage, CompaniesPage, SubdivisionsPage, ContractsPage, WorkPage, PositionPage):
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

        btn_subdivisions = tk.Button(self.sidebar, text="Контракти", **btn_style, command=lambda: self.show_page("ContractsPage"))
        btn_subdivisions.pack(fill=tk.X, padx=10, pady=5, ipady=8)

        btn_subdivisions = tk.Button(self.sidebar, text="Призначити посаду", **btn_style, command=lambda: self.show_page("WorkPage"))
        btn_subdivisions.pack(fill=tk.X, padx=10, pady=5, ipady=8)

        btn_subdivisions = tk.Button(self.sidebar, text="Посади", **btn_style, command=lambda: self.show_page("PositionPage"))
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
        radio_frame.pack(side=tk.LEFT, anchor="nw")

        tk.Radiobutton(radio_frame, text="Отримати (SELECT)", variable=self.action_var, value="SELECT", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Додати (INSERT)", variable=self.action_var, value="INSERT", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Оновити (UPDATE)", variable=self.action_var, value="UPDATE", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Вилучити (DELETE)", variable=self.action_var, value="DELETE", bg="white").pack(anchor="w")

        input_frame = tk.LabelFrame(self, text=" Поля запису таблиці `projects` ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        input_frame.pack(fill=tk.X, padx=20, pady=15)

        labels = ["ID", "Назва проєкту", "Дата завершення (РРРР-ММ-ДД)", "Адреса", "Вартість (грн)", "Компанія (ЄДРПОУ)", "Субпідрядник", "Тип проєкту"]
        self.entries = {}
        db_keys = ["id", "name", "completion_date", "address", "price"]

        for i, label_text in enumerate(labels):
            tk.Label(input_frame, text=label_text, bg="white", font=("Arial", 9)).grid(row=0, column=i, padx=5, sticky="w")
            
            if label_text == "Компанія (ЄДРПОУ)":
                self.company_cb = ttk.Combobox(input_frame, width=15, state="readonly")
                self.company_cb.grid(row=1, column=i, padx=5, pady=5)
                self.entries["company"] = self.company_cb
            elif label_text == "Субпідрядник":
                self.subcontractor_cb = ttk.Combobox(input_frame, width=15, state="readonly")
                self.subcontractor_cb.grid(row=1, column=i, padx=5, pady=5)
                self.entries["subcontractor"] = self.subcontractor_cb
            elif label_text == "Тип проєкту":
                self.type_cb = ttk.Combobox(input_frame, width=15, values=["", "Індустріальний", "Інфраструктурний", "Житловий"], state="readonly")
                self.type_cb.grid(row=1, column=i, padx=5, pady=5)
                self.type_cb.bind("<<ComboboxSelected>>", self.toggle_sub_fields)
            else:
                entry = tk.Entry(input_frame, width=8 if i == 0 else 18)
                entry.grid(row=1, column=i, padx=5, pady=5)
                self.entries[db_keys[i]] = entry

        self.sub_fields_frame = tk.Frame(input_frame, bg="white")
        self.sub_fields_frame.grid(row=2, column=0, columnspan=8, sticky="w", pady=5)

        self.sub_entries = {
            "difficulty": tk.Entry(self.sub_fields_frame, width=15),
            "electricity_power": tk.Entry(self.sub_fields_frame, width=15),
            "length": tk.Entry(self.sub_fields_frame, width=15),
            "material": tk.Entry(self.sub_fields_frame, width=15),
            "floors_quantity": tk.Entry(self.sub_fields_frame, width=15),
            "rooms_quantity": tk.Entry(self.sub_fields_frame, width=15)
        }

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

        columns = ("id", "name", "date", "address", "price", "company", "subcontractor", "type", "details")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=10)

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Назва проєкту")
        self.tree.heading("date", text="Дата заверш.")
        self.tree.heading("address", text="Адреса")
        self.tree.heading("price", text="Ціна")
        self.tree.heading("company", text="Генпідрядник")
        self.tree.heading("subcontractor", text="Субпідрядник")
        self.tree.heading("type", text="Тип проєкту")
        self.tree.heading("details", text="Додаткові відомості")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("name", width=130, anchor="w")
        self.tree.column("date", width=80, anchor="center")
        self.tree.column("address", width=160, anchor="w")
        self.tree.column("price", width=70, anchor="e")
        self.tree.column("company", width=90, anchor="center")
        self.tree.column("subcontractor", width=90, anchor="center")
        self.tree.column("type", width=100, anchor="center")
        self.tree.column("details", width=200, anchor="w")

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_y = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=scrollbar_y.set)

    def toggle_sub_fields(self, event=None):
        for widget in self.sub_fields_frame.winfo_children():
            widget.grid_forget()
            
        p_type = self.type_cb.get()
        if p_type == "Індустріальний":
            tk.Label(self.sub_fields_frame, text="Складність (difficulty)", bg="white", font=("Arial", 8)).grid(row=0, column=0, padx=5, sticky="w")
            self.sub_entries["difficulty"].grid(row=1, column=0, padx=5, pady=2)
            tk.Label(self.sub_fields_frame, text="Потужність (electricity_power)", bg="white", font=("Arial", 8)).grid(row=0, column=1, padx=5, sticky="w")
            self.sub_entries["electricity_power"].grid(row=1, column=1, padx=5, pady=2)
        elif p_type == "Інфраструктурний":
            tk.Label(self.sub_fields_frame, text="Довжина (length)", bg="white", font=("Arial", 8)).grid(row=0, column=0, padx=5, sticky="w")
            self.sub_entries["length"].grid(row=1, column=0, padx=5, pady=2)
            tk.Label(self.sub_fields_frame, text="Матеріал (material)", bg="white", font=("Arial", 8)).grid(row=0, column=1, padx=5, sticky="w")
            self.sub_entries["material"].grid(row=1, column=1, padx=5, pady=2)
        elif p_type == "Житловий":
            tk.Label(self.sub_fields_frame, text="Кількість поверхів (floors)", bg="white", font=("Arial", 8)).grid(row=0, column=0, padx=5, sticky="w")
            self.sub_entries["floors_quantity"].grid(row=1, column=0, padx=5, pady=2)
            tk.Label(self.sub_fields_frame, text="Кількість кімнат (rooms)", bg="white", font=("Arial", 8)).grid(row=0, column=1, padx=5, sticky="w")
            self.sub_entries["rooms_quantity"].grid(row=1, column=1, padx=5, pady=2)

    def load_companies(self):
        conn = self.controller.get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT USREOU FROM construction_companies")
                companies = [row[0] for row in cursor.fetchall()]
                companies.insert(0, "")
                self.company_cb['values'] = companies
                self.subcontractor_cb['values'] = companies
            except:
                pass
            finally:
                cursor.close()
                conn.close()

    def clear_entries(self):
        for key in ["id", "name", "completion_date", "address", "price"]:
            self.entries[key].delete(0, tk.END)
        self.company_cb.set("")
        self.subcontractor_cb.set("")
        self.type_cb.set("")
        for entry in self.sub_entries.values():
            entry.delete(0, tk.END)
        self.toggle_sub_fields()

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
                query = """SELECT p.*, s.USREOU as subcontractor,
                           ind.difficulty, ind.electricity_power,
                           inf.length, inf.material,
                           res.floors_quantity, res.rooms_quantity
                           FROM projects p
                           LEFT JOIN subcontractor s ON p.id = s.project_id
                           LEFT JOIN industrial_buildings ind ON p.id = ind.project_id
                           LEFT JOIN infrastructure_buildings inf ON p.id = inf.project_id
                           LEFT JOIN residential_buildings res ON p.id = res.project_id
                           WHERE 1=1"""
                params = []
                
                if self.entries['id'].get():
                    query += " AND p.id = %s"
                    params.append(self.entries['id'].get())
                if self.entries['name'].get():
                    query += " AND p.name LIKE %s"
                    params.append(f"%{self.entries['name'].get()}%")
                if self.entries['completion_date'].get():
                    query += " AND p.completion_date LIKE %s"
                    params.append(f"%{self.entries['completion_date'].get()}%")
                if self.entries['address'].get():
                    query += " AND p.address LIKE %s"
                    params.append(f"%{self.entries['address'].get()}%")
                if self.entries['price'].get():
                    query += " AND p.price = %s"
                    params.append(self.entries['price'].get())
                if self.company_cb.get():
                    query += " AND p.company = %s"
                    params.append(self.company_cb.get())
                if self.subcontractor_cb.get():
                    query += " AND s.USREOU = %s"
                    params.append(self.subcontractor_cb.get())
                    
                p_type = self.type_cb.get()
                if p_type == "Індустріальний":
                    query += " AND ind.project_id IS NOT NULL"
                    if self.sub_entries['difficulty'].get():
                        query += " AND ind.difficulty LIKE %s"
                        params.append(f"%{self.sub_entries['difficulty'].get()}%")
                    if self.sub_entries['electricity_power'].get():
                        query += " AND ind.electricity_power LIKE %s"
                        params.append(f"%{self.sub_entries['electricity_power'].get()}%")
                elif p_type == "Інфраструктурний":
                    query += " AND inf.project_id IS NOT NULL"
                    if self.sub_entries['length'].get():
                        query += " AND inf.length LIKE %s"
                        params.append(f"%{self.sub_entries['length'].get()}%")
                    if self.sub_entries['material'].get():
                        query += " AND inf.material LIKE %s"
                        params.append(f"%{self.sub_entries['material'].get()}%")
                elif p_type == "Житловий":
                    query += " AND res.project_id IS NOT NULL"
                    if self.sub_entries['floors_quantity'].get():
                        query += " AND res.floors_quantity = %s"
                        params.append(self.sub_entries['floors_quantity'].get())
                    if self.sub_entries['rooms_quantity'].get():
                        query += " AND res.rooms_quantity = %s"
                        params.append(self.sub_entries['rooms_quantity'].get())

                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                
                if rows:
                    for row in rows:
                        derived_type = "Звичайний"
                        details = ""
                        if row['difficulty'] is not None or row['electricity_power'] is not None:
                            derived_type = "Індустріальний"
                            details = f"Складність: {row['difficulty'] or '-'}, Потужність: {row['electricity_power'] or '-'}"
                        elif row['length'] is not None or row['material'] is not None:
                            derived_type = "Інфраструктурний"
                            details = f"Довжина: {row['length'] or '-'}, Матеріал: {row['material'] or '-'}"
                        elif row['floors_quantity'] is not None or row['rooms_quantity'] is not None:
                            derived_type = "Житловий"
                            details = f"Поверхів: {row['floors_quantity'] or '-'}, Кімнат: {row['rooms_quantity'] or '-'}"
                            
                        self.tree.insert("", tk.END, values=(
                            row['id'], row['name'], row['completion_date'], 
                            row['address'], row['price'], row['company'],
                            row['subcontractor'] or "-", derived_type, details
                        ))
                    self.status_label.config(text=f"Успіх: Знайдено {len(rows)} записів.", fg="#27ae60")
                else:
                    self.status_label.config(text="Записів не знайдено.", fg="#e67e22")

            elif action == "INSERT":
                if not self.company_cb.get():
                    raise ValueError("Необхідно обрати Компанію.")
                    
                query = """INSERT INTO projects (name, completion_date, address, price, company) 
                           VALUES (%s, %s, %s, %s, %s)"""
                params = (
                    self.entries['name'].get(),
                    self.entries['completion_date'].get(),
                    self.entries['address'].get(),
                    self.entries['price'].get() or None,
                    self.company_cb.get()
                )
                cursor.execute(query, params)
                project_id = cursor.lastrowid
                
                sub_company = self.subcontractor_cb.get()
                if sub_company:
                    cursor.execute("INSERT INTO subcontractor (project_id, USREOU) VALUES (%s, %s)", (project_id, sub_company))

                p_type = self.type_cb.get()
                if p_type == "Індустріальний":
                    cursor.execute("INSERT INTO industrial_buildings (project_id, difficulty, electricity_power) VALUES (%s, %s, %s)",
                                   (project_id, self.sub_entries['difficulty'].get() or None, self.sub_entries['electricity_power'].get() or None))
                elif p_type == "Інфраструктурний":
                    cursor.execute("INSERT INTO infrastructure_buildings (project_id, length, material) VALUES (%s, %s, %s)",
                                   (project_id, self.sub_entries['length'].get() or None, self.sub_entries['material'].get() or None))
                elif p_type == "Житловий":
                    cursor.execute("INSERT INTO residential_buildings (project_id, floors_quantity, rooms_quantity) VALUES (%s, %s, %s)",
                                   (project_id, self.sub_entries['floors_quantity'].get() or None, self.sub_entries['rooms_quantity'].get() or None))
                                   
                conn.commit()
                self.status_label.config(text=f"Успішно додано новий проєкт! ID: {project_id}")

            elif action == "UPDATE":
                project_id = self.entries['id'].get()
                if not project_id:
                    raise ValueError("Необхідно вказати ID проєкту для оновлення.")
                
                query = """UPDATE projects SET name=%s, completion_date=%s, address=%s, price=%s, company=%s WHERE id=%s"""
                params = (
                    self.entries['name'].get(),
                    self.entries['completion_date'].get(),
                    self.entries['address'].get(),
                    self.entries['price'].get() or None,
                    self.company_cb.get(),
                    project_id
                )
                cursor.execute(query, params)
                
                cursor.execute("DELETE FROM subcontractor WHERE project_id=%s", (project_id,))
                sub_company = self.subcontractor_cb.get()
                if sub_company:
                    cursor.execute("INSERT INTO subcontractor (project_id, USREOU) VALUES (%s, %s)", (project_id, sub_company))

                cursor.execute("DELETE FROM industrial_buildings WHERE project_id=%s", (project_id,))
                cursor.execute("DELETE FROM infrastructure_buildings WHERE project_id=%s", (project_id,))
                cursor.execute("DELETE FROM residential_buildings WHERE project_id=%s", (project_id,))
                
                p_type = self.type_cb.get()
                if p_type == "Індустріальний":
                    cursor.execute("INSERT INTO industrial_buildings (project_id, difficulty, electricity_power) VALUES (%s, %s, %s)",
                                   (project_id, self.sub_entries['difficulty'].get() or None, self.sub_entries['electricity_power'].get() or None))
                elif p_type == "Інфраструктурний":
                    cursor.execute("INSERT INTO infrastructure_buildings (project_id, length, material) VALUES (%s, %s, %s)",
                                   (project_id, self.sub_entries['length'].get() or None, self.sub_entries['material'].get() or None))
                elif p_type == "Житловий":
                    cursor.execute("INSERT INTO residential_buildings (project_id, floors_quantity, rooms_quantity) VALUES (%s, %s, %s)",
                                   (project_id, self.sub_entries['floors_quantity'].get() or None, self.sub_entries['rooms_quantity'].get() or None))
                                   
                conn.commit()
                self.status_label.config(text=f"Успішно оновлено проєкт з ID: {project_id}")

            elif action == "DELETE":
                project_id = self.entries['id'].get()
                if not project_id:
                    raise ValueError("Необхідно вказати ID проєкту для видалення.")
                
                cursor.execute("DELETE FROM industrial_buildings WHERE project_id=%s", (project_id,))
                cursor.execute("DELETE FROM infrastructure_buildings WHERE project_id=%s", (project_id,))
                cursor.execute("DELETE FROM residential_buildings WHERE project_id=%s", (project_id,))
                cursor.execute("DELETE FROM subcontractor WHERE project_id=%s", (project_id,))
                cursor.execute("DELETE FROM work WHERE project_id=%s", (project_id,))
                cursor.execute("DELETE FROM contract WHERE project_id=%s", (project_id,))
                cursor.execute("DELETE FROM projects WHERE id=%s", (project_id,))
                
                conn.commit()
                self.status_label.config(text=f"Запис ID {project_id} успішно видалено.")

        except Exception as e:
            self.status_label.config(text=f"Помилка: {e}", fg="#e74c3c")
        finally:
            cursor.close()
            conn.close()

class BuildersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f5f6fa")
        self.controller = controller
        self.setup_ui()
        self.load_foreign_keys()

    def setup_ui(self):
        title = tk.Label(self, text="Управління Персоналом", 
                         font=("Arial", 18, "bold"), bg="#f5f6fa", fg="#2c3e50")
        title.pack(anchor="w", padx=20, pady=15)
        
        top_management_frame = tk.Frame(self, bg="#f5f6fa")
        top_management_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.action_var = tk.StringVar(value="SELECT")
        radio_frame = tk.LabelFrame(top_management_frame, text=" Оберіть операцію ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=5)
        radio_frame.pack(side=tk.LEFT, anchor="nw")

        tk.Radiobutton(radio_frame, text="Отримати (SELECT)", variable=self.action_var, value="SELECT", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Додати (INSERT)", variable=self.action_var, value="INSERT", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Оновити (UPDATE)", variable=self.action_var, value="UPDATE", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Вилучити (DELETE)", variable=self.action_var, value="DELETE", bg="white").pack(anchor="w")

        input_frame = tk.LabelFrame(self, text=" Поля запису таблиці `builders` + `general_directors` ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        input_frame.pack(fill=tk.X, padx=20, pady=15)

        labels = ["Паспорт", "ПІБ", "Досвід", "Кваліфікація", "Дата нар.(РРРР-ММ-ДД)", "Паспорт (Б)", "Паспорт (М)", "Ген.дир (Компанія ЄДРПОУ)"]
        self.entries = {}
        db_keys = ["passport", "name", "experience", "qualification", "birth_date", "passport_f", "passport_m", "director_company"]

        for i, label_text in enumerate(labels):
            tk.Label(input_frame, text=label_text, bg="white", font=("Arial", 9)).grid(row=0, column=i, padx=5, sticky="w")
            
            if db_keys[i] == "qualification":
                entry = ttk.Combobox(input_frame, width=12, values=["Introduction", "Intermediate", "Advanced"])
            elif db_keys[i] == "director_company":
                entry = ttk.Combobox(input_frame, width=15, state="readonly")
            elif db_keys[i] in ["passport_f", "passport_m"]:
                entry = ttk.Combobox(input_frame, width=10, state="readonly")
            else:
                entry_width = 22 if db_keys[i] == "name" else 10
                entry = tk.Entry(input_frame, width=entry_width)
            
            entry.grid(row=1, column=i, padx=5, pady=5)
            self.entries[db_keys[i]] = entry

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

        columns = ("passport", "name", "experience", "qualification", "birth_date", "passport_f", "passport_m", "director_company")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=10)

        self.tree.heading("passport", text="Паспорт")
        self.tree.heading("name", text="ПІБ")
        self.tree.heading("experience", text="Досвід")
        self.tree.heading("qualification", text="Кваліфікація")
        self.tree.heading("birth_date", text="Дата нар.")
        self.tree.heading("passport_f", text="Паспорт (Б)")
        self.tree.heading("passport_m", text="Паспорт (М)")
        self.tree.heading("director_company", text="Директор компанії")

        self.tree.column("passport", width=80, anchor="center")
        self.tree.column("name", width=180, anchor="w")
        self.tree.column("experience", width=70, anchor="center")
        self.tree.column("qualification", width=90, anchor="center")
        self.tree.column("birth_date", width=80, anchor="center")
        self.tree.column("passport_f", width=80, anchor="center")
        self.tree.column("passport_m", width=80, anchor="center")
        self.tree.column("director_company", width=110, anchor="center")

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_y = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=scrollbar_y.set)

    def load_foreign_keys(self):
        conn = self.controller.get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT USREOU FROM construction_companies")
                companies = [row[0] for row in cursor.fetchall()]
                companies.insert(0, "")
                self.entries["director_company"]['values'] = companies

                cursor.execute("SELECT passport FROM builders")
                passports = [row[0] for row in cursor.fetchall()]
                passports.insert(0, "")
                self.entries["passport_f"]['values'] = passports
                self.entries["passport_m"]['values'] = passports
            except:
                pass
            finally:
                cursor.close()
                conn.close()

    def clear_entries(self):
        for entry in self.entries.values():
            if isinstance(entry, ttk.Combobox):
                entry.set("")
            else:
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
                query = """SELECT b.*, gd.company as director_company 
                           FROM builders b 
                           LEFT JOIN general_directors gd ON b.passport = gd.passport 
                           WHERE 1=1"""
                params = []
                
                if self.entries['passport'].get():
                    query += " AND b.passport = %s"
                    params.append(self.entries['passport'].get())
                    
                if self.entries['name'].get():
                    query += " AND b.name LIKE %s"
                    params.append(f"%{self.entries['name'].get()}%")
                    
                if self.entries['experience'].get():
                    query += " AND b.experience LIKE %s"
                    params.append(f"%{self.entries['experience'].get()}%")
                    
                if self.entries['qualification'].get():
                    query += " AND b.qualification_level = %s"
                    params.append(self.entries['qualification'].get())
                    
                if self.entries['birth_date'].get():
                    query += " AND b.birth_date = %s"
                    params.append(self.entries['birth_date'].get())
                    
                if self.entries['passport_f'].get():
                    query += " AND b.passport_f = %s"
                    params.append(self.entries['passport_f'].get())
                    
                if self.entries['passport_m'].get():
                    query += " AND b.passport_m = %s"
                    params.append(self.entries['passport_m'].get())

                if self.entries['director_company'].get():
                    query += " AND gd.company = %s"
                    params.append(self.entries['director_company'].get())
                    
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                
                if rows:
                    for row in rows:
                        self.tree.insert("", tk.END, values=(
                            row['passport'], row['name'], row['experience'], 
                            row['qualification_level'], row['birth_date'], 
                            row['passport_f'], row['passport_m'], row['director_company']
                        ))
                    self.status_label.config(text=f"Успіх: Знайдено {len(rows)} записів.", fg="#27ae60")
                else:
                    self.status_label.config(text="Записів не знайдено.", fg="#e67e22")

            elif action == "INSERT":
                passport = self.entries['passport'].get()
                name = self.entries['name'].get()
                director_comp = self.entries['director_company'].get()
                
                if not passport:
                    raise ValueError("Паспорт є обов'язковим для додавання.")
                    
                query_builder = """INSERT INTO builders (passport, name, experience, qualification_level, birth_date, passport_f, passport_m) 
                                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                params_builder = (
                    passport, name or None,
                    self.entries['experience'].get() or None,
                    self.entries['qualification'].get() or None,
                    self.entries['birth_date'].get() or None,
                    self.entries['passport_f'].get() or None,
                    self.entries['passport_m'].get() or None
                )
                cursor.execute(query_builder, params_builder)
                
                if director_comp:
                    cursor.execute("DELETE FROM general_directors WHERE company=%s", (director_comp,))
                    query_dir = "INSERT INTO general_directors (passport, name, company) VALUES (%s, %s, %s)"
                    cursor.execute(query_dir, (passport, name or None, director_comp))
                    
                conn.commit()
                self.status_label.config(text=f"Успішно додано будівельника: {passport}")

            elif action == "UPDATE":
                passport = self.entries['passport'].get()
                name = self.entries['name'].get()
                director_comp = self.entries['director_company'].get()
                
                if not passport:
                    raise ValueError("Необхідно вказати паспорт для оновлення.")
                
                query_builder = """UPDATE builders SET name=%s, experience=%s, qualification_level=%s, birth_date=%s, passport_f=%s, passport_m=%s 
                                   WHERE passport=%s"""
                params_builder = (
                    name or None,
                    self.entries['experience'].get() or None,
                    self.entries['qualification'].get() or None,
                    self.entries['birth_date'].get() or None,
                    self.entries['passport_f'].get() or None,
                    self.entries['passport_m'].get() or None,
                    passport
                )
                cursor.execute(query_builder, params_builder)
                
                cursor.execute("DELETE FROM general_directors WHERE passport=%s", (passport,))
                if director_comp:
                    cursor.execute("DELETE FROM general_directors WHERE company=%s", (director_comp,))
                    query_dir = "INSERT INTO general_directors (passport, name, company) VALUES (%s, %s, %s)"
                    cursor.execute(query_dir, (passport, name or None, director_comp))

                conn.commit()
                self.status_label.config(text=f"Дані успішно оновлено.")

            elif action == "DELETE":
                passport = self.entries['passport'].get()
                if not passport:
                    raise ValueError("Необхідно вказати паспорт для видалення.")
                
                cursor.execute("DELETE FROM general_directors WHERE passport=%s", (passport,))
                cursor.execute("DELETE FROM work WHERE builder_passport=%s", (passport,))
                cursor.execute("DELETE FROM contract WHERE builder_passport=%s", (passport,))
                cursor.execute("DELETE FROM builders WHERE passport=%s", (passport,))
                
                conn.commit()
                self.status_label.config(text="Запис успішно видалено з усіх таблиць.")

        except Exception as e:
            self.status_label.config(text=f"Помилка: {e}", fg="#e74c3c")
        finally:
            cursor.close()
            conn.close()

class CompaniesPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f5f6fa")
        self.controller = controller
        self.setup_ui()
        self.load_partners()

    def setup_ui(self):
        title = tk.Label(self, text="Будівельні Організації", 
                         font=("Arial", 18, "bold"), bg="#f5f6fa", fg="#2c3e50")
        title.pack(anchor="w", padx=20, pady=15)
        
        top_management_frame = tk.Frame(self, bg="#f5f6fa")
        top_management_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.action_var = tk.StringVar(value="SELECT")
        radio_frame = tk.LabelFrame(top_management_frame, text=" Оберіть операцію ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=5)
        radio_frame.pack(side=tk.LEFT, anchor="nw")

        tk.Radiobutton(radio_frame, text="Отримати (SELECT)", variable=self.action_var, value="SELECT", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Додати (INSERT)", variable=self.action_var, value="INSERT", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Оновити (UPDATE)", variable=self.action_var, value="UPDATE", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Вилучити (DELETE)", variable=self.action_var, value="DELETE", bg="white").pack(anchor="w")

        input_frame = tk.LabelFrame(self, text=" Поля запису таблиці `construction_companies` ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        input_frame.pack(fill=tk.X, padx=20, pady=15)

        labels = ["Код ЄДРПОУ", "Назва компанії", "Номер ліцензії", "Юридична адреса", "Партнер (ЄДРПОУ)"]
        self.entries = {}
        db_keys = ["usreou", "name", "license_number", "legal_address", "partner"]

        for i, label_text in enumerate(labels):
            tk.Label(input_frame, text=label_text, bg="white", font=("Arial", 9)).grid(row=0, column=i, padx=5, sticky="w")
            
            if db_keys[i] == "partner":
                entry = ttk.Combobox(input_frame, width=15, state="readonly")
            else:
                entry_width = 30 if db_keys[i] == "legal_address" else 15
                entry = tk.Entry(input_frame, width=entry_width)
            
            entry.grid(row=1, column=i, padx=5, pady=5)
            self.entries[db_keys[i]] = entry

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

        columns = ("usreou", "name", "license", "address", "partner")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=10)

        self.tree.heading("usreou", text="ЄДРПОУ")
        self.tree.heading("name", text="Назва компанії")
        self.tree.heading("license", text="Ліцензія")
        self.tree.heading("address", text="Юридична адреса")
        self.tree.heading("partner", text="Партнер")

        self.tree.column("usreou", width=90, anchor="center")
        self.tree.column("name", width=150, anchor="w")
        self.tree.column("license", width=110, anchor="center")
        self.tree.column("address", width=250, anchor="w")
        self.tree.column("partner", width=100, anchor="center")

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_y = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=scrollbar_y.set)

    def load_partners(self):
        conn = self.controller.get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT USREOU FROM construction_companies")
                companies = [row[0] for row in cursor.fetchall()]
                companies.insert(0, "")
                self.entries['partner']['values'] = companies
            except:
                pass
            finally:
                cursor.close()
                conn.close()

    def clear_entries(self):
        for entry in self.entries.values():
            if isinstance(entry, ttk.Combobox):
                entry.set("")
            else:
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
                query = """SELECT c.*, p.company_b as partner 
                           FROM construction_companies c
                           LEFT JOIN partnership p ON c.USREOU = p.company_a
                           WHERE 1=1"""
                params = []
                
                if self.entries['usreou'].get():
                    query += " AND c.USREOU = %s"
                    params.append(self.entries['usreou'].get())
                    
                if self.entries['name'].get():
                    query += " AND c.name LIKE %s"
                    params.append(f"%{self.entries['name'].get()}%")
                    
                if self.entries['license_number'].get():
                    query += " AND c.license_number LIKE %s"
                    params.append(f"%{self.entries['license_number'].get()}%")
                    
                if self.entries['legal_address'].get():
                    query += " AND c.legal_address LIKE %s"
                    params.append(f"%{self.entries['legal_address'].get()}%")
                    
                if self.entries['partner'].get():
                    query += " AND p.company_b = %s"
                    params.append(self.entries['partner'].get())
                    
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                
                if rows:
                    for row in rows:
                        self.tree.insert("", tk.END, values=(
                            row['USREOU'], row['name'], 
                            row['license_number'], row['legal_address'], row['partner']
                        ))
                    self.status_label.config(text=f"Успіх: Знайдено {len(rows)} записів.", fg="#27ae60")
                else:
                    self.status_label.config(text="Записів за вказаними критеріями не знайдено.", fg="#e67e22")

            elif action == "INSERT":
                usreou = self.entries['usreou'].get()
                if not usreou:
                    raise ValueError("Код ЄДРПОУ є обов'язковим для додавання компанії.")
                    
                query = """INSERT INTO construction_companies (USREOU, name, license_number, legal_address) 
                           VALUES (%s, %s, %s, %s)"""
                params = (
                    usreou,
                    self.entries['name'].get() or None,
                    self.entries['license_number'].get() or None,
                    self.entries['legal_address'].get() or None
                )
                cursor.execute(query, params)
                
                partner = self.entries['partner'].get()
                if partner:
                    cursor.execute("INSERT INTO partnership (company_a, company_b) VALUES (%s, %s)", (usreou, partner))
                    
                conn.commit()
                self.status_label.config(text=f"Успішно додано компанію з ЄДРПОУ: {usreou}")
                self.load_partners()

            elif action == "UPDATE":
                usreou = self.entries['usreou'].get()
                if not usreou:
                    raise ValueError("Необхідно вказати ЄДРПОУ компанії для оновлення.")
                
                query = """UPDATE construction_companies SET name=%s, license_number=%s, legal_address=%s 
                           WHERE USREOU=%s"""
                params = (
                    self.entries['name'].get() or None,
                    self.entries['license_number'].get() or None,
                    self.entries['legal_address'].get() or None,
                    usreou
                )
                cursor.execute(query, params)
                
                cursor.execute("DELETE FROM partnership WHERE company_a=%s", (usreou,))
                partner = self.entries['partner'].get()
                if partner:
                    cursor.execute("INSERT INTO partnership (company_a, company_b) VALUES (%s, %s)", (usreou, partner))
                    
                conn.commit()
                self.status_label.config(text=f"Успішно оновлено.")

            elif action == "DELETE":
                usreou = self.entries['usreou'].get()
                if not usreou:
                    raise ValueError("Необхідно вказати ЄДРПОУ компанії для видалення.")
                
                cursor.execute("DELETE FROM partnership WHERE company_a=%s OR company_b=%s", (usreou, usreou))
                cursor.execute("DELETE FROM general_directors WHERE company=%s", (usreou,))
                cursor.execute("DELETE FROM subcontractor WHERE USREOU=%s", (usreou,))
                cursor.execute("DELETE FROM subdivisions WHERE company=%s", (usreou,))
                
                cursor.execute("SELECT id FROM projects WHERE company=%s", (usreou,))
                projects_ids = cursor.fetchall()
                for pid in projects_ids:
                    p_id = pid['id']
                    cursor.execute("DELETE FROM industrial_buildings WHERE project_id=%s", (p_id,))
                    cursor.execute("DELETE FROM infrastructure_buildings WHERE project_id=%s", (p_id,))
                    cursor.execute("DELETE FROM residential_buildings WHERE project_id=%s", (p_id,))
                    cursor.execute("DELETE FROM subcontractor WHERE project_id=%s", (p_id,))
                    cursor.execute("DELETE FROM work WHERE project_id=%s", (p_id,))
                    cursor.execute("DELETE FROM contract WHERE project_id=%s", (p_id,))
                    cursor.execute("DELETE FROM projects WHERE id=%s", (p_id,))
                
                cursor.execute("DELETE FROM construction_companies WHERE USREOU=%s", (usreou,))
                conn.commit()
                
                self.status_label.config(text=f"Запис компанії видалено.")
                self.load_partners()

        except Exception as e:
            self.status_label.config(text=f"Помилка: {e}", fg="#e74c3c")
        finally:
            cursor.close()
            conn.close()
    
class SubdivisionsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f5f6fa")
        self.controller = controller
        self.setup_ui()
        self.load_companies()

    def setup_ui(self):
        title = tk.Label(self, text="Управління Підрозділами", 
                         font=("Arial", 18, "bold"), bg="#f5f6fa", fg="#2c3e50")
        title.pack(anchor="w", padx=20, pady=15)
        
        top_management_frame = tk.Frame(self, bg="#f5f6fa")
        top_management_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.action_var = tk.StringVar(value="SELECT")
        radio_frame = tk.LabelFrame(top_management_frame, text=" Оберіть операцію ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=5)
        radio_frame.pack(side=tk.LEFT, anchor="nw")

        tk.Radiobutton(radio_frame, text="Отримати (SELECT)", variable=self.action_var, value="SELECT", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Додати (INSERT)", variable=self.action_var, value="INSERT", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Оновити за назвою (UPDATE)", variable=self.action_var, value="UPDATE", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Вилучити за назвою (DELETE)", variable=self.action_var, value="DELETE", bg="white").pack(anchor="w")

        input_frame = tk.LabelFrame(self, text=" Поля запису таблиці `subdivisions` ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        input_frame.pack(fill=tk.X, padx=20, pady=15)

        labels = ["Назва підрозділу", "Кількість працівників", "Кількість спецтехніки", "Компанія (ЄДРПОУ)"]
        self.entries = {}
        db_keys = ["name", "workers_quantity", "special_equipment_quantity", "company"]

        for i, label_text in enumerate(labels):
            tk.Label(input_frame, text=label_text, bg="white", font=("Arial", 9)).grid(row=0, column=i, padx=5, sticky="w")
            
            if db_keys[i] == "company":
                self.company_cb = ttk.Combobox(input_frame, width=18, state="readonly")
                self.company_cb.grid(row=1, column=i, padx=5, pady=5)
                self.entries["company"] = self.company_cb
            else:
                entry_width = 30 if db_keys[i] == "name" else 15
                entry = tk.Entry(input_frame, width=entry_width)
                entry.grid(row=1, column=i, padx=5, pady=5)
                self.entries[db_keys[i]] = entry

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

        columns = ("name", "workers_quantity", "special_equipment_quantity", "company")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=10)

        self.tree.heading("name", text="Назва підрозділу")
        self.tree.heading("workers_quantity", text="Кількість працівників")
        self.tree.heading("special_equipment_quantity", text="Кількість спецтехніки")
        self.tree.heading("company", text="Компанія (ЄДРПОУ)")

        self.tree.column("name", width=250, anchor="w")
        self.tree.column("workers_quantity", width=120, anchor="center")
        self.tree.column("special_equipment_quantity", width=120, anchor="center")
        self.tree.column("company", width=120, anchor="center")

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
                print(f"Error loading companies: {e}")
            finally:
                cursor.close()
                conn.close()

    def clear_entries(self):
        for entry in self.entries.values():
            if isinstance(entry, ttk.Combobox):
                entry.set("")
            else:
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
                query = "SELECT * FROM subdivisions WHERE 1=1"
                params = []
                
                if self.entries['name'].get():
                    query += " AND name LIKE %s"
                    params.append(f"%{self.entries['name'].get()}%")
                    
                if self.entries['workers_quantity'].get():
                    query += " AND workers_quantity = %s"
                    params.append(self.entries['workers_quantity'].get())
                    
                if self.entries['special_equipment_quantity'].get():
                    query += " AND special_equipment_quantity = %s"
                    params.append(self.entries['special_equipment_quantity'].get())
                    
                if self.entries['company'].get():
                    query += " AND company = %s"
                    params.append(self.entries['company'].get())
                    
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                
                if rows:
                    for row in rows:
                        self.tree.insert("", tk.END, values=(
                            row['name'], row['workers_quantity'], 
                            row['special_equipment_quantity'], row['company']
                        ))
                    self.status_label.config(text=f"Успіх: Знайдено {len(rows)} записів.", fg="#27ae60")
                else:
                    self.status_label.config(text="Записів не знайдено.", fg="#e67e22")

            elif action == "INSERT":
                if not self.entries['name'].get() or not self.entries['company'].get():
                    raise ValueError("Назва підрозділу та Компанія є обов'язковими для заповнення.")
                    
                query = """INSERT INTO subdivisions (name, workers_quantity, special_equipment_quantity, company) 
                           VALUES (%s, %s, %s, %s)"""
                params = (
                    self.entries['name'].get(),
                    self.entries['workers_quantity'].get() or None,
                    self.entries['special_equipment_quantity'].get() or None,
                    self.entries['company'].get()
                )
                cursor.execute(query, params)
                conn.commit()
                self.status_label.config(text=f"Успішно додано підрозділ: {self.entries['name'].get()}")

            elif action == "UPDATE":
                if not self.entries['name'].get():
                    raise ValueError("Необхідно вказати назву підрозділу для оновлення.")
                
                query = """UPDATE subdivisions SET workers_quantity=%s, special_equipment_quantity=%s, company=%s 
                           WHERE name=%s"""
                params = (
                    self.entries['workers_quantity'].get() or None,
                    self.entries['special_equipment_quantity'].get() or None,
                    self.entries['company'].get() or None,
                    self.entries['name'].get()
                )
                cursor.execute(query, params)
                conn.commit()
                if cursor.rowcount == 0:
                    self.status_label.config(text="Підрозділ з такою назвою не знайдено.", fg="#e67e22")
                else:
                    self.status_label.config(text=f"Оновлено. Змінено рядків: {cursor.rowcount}")

            elif action == "DELETE":
                if not self.entries['name'].get():
                    raise ValueError("Необхідно вказати назву підрозділу для видалення.")
                
                query = "DELETE FROM subdivisions WHERE name=%s"
                cursor.execute(query, (self.entries['name'].get(),))
                conn.commit()
                if cursor.rowcount == 0:
                    self.status_label.config(text="Підрозділ з такою назвою не знайдено.", fg="#e67e22")
                else:
                    self.status_label.config(text=f"Видалено. Вилучено рядків: {cursor.rowcount}")

        except Exception as e:
            self.status_label.config(text=f"Помилка: {e}", fg="#e74c3c")
        finally:
            cursor.close()
            conn.close()

class ContractsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f5f6fa")
        self.controller = controller
        self.setup_ui()
        self.load_foreign_keys()

    def setup_ui(self):
        title = tk.Label(self, text="Управління Контрактами", 
                         font=("Arial", 18, "bold"), bg="#f5f6fa", fg="#2c3e50")
        title.pack(anchor="w", padx=20, pady=15)
        
        top_management_frame = tk.Frame(self, bg="#f5f6fa")
        top_management_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.action_var = tk.StringVar(value="SELECT")
        radio_frame = tk.LabelFrame(top_management_frame, text=" Оберіть операцію ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=5)
        radio_frame.pack(side=tk.LEFT, anchor="nw")

        tk.Radiobutton(radio_frame, text="Отримати (SELECT)", variable=self.action_var, value="SELECT", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Додати (INSERT)", variable=self.action_var, value="INSERT", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Оновити за Паспортом та ID проєкту (UPDATE)", variable=self.action_var, value="UPDATE", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Вилучити за Паспортом та ID проєкту (DELETE)", variable=self.action_var, value="DELETE", bg="white").pack(anchor="w")

        input_frame = tk.LabelFrame(self, text=" Поля запису таблиці `contract` ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        input_frame.pack(fill=tk.X, padx=20, pady=15)

        labels = ["Паспорт будівельника", "ID проєкту", "Зарплата (грн)", "Термін (РРРР-ММ-ДД)"]
        self.entries = {}
        db_keys = ["builder_passport", "project_id", "salary", "term"]

        for i, label_text in enumerate(labels):
            tk.Label(input_frame, text=label_text, bg="white", font=("Arial", 9)).grid(row=0, column=i, padx=5, sticky="w")
            
            if db_keys[i] in ["builder_passport", "project_id"]:
                entry = ttk.Combobox(input_frame, width=18, state="readonly")
            else:
                entry = tk.Entry(input_frame, width=20)
                
            entry.grid(row=1, column=i, padx=5, pady=5)
            self.entries[db_keys[i]] = entry

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

        columns = ("builder_passport", "project_id", "salary", "term")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=10)

        self.tree.heading("builder_passport", text="Паспорт будівельника")
        self.tree.heading("project_id", text="ID проєкту")
        self.tree.heading("salary", text="Зарплата")
        self.tree.heading("term", text="Термін")

        self.tree.column("builder_passport", width=150, anchor="center")
        self.tree.column("project_id", width=100, anchor="center")
        self.tree.column("salary", width=120, anchor="e")
        self.tree.column("term", width=120, anchor="center")

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_y = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=scrollbar_y.set)

    def load_foreign_keys(self):
        conn = self.controller.get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT passport FROM builders")
                passports = [row[0] for row in cursor.fetchall()]
                passports.insert(0, "")
                self.entries['builder_passport']['values'] = passports
                
                cursor.execute("SELECT id FROM projects")
                project_ids = [str(row[0]) for row in cursor.fetchall()]
                project_ids.insert(0, "")
                self.entries['project_id']['values'] = project_ids
            except Error as e:
                print(f"Error loading foreign keys: {e}")
            finally:
                cursor.close()
                conn.close()

    def clear_entries(self):
        for entry in self.entries.values():
            if isinstance(entry, ttk.Combobox):
                entry.set("")
            else:
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
                query = "SELECT * FROM contract WHERE 1=1"
                params = []
                
                if self.entries['builder_passport'].get():
                    query += " AND builder_passport = %s"
                    params.append(self.entries['builder_passport'].get())
                    
                if self.entries['project_id'].get():
                    query += " AND project_id = %s"
                    params.append(self.entries['project_id'].get())
                    
                if self.entries['salary'].get():
                    query += " AND salary = %s"
                    params.append(self.entries['salary'].get())
                    
                if self.entries['term'].get():
                    query += " AND term LIKE %s"
                    params.append(f"%{self.entries['term'].get()}%")
                    
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                
                if rows:
                    for row in rows:
                        self.tree.insert("", tk.END, values=(
                            row['builder_passport'], row['project_id'], 
                            row['salary'], row['term']
                        ))
                    self.status_label.config(text=f"Успіх: Знайдено {len(rows)} записів.", fg="#27ae60")
                else:
                    self.status_label.config(text="Записів не знайдено.", fg="#e67e22")

            elif action == "INSERT":
                if not self.entries['builder_passport'].get() or not self.entries['project_id'].get():
                    raise ValueError("Паспорт будівельника та ID проєкту є обов'язковими.")
                    
                query = """INSERT INTO contract (builder_passport, project_id, salary, term) 
                           VALUES (%s, %s, %s, %s)"""
                params = (
                    self.entries['builder_passport'].get(),
                    self.entries['project_id'].get(),
                    self.entries['salary'].get() or None,
                    self.entries['term'].get() or None
                )
                cursor.execute(query, params)
                conn.commit()
                self.status_label.config(text="Успішно додано новий контракт.")

            elif action == "UPDATE":
                if not self.entries['builder_passport'].get() or not self.entries['project_id'].get():
                    raise ValueError("Необхідно вказати Паспорт та ID проєкту для ідентифікації контракту.")
                
                query = """UPDATE contract SET salary=%s, term=%s 
                           WHERE builder_passport=%s AND project_id=%s"""
                params = (
                    self.entries['salary'].get() or None,
                    self.entries['term'].get() or None,
                    self.entries['builder_passport'].get(),
                    self.entries['project_id'].get()
                )
                cursor.execute(query, params)
                conn.commit()
                if cursor.rowcount == 0:
                    self.status_label.config(text="Контракт із такими параметрами не знайдено.", fg="#e67e22")
                else:
                    self.status_label.config(text=f"Оновлено. Змінено рядків: {cursor.rowcount}")

            elif action == "DELETE":
                if not self.entries['builder_passport'].get() or not self.entries['project_id'].get():
                    raise ValueError("Необхідно вказати Паспорт та ID проєкту для видалення контракту.")
                
                query = "DELETE FROM contract WHERE builder_passport=%s AND project_id=%s"
                cursor.execute(query, (self.entries['builder_passport'].get(), self.entries['project_id'].get()))
                conn.commit()
                if cursor.rowcount == 0:
                    self.status_label.config(text="Контракт із такими параметрами не знайдено.", fg="#e67e22")
                else:
                    self.status_label.config(text=f"Видалено. Вилучено рядків: {cursor.rowcount}")

        except Exception as e:
            self.status_label.config(text=f"Помилка: {e}", fg="#e74c3c")
        finally:
            cursor.close()
            conn.close()

class WorkPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f5f6fa")
        self.controller = controller
        self.setup_ui()
        self.load_foreign_keys()

    def setup_ui(self):
        title = tk.Label(self, text="Призначення на роботу", 
                         font=("Arial", 18, "bold"), bg="#f5f6fa", fg="#2c3e50")
        title.pack(anchor="w", padx=20, pady=15)
        
        top_management_frame = tk.Frame(self, bg="#f5f6fa")
        top_management_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.action_var = tk.StringVar(value="SELECT")
        radio_frame = tk.LabelFrame(top_management_frame, text=" Оберіть операцію ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=5)
        radio_frame.pack(side=tk.LEFT, anchor="nw")

        tk.Radiobutton(radio_frame, text="Отримати (SELECT)", variable=self.action_var, value="SELECT", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Додати (INSERT)", variable=self.action_var, value="INSERT", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Оновити за Паспортом та ID проєкту (UPDATE)", variable=self.action_var, value="UPDATE", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Вилучити (DELETE)", variable=self.action_var, value="DELETE", bg="white").pack(anchor="w")

        input_frame = tk.LabelFrame(self, text=" Поля запису таблиці `work` ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        input_frame.pack(fill=tk.X, padx=20, pady=15)

        labels = ["Паспорт будівельника", "ID проєкту", "Посада"]
        self.entries = {}
        db_keys = ["builder_passport", "project_id", "position_name"]

        for i, label_text in enumerate(labels):
            tk.Label(input_frame, text=label_text, bg="white", font=("Arial", 9)).grid(row=0, column=i, padx=5, sticky="w")
            entry = ttk.Combobox(input_frame, width=25, state="readonly")
            entry.grid(row=1, column=i, padx=5, pady=5)
            self.entries[db_keys[i]] = entry

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

        columns = ("builder_passport", "project_id", "position_name")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=10)

        self.tree.heading("builder_passport", text="Паспорт будівельника")
        self.tree.heading("project_id", text="ID проєкту")
        self.tree.heading("position_name", text="Посада")

        self.tree.column("builder_passport", width=150, anchor="center")
        self.tree.column("project_id", width=100, anchor="center")
        self.tree.column("position_name", width=250, anchor="w")

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_y = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=scrollbar_y.set)

    def load_foreign_keys(self):
        conn = self.controller.get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT passport FROM builders")
                passports = [row[0] for row in cursor.fetchall()]
                passports.insert(0, "")
                self.entries['builder_passport']['values'] = passports
                
                cursor.execute("SELECT id FROM projects")
                project_ids = [str(row[0]) for row in cursor.fetchall()]
                project_ids.insert(0, "")
                self.entries['project_id']['values'] = project_ids

                cursor.execute("SELECT name FROM job_position")
                positions = [row[0] for row in cursor.fetchall()]
                positions.insert(0, "")
                self.entries['position_name']['values'] = positions
            except:
                pass
            finally:
                cursor.close()
                conn.close()

    def clear_entries(self):
        for entry in self.entries.values():
            entry.set("")

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
                query = "SELECT * FROM work WHERE 1=1"
                params = []
                
                if self.entries['builder_passport'].get():
                    query += " AND builder_passport = %s"
                    params.append(self.entries['builder_passport'].get())
                    
                if self.entries['project_id'].get():
                    query += " AND project_id = %s"
                    params.append(self.entries['project_id'].get())
                    
                if self.entries['position_name'].get():
                    query += " AND position_name = %s"
                    params.append(self.entries['position_name'].get())
                    
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                
                if rows:
                    for row in rows:
                        self.tree.insert("", tk.END, values=(
                            row['builder_passport'], row['project_id'], row['position_name']
                        ))
                    self.status_label.config(text=f"Успіх: Знайдено {len(rows)} записів.", fg="#27ae60")
                else:
                    self.status_label.config(text="Записів не знайдено.", fg="#e67e22")

            elif action == "INSERT":
                if not self.entries['builder_passport'].get() or not self.entries['project_id'].get() or not self.entries['position_name'].get():
                    raise ValueError("Всі поля є обов'язковими для додавання.")
                    
                query = "INSERT INTO work (builder_passport, project_id, position_name) VALUES (%s, %s, %s)"
                params = (
                    self.entries['builder_passport'].get(),
                    self.entries['project_id'].get(),
                    self.entries['position_name'].get()
                )
                cursor.execute(query, params)
                conn.commit()
                self.status_label.config(text="Успішно додано новий запис.")

            elif action == "UPDATE":
                if not self.entries['builder_passport'].get() or not self.entries['project_id'].get():
                    raise ValueError("Необхідно вказати Паспорт та ID проєкту.")
                
                query = "UPDATE work SET position_name=%s WHERE builder_passport=%s AND project_id=%s"
                params = (
                    self.entries['position_name'].get(),
                    self.entries['builder_passport'].get(),
                    self.entries['project_id'].get()
                )
                cursor.execute(query, params)
                conn.commit()
                if cursor.rowcount == 0:
                    self.status_label.config(text="Запис не знайдено.", fg="#e67e22")
                else:
                    self.status_label.config(text=f"Оновлено. Змінено рядків: {cursor.rowcount}")

            elif action == "DELETE":
                if not self.entries['builder_passport'].get() or not self.entries['project_id'].get():
                    raise ValueError("Необхідно вказати Паспорт та ID проєкту.")
                
                query = "DELETE FROM work WHERE builder_passport=%s AND project_id=%s"
                params = [self.entries['builder_passport'].get(), self.entries['project_id'].get()]
                
                if self.entries['position_name'].get():
                    query += " AND position_name=%s"
                    params.append(self.entries['position_name'].get())

                cursor.execute(query, tuple(params))
                conn.commit()
                if cursor.rowcount == 0:
                    self.status_label.config(text="Запис не знайдено.", fg="#e67e22")
                else:
                    self.status_label.config(text=f"Видалено. Вилучено рядків: {cursor.rowcount}")

        except Exception as e:
            self.status_label.config(text=f"Помилка: {e}", fg="#e74c3c")
        finally:
            cursor.close()
            conn.close()

class PositionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f5f6fa")
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        title = tk.Label(self, text="Управління Посадами", 
                         font=("Arial", 18, "bold"), bg="#f5f6fa", fg="#2c3e50")
        title.pack(anchor="w", padx=20, pady=15)
        
        top_management_frame = tk.Frame(self, bg="#f5f6fa")
        top_management_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.action_var = tk.StringVar(value="SELECT")
        radio_frame = tk.LabelFrame(top_management_frame, text=" Оберіть операцію ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=5)
        radio_frame.pack(side=tk.LEFT, anchor="nw")

        tk.Radiobutton(radio_frame, text="Отримати (SELECT)", variable=self.action_var, value="SELECT", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Додати (INSERT)", variable=self.action_var, value="INSERT", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Оновити за назвою (UPDATE)", variable=self.action_var, value="UPDATE", bg="white").pack(anchor="w")
        tk.Radiobutton(radio_frame, text="Вилучити за назвою (DELETE)", variable=self.action_var, value="DELETE", bg="white").pack(anchor="w")

        input_frame = tk.LabelFrame(self, text=" Поля запису таблиці `job_position` ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        input_frame.pack(fill=tk.X, padx=20, pady=15)

        labels = ["Назва посади", "Опис посади"]
        self.entries = {}
        db_keys = ["name", "description"]

        for i, label_text in enumerate(labels):
            tk.Label(input_frame, text=label_text, bg="white", font=("Arial", 9)).grid(row=0, column=i, padx=5, sticky="w")
            entry_width = 25 if db_keys[i] == "name" else 50
            entry = tk.Entry(input_frame, width=entry_width)
            entry.grid(row=1, column=i, padx=5, pady=5)
            self.entries[db_keys[i]] = entry

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

        columns = ("name", "description")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=10)

        self.tree.heading("name", text="Назва посади")
        self.tree.heading("description", text="Опис")
        
        self.tree.column("name", width=200, anchor="w")
        self.tree.column("description", width=450, anchor="w")

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
                query = "SELECT * FROM job_position WHERE 1=1"
                params = []
                
                if self.entries['name'].get():
                    query += " AND name LIKE %s"
                    params.append(f"%{self.entries['name'].get()}%")
                    
                if self.entries['description'].get():
                    query += " AND description LIKE %s"
                    params.append(f"%{self.entries['description'].get()}%")
                    
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                
                if rows:
                    for row in rows:
                        self.tree.insert("", tk.END, values=(row.get('name', ''), row.get('description', '')))
                    self.status_label.config(text=f"Успіх: Знайдено {len(rows)} записів.", fg="#27ae60")
                else:
                    self.status_label.config(text="Записів не знайдено.", fg="#e67e22")

            elif action == "INSERT":
                position_name = self.entries['name'].get()
                if not position_name:
                    raise ValueError("Назва посади є обов'язковою для заповнення.")
                    
                query = "INSERT INTO job_position (name, description) VALUES (%s, %s)"
                params = (position_name, self.entries['description'].get() or None)
                cursor.execute(query, params)
                conn.commit()
                self.status_label.config(text=f"Успішно додано посаду: {position_name}")
                
            elif action == "UPDATE":
                position_name = self.entries['name'].get()
                if not position_name:
                    raise ValueError("Необхідно вказати назву посади для оновлення.")
                    
                query = "UPDATE job_position SET description=%s WHERE name=%s"
                params = (self.entries['description'].get() or None, position_name)
                cursor.execute(query, params)
                conn.commit()
                if cursor.rowcount == 0:
                    self.status_label.config(text="Посаду з такою назвою не знайдено.", fg="#e67e22")
                else:
                    self.status_label.config(text=f"Опис посади успішно оновлено.")

            elif action == "DELETE":
                position_name = self.entries['name'].get()
                if not position_name:
                    raise ValueError("Необхідно вказати назву посади для видалення.")
                
                cursor.execute("DELETE FROM work WHERE position_name=%s", (position_name,))
                cursor.execute("DELETE FROM job_position WHERE name=%s", (position_name,))
                conn.commit()
                
                if cursor.rowcount == 0:
                    self.status_label.config(text="Посаду з такою назвою не знайдено.", fg="#e67e22")
                else:
                    self.status_label.config(text=f"Посаду успішно видалено.")

        except Exception as e:
            self.status_label.config(text=f"Помилка: {e}", fg="#e74c3c")
        finally:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()