import os
import datetime
import csv

class DatabaseManager:
    def __init__(self, db_file="database.txt"):
        self.db_file = db_file
        self.visitors_file = "visitors.txt"
        self.access_log_file = "access_log.txt"
        
        # Create files if they don't exist
        self._create_files_if_not_exist()
    
    def _create_files_if_not_exist(self):
        """Create necessary files if they don't exist"""
        if not os.path.exists(self.visitors_file):
            with open(self.visitors_file, 'w') as f:
                f.write("# Visitor Database\n")
                f.write("# Format: NAME,CONTACT,VISITING_AS,PURPOSE,VISITING,ID_TYPE,SPECIAL_PASS,CREATED_AT,EXPIRES_AT,STATUS\n")
        
        if not os.path.exists(self.access_log_file):
            with open(self.access_log_file, 'w') as f:
                f.write("# Access Log\n")
                f.write("# Format: TIMESTAMP,ID,ACTION,STATUS\n")
    
    def find_person(self, card_id):
        """Find a person by their card ID"""
        # First check visitors.txt for Special Pass IDs (prioritize fresh registrations)
        try:
            with open(self.visitors_file, 'r') as f:
                # Find the most recent valid entry for this Special Pass ID
                best_match = None
                best_created_at = None
                
                for line in f:
                    line = line.strip()
                    if line.startswith('#') or not line:
                        continue
                    
                    parts = line.split(',')
                    if len(parts) >= 10:
                        visitor_special_pass = parts[6]  # Special Pass ID
                        status = parts[9]  # Status
                        visitor_name = parts[0]  # Visitor name
                        created_at_str = parts[7]  # Creation timestamp
                        expires_at_str = parts[8]  # Expiration timestamp
                        
                        if visitor_special_pass == card_id and status == "ACTIVE":
                            try:
                                created_at = datetime.datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
                                expires_at = datetime.datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S")
                                current_time = datetime.datetime.now()
                                
                                # Only consider entries that haven't expired yet
                                if expires_at > current_time:
                                    # Keep track of the entry with the most recent creation time
                                    if best_match is None or created_at > best_created_at:
                                        best_match = {
                                            'id': visitor_special_pass,
                                            'role': 'SPECIAL',
                                            'name': visitor_name,
                                            'status': status
                                        }
                                        best_created_at = created_at
                            except Exception as e:
                                print(f"Error parsing dates: {e}")
                                # If we can't parse the dates, still consider this entry
                                if best_match is None:
                                    best_match = {
                                        'id': visitor_special_pass,
                                        'role': 'SPECIAL',
                                        'name': visitor_name,
                                        'status': status
                                    }
                
                if best_match:
                    return best_match
        except Exception as e:
            print(f"Error reading visitors file: {e}")
        
        # If not found in visitors, check the main database
        try:
            with open(self.db_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#') or not line:
                        continue
                    
                    parts = line.split(',')
                    if len(parts) >= 3:
                        db_id = parts[0]
                        role = parts[1]
                        name = parts[2]
                        status = parts[3] if len(parts) > 3 else "ACTIVE"
                        
                        if db_id == card_id and status == "ACTIVE":
                            return {
                                'id': db_id,
                                'role': role,
                                'name': name,
                                'status': status
                            }
        except Exception as e:
            print(f"Error reading database: {e}")
        
        return None
    
    def is_special_pass_in_use(self, special_pass_id):
        """Check if a special pass ID is currently in use"""
        try:
            with open(self.visitors_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#') or not line:
                        continue
                    
                    parts = line.split(',')
                    if len(parts) >= 10:  # Updated to 10 fields (removed ID)
                        visitor_special_pass = parts[6]  # Updated index
                        expires_at_str = parts[8]  # Updated index
                        status = parts[9]  # Updated index
                        
                        if visitor_special_pass == special_pass_id and status == "ACTIVE":
                            # Check if the pass has expired
                            try:
                                expires_at = datetime.datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S")
                                if expires_at > datetime.datetime.now():
                                    return True, {
                                        'name': parts[0],  # Updated index
                                        'expires_at': expires_at_str
                                    }
                            except:
                                pass
        except Exception as e:
            print(f"Error checking special pass: {e}")
        
        return False, None
    
    def add_visitor(self, visitor_data):
        """Add a new visitor to the database"""
        try:
            # First, deactivate any existing entries for the same special pass ID
            self._deactivate_existing_special_pass(visitor_data['special_pass'])
            
            with open(self.visitors_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    visitor_data['name'],
                    visitor_data['contact'],
                    visitor_data['visiting_as'],
                    visitor_data['purpose'],
                    visitor_data['visiting'],
                    visitor_data['id_type'],
                    visitor_data['special_pass'],
                    visitor_data['created_at'],
                    visitor_data['expires_at'],
                    visitor_data['status']
                ])
            return True
        except Exception as e:
            print(f"Error adding visitor: {e}")
            return False
    
    def log_access(self, id_number, action, status="SUCCESS"):
        """Log an access attempt"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.access_log_file, 'a') as f:
                f.write(f"{timestamp},{id_number},{action},{status}\n")
        except Exception as e:
            print(f"Error logging access: {e}")
    
    def get_guard_name(self, guard_id):
        """Get guard name by ID"""
        person = self.find_person(guard_id)
        if person and person['role'] == 'GUARD':
            return person['name']
        return "Unknown Guard"
    
    def is_student_number_valid(self, student_number):
        """Check if a student number is valid"""
        try:
            with open(self.db_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#') or not line:
                        continue
                    
                    parts = line.split(',')
                    if len(parts) >= 3:
                        db_id = parts[0]
                        role = parts[1]
                        status = parts[3] if len(parts) > 3 else "ACTIVE"
                        
                        # Check if it's a STUDENT_NUMBER entry and matches
                        if role == 'STUDENT_NUMBER' and db_id == student_number and status == "ACTIVE":
                            return True
        except Exception as e:
            print(f"Error checking student number: {e}")
        
        return False
    
    def is_special_pass_expired(self, special_pass_id):
        """Check if a special pass has expired"""
        try:
            with open(self.visitors_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#') or not line:
                        continue
                    
                    parts = line.split(',')
                    if len(parts) >= 10:  # Updated to 10 fields
                        visitor_special_pass = parts[6]  # Special Pass ID
                        expires_at_str = parts[8]  # Expiration timestamp
                        status = parts[9]  # Status
                        
                        if visitor_special_pass == special_pass_id and status == "ACTIVE":
                            # Check if the pass has expired
                            try:
                                expires_at = datetime.datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S")
                                current_time = datetime.datetime.now()
                                if expires_at < current_time:
                                    return True  # Pass has expired
                            except Exception as e:
                                print(f"Error parsing expiration date: {e}")
        except Exception as e:
            print(f"Error checking special pass expiration: {e}")
        
        return False
    
    def get_special_pass_check_status(self, special_pass_id):
        """Get the current check-in/check-out status of a special pass"""
        try:
            with open(self.visitors_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#') or not line:
                        continue
                    
                    parts = line.split(',')
                    if len(parts) >= 10:
                        visitor_special_pass = parts[6]  # Special Pass ID
                        status = parts[9]  # Status
                        
                        if visitor_special_pass == special_pass_id and status == "ACTIVE":
                            # Check if there's a check-in time recorded
                            if len(parts) >= 11:
                                check_in_time = parts[10]  # Check-in time
                                check_out_time = parts[11] if len(parts) > 11 else ""  # Check-out time
                                
                                if check_in_time and check_in_time != "":
                                    if check_out_time and check_out_time != "":
                                        # Has both check-in and check-out, next should be check-in
                                        return "CHECKED_OUT"
                                    else:
                                        # Has check-in but no check-out, next should be check-out
                                        return "CHECKED_IN"
                                else:
                                    # No check-in time, next should be check-in
                                    return "CHECKED_OUT"
                            else:
                                return "CHECKED_OUT"  # No check-in time recorded yet
        except Exception as e:
            print(f"Error getting check status: {e}")
        
        return "CHECKED_OUT"  # Default to checked out
    
    def record_special_pass_check(self, special_pass_id, check_type):
        """Record a check-in or check-out for a special pass"""
        try:
            # Read all lines
            with open(self.visitors_file, 'r') as f:
                lines = f.readlines()
            
            # Find and update the line with the special pass
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            updated_lines = []
            
            for line in lines:
                if line.startswith('#') or not line.strip():
                    updated_lines.append(line)
                    continue
                
                parts = line.strip().split(',')
                if len(parts) >= 10:
                    visitor_special_pass = parts[6]  # Special Pass ID
                    
                    if visitor_special_pass == special_pass_id:
                        # Ensure we have enough fields
                        while len(parts) < 12:
                            parts.append("")
                        
                        if check_type == "CHECK_IN":
                            parts[10] = current_time  # Check-in time
                            parts[11] = ""  # Clear check-out time
                        elif check_type == "CHECK_OUT":
                            parts[11] = current_time  # Check-out time
                        
                        # Reconstruct the line
                        updated_line = ','.join(parts) + '\n'
                        updated_lines.append(updated_line)
                    else:
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)
            
            # Write back to file
            with open(self.visitors_file, 'w') as f:
                f.writelines(updated_lines)
            
            return True
        except Exception as e:
            print(f"Error recording check: {e}")
            return False
    
    def get_special_pass_check_times(self, special_pass_id):
        """Get the check-in and check-out times for a special pass"""
        try:
            with open(self.visitors_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#') or not line:
                        continue
                    
                    parts = line.split(',')
                    if len(parts) >= 12:
                        visitor_special_pass = parts[6]  # Special Pass ID
                        
                        if visitor_special_pass == special_pass_id:
                            check_in_time = parts[10] if len(parts) > 10 else ""
                            check_out_time = parts[11] if len(parts) > 11 else ""
                            return check_in_time, check_out_time
        except Exception as e:
            print(f"Error getting check times: {e}")
        
        return "", ""
    
    def is_special_pass_in_grace_period(self, special_pass_id):
        """Check if a special pass is in grace period (can check-out but not check-in)"""
        try:
            with open(self.visitors_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#') or not line:
                        continue
                    
                    parts = line.split(',')
                    if len(parts) >= 10:
                        visitor_special_pass = parts[6]  # Special Pass ID
                        expires_at_str = parts[8]  # Expiration timestamp
                        status = parts[9]  # Status
                        
                        if visitor_special_pass == special_pass_id and status == "ACTIVE":
                            # Get check-in time
                            check_in_time = parts[10] if len(parts) > 10 else ""
                            
                            if check_in_time and check_in_time != "":
                                try:
                                    # Parse expiration and check-in times
                                    expires_at = datetime.datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S")
                                    check_in_dt = datetime.datetime.strptime(check_in_time, "%Y-%m-%d %H:%M:%S")
                                    current_time = datetime.datetime.now()
                                    
                                    # Calculate time remaining when checked in
                                    time_remaining_at_checkin = expires_at - check_in_dt
                                    minutes_remaining_at_checkin = time_remaining_at_checkin.total_seconds() / 60
                                    
                                    # If 10 minutes or less remaining at check-in, and now past expiration
                                    if minutes_remaining_at_checkin <= 10 and current_time > expires_at:
                                        return True  # In grace period
                                except Exception as e:
                                    print(f"Error parsing dates for grace period: {e}")
        except Exception as e:
            print(f"Error checking grace period: {e}")
        
        return False
    
    def is_special_pass_expired_for_checkin(self, special_pass_id):
        """Check if a special pass has expired for check-in (considers grace period)"""
        try:
            with open(self.visitors_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#') or not line:
                        continue
                    
                    parts = line.split(',')
                    if len(parts) >= 10:
                        visitor_special_pass = parts[6]  # Special Pass ID
                        expires_at_str = parts[8]  # Expiration timestamp
                        status = parts[9]  # Status
                        
                        if visitor_special_pass == special_pass_id and status == "ACTIVE":
                            try:
                                expires_at = datetime.datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S")
                                current_time = datetime.datetime.now()
                                
                                # For check-in, always check against expiration (no grace period)
                                if current_time > expires_at:
                                    return True  # Expired for check-in
                            except Exception as e:
                                print(f"Error parsing expiration date: {e}")
        except Exception as e:
            print(f"Error checking expiration for check-in: {e}")
        
        return False
    
    def cleanup_expired_special_passes(self):
        """Remove expired Special Passes from visitors.txt to allow reuse"""
        try:
            # Read all lines
            with open(self.visitors_file, 'r') as f:
                lines = f.readlines()
            
            # Filter out expired entries
            current_time = datetime.datetime.now()
            updated_lines = []
            removed_count = 0
            
            for line in lines:
                if line.startswith('#') or not line.strip():
                    updated_lines.append(line)
                    continue
                
                parts = line.strip().split(',')
                if len(parts) >= 10:
                    expires_at_str = parts[8]  # Expiration timestamp
                    status = parts[9]  # Status
                    
                    if status == "ACTIVE":
                        try:
                            expires_at = datetime.datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S")
                            
                            # Check if expired (past 24 hours + grace period)
                            # Add 1 hour grace period for cleanup
                            cleanup_time = expires_at + datetime.timedelta(hours=1)
                            
                            if current_time > cleanup_time:
                                # This Special Pass has expired and should be removed
                                removed_count += 1
                                print(f"Removing expired Special Pass: {parts[6]} (expired: {expires_at_str})")
                                continue  # Skip this line (don't add to updated_lines)
                            else:
                                # Still valid, keep it
                                updated_lines.append(line)
                        except Exception as e:
                            print(f"Error parsing expiration date for cleanup: {e}")
                            # Keep the line if we can't parse the date
                            updated_lines.append(line)
                    else:
                        # Keep non-active entries
                        updated_lines.append(line)
                else:
                    # Keep lines that don't have enough parts
                    updated_lines.append(line)
            
            # Write back to file
            with open(self.visitors_file, 'w') as f:
                f.writelines(updated_lines)
            
            if removed_count > 0:
                print(f"Cleanup completed: {removed_count} expired Special Pass(es) removed")
            
            return removed_count
        except Exception as e:
            print(f"Error during cleanup: {e}")
            return 0
    
    def _deactivate_existing_special_pass(self, special_pass_id):
        """Deactivate any existing entries for a special pass ID"""
        try:
            # Read all lines
            with open(self.visitors_file, 'r') as f:
                lines = f.readlines()
            
            # Update lines to deactivate existing entries
            updated_lines = []
            deactivated_count = 0
            
            for line in lines:
                if line.startswith('#') or not line.strip():
                    updated_lines.append(line)
                    continue
                
                parts = line.strip().split(',')
                if len(parts) >= 10:
                    visitor_special_pass = parts[6]  # Special Pass ID
                    status = parts[9]  # Status
                    
                    if visitor_special_pass == special_pass_id and status == "ACTIVE":
                        # Deactivate this entry
                        parts[9] = "INACTIVE"
                        updated_line = ','.join(parts) + '\n'
                        updated_lines.append(updated_line)
                        deactivated_count += 1
                        print(f"Deactivated existing Special Pass entry: {special_pass_id}")
                    else:
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)
            
            # Write back to file if any entries were deactivated
            if deactivated_count > 0:
                with open(self.visitors_file, 'w') as f:
                    f.writelines(updated_lines)
                print(f"Deactivated {deactivated_count} existing Special Pass entry(ies) for ID: {special_pass_id}")
            
            return deactivated_count
        except Exception as e:
            print(f"Error deactivating existing special pass: {e}")
            return 0

    def is_special_pass_available_for_registration(self, special_pass_id):
        """Check if a Special Pass ID is available for new registration"""
        # First, clean up any expired Special Passes
        self.cleanup_expired_special_passes()
        
        # Then check if the ID is currently in use
        is_in_use, existing_visitor = self.is_special_pass_in_use(special_pass_id)
        
        return not is_in_use
