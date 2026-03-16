import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Any, List, Dict

import styles # type: ignore
import database # type: ignore

class OwnerView(tk.Frame):
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
        
        tk.Label(header_frame, text="Owner Management", font=styles.FONT_TITLE, 
                bg=styles.SECONDARY_COLOR, fg=styles.PRIMARY_COLOR).pack(side="left")
        
        tk.Button(header_frame, text="+ Add New Owner", font=styles.FONT_BOLD,
                  bg=styles.COMPLEMENTARY_COLOR, fg=styles.TEXT_ON_COMPLEMENTARY,
                  padx=15, pady=8, bd=0, cursor="hand2",
                  command=self.show_add_owner_form).pack(side="right")

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
        
        columns = ("ID", "Name", "Contact", "Address")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.column("ID", width=50)
        self.tree.column("Address", width=300)
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Context Menu
        self.tree.bind("<Double-1>", self.on_double_click)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        owners = database.get_owners()
        for owner in owners:
            self.tree.insert("", "end", values=(owner['owner_id'], owner['name'], owner['contact'], owner['address']))

    def filter_data(self, event=None):
        search_term = self.search_entry.get().lower()
        self.load_data()
        if search_term:
            for item in self.tree.get_children():
                values = self.tree.item(item)['values']
                if not any(search_term in str(val).lower() for val in values):
                    self.tree.delete(item)

    def show_add_owner_form(self):
        self.show_owner_form()

    def on_double_click(self, event: Any):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            owner_values = self.tree.item(item)['values']
            self.show_owner_form(owner_values)

    def show_owner_form(self, owner_data=None):
        form_win = tk.Toplevel(self)
        form_win.title("Edit Owner" if owner_data else "Add New Owner")
        form_win.geometry("400x450")
        form_win.configure(bg=styles.SECONDARY_COLOR, padx=20, pady=20)
        
        tk.Label(form_win, text="Owner Details", font=styles.FONT_SUBTITLE, 
                bg=styles.SECONDARY_COLOR, fg=styles.PRIMARY_COLOR).pack(pady=(0, 20))
        
        fields = [("Name:", "name"), ("Contact:", "contact"), ("Address:", "address")]
        entries = {}
        
        for i, (label_text, key) in enumerate(fields):
            tk.Label(form_win, text=label_text, font=styles.FONT_NORMAL, 
                    bg=styles.SECONDARY_COLOR, fg=styles.TEXT_ON_SECONDARY).pack(anchor="w")
            entry = tk.Entry(form_win, font=styles.FONT_NORMAL, bd=1, relief="solid")
            if key == "address":
                 # Use a larger entry for address if needed, but for simplicity keeping it Entry for now
                 pass
            entry.pack(fill="x", pady=(5, 15))
            entries[key] = entry
            
            if owner_data:
                # Map values from table to entries
                val = owner_data[i+1] # Skip ID
                entry.insert(0, val)

        def save():
            name = entries['name'].get()
            contact = entries['contact'].get()
            address = entries['address'].get()
            
            if not name:
                messagebox.showerror("Error", "Name is required.")
                return
            
            try:
                if owner_data:
                    database.update_owner(owner_data[0], name, contact, address)
                else:
                    database.add_owner(name, contact, address)
                    
                self.load_data()
                form_win.destroy()
            except ValueError as e:
                messagebox.showerror("Duplicate Entry", str(e))

        save_btn = tk.Button(form_win, text="Save Record", font=styles.FONT_BOLD,
                           bg=styles.PRIMARY_COLOR, fg=styles.TEXT_ON_PRIMARY,
                           padx=20, pady=10, bd=0, cursor="hand2", command=save)
        save_btn.pack(pady=10)
        
        if owner_data:
            def delete():
                if messagebox.askyesno("Confirm", f"Are you sure you want to delete {owner_data[1]}?"):
                    database.delete_owner(owner_data[0])
                    self.load_data()
                    form_win.destroy()
            
            del_btn = tk.Button(form_win, text="Delete Record", font=styles.FONT_BOLD,
                              bg="#FF4D4D", fg="#FFFFFF",
                              padx=20, pady=10, bd=0, cursor="hand2", command=delete)
            del_btn.pack()
