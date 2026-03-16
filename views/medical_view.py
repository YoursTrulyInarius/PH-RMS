import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Any, List, Dict

import styles # type: ignore
import database # type: ignore

class MedicalRecordView(tk.Frame):
    tree: ttk.Treeview

    def __init__(self, parent: tk.Widget):
        super().__init__(parent, bg=styles.SECONDARY_COLOR, padx=styles.PADDING_LARGE, pady=styles.PADDING_LARGE)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        header_frame = tk.Frame(self, bg=styles.SECONDARY_COLOR)
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(header_frame, text="Medical History & Treatments", font=styles.FONT_TITLE, 
                bg=styles.SECONDARY_COLOR, fg=styles.PRIMARY_COLOR).pack(side="left")
        
        tk.Button(header_frame, text="+ New Medical Record", font=styles.FONT_BOLD,
                  bg=styles.COMPLEMENTARY_COLOR, fg=styles.TEXT_ON_COMPLEMENTARY,
                  padx=15, pady=8, bd=0, cursor="hand2",
                  command=self.show_record_form).pack(side="right")

        table_frame = tk.Frame(self, bg=styles.SECONDARY_COLOR)
        table_frame.pack(fill="both", expand=True)
        
        columns = ("ID", "Pet Name", "Diagnosis", "Treatment", "Date")
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
        
        records = database.get_medical_records()
        for rec in records:
            self.tree.insert("", "end", values=(
                rec['record_id'], rec['pet_name'], rec['diagnosis'], 
                rec['treatment'], rec['date']
            ))

    def on_double_click(self, event: Any):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            rec_data = self.tree.item(item)['values']
            self.show_record_form(rec_data)

    def show_record_form(self, rec_data=None):
        form_win = tk.Toplevel(self)
        form_win.title("Edit Medical Record" if rec_data else "Add Medical Record")
        form_win.geometry("450x550")
        form_win.configure(bg=styles.SECONDARY_COLOR, padx=20, pady=20)
        
        tk.Label(form_win, text="Medical Details", font=styles.FONT_SUBTITLE, 
                bg=styles.SECONDARY_COLOR, fg=styles.PRIMARY_COLOR).pack(pady=(0, 20))
        
        pets = database.get_pets()
        pet_list = [f"{p['pet_id']} - {p['name']}" for p in pets]
        
        tk.Label(form_win, text="Select Pet:", font=styles.FONT_NORMAL, 
                bg=styles.SECONDARY_COLOR, fg=styles.TEXT_ON_SECONDARY).pack(anchor="w")
        pet_combo = ttk.Combobox(form_win, values=pet_list, font=styles.FONT_NORMAL)
        pet_combo.pack(fill="x", pady=(5, 10))
        if rec_data:
            pet_name = rec_data[1]
            for p_str in pet_list:
                if pet_name in p_str:
                    pet_combo.set(p_str)
                    break
            pet_combo.configure(state="disabled")
        
        tk.Label(form_win, text="Diagnosis:", font=styles.FONT_NORMAL, 
                bg=styles.SECONDARY_COLOR, fg=styles.TEXT_ON_SECONDARY).pack(anchor="w")
        diag_entry = tk.Entry(form_win, font=styles.FONT_NORMAL, bd=1, relief="solid")
        diag_entry.pack(fill="x", pady=(5, 10))
        if rec_data: diag_entry.insert(0, rec_data[2])
        
        tk.Label(form_win, text="Treatment:", font=styles.FONT_NORMAL, 
                bg=styles.SECONDARY_COLOR, fg=styles.TEXT_ON_SECONDARY).pack(anchor="w")
        treat_entry = tk.Entry(form_win, font=styles.FONT_NORMAL, bd=1, relief="solid")
        treat_entry.pack(fill="x", pady=(5, 10))
        if rec_data: treat_entry.insert(0, rec_data[3])
        
        tk.Label(form_win, text="Date (YYYY-MM-DD):", font=styles.FONT_NORMAL, 
                bg=styles.SECONDARY_COLOR, fg=styles.TEXT_ON_SECONDARY).pack(anchor="w")
        date_entry = tk.Entry(form_win, font=styles.FONT_NORMAL, bd=1, relief="solid")
        date_entry.pack(fill="x", pady=(5, 20))
        if rec_data: date_entry.insert(0, rec_data[4])

        def save():
            pet_val = pet_combo.get()
            diagnosis = diag_entry.get()
            treatment = treat_entry.get()
            date_val = date_entry.get()
            
            if not all([pet_val, diagnosis]):
                messagebox.showerror("Error", "Pet and Diagnosis are required.")
                return
            
            if rec_data:
                database.update_medical_record(rec_data[0], diagnosis, treatment, date_val)
            else:
                pet_id = int(pet_val.split(" - ")[0])
                database.add_medical_record(pet_id, diagnosis, treatment, date_val)
                
            self.load_data()
            form_win.destroy()

        save_btn = tk.Button(form_win, text="Save Record", font=styles.FONT_BOLD,
                           bg=styles.PRIMARY_COLOR, fg=styles.TEXT_ON_PRIMARY,
                           padx=20, pady=10, bd=0, cursor="hand2", command=save)
        save_btn.pack()
        
        if rec_data:
            def delete():
                if messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
                    database.delete_medical_record(rec_data[0])
                    self.load_data()
                    form_win.destroy()
            
            tk.Button(form_win, text="Delete Record", font=styles.FONT_BOLD,
                      bg="#FF4D4D", fg="#FFFFFF",
                      padx=20, pady=10, bd=0, cursor="hand2", command=delete).pack(pady=10)
