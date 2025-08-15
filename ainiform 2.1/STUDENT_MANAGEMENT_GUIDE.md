# AI-niform Student Management Guide

## Overview
The AI-niform system now supports storing student images directly in the database, making it more convenient to manage student photos and information.

## Database Structure
The database now includes an `IMAGE_PATH` field for each student record:
```
ID,ROLE,NAME,STATUS,IMAGE_PATH
```

## How to Add a New Student

### Method 1: Using the Admin Interface (Recommended)

1. **Run the Admin Interface:**
   ```bash
   python3 admin_interface.py
   ```

2. **Fill in the Student Information:**
   - **Student Number:** The student's ID number (e.g., 02000226226)
   - **RFID Number:** The student's RFID card number (e.g., 0095272825)
   - **Student Name:** Full name of the student
   - **Student Photo:** Click "Browse" to select an image file

3. **Add the Student:**
   - Click "Add Student" button
   - The system will automatically copy the image to the correct directory
   - Both the student record and RFID mapping will be created

### Method 2: Manual Database Editing

1. **Prepare the Image:**
   - Place the student's photo in `/Users/ichiroyamazaki/Desktop/ainiform/id-image/`
   - Use a descriptive filename (e.g., `student_02000226226.jpg`)

2. **Edit database.txt:**
   - Add the student number record:
     ```
     02000226226,STUDENT_NUMBER,Student Name,ACTIVE,student_02000226226.jpg
     ```
   - Add the RFID mapping:
     ```
     0095272825,STUDENT_RFID,02000226226,ACTIVE,
     ```

## Image Requirements

- **Supported Formats:** JPG, JPEG, PNG, GIF, BMP, WEBP
- **Recommended Size:** 80x80 pixels (will be automatically resized)
- **File Location:** `/Users/ichiroyamazaki/Desktop/ainiform/id-image/`
- **Naming Convention:** Use descriptive names (e.g., `student_name.jpg`)

## Current Student in Database

### Student: Ichiro Yamazaki
- **Student Number:** 02000226226
- **RFID Number:** 0095272825
- **Image:** `images.jpg`
- **Status:** ACTIVE

## Testing the System

1. **Run the main application:**
   ```bash
   python3 ai_niform_login.py
   ```

2. **Test student entry:**
   - Log in as a guard (use any guard ID from database)
   - Click "Student" button
   - Enter RFID number: `0095272825`
   - The system should display the student information with the photo

## Admin Interface Features

### Add New Student Tab
- Form to add new students with their photos
- Automatic image file copying
- Validation for duplicate entries

### View Students Tab
- List of all students in the database
- Shows student number, RFID, name, image, and status
- Refresh button to update the list

## Troubleshooting

### Image Not Displaying
1. Check if the image file exists in the correct directory
2. Verify the image path in the database is correct
3. Ensure the image file is not corrupted

### Student Not Found
1. Verify the RFID number is correctly mapped in the database
2. Check that both student number and RFID records are ACTIVE
3. Ensure the student number exists in the STUDENT_NUMBER section

### Database Errors
1. Make sure the database.txt file is properly formatted
2. Check that all required fields are present
3. Verify there are no syntax errors in the file

## File Structure
```
ainiform/
├── ai_niform_login.py          # Main application
├── admin_interface.py          # Student management interface
├── database_manager.py         # Database operations
├── database.txt               # Student and guard database
├── id-image/                  # Student photos directory
│   ├── images.jpg            # Current student photo
│   └── [other student photos]
└── STUDENT_MANAGEMENT_GUIDE.md # This guide
```

## Quick Commands

```bash
# Run main application
python3 ai_niform_login.py

# Run admin interface
python3 admin_interface.py

# Check database syntax
python3 -m py_compile ai_niform_login.py
python3 -m py_compile admin_interface.py
```
