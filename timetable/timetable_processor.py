"""
Timetable Processing Module for EdFast Application.
Adapts the TimeTable-Sorter functionality for Streamlit interface.
"""

import pandas as pd
import os
import random
import tempfile
import shutil
from typing import List, Dict, Tuple, Optional


class TimetableProcessor:
    """Class to handle timetable data processing and filtering."""
    
    def __init__(self, upload_dir: str = "uploaded_timetables"):
        """Initialize the timetable processor.
        
        Args:
            upload_dir: Directory to store uploaded timetable files
        """
        self.upload_dir = upload_dir
        self.lab_keywords = [
            'C-Margala 1', 'C-Margala 3', 'C-Margala 4', 'C-Rawal 1', 
            'Rawal 3 (B-232)', 'C-Rawal 4', 'C-GPU Lab', 'A-Karakoram 1', 
            'A-Karakoram 2', 'A-Karakoram 3', 'A-Mehran 1', 'A-Mehran 2', 
            'B-Digital', 'A-CALL-1', 'A-CALL-2', 'A-CALL-3'
        ]
        self._ensure_upload_dir()
    
    def _ensure_upload_dir(self):
        """Ensure upload directory exists."""
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
    
    def process_uploaded_files(self, uploaded_files: List) -> Dict[str, pd.DataFrame]:
        """Process uploaded timetable files and return structured data.
        
        Args:
            uploaded_files: List of uploaded file objects from Streamlit
            
        Returns:
            Dictionary with processed DataFrames for each file
        """
        processed_data = {}
        
        for uploaded_file in uploaded_files:
            try:
                # Save uploaded file temporarily
                temp_path = os.path.join(self.upload_dir, uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Process the file based on its extension
                if uploaded_file.name.endswith('.xlsx'):
                    df = self._process_excel_file(temp_path)
                elif uploaded_file.name.endswith('.csv'):
                    df = self._process_csv_file(temp_path)
                else:
                    continue
                
                processed_data[uploaded_file.name] = df
                
            except Exception as e:
                print(f"Error processing {uploaded_file.name}: {str(e)}")
                continue
        
        return processed_data
    
    def _process_excel_file(self, file_path: str) -> pd.DataFrame:
        """Process Excel file and convert to structured DataFrame.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Processed DataFrame
        """
        file = pd.ExcelFile(file_path)
        all_dfs = []
        
        # Process each sheet (day)
        for sheet in file.sheet_names:
            # Skip non-day sheets
            if sheet.lower() in ['welcome', 'info', 'instructions']:
                continue
                
            # Try different header positions and formats
            df = self._try_read_excel_sheet(file, sheet)
            if df is None or df.empty:
                continue
            
            # Extract day name from sheet name (handle both "Monday" and "Monday (May 12, 2025)" formats)
            day_name = sheet.split('(')[0].strip()
            
            # Debug: Print sheet processing info
            print(f"Processing sheet: '{sheet}' -> Day: '{day_name}'")
            
            data = []
            
            # For the new format, we need to process differently
            if self._is_new_format(df):
                data = self._process_new_format(df, day_name)
            else:
                data = self._process_old_format(df, day_name)
            
            # Create DataFrame and clean it
            if data:
                new_data = pd.DataFrame(data)
                new_data = self._clean_dataframe(new_data)
                all_dfs.append(new_data)
        
        # Combine all sheets
        combined_df = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()
        
        # Remove duplicates (same course, section, day, time, room)
        if not combined_df.empty:
            print(f"Before deduplication: {len(combined_df)} entries")
            combined_df = combined_df.drop_duplicates(subset=['Class', 'Day', 'Course', 'Section', 'Time'], keep='first')
            print(f"After deduplication: {len(combined_df)} entries")
            
            # Debug: Print processing summary
            day_summary = combined_df['Day'].value_counts()
            print("Day distribution after deduplication:")
            for day, count in day_summary.items():
                print(f"  {day}: {count}")
        
        # Store the processed data for conflict checking
        self.store_processed_data(combined_df)
        
        return combined_df
    
    def _try_read_excel_sheet(self, file, sheet):
        """Try reading Excel sheet with different parameters."""
        try:
            # Try header=None first (for new format)
            df = pd.read_excel(file, sheet, header=None)
            if not df.empty:
                return df
        except:
            pass
        
        try:
            # Try header=4 (for old format)
            df = pd.read_excel(file, sheet, header=4)
            if not df.empty:
                return df
        except:
            pass
        
        return None
    
    def _is_new_format(self, df):
        """Determine if this is the new FSC format."""
        # Check if row 4 contains 'Room' and time slots
        try:
            if len(df) > 4:
                row_4 = df.iloc[4]
                if 'Room' in str(row_4.iloc[0]) and any('08:30' in str(cell) for cell in row_4):
                    return True
        except:
            pass
        return False
    
    def _process_new_format(self, df, day_name):
        """Process the new FSC format."""
        data = []
        
        try:
            # Find the header row (should be around row 4)
            header_row_idx = 4
            header_row = df.iloc[header_row_idx]
            
            # Extract time slots from header row
            time_slots = []
            for i, cell in enumerate(header_row):
                if pd.notna(cell) and ':' in str(cell) and '-' in str(cell):
                    time_slots.append((i, str(cell)))
            
            # Process data rows (starting from row 5)
            for row_idx in range(header_row_idx + 1, len(df)):
                row_data = df.iloc[row_idx]
                room = str(row_data.iloc[0]) if pd.notna(row_data.iloc[0]) else ''
                
                # Skip empty rooms or invalid rows
                if not room or room == 'nan' or 'NaN' in room:
                    continue
                
                # Process each time slot
                for time_col_idx, time_slot in time_slots:
                    cell_value = row_data.iloc[time_col_idx] if time_col_idx < len(row_data) else None
                    
                    if pd.notna(cell_value) and str(cell_value) != 'nan':
                        course_text = str(cell_value).strip()
                        
                        # Extract course and section information
                        course_name, section = self._extract_course_section(course_text)
                        
                        if course_name:  # Only add if we have a valid course
                            # Determine type (Lab vs Theory)
                            course_type = 'Lab' if any(keyword.lower() in course_name.lower() for keyword in ['lab', 'laboratory']) else 'Theory'
                            
                            data.append({
                                'Class': room,
                                'Day': day_name,
                                'Course': course_name,
                                'Section': section,
                                'Type': course_type,
                                'Time': time_slot
                            })
        
        except Exception as e:
            print(f"Error processing new format for {day_name}: {str(e)}")
        
        return data
    
    def _process_old_format(self, df, day_name):
        """Process the old format (original TimeTable-Sorter format)."""
        data = []
        prev_time = None
        lab_time = None
        is_thursday = (day_name.lower() == "thursday")
        
        # Iterate through each cell in the excel sheet
        for i, row in enumerate(df.index):
            for j, col in enumerate(df.columns):
                cell = df.at[row, col]
                
                # Handle time columns
                if 'Unnamed' in str(col):
                    time = prev_time
                else:
                    time = str(col)
                    prev_time = time
                
                # Extract section information
                start_index = str(cell).find('(')
                end_index = str(cell).find(')')
                extracted_string = str(cell)[start_index + 1:end_index] if start_index != -1 and end_index != -1 else str(cell)
                
                # Create new row
                new_row = {
                    'Class': df.at[i, df.columns[0]] if len(df.columns) > 0 else '',
                    'Day': day_name,
                    'Course': str(cell).split('(')[0],
                    'Section': extracted_string if start_index != -1 and end_index != -1 else str(cell),
                    'Time': time,
                    'Type': 'Theory'  # Default
                }
                
                # Determine if it's a lab
                if is_thursday and new_row['Class'] in self.lab_keywords:
                    new_row['Type'] = 'Lab'
                    if j < len(df.columns):
                        lab_time = df.iat[38, j] if len(df) > 38 else ''
                        new_row['Time'] = lab_time
                
                data.append(new_row)
        
        return data
    
    def _extract_course_section(self, course_text):
        """Extract course name and section from text like 'DLD (CS-B)' or 'Psychology (AI-A) 10:00-11:45'."""
        if not course_text or course_text == 'nan':
            return None, None
        
        # Remove time information if present (like "10:00-11:45")
        import re
        course_text = re.sub(r'\d{2}:\d{2}-\d{2}:\d{2}', '', course_text).strip()
        
        # Find parentheses for section
        start_idx = course_text.find('(')
        end_idx = course_text.find(')')
        
        if start_idx != -1 and end_idx != -1:
            course_name = course_text[:start_idx].strip()
            section = course_text[start_idx + 1:end_idx].strip()
        else:
            course_name = course_text.strip()
            section = course_name  # Use course name as section if no parentheses
        
        return course_name, section
    
    def _process_csv_file(self, file_path: str) -> pd.DataFrame:
        """Process CSV file.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Processed DataFrame
        """
        try:
            df = pd.read_csv(file_path)
            return self._clean_dataframe(df)
        except Exception as e:
            print(f"Error processing CSV file: {str(e)}")
            return pd.DataFrame()
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean DataFrame by removing null and invalid entries.
        
        Args:
            df: DataFrame to clean
            
        Returns:
            Cleaned DataFrame
        """
        if df.empty:
            return df
        
        # Remove null rows
        df = df.dropna(subset=['Course'], how='all')
        
        # Remove rows with empty strings or 'nan' in Course
        df = df[df['Course'].notna()]
        df = df[df['Course'] != '']
        df = df[df['Course'] != 'nan']
        df = df[~df['Course'].str.contains('nan', case=False, na=False)]
        
        # Remove invalid time entries
        df = df[df['Time'] != 'Room']
        df = df[df['Time'] != 'Lab']
        df = df[df['Class'] != 'Lab']
        
        # Remove rows where Course is just whitespace
        df = df[df['Course'].str.strip() != '']
        
        # Remove rows where Course name is too short (likely invalid)
        df = df[df['Course'].str.len() > 1]
        
        # Clean up Course names - remove extra whitespace
        df['Course'] = df['Course'].str.strip()
        df['Section'] = df['Section'].str.strip()
        df['Class'] = df['Class'].str.strip()
        
        # Reset index
        df.reset_index(drop=True, inplace=True)
        
        return df
    
    def filter_timetable(self, df: pd.DataFrame, courses: List[str], departments: List[str]) -> pd.DataFrame:
        """Filter timetable data based on courses and departments.
        
        Args:
            df: DataFrame with timetable data
            courses: List of course codes/names to filter
            departments: List of department codes to filter
            
        Returns:
            Filtered DataFrame
        """
        if df.empty:
            return df
        
        # Clean and prepare filter data
        courses = [course.strip() for course in courses if course.strip()]
        departments = [dept.strip() for dept in departments if dept.strip()]
        
        # Filter by courses
        if courses:
            course_filter = df['Course'].str.strip().isin(courses)
        else:
            course_filter = pd.Series([True] * len(df))
        
        # Filter by departments (check first 2 characters of section)
        if departments:
            dept_filter = df['Section'].str[:2].isin(departments)
        else:
            dept_filter = pd.Series([True] * len(df))
        
        # Apply both filters
        filtered_df = df[course_filter & dept_filter]
        
        return filtered_df
    
    def generate_html_table(self, df: pd.DataFrame) -> str:
        """Generate HTML table with color-coded courses.
        
        Args:
            df: Filtered DataFrame
            
        Returns:
            HTML string for the table
        """
        if df.empty:
            return "<p>No data found for the selected courses and departments.</p>"
        
        # Generate color map for courses
        color_map = {}
        unique_courses = df['Course'].str.strip().unique()
        
        for course in unique_courses:
            color_map[course] = self._random_color()
        
        # Start HTML table
        html = """
        <div style="overflow-x: auto; margin: 20px 0;">
            <table style="border-collapse: collapse; width: 100%; min-width: 600px; font-family: Arial, sans-serif;">
                <thead>
                    <tr style="background-color: #f0f2f6; border: 2px solid #ddd;">
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Class/Room</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Day</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Course</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Section</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Type</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Time</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Add table rows
        for _, row in df.iterrows():
            course = row['Course'].strip()
            color = color_map.get(course, '#ffffff')
            
            html += f"""
                <tr style="background-color: {color}; border: 1px solid #ddd;">
                    <td style="border: 1px solid #ddd; padding: 10px;">{row['Class']}</td>
                    <td style="border: 1px solid #ddd; padding: 10px;">{row['Day']}</td>
                    <td style="border: 1px solid #ddd; padding: 10px; font-weight: bold;">{row['Course']}</td>
                    <td style="border: 1px solid #ddd; padding: 10px;">{row['Section']}</td>
                    <td style="border: 1px solid #ddd; padding: 10px;">
                        <span style="background-color: {'#4CAF50' if row['Type'] == 'Lab' else '#2196F3'}; 
                                     color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">
                            {row['Type']}
                        </span>
                    </td>
                    <td style="border: 1px solid #ddd; padding: 10px;">{row['Time']}</td>
                </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        
        return html
    
    def _random_color(self) -> str:
        """Generate a random pastel color.
        
        Returns:
            Hex color string
        """
        # Generate pastel colors (lighter shades)
        colors = [
            '#FFE6E6', '#E6F3FF', '#E6FFE6', '#FFFFE6', '#F3E6FF',
            '#FFE6F3', '#E6FFFF', '#FFF3E6', '#F0F0F0', '#E6F0FF',
            '#FFE6CC', '#E6CCFF', '#CCFFE6', '#FFCCCC', '#CCE6FF'
        ]
        return random.choice(colors)
    
    def get_course_statistics(self, df: pd.DataFrame) -> Dict:
        """Get statistics about the filtered timetable.
        
        Args:
            df: Filtered DataFrame
            
        Returns:
            Dictionary with statistics
        """
        if df.empty:
            return {}
        
        stats = {
            'total_classes': len(df),
            'unique_courses': df['Course'].nunique(),
            'theory_classes': len(df[df['Type'] == 'Theory']),
            'lab_classes': len(df[df['Type'] == 'Lab']),
            'days_with_classes': df['Day'].nunique(),
            'unique_rooms': df['Class'].nunique()
        }
        
        return stats
    
    def check_time_conflicts(self, selected_courses: List[str], selected_sections: List[str] = None) -> Dict:
        """Check for time conflicts in selected courses.
        
        Args:
            selected_courses: List of course names to check
            selected_sections: Optional list of specific sections
            
        Returns:
            Dictionary with conflict information
        """
        if not hasattr(self, '_processed_data') or self._processed_data.empty:
            return {'conflicts': [], 'conflict_free_schedule': pd.DataFrame(), 'recommendations': []}
        
        df = self._processed_data
        
        # Filter for selected courses
        course_filter = df['Course'].isin(selected_courses)
        if selected_sections:
            section_filter = df['Section'].isin(selected_sections)
            filtered_df = df[course_filter & section_filter]
        else:
            filtered_df = df[course_filter]
        
        conflicts = []
        conflict_free_schedule = []
        recommendations = []
        
        # Group by day to check for time overlaps
        for day in filtered_df['Day'].unique():
            day_classes = filtered_df[filtered_df['Day'] == day].copy()
            
            # Parse time slots for overlap detection
            day_classes['start_time'], day_classes['end_time'] = zip(*day_classes['Time'].apply(self._parse_time_slot))
            
            # Sort by start time
            day_classes = day_classes.sort_values('start_time')
            
            # Check for overlaps
            for i in range(len(day_classes)):
                for j in range(i + 1, len(day_classes)):
                    class1 = day_classes.iloc[i]
                    class2 = day_classes.iloc[j]
                    
                    # Check if times overlap
                    if self._times_overlap(class1['start_time'], class1['end_time'], 
                                         class2['start_time'], class2['end_time']):
                        conflict = {
                            'day': day,
                            'course1': class1['Course'],
                            'section1': class1['Section'],
                            'time1': class1['Time'],
                            'room1': class1['Class'],
                            'course2': class2['Course'],
                            'section2': class2['Section'],
                            'time2': class2['Time'],
                            'room2': class2['Class'],
                            'type': 'Time Overlap'
                        }
                        conflicts.append(conflict)
                    else:
                        # No conflict, add both to conflict-free schedule
                        conflict_free_schedule.append(class1.to_dict())
                        conflict_free_schedule.append(class2.to_dict())
        
        # Remove duplicates from conflict-free schedule
        if conflict_free_schedule:
            conflict_free_df = pd.DataFrame(conflict_free_schedule).drop_duplicates()
        else:
            conflict_free_df = filtered_df.copy()
        
        # Generate recommendations for conflicts
        for conflict in conflicts:
            recommendation = self._get_conflict_recommendations(df, conflict)
            if recommendation:
                recommendations.append(recommendation)
        
        return {
            'conflicts': conflicts,
            'conflict_free_schedule': conflict_free_df,
            'recommendations': recommendations,
            'total_courses': len(selected_courses),
            'conflicted_courses': len(set([c['course1'] for c in conflicts] + [c['course2'] for c in conflicts]))
        }
    
    def _parse_time_slot(self, time_str: str) -> Tuple[str, str]:
        """Parse time slot string into start and end times.
        
        Args:
            time_str: Time string like "09:00-10:20"
            
        Returns:
            Tuple of (start_time, end_time)
        """
        try:
            if '-' in time_str:
                start, end = time_str.split('-')
                return start.strip(), end.strip()
            else:
                # If no end time, assume 1 hour duration
                start = time_str.strip()
                start_hour = int(start.split(':')[0])
                start_min = start.split(':')[1]
                end_hour = start_hour + 1
                end = f"{end_hour:02d}:{start_min}"
                return start, end
        except:
            return "00:00", "23:59"
    
    def _times_overlap(self, start1: str, end1: str, start2: str, end2: str) -> bool:
        """Check if two time ranges overlap.
        
        Args:
            start1, end1: First time range
            start2, end2: Second time range
            
        Returns:
            True if times overlap
        """
        try:
            # Convert to minutes for easier comparison
            def time_to_minutes(time_str):
                hours, minutes = map(int, time_str.split(':'))
                return hours * 60 + minutes
            
            start1_min = time_to_minutes(start1)
            end1_min = time_to_minutes(end1)
            start2_min = time_to_minutes(start2)
            end2_min = time_to_minutes(end2)
            
            # Check for overlap
            return not (end1_min <= start2_min or end2_min <= start1_min)
        except:
            return False
    
    def _get_conflict_recommendations(self, df: pd.DataFrame, conflict: Dict) -> Dict:
        """Get recommendations to resolve conflicts.
        
        Args:
            df: Full timetable DataFrame
            conflict: Conflict information
            
        Returns:
            Recommendation dictionary
        """
        course1 = conflict['course1']
        course2 = conflict['course2']
        day = conflict['day']
        
        # Find alternative sections for conflicting courses
        course1_alternatives = df[(df['Course'] == course1) & (df['Day'] == day) & 
                                (df['Section'] != conflict['section1'])]
        course2_alternatives = df[(df['Course'] == course2) & (df['Day'] == day) & 
                                (df['Section'] != conflict['section2'])]
        
        recommendation = {
            'conflict_type': 'Time Overlap',
            'conflicted_courses': [course1, course2],
            'day': day,
            'suggestions': []
        }
        
        if not course1_alternatives.empty:
            for _, alt in course1_alternatives.iterrows():
                recommendation['suggestions'].append({
                    'course': course1,
                    'alternative_section': alt['Section'],
                    'alternative_time': alt['Time'],
                    'alternative_room': alt['Class']
                })
        
        if not course2_alternatives.empty:
            for _, alt in course2_alternatives.iterrows():
                recommendation['suggestions'].append({
                    'course': course2,
                    'alternative_section': alt['Section'],
                    'alternative_time': alt['Time'],
                    'alternative_room': alt['Class']
                })
        
        return recommendation
    
    def build_personal_schedule(self, selected_courses: List[str]) -> Dict:
        """Build a personalized conflict-free schedule.
        
        Args:
            selected_courses: List of courses to include
            
        Returns:
            Dictionary with schedule and conflict information
        """
        if not hasattr(self, '_processed_data') or self._processed_data.empty:
            return {'error': 'No timetable data available'}
        
        df = self._processed_data
        
        # Get all sections for selected courses
        available_options = {}
        for course in selected_courses:
            course_data = df[df['Course'] == course]
            if not course_data.empty:
                available_options[course] = course_data.groupby(['Section', 'Day', 'Time']).first().reset_index()
        
        # Try to find the best combination with minimal conflicts
        best_schedule = self._find_optimal_schedule(available_options)
        
        return best_schedule
    
    def _find_optimal_schedule(self, available_options: Dict) -> Dict:
        """Find optimal schedule with minimal conflicts.
        
        Args:
            available_options: Dictionary of course options
            
        Returns:
            Optimal schedule information
        """
        from itertools import product
        
        courses = list(available_options.keys())
        if not courses:
            return {'schedule': pd.DataFrame(), 'conflicts': [], 'success': False}
        
        # Generate all possible combinations
        option_lists = []
        for course in courses:
            if course in available_options and not available_options[course].empty:
                # Group by section to get unique section options
                sections = available_options[course]['Section'].unique()
                course_options = []
                for section in sections:
                    section_data = available_options[course][available_options[course]['Section'] == section]
                    course_options.append(section_data)
                option_lists.append(course_options)
            else:
                option_lists.append([pd.DataFrame()])  # Empty option if course not available
        
        if not option_lists:
            return {'schedule': pd.DataFrame(), 'conflicts': [], 'success': False}
        
        best_combination = None
        min_conflicts = float('inf')
        
        # Try different combinations (limit to prevent performance issues)
        combinations_to_try = min(100, len(list(product(*option_lists))))
        
        for combination in list(product(*option_lists))[:combinations_to_try]:
            # Combine all DataFrames in this combination
            schedule_parts = [part for part in combination if not part.empty]
            if schedule_parts:
                test_schedule = pd.concat(schedule_parts, ignore_index=True)
                
                # Count conflicts in this combination
                conflicts = self._count_schedule_conflicts(test_schedule)
                
                if len(conflicts) < min_conflicts:
                    min_conflicts = len(conflicts)
                    best_combination = test_schedule
        
        if best_combination is not None:
            final_conflicts = self._count_schedule_conflicts(best_combination)
            return {
                'schedule': best_combination,
                'conflicts': final_conflicts,
                'success': len(final_conflicts) == 0,
                'total_courses': len(courses),
                'scheduled_courses': len(best_combination['Course'].unique()) if not best_combination.empty else 0
            }
        else:
            return {'schedule': pd.DataFrame(), 'conflicts': [], 'success': False}
    
    def _count_schedule_conflicts(self, schedule_df: pd.DataFrame) -> List[Dict]:
        """Count conflicts in a given schedule.
        
        Args:
            schedule_df: Schedule DataFrame
            
        Returns:
            List of conflicts
        """
        conflicts = []
        
        for day in schedule_df['Day'].unique():
            day_classes = schedule_df[schedule_df['Day'] == day].copy()
            
            # Parse times
            time_data = day_classes['Time'].apply(self._parse_time_slot)
            day_classes['start_time'] = [t[0] for t in time_data]
            day_classes['end_time'] = [t[1] for t in time_data]
            
            # Check for overlaps
            for i in range(len(day_classes)):
                for j in range(i + 1, len(day_classes)):
                    class1 = day_classes.iloc[i]
                    class2 = day_classes.iloc[j]
                    
                    if self._times_overlap(class1['start_time'], class1['end_time'],
                                         class2['start_time'], class2['end_time']):
                        conflicts.append({
                            'day': day,
                            'course1': class1['Course'],
                            'course2': class2['Course'],
                            'time1': class1['Time'],
                            'time2': class2['Time'],
                            'section1': class1['Section'],
                            'section2': class2['Section']
                        })
        
        return conflicts
    
    def store_processed_data(self, df: pd.DataFrame):
        """Store processed data for conflict checking.
        
        Args:
            df: Processed DataFrame to store
        """
        self._processed_data = df 