#!/usr/bin/env python3
"""
Admin Interface for AI-niform Database Management
Simple interface to add, edit, and view database entries.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database_manager import DatabaseManager

class AdminInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("AI-niform Admin")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        self.db_manager = DatabaseManager()
        
        self.setup_ui()
        self.refresh_list()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title_label = tk.Label(
            self.root,
            text="AI-niform Database Management",
            font=('Arial', 20, 'bold'),
            fg='#007BFF'
        )
        title_label.pack(pady=20)
        
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left side - Add/Edit form
        left_frame = tk.Frame(main_frame, width=300)
        left_frame.pack(side='left', fill='y', padx=(0, 20))
        left_frame.pack_propagate(False)
        
        # Form title
        form_title = tk.Label(left_frame, text="Add/Edit Person", font=('Arial', 14, 'bold'))
        form_title.pack(pady=(0, 20))
        
        # Card ID
        tk.Label(left_frame, text="Card ID:").pack(anchor='w')
        self.card_id_var = tk.StringVar()
        card_id_entry = tk.Entry(left_frame, textvariable=self.card_id_var, width=25)
        card_id_entry.pack(fill='x', pady=(5, 15))
        
        # Role
        tk.Label(left_frame, text="Role:").pack(anchor='w')
        self.role_var = tk.StringVar(value="STUDENT")
        role_combo = ttk.Combobox(left_frame, textvariable=self.role_var, 
                                 values=["STUDENT", "GUARD", "SPECIAL"], state="readonly", width=22)
        role_combo.pack(fill='x', pady=(5, 15))
        
        # Name
        tk.Label(left_frame, text="Name:").pack(anchor='w')
        self.name_var = tk.StringVar()
        name_entry = tk.Entry(left_frame, textvariable=self.name_var, width=25)
        name_entry.pack(fill='x', pady=(5, 15))
        
        # Buttons
        button_frame = tk.Frame(left_frame)
        button_frame.pack(fill='x', pady=20)
        
        add_button = tk.Button(
            button_frame,
            text="Add Person",
            command=self.add_person,
            bg='#28a745',
            fg='white',
            relief='flat',
            padx=20,
            pady=5
        )
        add_button.pack(side='left', padx=(0, 10))
        
        clear_button = tk.Button(
            button_frame,
            text="Clear Form",
            command=self.clear_form,
            bg='#6c757d',
            fg='white',
            relief='flat',
            padx=20,
            pady=5
        )
        clear_button.pack(side='left')
        
        # Right side - Database list
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # List title
        list_title = tk.Label(right_frame, text="Database Entries", font=('Arial', 14, 'bold'))
        list_title.pack(pady=(0, 10))
        
        # Treeview for database entries
        columns = ('ID', 'Role', 'Name', 'Status')
        self.tree = ttk.Treeview(right_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Action buttons for selected entry
        action_frame = tk.Frame(right_frame)
        action_frame.pack(fill='x', pady=10)
        
        edit_button = tk.Button(
            action_frame,
            text="Edit Selected",
            command=self.edit_selected,
            bg='#007bff',
            fg='white',
            relief='flat',
            padx=15,
            pady=5
        )
        edit_button.pack(side='left', padx=(0, 10))
        
        delete_button = tk.Button(
            action_frame,
            text="Delete Selected",
            command=self.delete_selected,
            bg='#dc3545',
            fg='white',
            relief='flat',
            padx=15,
            pady=5
        )
        delete_button.pack(side='left')
        
        refresh_button = tk.Button(
            action_frame,
            text="Refresh List",
            command=self.refresh_list,
            bg='#17a2b8',
            fg='white',
            relief='flat',
            padx=15,
            pady=5
        )
        refresh_button.pack(side='right')
    
    def add_person(self):
        """Add a new person to the database"""
        card_id = self.card_id_var.get().strip()
        role = self.role_var.get()
        name = self.name_var.get().strip()
        
        if not card_id or not name:
            messagebox.showwarning("Missing Information", "Please fill in all fields")
            return
        
        success, message = self.db_manager.add_person(card_id, role, name)
        
        if success:
            messagebox.showinfo("Success", message)
            self.clear_form()
            self.refresh_list()
        else:
            messagebox.showerror("Error", message)
    
    def clear_form(self):
        """Clear the form fields"""
        self.card_id_var.set("")
        self.name_var.set("")
        self.role_var.set("STUDENT")
    
    def refresh_list(self):
        """Refresh the database list"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load and display all records
        records = self.db_manager.load_database()
        for record in records:
            self.tree.insert('', 'end', values=(
                record['id'],
                record['role'],
                record['name'],
                record['status']
            ))
    
    def on_select(self, event):
        """Handle selection of a database entry"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            
            # Fill form with selected values
            self.card_id_var.set(values[0])
            self.role_var.set(values[1])
            self.name_var.set(values[2])
    
    def edit_selected(self):
        """Edit the selected database entry"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an entry to edit")
            return
        
        card_id = self.card_id_var.get().strip()
        role = self.role_var.get()
        name = self.name_var.get().strip()
        
        if not card_id or not name:
            messagebox.showwarning("Missing Information", "Please fill in all fields")
            return
        
        success, message = self.db_manager.update_person(card_id, role, name)
        
        if success:
            messagebox.showinfo("Success", message)
            self.clear_form()
            self.refresh_list()
        else:
            messagebox.showerror("Error", message)
    
    def delete_selected(self):
        """Delete the selected database entry"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an entry to delete")
            return
        
        item = self.tree.item(selection[0])
        card_id = item['values'][0]
        name = item['values'][2]
        
        result = messagebox.askyesno("Confirm Delete", 
                                   f"Are you sure you want to delete {name} (ID: {card_id})?")
        
        if result:
            success, message = self.db_manager.delete_person(card_id)
            
            if success:
                messagebox.showinfo("Success", message)
                self.clear_form()
                self.refresh_list()
            else:
                messagebox.showerror("Error", message)

def main():
    """Main function"""
    root = tk.Tk()
    app = AdminInterface(root)
    root.mainloop()

if __name__ == "__main__":
    main() 