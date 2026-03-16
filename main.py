import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from typing import Optional, List, Tuple, Callable, Any, cast

# Ensure the current directory is in the path for imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import styles # type: ignore
import database # type: ignore
from views.owner_view import OwnerView # type: ignore
from views.pet_view import PetView # type: ignore
from views.vaccination_view import VaccinationView # type: ignore
from views.medical_view import MedicalRecordView # type: ignore

class MainApp(tk.Tk):
    sidebar: Any
    content_area: Any
    current_frame: Any

    def __init__(self):
        super().__init__()
        self.title("AlagangHayop – Pet Health & Records Management System")
        self.geometry("1100x700")
        self.configure(bg=styles.SECONDARY_COLOR)
        
        # Initialize containers to empty frames so they are never None
        self.sidebar = tk.Frame(self)
        self.content_area = tk.Frame(self)
        self.current_frame = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Sidebar
        self.sidebar.configure(bg=styles.PRIMARY_COLOR, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # App Title in Sidebar
        title_label = tk.Label(self.sidebar, text="Alagang\nHayop", 
                             font=styles.FONT_TITLE, bg=styles.PRIMARY_COLOR, 
                             fg=styles.TEXT_ON_PRIMARY, pady=styles.PADDING_LARGE)
        title_label.pack()
        
        # Navigation Buttons
        nav_items = [
            ("Dashboard", self.show_dashboard),
            ("Owners", self.show_owners),
            ("Pets", self.show_pets),
            ("Vaccinations", self.show_vaccinations),
            ("Medical Records", self.show_medical_records)
        ]
        
        for text, command in nav_items:
            btn = tk.Button(self.sidebar, text=text, font=styles.FONT_BOLD,
                          bg=styles.PRIMARY_COLOR, fg=styles.TEXT_ON_PRIMARY,
                          activebackground=styles.COMPLEMENTARY_COLOR,
                          activeforeground=styles.TEXT_ON_COMPLEMENTARY,
                          bd=0, padx=20, pady=15, anchor="w", cursor="hand2",
                          command=command)
            btn.pack(fill="x")
            
        # Main Content Area
        self.content_area = tk.Frame(self, bg=styles.SECONDARY_COLOR)
        self.content_area.pack(side="right", fill="both", expand=True) # type: ignore
        
        # Initial View
        self.show_dashboard()

    def clear_content(self):
        if self.current_frame is not None:
            cast(tk.Frame, self.current_frame).destroy()
            self.current_frame = None

    def show_dashboard(self):
        self.clear_content()
        self.current_frame = tk.Frame(self.content_area, bg=styles.SECONDARY_COLOR, padx=styles.PADDING_LARGE, pady=styles.PADDING_LARGE)
        self.current_frame.pack(fill="both", expand=True)
        
        label = tk.Label(self.current_frame, text="Admin Dashboard", font=styles.FONT_TITLE, 
                        bg=styles.SECONDARY_COLOR, fg=styles.PRIMARY_COLOR)
        label.pack(anchor="w")
        
        desc = tk.Label(self.current_frame, text="Welcome to AlagangHayop Pet Health & Records Management System.", 
                       font=styles.FONT_NORMAL, bg=styles.SECONDARY_COLOR, fg=styles.TEXT_ON_SECONDARY)
        desc.pack(anchor="w", pady=(10, 30))
        
        # Stats Cards
        stats_frame = tk.Frame(self.current_frame, bg=styles.SECONDARY_COLOR)
        stats_frame.pack(fill="x") # type: ignore
        
        owners_count = len(database.get_owners())
        pets_count = len(database.get_pets())
        vax_count = len(database.get_vaccinations())
        
        stats = [
            ("Owners", owners_count),
            ("Pets", pets_count),
            ("Vaccinations", vax_count)
        ]
        
        for text, count in stats:
            card = tk.Frame(stats_frame, bg=styles.PRIMARY_COLOR, padx=20, pady=20, width=200, height=120)
            card.pack(side="left", padx=(0, 20)) # type: ignore
            card.pack_propagate(False) # type: ignore
            
            val = tk.Label(card, text=str(count), font=styles.FONT_TITLE, bg=styles.PRIMARY_COLOR, fg=styles.TEXT_ON_PRIMARY)
            val.pack() # type: ignore
            
            title = tk.Label(card, text=text, font=styles.FONT_BOLD, bg=styles.PRIMARY_COLOR, fg=styles.TEXT_ON_PRIMARY)
            title.pack() # type: ignore

    def show_owners(self):
        self.clear_content()
        self.current_frame = OwnerView(self.content_area)
        self.current_frame.pack(fill="both", expand=True)

    def show_pets(self):
        self.clear_content()
        self.current_frame = PetView(self.content_area)
        self.current_frame.pack(fill="both", expand=True)

    def show_vaccinations(self):
        self.clear_content()
        self.current_frame = VaccinationView(self.content_area)
        self.current_frame.pack(fill="both", expand=True)

    def show_medical_records(self):
        self.clear_content()
        self.current_frame = MedicalRecordView(self.content_area)
        self.current_frame.pack(fill="both", expand=True)

    def _placeholder_view(self, title_text):
        self.clear_content()
        self.current_frame = tk.Frame(self.content_area, bg=styles.SECONDARY_COLOR, padx=styles.PADDING_LARGE, pady=styles.PADDING_LARGE)
        self.current_frame.pack(fill="both", expand=True)
        
        tk.Label(self.current_frame, text=title_text, font=styles.FONT_TITLE, 
                bg=styles.SECONDARY_COLOR, fg=styles.PRIMARY_COLOR).pack(anchor="w")
        tk.Label(self.current_frame, text="Work in progress...", font=styles.FONT_NORMAL,
                bg=styles.SECONDARY_COLOR, fg=styles.TEXT_ON_SECONDARY).pack(anchor="w", pady=10)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
