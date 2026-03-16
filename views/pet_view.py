import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Any, List, Dict

import styles # type: ignore
import database # type: ignore

class PetView(tk.Frame):
    search_entry: ttk.Entry
    tree: ttk.Treeview

    def __init__(self, parent: tk.Widget):
        super().__init__(parent, bg=styles.SECONDARY_COLOR, padx=styles.PADDING_LARGE, pady=styles.PADDING_LARGE)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self, bg=styles.SECONDARY_COLOR)
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(header_frame, text="Pet Management", font=styles.FONT_TITLE, 
                bg=styles.SECONDARY_COLOR, fg=styles.PRIMARY_COLOR).pack(side="left")
        
        tk.Button(header_frame, text="+ Add New Pet", font=styles.FONT_BOLD,
                  bg=styles.COMPLEMENTARY_COLOR, fg=styles.TEXT_ON_COMPLEMENTARY,
                  padx=15, pady=8, bd=0, cursor="hand2",
                  command=self.show_pet_form).pack(side="right")

        # Search Bar
        search_frame = tk.Frame(self, bg=styles.SECONDARY_COLOR)
        search_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(search_frame, text="Search:", font=styles.FONT_NORMAL, 
                bg=styles.SECONDARY_COLOR, fg=styles.TEXT_ON_SECONDARY).pack(side="left")
        self.search_entry = ttk.Entry(search_frame, font=styles.FONT_NORMAL)
        self.search_entry.pack(side="left", padx=10, fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.filter_data)

        # Table (Treeview)
        table_frame = tk.Frame(self, bg=styles.SECONDARY_COLOR)
        table_frame.pack(fill="both", expand=True)
        
        columns = ("ID", "Name", "Species", "Breed", "Birthdate", "Owner")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<Double-1>", self.on_double_click)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        pets = database.get_pets()
        for pet in pets:
            self.tree.insert("", "end", values=(
                pet['pet_id'], pet['name'], pet['species'], 
                pet['breed'], pet['birthdate'], pet['owner_name']
            ))

    def filter_data(self, event=None):
        search_term = self.search_entry.get().lower()
        self.load_data()
        if search_term:
            for item in self.tree.get_children():
                values = self.tree.item(item)['values']
                if not any(search_term in str(val).lower() for val in values):
                    self.tree.delete(item)

    def on_double_click(self, event: Any):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            pet_values = self.tree.item(item)['values']
            self.show_pet_form(pet_values)

    def show_pet_form(self, pet_data=None):
        form_win = tk.Toplevel(self)
        form_win.title("Edit Pet" if pet_data else "Add New Pet")
        form_win.geometry("450x550")
        form_win.configure(bg=styles.SECONDARY_COLOR, padx=20, pady=20)
        
        tk.Label(form_win, text="Pet Details", font=styles.FONT_SUBTITLE, 
                bg=styles.SECONDARY_COLOR, fg=styles.PRIMARY_COLOR).pack(pady=(0, 10))
        
        owners = database.get_owners()
        owner_names = [f"{o['owner_id']} - {o['name']}" for o in owners]
        
        fields = [
            ("Pet Name:", "name", "entry"),
            ("Species:", "species", "entry"),
            ("Breed:", "breed", "entry"),
            ("Birthdate (YYYY-MM-DD):", "birthdate", "entry"),
            ("Owner:", "owner", "combo")
        ]
        
        entries = {}
        for label_text, key, field_type in fields:
            tk.Label(form_win, text=label_text, font=styles.FONT_NORMAL, 
                    bg=styles.SECONDARY_COLOR, fg=styles.TEXT_ON_SECONDARY).pack(anchor="w")
            if field_type == "entry":
                entry = tk.Entry(form_win, font=styles.FONT_NORMAL, bd=1, relief="solid")
                entry.pack(fill="x", pady=(5, 10))
                entries[key] = entry
                if pet_data:
                    # Map based on index: ID, Name, Species, Breed, Birthdate, OwnerName
                    idx_map = {"name": 1, "species": 2, "breed": 3, "birthdate": 4}
                    if key in idx_map:
                        val = pet_data[idx_map[key]]
                        entry.insert(0, val)
            else:
                combo = ttk.Combobox(form_win, values=owner_names, font=styles.FONT_NORMAL)
                combo.pack(fill="x", pady=(5, 10))
                entries[key] = combo
                if pet_data:
                    # Find and set current owner
                    owner_name = pet_data[5]
                    for name in owner_names:
                        if owner_name in name:
                            combo.set(name)
                            break

        def save():
            name = entries['name'].get()
            species = entries['species'].get()
            breed = entries['breed'].get()
            birthdate = entries['birthdate'].get()
            owner_val = entries['owner'].get()
            
            if not all([name, owner_val]):
                messagebox.showerror("Error", "Name and Owner are required.")
                return
            
            owner_id = int(owner_val.split(" - ")[0])
            
            if pet_data:
                database.update_pet(pet_data[0], name, species, breed, birthdate)
            else:
                database.add_pet(owner_id, name, species, breed, birthdate)
                
            self.load_data()
            form_win.destroy()

        save_btn = tk.Button(form_win, text="Save Record", font=styles.FONT_BOLD,
                           bg=styles.PRIMARY_COLOR, fg=styles.TEXT_ON_PRIMARY,
                           padx=20, pady=10, bd=0, cursor="hand2", command=save)
        save_btn.pack(pady=10)
        
        if pet_data:
            def delete():
                if messagebox.askyesno("Confirm", f"Are you sure you want to delete {pet_data[1]}?"):
                    database.delete_pet(pet_data[0])
                    self.load_data()
                    form_win.destroy()
            
            del_btn = tk.Button(form_win, text="Delete Record", font=styles.FONT_BOLD,
                              bg="#FF4D4D", fg="#FFFFFF",
                              padx=20, pady=10, bd=0, cursor="hand2", command=delete)
            del_btn.pack()
