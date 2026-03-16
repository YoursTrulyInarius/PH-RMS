import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Any, List, Dict

import styles # type: ignore
import database # type: ignore

class VaccinationView(tk.Frame):
    tree: ttk.Treeview

    def __init__(self, parent: tk.Widget):
        super().__init__(parent, bg=styles.SECONDARY_COLOR, padx=styles.PADDING_LARGE, pady=styles.PADDING_LARGE)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self, bg=styles.SECONDARY_COLOR)
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(header_frame, text="Vaccination Records", font=styles.FONT_TITLE, 
                bg=styles.SECONDARY_COLOR, fg=styles.PRIMARY_COLOR).pack(side="left")
        
        tk.Button(header_frame, text="+ Add New Record", font=styles.FONT_BOLD,
                  bg=styles.COMPLEMENTARY_COLOR, fg=styles.TEXT_ON_COMPLEMENTARY,
                  padx=15, pady=8, bd=0, cursor="hand2",
                  command=self.show_vax_form).pack(side="right")

        # Table (Treeview)
        table_frame = tk.Frame(self, bg=styles.SECONDARY_COLOR)
        table_frame.pack(fill="both", expand=True)
        
        columns = ("ID", "Pet Name", "Vaccine Name", "Date Given", "Next Due")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<Double-1>", self.on_double_click)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        records = database.get_vaccinations()
        for rec in records:
            self.tree.insert("", "end", values=(
                rec['vaccine_id'], rec['pet_name'], rec['vaccine_name'], 
                rec['date_given'], rec['next_due']
            ))

    def on_double_click(self, event: Any):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            vax_data = self.tree.item(item)['values']
            self.show_vax_form(vax_data)

    def show_vax_form(self, vax_data=None):
        form_win = tk.Toplevel(self)
        form_win.title("Edit Vaccination Record" if vax_data else "Add Vaccination Record")
        form_win.geometry("400x500")
        form_win.configure(bg=styles.SECONDARY_COLOR, padx=20, pady=20)
        
        tk.Label(form_win, text="Vaccination Details", font=styles.FONT_SUBTITLE, 
                bg=styles.SECONDARY_COLOR, fg=styles.PRIMARY_COLOR).pack(pady=(0, 20))
        
        pets = database.get_pets()
        pet_list = [f"{p['pet_id']} - {p['name']}" for p in pets]
        
        tk.Label(form_win, text="Select Pet:", font=styles.FONT_NORMAL, 
                bg=styles.SECONDARY_COLOR, fg=styles.TEXT_ON_SECONDARY).pack(anchor="w")
        pet_combo = ttk.Combobox(form_win, values=pet_list, font=styles.FONT_NORMAL)
        pet_combo.pack(fill="x", pady=(5, 10))
        if vax_data:
            pet_name = vax_data[1]
            for p_str in pet_list:
                if pet_name in p_str:
                    pet_combo.set(p_str)
                    break
            pet_combo.configure(state="disabled") # Don't allow changing pet for existing record
        
        tk.Label(form_win, text="Vaccine Name:", font=styles.FONT_NORMAL, 
                bg=styles.SECONDARY_COLOR, fg=styles.TEXT_ON_SECONDARY).pack(anchor="w")
        vax_entry = tk.Entry(form_win, font=styles.FONT_NORMAL, bd=1, relief="solid")
        vax_entry.pack(fill="x", pady=(5, 10))
        if vax_data: vax_entry.insert(0, vax_data[2])
        
        tk.Label(form_win, text="Date Given (YYYY-MM-DD):", font=styles.FONT_NORMAL, 
                bg=styles.SECONDARY_COLOR, fg=styles.TEXT_ON_SECONDARY).pack(anchor="w")
        date_entry = tk.Entry(form_win, font=styles.FONT_NORMAL, bd=1, relief="solid")
        date_entry.pack(fill="x", pady=(5, 10))
        if vax_data: date_entry.insert(0, vax_data[3])
        
        tk.Label(form_win, text="Next Due (YYYY-MM-DD):", font=styles.FONT_NORMAL, 
                bg=styles.SECONDARY_COLOR, fg=styles.TEXT_ON_SECONDARY).pack(anchor="w")
        due_entry = tk.Entry(form_win, font=styles.FONT_NORMAL, bd=1, relief="solid")
        due_entry.pack(fill="x", pady=(5, 20))
        if vax_data: due_entry.insert(0, vax_data[4])

        def save():
            pet_val = pet_combo.get()
            vax_name = vax_entry.get()
            date_val = date_entry.get()
            due_val = due_entry.get()
            
            if not all([pet_val, vax_name]):
                messagebox.showerror("Error", "Pet and Vaccine Name are required.")
                return
            
            if vax_data:
                database.update_vaccination(vax_data[0], vax_name, date_val, due_val)
            else:
                pet_id = int(pet_val.split(" - ")[0])
                database.add_vaccination(pet_id, vax_name, date_val, due_val)
            
            self.load_data()
            form_win.destroy()

        tk.Button(form_win, text="Save Record", font=styles.FONT_BOLD,
                  bg=styles.PRIMARY_COLOR, fg=styles.TEXT_ON_PRIMARY,
                  padx=20, pady=10, bd=0, cursor="hand2", command=save).pack()
        
        if vax_data:
            def delete():
                if messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
                    database.delete_vaccination(vax_data[0])
                    self.load_data()
                    form_win.destroy()
            
            tk.Button(form_win, text="Delete Record", font=styles.FONT_BOLD,
                      bg="#FF4D4D", fg="#FFFFFF",
                      padx=20, pady=10, bd=0, cursor="hand2", command=delete).pack(pady=10)
