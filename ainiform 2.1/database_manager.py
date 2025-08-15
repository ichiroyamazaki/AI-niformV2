#!/usr/bin/env python3
"""
Database Manager for AI-niform
Handles local text file database operations for guard and student IDs.
"""

import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, database_file="database.txt"):
        self.database_file = database_file
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """Ensure the database file exists with header"""
        if not os.path.exists(self.database_file):
            with open(self.database_file, 'w', encoding='utf-8') as f:
                f.write("# AI-niform Local Database\n")
                f.write("# Format: ID,ROLE,NAME,STATUS\n")
                f.write("# ROLE: GUARD or STUDENT\n")
                f.write("# STATUS: ACTIVE or INACTIVE\n\n")
    
    def load_database(self):
        """Load all records from the database file"""
        records = []
        try:
            with open(self.database_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split(',')
                        if len(parts) >= 4:
                            record = {
                                'id': parts[0],
                                'role': parts[1],
                                'name': parts[2],
                                'status': parts[3]
                            }
                            # Add image path if available (5th field)
                            if len(parts) >= 5:
                                record['image_path'] = parts[4] if parts[4] else None
                            else:
                                record['image_path'] = None
                            # Add violation count if available (6th field)
                            if len(parts) >= 6:
                                try:
                                    record['violation_count'] = int(parts[5]) if parts[5] else 0
                                except ValueError:
                                    record['violation_count'] = 0
                            else:
                                record['violation_count'] = 0
                            records.append(record)
        except FileNotFoundError:
            print(f"Database file {self.database_file} not found. Creating new one.")
            self.ensure_database_exists()
        
        return records
    
    def save_database(self, records):
        """Save records to the database file"""
        try:
            with open(self.database_file, 'w', encoding='utf-8') as f:
                f.write("# AI-niform Local Database\n")
                f.write("# Format: ID,ROLE,NAME,STATUS,IMAGE_PATH,VIOLATION_COUNT\n")
                f.write("# ROLE: GUARD, STUDENT, or SPECIAL\n")
                f.write("# STATUS: ACTIVE or INACTIVE\n")
                f.write("# IMAGE_PATH: Path to student photo (optional, only for students)\n")
                f.write("# VIOLATION_COUNT: Number of active violations (0 = no violations, 1+ = has violations)\n\n")
                
                for record in records:
                    image_path = record.get('image_path', '')
                    violation_count = record.get('violation_count', 0)
                    f.write(f"{record['id']},{record['role']},{record['name']},{record['status']},{image_path},{violation_count}\n")
        except Exception as e:
            print(f"Error saving database: {e}")
    
    def find_person(self, card_id):
        """Find a person by their card ID"""
        records = self.load_database()
        for record in records:
            if record['id'] == card_id and record['status'] == 'ACTIVE':
                return record
        return None
    
    def find_student_by_rfid(self, rfid_number):
        """Find a student by their RFID number"""
        records = self.load_database()
        
        # First, find the RFID mapping
        for record in records:
            if record['id'] == rfid_number and record['role'] == 'STUDENT_RFID' and record['status'] == 'ACTIVE':
                # Get the student number from the name field (which stores the student number)
                student_number = record['name']
                
                # Now find the student record
                for student_record in records:
                    if student_record['id'] == student_number and student_record['role'] == 'STUDENT_NUMBER' and student_record['status'] == 'ACTIVE':
                        return student_record
                break
        
        return None
    
    def add_person(self, card_id, role, name, image_path=None, violation_count=0):
        """Add a new person to the database"""
        records = self.load_database()
        
        # Check if ID already exists
        for record in records:
            if record['id'] == card_id:
                return False, "ID already exists in database"
        
        # Add new record
        new_record = {
            'id': card_id,
            'role': role.upper(),
            'name': name,
            'status': 'ACTIVE',
            'image_path': image_path,
            'violation_count': violation_count
        }
        records.append(new_record)
        self.save_database(records)
        return True, "Person added successfully"
    
    def update_person(self, card_id, role=None, name=None, status=None):
        """Update an existing person's information"""
        records = self.load_database()
        
        for record in records:
            if record['id'] == card_id:
                if role:
                    record['role'] = role.upper()
                if name:
                    record['name'] = name
                if status:
                    record['status'] = status.upper()
                
                self.save_database(records)
                return True, "Person updated successfully"
        
        return False, "Person not found"
    
    def delete_person(self, card_id):
        """Delete a person from the database (set status to INACTIVE)"""
        return self.update_person(card_id, status='INACTIVE')
    
    def get_all_active(self):
        """Get all active records"""
        records = self.load_database()
        return [record for record in records if record['status'] == 'ACTIVE']
    
    def get_by_role(self, role):
        """Get all active records by role"""
        records = self.load_database()
        return [record for record in records if record['role'] == role.upper() and record['status'] == 'ACTIVE']
    
    def log_access(self, card_id, access_type="TAP"):
        """Log access attempts to a separate log file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        person = self.find_person(card_id)
        
        log_entry = f"{timestamp},{card_id},{access_type}"
        if person:
            log_entry += f",{person['role']},{person['name']},SUCCESS"
        else:
            log_entry += f",UNKNOWN,UNKNOWN,FAILED"
        
        try:
            with open('access_log.txt', 'a', encoding='utf-8') as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"Error logging access: {e}")

    def add_visitor(self, visitor_data):
        """Add a new visitor to the database"""
        try:
            # Create visitor database file if it doesn't exist
            visitor_file = "visitors.txt"
            if not os.path.exists(visitor_file):
                with open(visitor_file, 'w', encoding='utf-8') as f:
                    f.write("# AI-niform Visitor Database\n")
                    f.write("# Format: ID,NAME,CONTACT,VISITING_AS,PURPOSE,VISITING,ID_TYPE,SPECIAL_PASS,CREATED_AT,EXPIRES_AT,STATUS\n\n")
            
            # Add visitor record
            with open(visitor_file, 'a', encoding='utf-8') as f:
                f.write(f"{visitor_data['id']},{visitor_data['name']},{visitor_data['contact']},{visitor_data['visiting_as']},{visitor_data['purpose']},{visitor_data['visiting']},{visitor_data['id_type']},{visitor_data['special_pass']},{visitor_data['created_at']},{visitor_data['expires_at']},{visitor_data['status']}\n")
            
            return True
        except Exception as e:
            print(f"Error adding visitor: {e}")
            return False
    
    def get_visitors(self):
        """Get all visitor records"""
        visitors = []
        visitor_file = "visitors.txt"
        
        if not os.path.exists(visitor_file):
            return visitors
        
        try:
            with open(visitor_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split(',')
                        if len(parts) >= 11:
                            visitors.append({
                                'id': parts[0],
                                'name': parts[1],
                                'contact': parts[2],
                                'visiting_as': parts[3],
                                'purpose': parts[4],
                                'visiting': parts[5],
                                'id_type': parts[6],
                                'special_pass': parts[7],
                                'created_at': parts[8],
                                'expires_at': parts[9],
                                'status': parts[10]
                            })
        except Exception as e:
            print(f"Error reading visitors: {e}")
        
        return visitors
    
    def find_visitor(self, visitor_id):
        """Find a visitor by ID"""
        visitors = self.get_visitors()
        for visitor in visitors:
            if visitor['id'] == visitor_id and visitor['status'] == 'ACTIVE':
                # Check if visitor is still valid (not expired)
                from datetime import datetime
                try:
                    expires_at = datetime.strptime(visitor['expires_at'], "%Y-%m-%d %H:%M:%S")
                    if datetime.now() < expires_at:
                        return visitor
                    else:
                        # Mark as expired
                        self.update_visitor_status(visitor_id, 'EXPIRED')
                        return None
                except:
                    return None
        return None
    
    def update_visitor_status(self, visitor_id, status):
        """Update visitor status"""
        visitors = self.get_visitors()
        visitor_file = "visitors.txt"
        
        try:
            with open(visitor_file, 'w', encoding='utf-8') as f:
                f.write("# AI-niform Visitor Database\n")
                f.write("# Format: ID,NAME,CONTACT,VISITING_AS,PURPOSE,VISITING,ID_TYPE,SPECIAL_PASS,CREATED_AT,EXPIRES_AT,STATUS\n\n")
                
                for visitor in visitors:
                    if visitor['id'] == visitor_id:
                        visitor['status'] = status
                    f.write(f"{visitor['id']},{visitor['name']},{visitor['contact']},{visitor['visiting_as']},{visitor['purpose']},{visitor['visiting']},{visitor['id_type']},{visitor['special_pass']},{visitor['created_at']},{visitor['expires_at']},{visitor['status']}\n")
            
            return True
        except Exception as e:
            print(f"Error updating visitor status: {e}")
            return False
    
    def is_special_pass_in_use(self, special_pass_id):
        """Check if a special pass ID is currently being used by an active visitor"""
        if not special_pass_id or special_pass_id.strip() == "":
            return False, None
        
        visitors = self.get_visitors()
        from datetime import datetime
        
        for visitor in visitors:
            if (visitor['special_pass'] == special_pass_id.strip() and 
                visitor['status'] == 'ACTIVE'):
                # Check if visitor is still valid (not expired)
                try:
                    expires_at = datetime.strptime(visitor['expires_at'], "%Y-%m-%d %H:%M:%S")
                    if datetime.now() < expires_at:
                        return True, visitor
                    else:
                        # Mark as expired
                        self.update_visitor_status(visitor['id'], 'EXPIRED')
                        return False, None
                except:
                    return False, None
        
        return False, None
    
    def cleanup_expired_visitors(self):
        """Clean up expired visitors (mark as EXPIRED)"""
        visitors = self.get_visitors()
        from datetime import datetime
        
        for visitor in visitors:
            if visitor['status'] == 'ACTIVE':
                try:
                    expires_at = datetime.strptime(visitor['expires_at'], "%Y-%m-%d %H:%M:%S")
                    if datetime.now() >= expires_at:
                        self.update_visitor_status(visitor['id'], 'EXPIRED')
                except:
                    pass

# Example usage and testing
if __name__ == "__main__":
    db = DatabaseManager()
    
    # Test finding the guard
    guard = db.find_person("0095339862")
    if guard:
        print(f"Found guard: {guard['name']} ({guard['role']})")
    else:
        print("Guard not found")
    
    # Test finding a student
    student = db.find_person("0095095703")
    if student:
        print(f"Found student: {student['name']} ({student['role']})")
    else:
        print("Student not found")
    
    # Test adding a new person
    success, message = db.add_person("1234567890", "STUDENT", "Test Student")
    print(f"Add result: {message}")
    
    # Test logging access
    db.log_access("0095339862", "TAP") 