#!/usr/bin/env python3
"""
AI-niform Application
A Python GUI application with login and turnstile interfaces in one application.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
from datetime import datetime
from database_manager import DatabaseManager

class AINiformApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI-niform")
        self.root.geometry("1280x768")
        self.root.resizable(False, False)
        
        # Configure the main window
        self.root.configure(bg='white')
        
        # Create main frame with border
        self.main_frame = tk.Frame(root, bg='#f0f0f0', relief='solid', bd=1)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create content frame (white background)
        self.content_frame = tk.Frame(self.main_frame, bg='white')
        self.content_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Initialize variables
        self.current_screen = "login"
        self.time_label = None
        self.date_label = None
        self.db_manager = DatabaseManager()
        self.card_input_var = tk.StringVar()
        self.card_entry = None  # Store reference to card entry field
        self.is_processing = False  # Flag to prevent duplicate processing
        
        # Start with login screen
        self.show_login_screen()
        self.update_time()
    
    def clear_content(self):
        """Clear all widgets from content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Show the login screen"""
        self.current_screen = "login"
        self.clear_content()
        
        # Create main content area
        content_area = tk.Frame(self.content_frame, bg='white')
        content_area.pack(fill='both', expand=True)
        
        # Application name/logo
        app_name_frame = tk.Frame(content_area, bg='white')
        app_name_frame.pack(expand=True)
        
        # AI-niform text with different colors
        ai_text = tk.Label(
            app_name_frame,
            text="AI-",
            font=('Arial', 36, 'bold'),
            fg='#0066cc',  # Bright blue
            bg='white'
        )
        ai_text.pack(side='left')
        
        niform_text = tk.Label(
            app_name_frame,
            text="niform",
            font=('Arial', 36, 'bold'),
            fg='#003366',  # Dark blue/black
            bg='white'
        )
        niform_text.pack(side='left')
        
        # Log-in button
        login_button = tk.Button(
            content_area,
            text="Log-in",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#28a745',  # Green
            relief='flat',
            bd=0,
            padx=40,
            pady=10,
            cursor='hand2',
            command=self.show_turnstile_screen
        )
        login_button.pack(pady=20)
        
        # Footer bar
        self.create_footer("quit")
    
    def show_turnstile_screen(self):
        """Show the turnstile screen"""
        self.current_screen = "turnstile"
        self.clear_content()
        
        # Top banner (orange)
        self.create_top_banner()
        
        # Main content area
        self.create_main_content()
        
        # Footer bar
        self.create_footer("back")
    
    def create_top_banner(self):
        """Create the orange top banner with 'Turnstile is Closed' text"""
        banner_frame = tk.Frame(self.content_frame, bg='#FF8C00', height=80)
        banner_frame.pack(fill='x')
        banner_frame.pack_propagate(False)
        
        # Turnstile status text
        status_label = tk.Label(
            banner_frame,
            text="Turnstile is Closed",
            font=('Arial', 24, 'bold'),
            fg='black',
            bg='#FF8C00'
        )
        status_label.pack(expand=True)
        
        # Light grey separator line
        separator = tk.Frame(self.content_frame, bg='#d3d3d3', height=2)
        separator.pack(fill='x')
    
    def create_main_content(self):
        """Create the main content area with logo and instructions"""
        content_area = tk.Frame(self.content_frame, bg='white')
        content_area.pack(fill='both', expand=True)
        
        # Left side (white panel with AI-niform logo)
        left_panel = tk.Frame(content_area, bg='white')
        left_panel.pack(side='left', fill='both', expand=True)
        
        # AI-niform logo
        logo_frame = tk.Frame(left_panel, bg='white')
        logo_frame.pack(expand=True)
        
        # AI-niform text
        ai_text = tk.Label(
            logo_frame,
            text="AI-",
            font=('Arial', 48, 'bold'),
            fg='#007BFF',  # Bright blue
            bg='white'
        )
        ai_text.pack(side='left')
        
        niform_text = tk.Label(
            logo_frame,
            text="niform",
            font=('Arial', 48, 'bold'),
            fg='#212529',  # Dark blue/black
            bg='white'
        )
        niform_text.pack(side='left')
        
        # Right side (blue panel with instructions)
        right_panel = tk.Frame(content_area, bg='#1E90FF', width=400)
        right_panel.pack(side='right', fill='y')
        right_panel.pack_propagate(False)
        
        # Instructions text
        instructions_frame = tk.Frame(right_panel, bg='#1E90FF')
        instructions_frame.pack(expand=True, padx=40, pady=40)
        
        instructions_text = """Please tap
your ID to
the Card
Reader."""
        
        instructions_label = tk.Label(
            instructions_frame,
            text=instructions_text,
            font=('Arial', 28, 'bold'),
            fg='white',
            bg='#1E90FF',
            justify='left'
        )
        instructions_label.pack(anchor='w')
        
        # Card input section
        card_frame = tk.Frame(right_panel, bg='#1E90FF')
        card_frame.pack(fill='x', padx=40, pady=20)
        
        # Card ID input (hidden for RFID keyboard input)
        self.card_entry = tk.Entry(
            card_frame,
            textvariable=self.card_input_var,
            font=('Arial', 14),
            width=15,
            relief='solid',
            bd=1,
            show='*'  # Hide the input for security
        )
        self.card_entry.pack(anchor='w', pady=(5, 10))
        self.card_entry.focus()
        
        # Bind events for automatic RFID processing
        self.card_entry.bind('<KeyRelease>', self.on_rfid_input)
        self.card_entry.bind('<Return>', self.process_card)
        
        # Status label
        self.status_label = tk.Label(
            card_frame,
            text="Ready for card tap...",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#1E90FF'
        )
        self.status_label.pack(anchor='w', pady=(5, 10))
        
        # Manual entry button (for testing)
        manual_button = tk.Button(
            card_frame,
            text="Enter",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#42BE40',
            relief='flat',
            bd=0,
            padx=15,
            pady=5,
            cursor='hand2',
            command=self.process_card
        )
        manual_button.pack(anchor='w')
    
    def create_footer(self, button_type):
        """Create the footer bar with time, date, and button"""
        footer_frame = tk.Frame(self.content_frame, bg='white')
        footer_frame.pack(side='bottom', fill='x')
        
        # Time section (light blue)
        time_frame = tk.Frame(footer_frame, bg='#ADD8E6', height=50)
        time_frame.pack(side='left', fill='x', expand=True)
        time_frame.pack_propagate(False)
        
        self.time_label = tk.Label(
            time_frame,
            text="",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#ADD8E6'
        )
        self.time_label.pack(expand=True)
        
        # Date section (dark blue)
        date_frame = tk.Frame(footer_frame, bg='#003366', height=50)
        date_frame.pack(side='left', fill='x', expand=True)
        date_frame.pack_propagate(False)
        
        self.date_label = tk.Label(
            date_frame,
            text="",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#003366'
        )
        self.date_label.pack(expand=True)
        
        # Button section (orange)
        button_frame = tk.Frame(footer_frame, bg='#FF8C00', height=50)
        button_frame.pack(side='left', fill='x', expand=True)
        button_frame.pack_propagate(False)
        
        if button_type == "quit":
            button_text = "Quit"
            button_command = self.quit_action
        elif button_type == "logout":
            button_text = "Log out"
            button_command = self.logout_action
        else:  # back
            button_text = "Back"
            button_command = self.back_action
        
        button = tk.Label(
            button_frame,
            text=button_text,
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#FF8C00',
            cursor='hand2'
        )
        button.pack(expand=True)
        button.bind('<Button-1>', button_command)
    
    def update_time(self):
        """Update the time and date display"""
        if self.time_label and self.date_label:
            now = datetime.now()
            
            # Format time (12-hour format with am/pm)
            time_str = now.strftime("%I:%M:%S %p").lower()
            self.time_label.config(text=time_str)
            
            # Format date
            date_str = now.strftime("%B %d, %Y")
            self.date_label.config(text=date_str)
        
        # Update every second
        self.root.after(1000, self.update_time)
    
    def on_rfid_input(self, event=None):
        """Handle automatic RFID keyboard input"""
        if self.is_processing:
            return  # Prevent duplicate processing
        
        card_id = self.card_input_var.get().strip()
        
        # Check if we have a complete RFID code (typically 10 digits)
        if len(card_id) >= 10:
            self.is_processing = True
            # Update status
            self.status_label.config(text="Processing card...")
            self.root.update()
            
            # Process the card after a short delay to ensure complete input
            self.root.after(100, self.process_card)
    
    def process_card(self, event=None):
        """Process the card tap"""
        if not self.is_processing:
            return  # Prevent duplicate processing from Enter key
        
        card_id = self.card_input_var.get().strip()
        
        if not card_id:
            self.is_processing = False
            return
        
        # Update status
        self.status_label.config(text="Validating access...")
        self.root.update()
        
        # Log the access attempt
        self.db_manager.log_access(card_id, "TAP")
        
        # Find the person in database
        person = self.db_manager.find_person(card_id)
        
        if person:
            if person['role'] == 'GUARD':
                # Guard access granted - show new splash screen
                self.status_label.config(text=f"Welcome Guard {person['name']} - ACCESS GRANTED", fg='green')
                # Clear the input field
                self.card_input_var.set("")
                # Show guard splash screen after 2 seconds
                self.root.after(2000, self.show_guard_splash_screen)
            elif person['role'] == 'SPECIAL':
                # Special pass access denied on turnstile screen
                self.status_label.config(text=f"Special Pass {person['name']} - ACCESS DENIED", fg='red')
                # Clear the input field and reset after delay
                self.card_input_var.set("")
                # Reset status and processing flag after 3 seconds
                self.root.after(3000, self.reset_status)
                # Refocus the entry field for next card
                if self.card_entry and self.current_screen == "turnstile":
                    self.card_entry.focus()
            else:
                # Student access denied
                self.status_label.config(text=f"Student {person['name']} - ACCESS DENIED", fg='red')
                # Clear the input field and reset after delay
                self.card_input_var.set("")
                # Reset status and processing flag after 3 seconds
                self.root.after(3000, self.reset_status)
                # Refocus the entry field for next card
                if self.card_entry and self.current_screen == "turnstile":
                    self.card_entry.focus()
        else:
            # Show access denied status (no message box)
            self.status_label.config(text=f"Card {card_id} - ACCESS DENIED", fg='red')
            # Clear the input field and reset after delay
            self.card_input_var.set("")
            # Reset status and processing flag after 3 seconds
            self.root.after(3000, self.reset_status)
            # Refocus the entry field for next card
            if self.card_entry and self.current_screen == "turnstile":
                self.card_entry.focus()
    
    def reset_status(self):
        """Reset the status and processing flag"""
        self.status_label.config(text="Ready for card tap...", fg='white')
        self.is_processing = False
    
    def show_guard_splash_screen(self):
        """Show the guard splash screen"""
        self.current_screen = "guard_splash"
        self.clear_content()
        
        # Top banner (orange)
        self.create_top_banner()
        
        # Main content area
        self.create_guard_main_content()
        
        # Footer bar
        self.create_footer("logout")
    
    def create_guard_main_content(self):
        """Create the main content area for guard splash screen"""
        content_area = tk.Frame(self.content_frame, bg='white')
        content_area.pack(fill='both', expand=True)
        
        # Left side (white panel with AI-niform logo)
        left_panel = tk.Frame(content_area, bg='white')
        left_panel.pack(side='left', fill='both', expand=True)
        
        # AI-niform logo
        logo_frame = tk.Frame(left_panel, bg='white')
        logo_frame.pack(expand=True)
        
        # AI-niform text
        ai_text = tk.Label(
            logo_frame,
            text="AI-",
            font=('Arial', 48, 'bold'),
            fg='#007BFF',  # Bright blue
            bg='white'
        )
        ai_text.pack(side='left')
        
        niform_text = tk.Label(
            logo_frame,
            text="niform",
            font=('Arial', 48, 'bold'),
            fg='#212529',  # Dark blue/black
            bg='white'
        )
        niform_text.pack(side='left')
        
        # Right side (blue panel with options)
        right_panel = tk.Frame(content_area, bg='#1E90FF', width=400)
        right_panel.pack(side='right', fill='y')
        right_panel.pack_propagate(False)
        
        # Content frame for right panel
        content_frame = tk.Frame(right_panel, bg='#1E90FF')
        content_frame.pack(expand=True, padx=40, pady=40)
        
        # Awaiting ID card scan text
        awaiting_label = tk.Label(
            content_frame,
            text="Awaiting ID card scan.",
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#1E90FF'
        )
        awaiting_label.pack(anchor='w', pady=(0, 30))
        
        # Visitor button
        visitor_button = tk.Button(
            content_frame,
            text="Visitor",
            font=('Arial', 18, 'bold'),
            fg='black',
            bg='#FFD700',  # Yellow
            relief='flat',
            bd=0,
            padx=40,
            pady=15,
            cursor='hand2',
            command=self.visitor_action
        )
        visitor_button.pack(fill='x', pady=(0, 15))
        
        # Student button
        student_button = tk.Button(
            content_frame,
            text="Student",
            font=('Arial', 18, 'bold'),
            fg='black',
            bg='#FFD700',  # Yellow
            relief='flat',
            bd=0,
            padx=40,
            pady=15,
            cursor='hand2',
            command=self.student_action
        )
        student_button.pack(fill='x', pady=(0, 30))
        
        # Guard in-charge section
        guard_frame = tk.Frame(content_frame, bg='#1E90FF')
        guard_frame.pack(fill='x')
        
        guard_label = tk.Label(
            guard_frame,
            text="Guard in-charge:",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#1E90FF'
        )
        guard_label.pack(anchor='w')
        
        guard_name_label = tk.Label(
            guard_frame,
            text="John Jason Domingo",
            font=('Arial', 12),
            fg='white',
            bg='#1E90FF'
        )
        guard_name_label.pack(anchor='w')
    
    def visitor_action(self):
        """Handle visitor button click"""
        messagebox.showinfo("Visitor", "Visitor registration would be implemented here!")
    
    def student_action(self):
        """Handle student button click"""
        messagebox.showinfo("Student", "Student registration would be implemented here!")
    
    def logout_action(self, event=None):
        """Handle logout button click"""
        result = messagebox.askyesno("Confirm Logout", "Are you sure you want to log out?")
        if result:
            self.show_login_screen()
    
    def back_action(self, event=None):
        """Handle back button click"""
        result = messagebox.askyesno("Confirm Exit", "Are you sure you want to go back to login?")
        if result:
            self.show_login_screen()
    
    def quit_action(self, event=None):
        """Handle quit button click"""
        result = messagebox.askyesno("Confirm Exit", "Are you sure you want to quit AI-niform?")
        if result:
            self.root.quit()

def main():
    """Main function"""
    root = tk.Tk()
    app = AINiformApp(root)
    
    # Center the window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main() 