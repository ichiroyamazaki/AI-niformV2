#!/usr/bin/env python3
"""
Admin Interface for AI-niform
Simple interface to manage students and their images in the database.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database_manager import DatabaseManager
import os
import shutil

class AdminInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("AI-niform Admin Interface")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Image directory
        self.image_dir = "/Users/ichiroyamazaki/Desktop/ainiform/id-image"
        
        # Create main frame
        self.main_frame = tk.Frame(root, bg='white')
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            self.main_frame,
            text="AI-niform Student Management",
            font=('Arial', 20, 'bold'),
            fg='#007BFF',
            bg='white'
        )
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Add Student tab
        self.add_student_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.add_student_frame, text="Add New Student")
        self.create_add_student_tab()
        
        # View Students tab
        self.view_students_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.view_students_frame, text="View Students")
        self.create_view_students_tab()
        
        # Refresh student list
        self.refresh_student_list()
    
    def create_add_student_tab(self):
        """Create the add student tab"""
        # Form frame
        form_frame = tk.Frame(self.add_student_frame, bg='white')
        form_frame.pack(expand=True, padx=20, pady=20)
        
        # Student Number
        tk.Label(form_frame, text="Student Number:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(0, 5))
        self.student_number_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.student_number_var, font=('Arial', 12), width=30).pack(fill='x', pady=(0, 15))
        
        # RFID Number
        tk.Label(form_frame, text="RFID Number:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(0, 5))
        self.rfid_number_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.rfid_number_var, font=('Arial', 12), width=30).pack(fill='x', pady=(0, 15))
        
        # Student Name
        tk.Label(form_frame, text="Student Name:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(0, 5))
        self.student_name_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.student_name_var, font=('Arial', 12), width=30).pack(fill='x', pady=(0, 15))
        
        # Image selection
        image_frame = tk.Frame(form_frame, bg='white')
        image_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(image_frame, text="Student Photo:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(0, 5))
        
        self.image_path_var = tk.StringVar()
        image_entry = tk.Entry(image_frame, textvariable=self.image_path_var, font=('Arial', 12), width=25)
        image_entry.pack(side='left', fill='x', expand=True, pady=(0, 5))
        
        browse_button = tk.Button(
            image_frame,
            text="Browse",
            font=('Arial', 10),
            command=self.browse_image
        )
        browse_button.pack(side='right', padx=(10, 0))
        
        # Violation Count
        violation_frame = tk.Frame(form_frame, bg='white')
        violation_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(violation_frame, text="Violation Count:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(0, 5))
        
        self.violation_count_var = tk.StringVar(value="0")
        violation_entry = tk.Entry(violation_frame, textvariable=self.violation_count_var, font=('Arial', 12), width=10)
        violation_entry.pack(anchor='w', pady=(0, 5))
        
        # Add button
        add_button = tk.Button(
            form_frame,
            text="Add Student",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#28a745',
            command=self.add_student
        )
        add_button.pack(pady=20)
    
    def create_view_students_tab(self):
        """Create the view students tab"""
        # Control frame
        control_frame = tk.Frame(self.view_students_frame, bg='white')
        control_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        refresh_button = tk.Button(
            control_frame,
            text="Refresh List",
            font=('Arial', 12),
            command=self.refresh_student_list
        )
        refresh_button.pack(side='left')
        
        # Student list frame
        list_frame = tk.Frame(self.view_students_frame, bg='white')
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Create Treeview
        columns = ('Student Number', 'RFID', 'Name', 'Image', 'Status')
        self.student_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.student_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind double-click event
        self.student_tree.bind('<Double-1>', self.edit_student)
    
    def browse_image(self):
        """Browse for an image file"""
        file_path = filedialog.askopenfilename(
            title="Select Student Photo",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            # Get just the filename
            filename = os.path.basename(file_path)
            self.image_path_var.set(filename)
    
    def add_student(self):
        """Add a new student to the database"""
        student_number = self.student_number_var.get().strip()
        rfid_number = self.rfid_number_var.get().strip()
        student_name = self.student_name_var.get().strip()
        image_filename = self.image_path_var.get().strip()
        violation_count = self.violation_count_var.get().strip()
        
        # Validate inputs
        if not student_number or not rfid_number or not student_name:
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        # Validate violation count
        try:
            violation_count = int(violation_count) if violation_count else 0
            if violation_count < 0:
                messagebox.showerror("Error", "Violation count must be 0 or greater")
                return
        except ValueError:
            messagebox.showerror("Error", "Violation count must be a number")
            return
        
        # Check if student number already exists
        existing_student = self.db_manager.find_person(student_number)
        if existing_student:
            messagebox.showerror("Error", f"Student number {student_number} already exists")
            return
        
        # Check if RFID already exists
        existing_rfid = self.db_manager.find_person(rfid_number)
        if existing_rfid:
            messagebox.showerror("Error", f"RFID number {rfid_number} already exists")
            return
        
        # Copy image file if provided
        image_path = None
        if image_filename:
            source_path = filedialog.askopenfilename(
                title="Select the image file to copy",
                filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.webp")]
            )
            if source_path:
                try:
                    # Ensure image directory exists
                    os.makedirs(self.image_dir, exist_ok=True)
                    
                    # Copy file to image directory
                    dest_path = os.path.join(self.image_dir, image_filename)
                    shutil.copy2(source_path, dest_path)
                    image_path = image_filename
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to copy image: {e}")
                    return
        
        # Add student number record
        success, message = self.db_manager.add_person(student_number, "STUDENT_NUMBER", student_name, image_path, violation_count)
        if not success:
            messagebox.showerror("Error", f"Failed to add student: {message}")
            return
        
        # Add RFID mapping
        success, message = self.db_manager.add_person(rfid_number, "STUDENT_RFID", student_number, None, 0)
        if not success:
            messagebox.showerror("Error", f"Failed to add RFID mapping: {message}")
            return
        
        messagebox.showinfo("Success", f"Student {student_name} added successfully!")
        
        # Clear form
        self.student_number_var.set("")
        self.rfid_number_var.set("")
        self.student_name_var.set("")
        self.image_path_var.set("")
        self.violation_count_var.set("0")
        
        # Refresh student list
        self.refresh_student_list()
    
    def refresh_student_list(self):
        """Refresh the student list"""
        # Clear existing items
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        # Load all records
        records = self.db_manager.load_database()
        
        # Find student numbers and their RFID mappings
        students = []
        for record in records:
            if record['role'] == 'STUDENT_NUMBER' and record['status'] == 'ACTIVE':
                # Find corresponding RFID
                rfid = "Not found"
                for rfid_record in records:
                    if (rfid_record['role'] == 'STUDENT_RFID' and 
                        rfid_record['status'] == 'ACTIVE' and 
                        rfid_record['name'] == record['id']):
                        rfid = rfid_record['id']
                        break
                
                students.append({
                    'student_number': record['id'],
                    'rfid': rfid,
                    'name': record['name'],
                    'image': record.get('image_path', 'No image'),
                    'status': record['status']
                })
        
        # Add to treeview
        for student in students:
            self.student_tree.insert('', 'end', values=(
                student['student_number'],
                student['rfid'],
                student['name'],
                student['image'],
                student['status']
            ))
    
    def edit_student(self, event):
        """Edit a student (placeholder for future implementation)"""
        selection = self.student_tree.selection()
        if selection:
            item = self.student_tree.item(selection[0])
            student_number = item['values'][0]
            messagebox.showinfo("Edit Student", f"Edit functionality for student {student_number} will be implemented in the future.")

def main():
    """Main function"""
    root = tk.Tk()
    app = AdminInterface(root)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main() 