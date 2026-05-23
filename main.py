import tkinter as tk
from tkinter import ttk

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Система управління будівельною БД")
        self.geometry("1000x650")
        self.configure(bg="#f5f6fa")

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

class ProjectsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f5f6fa")

        title = tk.Label(self, text="Управління Проєктами", font=("Arial", 18, "bold"), bg="#f5f6fa", fg="#2c3e50")
        title.pack(anchor="w", padx=20, pady=20)

        content_frame = tk.LabelFrame(self, text="Панель дій для проектів", font=("Arial", 10, "bold"), bg="white", padx=15, pady=15)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)


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
        
        title = tk.Label(self, text="Будівельні Компанії", font=("Arial", 18, "bold"), bg="#f5f6fa", fg="#2c3e50")
        title.pack(anchor="w", padx=20, pady=20)
        
        content_frame = tk.LabelFrame(self, text="Реєстр компаній", font=("Arial", 10, "bold"), bg="white", padx=15, pady=15)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
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