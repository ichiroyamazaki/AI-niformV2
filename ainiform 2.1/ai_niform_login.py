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
from PIL import Image, ImageTk
import os

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
        self.current_guard = None  # Store current guard information
        self.last_response_message = ""  # Message to show on guard splash right panel
        self.guard_message_label = None  # Reference to splash message label for updates
        self.message_reset_after_id = None  # Timer handle for auto-clearing panel message
        self.guard_student_inline_var = None  # Guard splash student ID var
        self.visitor_student_inline_var = None  # Visitor form student ID var
        
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
        
        # Guard ID label and input frame
        guard_input_frame = tk.Frame(card_frame, bg='#1E90FF')
        guard_input_frame.pack(anchor='w', pady=(5, 10))
        
        # Guard ID label
        guard_id_label = tk.Label(
            guard_input_frame,
            text="Guard ID: ",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#1E90FF'
        )
        guard_id_label.pack(side='left')
        
        # Card ID input (hidden for RFID keyboard input)
        self.card_entry = tk.Entry(
            guard_input_frame,
            textvariable=self.card_input_var,
            font=('Arial', 14),
            width=15,
            relief='solid',
            bd=1,
            show='*'  # Hide the input for security
        )
        self.card_entry.pack(side='left')
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
    
    def create_footer(self, button_type):
        """Create the footer bar with time, date, and button"""
        footer_frame = tk.Frame(self.content_frame, bg='white')
        footer_frame.pack(side='bottom', fill='x')
        
        # Time section (light blue)
        time_frame = tk.Frame(footer_frame, bg='#12A7FB', height=50)
        time_frame.pack(side='left', fill='x', expand=True)
        time_frame.pack_propagate(False)
        
        self.time_label = tk.Label(
            time_frame,
            text="",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#12A7FB'
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
        
        # Button section (orange) - fixed width to align with right panel
        button_frame = tk.Frame(footer_frame, bg='#FF8C00', height=50, width=400)
        button_frame.pack(side='right')
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
                # Store current guard information
                self.current_guard = person
                # Guard access granted - show new splash screen
                self.status_label.config(text="ACCESS GRANTED", fg='green')
                # Clear the input field
                self.card_input_var.set("")
                # Show guard splash screen after 2 seconds
                self.root.after(2000, self.show_guard_splash_screen)
                # Clear any previous message after showing success
                self.last_response_message = ""
            elif person['role'] == 'SPECIAL':
                # Special pass access denied on turnstile screen
                self.status_label.config(text="ACCESS DENIED", fg='red')
                self.last_response_message = "Unknown / Invalid ID has been scanned."
                # Clear the input field and reset after delay
                self.card_input_var.set("")
                # Reset status and processing flag after 3 seconds
                self.root.after(3000, self.reset_status)
                # Refocus the entry field for next card
                if self.card_entry and self.current_screen == "turnstile":
                    self.card_entry.focus()
            else:
                # Student access denied
                self.status_label.config(text="ACCESS DENIED", fg='red')
                # Clear the input field and reset after delay
                self.card_input_var.set("")
                # Reset status and processing flag after 3 seconds
                self.root.after(3000, self.reset_status)
                # Refocus the entry field for next card
                if self.card_entry and self.current_screen == "turnstile":
                    self.card_entry.focus()
        else:
            # Show access denied status (no message box)
            self.status_label.config(text="ACCESS DENIED", fg='red')
            self.last_response_message = "Unknown / Invalid ID has been scanned."
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
        
        # Schedule auto-clear of any prior message to default after 5 seconds
        if self.last_response_message:
            if self.message_reset_after_id is not None:
                try:
                    self.root.after_cancel(self.message_reset_after_id)
                except Exception:
                    pass
            self.message_reset_after_id = self.root.after(5000, self.reset_guard_message)
    
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
        
        # Message area (shows last response or default text)
        message_text = self.last_response_message if self.last_response_message else "Awaiting ID card scan."
        self.guard_message_label = tk.Label(
            content_frame,
            text=message_text,
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#1E90FF'
        )
        self.guard_message_label.pack(anchor='w', pady=(0, 30))
        
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

        
        
        # ID Number inline textbox (guard splash)
        inline_student_label = tk.Label(
            content_frame,
            text="ID Number:",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#1E90FF'
        )
        inline_student_label.pack(anchor='w')
        
        self.guard_student_inline_var = tk.StringVar()
        inline_student_entry = tk.Entry(
            content_frame,
            textvariable=self.guard_student_inline_var,
            font=('Arial', 14),
            width=20,
            relief='solid',
            bd=1
        )
        inline_student_entry.pack(fill='x', pady=(0, 15))
        inline_student_entry.bind('<Return>', self.submit_student_inline)
        inline_student_entry.bind('<KeyRelease>', self.on_rfid_input_inline)
        
        # Focus on the inline textbox for immediate RFID input
        inline_student_entry.focus()
        
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
        
        # Get guard name from stored information or use default
        guard_name = self.current_guard['name'] if self.current_guard else "Unknown Guard"
        
        guard_name_label = tk.Label(
            guard_frame,
            text=guard_name,
            font=('Arial', 12),
            fg='white',
            bg='#1E90FF'
        )
        guard_name_label.pack(anchor='w')
    
    def visitor_action(self):
        """Handle visitor button click"""
        self.show_visitor_form_screen()
    
    def show_visitor_form_screen(self):
        """Show the visitor form screen"""
        self.current_screen = "visitor_form"
        self.clear_content()
        
        # Top banner (orange)
        self.create_top_banner()
        
        # Main content area (with reduced expansion to leave space for footer)
        content_area = tk.Frame(self.content_frame, bg='white')
        content_area.pack(fill='both', expand=True, pady=(0, 10))  # Minimal space for footer
        
        # Create visitor form content within the content area
        self.create_visitor_form_content(content_area)
        
        # Footer bar
        self.create_footer("back")
    
    def create_visitor_form_content(self, content_area):
        """Create the visitor form content within the provided content area"""
        
        # Left side (white panel with visitor form)
        left_panel = tk.Frame(content_area, bg='white')
        left_panel.pack(side='left', fill='both', expand=True)
        
        # Create a canvas with scrollbar for the form
        canvas = tk.Canvas(left_panel, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Unbind mouse wheel when leaving the canvas
        def _on_leave(event):
            canvas.unbind_all("<MouseWheel>")
        
        def _on_enter(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.bind("<Enter>", _on_enter)
        canvas.bind("<Leave>", _on_leave)
        
        # Visitor form section
        form_frame = tk.Frame(scrollable_frame, bg='white')
        form_frame.pack(expand=True, padx=50, pady=30)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Form title
        title_label = tk.Label(
            form_frame,
            text="Visitor Registration Form",
            font=('Arial', 20, 'bold'),
            fg='black',
            bg='white'
        )
        title_label.pack(pady=(0, 30))
        
        # Initialize form variables
        self.visitor_name_var = tk.StringVar()
        self.visitor_contact_var = tk.StringVar()
        self.visitor_type_var = tk.StringVar()
        self.visitor_purpose_var = tk.StringVar()
        self.visitor_visiting_var = tk.StringVar()
        self.visitor_id_type_var = tk.StringVar()
        self.visitor_special_pass_var = tk.StringVar()
        
        # Full Name
        name_label = tk.Label(form_frame, text="Full Name:", font=('Arial', 12, 'bold'), fg='black', bg='white')
        name_label.pack(anchor='w', pady=(0, 5))
        name_entry = tk.Entry(form_frame, textvariable=self.visitor_name_var, font=('Arial', 12), 
                             width=40, relief='solid', bd=1, bg='#f0f0f0')
        name_entry.pack(fill='x', pady=(0, 15))
        
        # Contact Number
        contact_label = tk.Label(form_frame, text="Contact Number:", font=('Arial', 12, 'bold'), fg='black', bg='white')
        contact_label.pack(anchor='w', pady=(0, 5))
        contact_entry = tk.Entry(form_frame, textvariable=self.visitor_contact_var, font=('Arial', 12), 
                                width=40, relief='solid', bd=1, bg='#f0f0f0')
        contact_entry.pack(fill='x', pady=(0, 15))
        
        # Visiting as
        visiting_as_label = tk.Label(form_frame, text="Visiting as:", font=('Arial', 12, 'bold'), fg='black', bg='white')
        visiting_as_label.pack(anchor='w', pady=(0, 5))
        visiting_as_combo = ttk.Combobox(form_frame, textvariable=self.visitor_type_var, 
                                        values=["Guest", "Contractor", "Vendor", "Official Visitor", "Other"], 
                                        state="readonly", width=37)
        visiting_as_combo.pack(fill='x', pady=(0, 15))
        
        # Purpose of Visit
        purpose_label = tk.Label(form_frame, text="Purpose of Visit:", font=('Arial', 12, 'bold'), fg='black', bg='white')
        purpose_label.pack(anchor='w', pady=(0, 5))
        purpose_entry = tk.Entry(form_frame, textvariable=self.visitor_purpose_var, font=('Arial', 12), 
                                width=40, relief='solid', bd=1, bg='#f0f0f0')
        purpose_entry.pack(fill='x', pady=(0, 15))
        
        # Who are you visiting
        visiting_label = tk.Label(form_frame, text="Who are you visiting?:", font=('Arial', 12, 'bold'), fg='black', bg='white')
        visiting_label.pack(anchor='w', pady=(0, 5))
        visiting_entry = tk.Entry(form_frame, textvariable=self.visitor_visiting_var, font=('Arial', 12), 
                                 width=40, relief='solid', bd=1, bg='#f0f0f0')
        visiting_entry.pack(fill='x', pady=(0, 15))
        
        # Type of Valid ID
        id_type_label = tk.Label(form_frame, text="Type of Valid ID:", font=('Arial', 12, 'bold'), fg='black', bg='white')
        id_type_label.pack(anchor='w', pady=(0, 5))
        id_type_combo = ttk.Combobox(form_frame, textvariable=self.visitor_id_type_var, 
                                    values=["Driver's License", "Passport", "National ID", "Company ID", "Other"], 
                                    state="readonly", width=37)
        id_type_combo.pack(fill='x', pady=(0, 15))
        
        # Special Pass ID
        special_pass_label = tk.Label(form_frame, text="Special Pass ID:", font=('Arial', 12, 'bold'), fg='black', bg='white')
        special_pass_label.pack(anchor='w', pady=(0, 5))
        special_pass_entry = tk.Entry(form_frame, textvariable=self.visitor_special_pass_var, 
                                     font=('Arial', 12), width=37, relief='solid', bd=1)
        special_pass_entry.pack(fill='x', pady=(0, 30))
        
        # Submit button
        submit_button = tk.Button(
            form_frame,
            text="Submit",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#007BFF',  # Blue
            relief='flat',
            bd=0,
            padx=40,
            pady=10,
            cursor='hand2',
            command=self.submit_visitor
        )
        submit_button.pack(anchor='e')
        
        # Right side (blue panel with options)
        right_panel = tk.Frame(content_area, bg='#1E90FF', width=400)
        right_panel.pack(side='right', fill='y')
        right_panel.pack_propagate(False)
        
        # Content frame for right panel
        content_frame = tk.Frame(right_panel, bg='#1E90FF')
        content_frame.pack(expand=True, padx=40, pady=40)
        
        # Right panel message area (shared behavior)
        right_message_text = self.last_response_message if self.last_response_message else "Awaiting ID card scan."
        self.guard_message_label = tk.Label(
            content_frame,
            text=right_message_text,
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#1E90FF'
        )
        self.guard_message_label.pack(anchor='w', pady=(0, 30))
        
        # Visitor button (bright yellow)
        visitor_button = tk.Button(
            content_frame,
            text="Visitor",
            font=('Arial', 18, 'bold'),
            fg='black',
            bg='#FFD700',  # Bright yellow
            relief='flat',
            bd=0,
            padx=40,
            pady=15,
            cursor='hand2',
            command=self.visitor_action
        )
        visitor_button.pack(fill='x', pady=(0, 15))
        
        # Student button (light grey)
        student_button = tk.Button(
            content_frame,
            text="Student",
            font=('Arial', 18, 'bold'),
            fg='black',
            bg='#d3d3d3',  # Light grey
            relief='flat',
            bd=0,
            padx=40,
            pady=15,
            cursor='hand2',
            command=self.student_action
        )
        student_button.pack(fill='x', pady=(0, 30))
        
        # ID Number inline textbox on visitor form right panel
        inline_student_label = tk.Label(
            content_frame,
            text="ID Number:",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#1E90FF'
        )
        inline_student_label.pack(anchor='w')
        
        self.visitor_student_inline_var = tk.StringVar()
        inline_student_entry = tk.Entry(
            content_frame,
            textvariable=self.visitor_student_inline_var,
            font=('Arial', 14),
            width=20,
            relief='solid',
            bd=1
        )
        inline_student_entry.pack(fill='x', pady=(0, 15))
        inline_student_entry.bind('<Return>', self.submit_student_inline)
        inline_student_entry.bind('<KeyRelease>', self.on_rfid_input_inline)
        
        # Focus on the inline textbox for immediate RFID input
        inline_student_entry.focus()
        
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
        
        # Get guard name from stored information or use default
        guard_name = self.current_guard['name'] if self.current_guard else "Unknown Guard"
        
        guard_name_label = tk.Label(
            guard_frame,
            text=guard_name,
            font=('Arial', 12),
            fg='white',
            bg='#1E90FF'
        )
        guard_name_label.pack(anchor='w')
    
    def submit_visitor(self):
        """Handle visitor form submission"""
        # Get form data
        name = self.visitor_name_var.get().strip()
        contact = self.visitor_contact_var.get().strip()
        visiting_as = self.visitor_type_var.get()
        purpose = self.visitor_purpose_var.get().strip()
        visiting = self.visitor_visiting_var.get().strip()
        id_type = self.visitor_id_type_var.get()
        special_pass = self.visitor_special_pass_var.get()  # This will contain the special pass ID if tapped
        
        # Validate required fields
        if not name or not contact or not visiting_as or not purpose or not visiting or not id_type:
            messagebox.showwarning("Missing Information", "Please fill in all required fields")
            return
        
        # Check if special pass ID is already in use
        if special_pass and special_pass.strip():
            is_in_use, existing_visitor = self.db_manager.is_special_pass_in_use(special_pass)
            if is_in_use:
                # Show error splash screen
                self.show_visitor_error_screen(special_pass, existing_visitor['name'], existing_visitor['expires_at'])
                return
        
        # Generate unique visitor ID
        import uuid
        visitor_id = str(uuid.uuid4())[:8].upper()
        
        # Get current timestamp
        from datetime import datetime, timedelta
        current_time = datetime.now()
        expiry_time = current_time + timedelta(hours=24)
        
        # Create visitor record
        visitor_data = {
            'id': visitor_id,
            'name': name,
            'contact': contact,
            'visiting_as': visiting_as,
            'purpose': purpose,
            'visiting': visiting,
            'id_type': id_type,
            'special_pass': special_pass,
            'created_at': current_time.strftime("%Y-%m-%d %H:%M:%S"),
            'expires_at': expiry_time.strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'ACTIVE'
        }
        
        # Save to database
        success = self.db_manager.add_visitor(visitor_data)
        
        if success:
            # Log the visitor entry
            self.db_manager.log_access(visitor_id, "VISITOR_REGISTRATION")
            
            # Show success splash screen
            self.show_visitor_success_screen(visitor_id, name, expiry_time.strftime('%Y-%m-%d %H:%M:%S'))
        else:
            messagebox.showerror("Registration Failed", "Failed to register visitor. Please try again.")
    

    
    def show_visitor_success_screen(self, visitor_id, visitor_name, expiry_time):
        """Show visitor registration success splash screen"""
        self.current_screen = "visitor_success"
        self.clear_content()
        
        # Top banner (orange)
        self.create_top_banner()
        
        # Main content area
        content_area = tk.Frame(self.content_frame, bg='white')
        content_area.pack(fill='both', expand=True)
        
        # Left side (white panel with success message)
        left_panel = tk.Frame(content_area, bg='white')
        left_panel.pack(side='left', fill='both', expand=True)
        
        # Success message frame
        success_frame = tk.Frame(left_panel, bg='white')
        success_frame.pack(expand=True)
        
        # INFORMATION LINKED text
        info_linked_label = tk.Label(
            success_frame,
            text="INFORMATION LINKED",
            font=('Arial', 36, 'bold'),
            fg='#28a745',  # Green
            bg='white'
        )
        info_linked_label.pack(pady=(0, 20))
        
        # Special Pass ready message
        pass_ready_label = tk.Label(
            success_frame,
            text=f"Special Pass No. {visitor_id} is ready to use",
            font=('Arial', 16),
            fg='black',
            bg='white'
        )
        pass_ready_label.pack(pady=(0, 40))
        
        # OK button
        ok_button = tk.Button(
            success_frame,
            text="OK",
            font=('Arial', 18, 'bold'),
            fg='white',
            bg='#007BFF',  # Blue
            relief='flat',
            bd=0,
            padx=60,
            pady=15,
            cursor='hand2',
            command=self.visitor_success_ok_action
        )
        ok_button.pack()
        
        # Right side (blue panel with options)
        right_panel = tk.Frame(content_area, bg='#1E90FF', width=400)
        right_panel.pack(side='right', fill='y')
        right_panel.pack_propagate(False)
        
        # Content frame for right panel
        content_frame = tk.Frame(right_panel, bg='#1E90FF')
        content_frame.pack(expand=True, padx=40, pady=40)
        
        # Right panel message area (shared behavior)
        right_message_text = self.last_response_message if self.last_response_message else "Awaiting ID card scan."
        self.guard_message_label = tk.Label(
            content_frame,
            text=right_message_text,
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#1E90FF'
        )
        self.guard_message_label.pack(anchor='w', pady=(0, 30))
        
        # Visitor button (bright yellow)
        visitor_button = tk.Button(
            content_frame,
            text="Visitor",
            font=('Arial', 18, 'bold'),
            fg='black',
            bg='#FFD700',  # Bright yellow
            relief='flat',
            bd=0,
            padx=40,
            pady=15,
            cursor='hand2',
            command=self.visitor_action
        )
        visitor_button.pack(fill='x', pady=(0, 15))
        
        # Student button (light grey)
        student_button = tk.Button(
            content_frame,
            text="Student",
            font=('Arial', 18, 'bold'),
            fg='black',
            bg='#d3d3d3',  # Light grey
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
        
        # Get guard name from stored information or use default
        guard_name = self.current_guard['name'] if self.current_guard else "Unknown Guard"
        
        guard_name_label = tk.Label(
            guard_frame,
            text=guard_name,
            font=('Arial', 12),
            fg='white',
            bg='#1E90FF'
        )
        guard_name_label.pack(anchor='w')
        
        # Footer bar
        self.create_footer("back")
    
    def show_visitor_error_screen(self, special_pass_id, visitor_name, expires_at):
        """Show visitor registration error splash screen"""
        self.current_screen = "visitor_error"
        self.clear_content()
        
        # Top banner (orange)
        self.create_top_banner()
        
        # Main content area
        content_area = tk.Frame(self.content_frame, bg='white')
        content_area.pack(fill='both', expand=True)
        
        # Left side (white panel with error message)
        left_panel = tk.Frame(content_area, bg='white')
        left_panel.pack(side='left', fill='both', expand=True)
        
        # Error message frame
        error_frame = tk.Frame(left_panel, bg='white')
        error_frame.pack(expand=True)
        
        # ERROR text
        error_label = tk.Label(
            error_frame,
            text="ERROR",
            font=('Arial', 36, 'bold'),
            fg='#dc3545',  # Red
            bg='white'
        )
        error_label.pack(pady=(0, 20))
        
        # Special Pass active message
        pass_active_label = tk.Label(
            error_frame,
            text=f"Special Pass No. {special_pass_id} is currently active",
            font=('Arial', 16),
            fg='black',
            bg='white'
        )
        pass_active_label.pack(pady=(0, 10))
        
        # Wait 24 hours message
        wait_message_label = tk.Label(
            error_frame,
            text="Please wait 24 hours after its submission before resubmitting.",
            font=('Arial', 14),
            fg='black',
            bg='white'
        )
        wait_message_label.pack(pady=(0, 40))
        
        # OK button
        ok_button = tk.Button(
            error_frame,
            text="OK",
            font=('Arial', 18, 'bold'),
            fg='white',
            bg='#007BFF',  # Blue
            relief='flat',
            bd=0,
            padx=60,
            pady=15,
            cursor='hand2',
            command=self.visitor_error_ok_action
        )
        ok_button.pack()
        
        # Right side (blue panel with options)
        right_panel = tk.Frame(content_area, bg='#1E90FF', width=400)
        right_panel.pack(side='right', fill='y')
        right_panel.pack_propagate(False)
        
        # Content frame for right panel
        content_frame = tk.Frame(right_panel, bg='#1E90FF')
        content_frame.pack(expand=True, padx=40, pady=40)
        
        # Right panel message area (shared behavior)
        right_message_text = self.last_response_message if self.last_response_message else "Awaiting ID card scan."
        self.guard_message_label = tk.Label(
            content_frame,
            text=right_message_text,
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#1E90FF'
        )
        self.guard_message_label.pack(anchor='w', pady=(0, 30))
        
        # Visitor button (bright yellow)
        visitor_button = tk.Button(
            content_frame,
            text="Visitor",
            font=('Arial', 18, 'bold'),
            fg='black',
            bg='#FFD700',  # Bright yellow
            relief='flat',
            bd=0,
            padx=40,
            pady=15,
            cursor='hand2',
            command=self.visitor_action
        )
        visitor_button.pack(fill='x', pady=(0, 15))
        
        # Student button (light grey)
        student_button = tk.Button(
            content_frame,
            text="Student",
            font=('Arial', 18, 'bold'),
            fg='black',
            bg='#d3d3d3',  # Light grey
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
        
        # Get guard name from stored information or use default
        guard_name = self.current_guard['name'] if self.current_guard else "Unknown Guard"
        
        guard_name_label = tk.Label(
            guard_frame,
            text=guard_name,
            font=('Arial', 12),
            fg='white',
            bg='#1E90FF'
        )
        guard_name_label.pack(anchor='w')
        
        # Footer bar
        self.create_footer("back")
    
    def visitor_success_ok_action(self):
        """Handle OK button click on visitor success screen"""
        # Clear form
        self.clear_visitor_form()
        # Return to guard splash screen
        self.show_guard_splash_screen()
    
    def visitor_error_ok_action(self):
        """Handle OK button click on visitor error screen"""
        # Return to visitor form screen
        self.show_visitor_form_screen()
    
    def clear_visitor_form(self):
        """Clear the visitor form fields"""
        self.visitor_name_var.set("")
        self.visitor_contact_var.set("")
        self.visitor_type_var.set("")
        self.visitor_purpose_var.set("")
        self.visitor_visiting_var.set("")
        self.visitor_id_type_var.set("")
        self.visitor_special_pass_var.set("")
    
    def student_action(self):
        """Handle student button click"""
        self.show_student_entry_screen()
    
    def show_student_entry_screen(self):
        """Show the student number entry screen"""
        self.current_screen = "student_entry"
        self.clear_content()
        
        # Top banner (orange)
        self.create_top_banner()
        
        # Main content area
        self.create_student_main_content()
        
        # Footer bar
        self.create_footer("back")
    
    def create_student_main_content(self):
        """Create the main content area for student entry screen"""
        content_area = tk.Frame(self.content_frame, bg='white')
        content_area.pack(fill='both', expand=True)
        
        # Left side (white panel with student entry)
        left_panel = tk.Frame(content_area, bg='white')
        left_panel.pack(side='left', fill='both', expand=True)
        
        # Student entry section
        entry_frame = tk.Frame(left_panel, bg='white')
        entry_frame.pack(expand=True)
        
        # "Enter the ID Number:" text
        student_label = tk.Label(
            entry_frame,
            text="Enter the ID Number:",
            font=('Arial', 24, 'bold'),
            fg='black',
            bg='white'
        )
        student_label.pack(pady=(0, 20))
        
        # ID number input
        self.student_number_var = tk.StringVar()
        student_entry = tk.Entry(
            entry_frame,
            textvariable=self.student_number_var,
            font=('Arial', 18),
            width=20,
            relief='solid',
            bd=1,
            bg='#f0f0f0'  # Light grey background
        )
        student_entry.pack(pady=(0, 20))
        student_entry.focus()
        student_entry.bind('<Return>', self.submit_student)
        student_entry.bind('<KeyRelease>', self.on_rfid_input_main)
        
        # Submit button
        submit_button = tk.Button(
            entry_frame,
            text="Submit",
            font=('Arial', 16, 'bold'),
            fg='white',
            bg='#007BFF',  # Blue
            relief='flat',
            bd=0,
            padx=40,
            pady=10,
            cursor='hand2',
            command=self.submit_student
        )
        submit_button.pack()
        
        # Right side (blue panel with options)
        right_panel = tk.Frame(content_area, bg='#1E90FF', width=400)
        right_panel.pack(side='right', fill='y')
        right_panel.pack_propagate(False)
        
        # Content frame for right panel
        content_frame = tk.Frame(right_panel, bg='#1E90FF')
        content_frame.pack(expand=True, padx=40, pady=40)
        
        # Right panel message area (shared behavior)
        right_message_text = self.last_response_message if self.last_response_message else "Awaiting ID card scan."
        self.guard_message_label = tk.Label(
            content_frame,
            text=right_message_text,
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#1E90FF'
        )
        self.guard_message_label.pack(anchor='w', pady=(0, 30))
        
        # Visitor button (light grey)
        visitor_button = tk.Button(
            content_frame,
            text="Visitor",
            font=('Arial', 18, 'bold'),
            fg='black',
            bg='#d3d3d3',  # Light grey
            relief='flat',
            bd=0,
            padx=40,
            pady=15,
            cursor='hand2',
            command=self.visitor_action
        )
        visitor_button.pack(fill='x', pady=(0, 15))
        
        # Student button (bright yellow)
        student_button = tk.Button(
            content_frame,
            text="Student",
            font=('Arial', 18, 'bold'),
            fg='black',
            bg='#FFD700',  # Bright yellow
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
        
        # Get guard name from stored information or use default
        guard_name = self.current_guard['name'] if self.current_guard else "Unknown Guard"
        
        guard_name_label = tk.Label(
            guard_frame,
            text=guard_name,
            font=('Arial', 12),
            fg='white',
            bg='#1E90FF'
        )
        guard_name_label.pack(anchor='w')
    
    def show_student_info_screen(self, student_data):
        """Show the student information screen with photo and details"""
        self.current_screen = "student_info"
        self.clear_content()
        
        # Top banner (orange)
        self.create_top_banner()
        
        # Main content area
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
            fg='#1E90FF',  # Blue
            bg='white'
        )
        ai_text.pack(side='left')
        
        niform_text = tk.Label(
            logo_frame,
            text="niform",
            font=('Arial', 48, 'bold'),
            fg='#000080',  # Dark blue
            bg='white'
        )
        niform_text.pack(side='left')
        
        # Right side (blue panel with student info)
        right_panel = tk.Frame(content_area, bg='#1E90FF', width=400)
        right_panel.pack(side='right', fill='both', expand=False)
        right_panel.pack_propagate(False)
        
        # Currently in-queue section
        queue_label = tk.Label(
            right_panel,
            text="Currently in-queue:",
            font=('Arial', 16, 'bold'),
            fg='white',
            bg='#1E90FF'
        )
        queue_label.pack(anchor='w', padx=20, pady=(20, 15))
        
        # Student photo and info frame
        student_info_frame = tk.Frame(right_panel, bg='#1E90FF')
        student_info_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        # Try to load student photo from database
        image_filename = student_data.get('image_path', 'images.jpg')  # Default to images.jpg if no path specified
        photo_path = os.path.join("/Users/ichiroyamazaki/Desktop/ainiform/id-image", image_filename)
        if os.path.exists(photo_path):
            try:
                # Load and resize image
                image = Image.open(photo_path)
                resized_image = image.resize((80, 80), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(resized_image)
                
                # Create circular photo frame
                photo_frame = tk.Frame(student_info_frame, bg='#1E90FF')
                photo_frame.pack(anchor='w', pady=(0, 10))
                
                photo_label = tk.Label(photo_frame, image=photo, bg='#1E90FF')
                photo_label.image = photo  # Keep a reference
                photo_label.pack()
            except Exception as e:
                print(f"Error loading image: {e}")
                # Create placeholder if image fails to load
                photo_label = tk.Label(student_info_frame, text="[Photo]", font=('Arial', 12), fg='white', bg='#1E90FF')
                photo_label.pack(anchor='w', pady=(0, 10))
        else:
            # Create placeholder if image doesn't exist
            photo_label = tk.Label(student_info_frame, text="[Photo]", font=('Arial', 12), fg='white', bg='#1E90FF')
            photo_label.pack(anchor='w', pady=(0, 10))
        
        # Student name (formatted as "Last, First M.")
        student_name = student_data.get('name', 'Unknown')
        # Split name and format as "Last, First M."
        name_parts = student_name.split()
        if len(name_parts) >= 2:
            formatted_name = f"{name_parts[-1]}, {' '.join(name_parts[:-1])}"
        else:
            formatted_name = student_name
            
        name_label = tk.Label(
            student_info_frame,
            text=formatted_name,
            font=('Arial', 18, 'bold'),
            fg='white',
            bg='#1E90FF'
        )
        name_label.pack(anchor='w', pady=(0, 5))
        
        # Student role
        role_label = tk.Label(
            student_info_frame,
            text="(Student)",
            font=('Arial', 14),
            fg='white',
            bg='#1E90FF'
        )
        role_label.pack(anchor='w', pady=(0, 10))
        
        # Time check-in
        current_time = datetime.now().strftime("%I:%M:%S %p")
        time_label = tk.Label(
            student_info_frame,
            text=f"Time Check-in: {current_time}",
            font=('Arial', 12),
            fg='white',
            bg='#1E90FF'
        )
        time_label.pack(anchor='w', pady=(0, 15))
        
        # Check for violations
        violation_count = int(student_data.get('violation_count', 0))
        if violation_count > 0:
            # Violation section (orange background)
            violation_frame = tk.Frame(right_panel, bg='#FF8C00')  # Orange
            violation_frame.pack(fill='x', padx=20, pady=(0, 15))
            
            violation_label = tk.Label(
                violation_frame,
                text="The student currently has an violation on record.",
                font=('Arial', 12, 'bold'),
                fg='white',
                bg='#FF8C00',
                wraplength=350
            )
            violation_label.pack(anchor='w', padx=15, pady=(10, 5))
            
            violation_count_label = tk.Label(
                violation_frame,
                text=f"                   Violation Count: {violation_count}",
                font=('Arial', 12, 'bold'),
                fg='white',
                bg='#FF8C00'
            )
            violation_count_label.pack(anchor='w', padx=15, pady=(0, 10))
        
        # Guard in-charge section
        guard_frame = tk.Frame(right_panel, bg='#1E90FF')
        guard_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        guard_label = tk.Label(
            guard_frame,
            text="Guard in-charge: John Jason Domingo",
            font=('Arial', 12),
            fg='white',
            bg='#1E90FF'
        )
        guard_label.pack(anchor='w')
        
        # Footer bar
        self.create_footer("logout")
        
        # Schedule return to guard splash screen after 3 seconds
        self.root.after(10000, self.return_to_guard_splash)
    
    def return_to_guard_splash(self):
        """Return to guard splash screen after student info display"""
        if self.current_screen == "student_info":
            self.show_guard_splash_screen()
    
    def on_rfid_input_main(self, event=None):
        """Handle automatic RFID keyboard input for main student entry screen"""
        rfid_number = self.student_number_var.get().strip()
        
        # Check if we have a complete RFID code (typically 10 digits)
        if len(rfid_number) >= 10:
            # Process the RFID after a short delay to ensure complete input
            self.root.after(100, lambda: self.process_rfid_main(rfid_number))
    
    def process_rfid_main(self, rfid_number):
        """Process RFID input from main student entry screen"""
        # Find student by RFID
        student_data = self.db_manager.find_student_by_rfid(rfid_number)
        
        if student_data:
            # Clear the input field
            self.student_number_var.set("")
            # Show student info screen
            self.show_student_info_screen(student_data)
        else:
            # Clear the input field
            self.student_number_var.set("")
            # Show error message
            self.last_response_message = "Unknown / Invalid ID has been scanned."
            self._schedule_panel_reset()
    
    def submit_student(self, event=None):
        """Handle student number submission"""
        rfid_number = self.student_number_var.get().strip()
        
        if not rfid_number:
            messagebox.showwarning("Missing Information", "Please enter an ID number")
            return
        
        # Find student by RFID
        student_data = self.db_manager.find_student_by_rfid(rfid_number)
        
        if student_data:
            # Clear the input field
            self.student_number_var.set("")
            # Show student info screen
            self.show_student_info_screen(student_data)
        else:
            # Clear the input field
            self.student_number_var.set("")
            # Show error message
            self.last_response_message = "Unknown / Invalid ID has been scanned."
            self._schedule_panel_reset()
    
    def on_rfid_input_inline(self, event=None):
        """Handle automatic RFID keyboard input for inline textbox"""
        # Choose the active inline var from the screen we're on
        if self.current_screen == "guard_splash":
            active_var = self.guard_student_inline_var
        elif self.current_screen == "visitor_form":
            active_var = self.visitor_student_inline_var
        else:
            # If we're not on a screen with inline textbox, just return
            return
            
        if not active_var:
            return
            
        rfid_number = active_var.get().strip()
        
        # Check if we have a complete RFID code (typically 10 digits)
        if len(rfid_number) >= 10:
            # Process the RFID after a short delay to ensure complete input
            self.root.after(100, lambda: self.process_rfid_inline(rfid_number))
    
    def process_rfid_inline(self, rfid_number):
        """Process RFID input from inline textbox"""
        # Choose the active inline var from the screen we're on
        if self.current_screen == "guard_splash":
            active_var = self.guard_student_inline_var
        elif self.current_screen == "visitor_form":
            active_var = self.visitor_student_inline_var
        else:
            # If we're not on a screen with inline textbox, just return
            return
            
        # Find student by RFID
        student_data = self.db_manager.find_student_by_rfid(rfid_number)
        
        if student_data:
            # Clear the input field
            if active_var:
                active_var.set("")
            # Show student info screen
            self.show_student_info_screen(student_data)
        else:
            # Clear the input field
            if active_var:
                active_var.set("")
            # Show error message
            self.last_response_message = "Unknown / Invalid ID has been scanned."
            self._schedule_panel_reset()
    
    def submit_student_inline(self, event=None):
        """Handle student number submission from guard splash inline textbox"""
        # Choose the active inline var from the screen we're on
        if self.current_screen == "guard_splash":
            active_var = self.guard_student_inline_var
        elif self.current_screen == "visitor_form":
            active_var = self.visitor_student_inline_var
        else:
            # If we're not on a screen with inline textbox, just return
            return
            
        if not active_var:
            return
            
        rfid_number = active_var.get().strip()
        
        if not rfid_number:
            messagebox.showwarning("Missing Information", "Please enter an ID number")
            return
        
        # Find student by RFID
        student_data = self.db_manager.find_student_by_rfid(rfid_number)
        
        if student_data:
            # Clear the input field
            active_var.set("")
            # Show student info screen
            self.show_student_info_screen(student_data)
        else:
            # Clear the input field
            active_var.set("")
            # Show error message
            self.last_response_message = "Unknown / Invalid ID has been scanned."
            self._schedule_panel_reset()

    def reset_guard_message(self):
        """Reset the guard splash message back to default and update the label if present"""
        self.last_response_message = ""
        if self.message_reset_after_id is not None:
            try:
                self.root.after_cancel(self.message_reset_after_id)
            except Exception:
                pass
            self.message_reset_after_id = None
        if self.current_screen == "guard_splash" and self.guard_message_label is not None:
            self.guard_message_label.config(text="Awaiting ID card scan.")

    def _schedule_panel_reset(self):
        """Schedule the right-panel message to return to default in 5s."""
        if self.message_reset_after_id is not None:
            try:
                self.root.after_cancel(self.message_reset_after_id)
            except Exception:
                pass
        self.message_reset_after_id = self.root.after(5000, self.reset_guard_message)
    
    def logout_action(self, event=None):
        """Handle logout button click"""
        # In-app only: immediate logout without modal
        result = True
        if result:
            # Clear current guard information
            self.current_guard = None
            self.show_login_screen()
    
    def back_action(self, event=None):
        """Handle back button click"""
        if self.current_screen == "turnstile":
            # From turnstile screen, go back to login
            self.show_login_screen()
        else:
            # From other screens (visitor form, student entry), go back to guard splash
            self.show_guard_splash_screen()
    
    def quit_action(self, event=None):
        """Handle quit button click"""
        # In-app only: immediate quit without modal
        result = True
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