"""
Timetable API Endpoints
Handles timetable upload, filtering, and schedule management
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from timetable.timetable_processor import TimetableProcessor

timetable_bp = Blueprint('timetable', __name__)

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# In-memory storage for processed timetables (move to database in production)
user_timetables = {}

# Test data for development
test_timetable_data = {
    'test_user': {
        'test_timetable': {
            'id': 'test_timetable',
            'files': [{'filename': 'test_timetable.xlsx'}],
            'processed_data': {
                'test_timetable.xlsx': [
                    {
                        'Course': 'CS2001',
                        'Section': 'A',
                        'Day': 'Monday',
                        'Time': '09:00-10:30',
                        'Type': 'Theory',
                        'Class': 'CS-101'
                    },
                    {
                        'Course': 'CS2001',
                        'Section': 'A',
                        'Day': 'Wednesday',
                        'Time': '09:00-10:30',
                        'Type': 'Theory',
                        'Class': 'CS-101'
                    },
                    {
                        'Course': 'CS2001',
                        'Section': 'A',
                        'Day': 'Friday',
                        'Time': '14:00-15:30',
                        'Type': 'Lab',
                        'Class': 'CS-Lab-1'
                    }
                ]
            },
            'created_at': '2024-01-01T00:00:00'
        }
    }
}


@timetable_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_timetable():
    """
    Upload timetable file(s)
    
    Form Data:
        files: One or more Excel/CSV files
    """
    try:
        username = get_jwt_identity()
        
        if 'files' not in request.files and 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No files provided'
            }), 400
        
        # Handle multiple files or single file
        files = request.files.getlist('files') if 'files' in request.files else [request.files['file']]
        
        uploaded_files = []
        processor = TimetableProcessor()
        
        for file in files:
            if file.filename == '':
                continue
            
            if not allowed_file(file.filename):
                return jsonify({
                    'success': False,
                    'error': f'Invalid file type: {file.filename}. Allowed: xlsx, xls, csv'
                }), 400
            
            # Save file
            filename = secure_filename(f"{username}_{file.filename}")
            upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'timetables')
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            uploaded_files.append({
                'filename': file.filename,
                'filepath': filepath
            })
        
        # Process files directly using file paths
        processed_data = {}
        print(f"Processing {len(uploaded_files)} files for user {username}")
        
        for uploaded_file in uploaded_files:
            try:
                print(f"Processing file: {uploaded_file['filename']} at {uploaded_file['filepath']}")
                
                # Process the file based on its extension
                if uploaded_file['filename'].endswith('.xlsx'):
                    df = processor._process_excel_file(uploaded_file['filepath'])
                elif uploaded_file['filename'].endswith('.csv'):
                    df = processor._process_csv_file(uploaded_file['filepath'])
                else:
                    print(f"Skipping unsupported file: {uploaded_file['filename']}")
                    continue
                
                print(f"Processed {uploaded_file['filename']}: {len(df)} rows")
                processed_data[uploaded_file['filename']] = df
                
            except Exception as e:
                print(f"Error processing {uploaded_file['filename']}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        # Store processed data
        if username not in user_timetables:
            user_timetables[username] = {}
        
        timetable_id = str(__import__('uuid').uuid4())
        print(f"Storing timetable {timetable_id} with {len(processed_data)} processed files")
        
        user_timetables[username][timetable_id] = {
            'id': timetable_id,
            'files': uploaded_files,
            'processed_data': processed_data,
            'created_at': __import__('datetime').datetime.now().isoformat()
        }
        
        print(f"Stored timetable data: {len(processed_data)} files, {sum(len(df) if hasattr(df, '__len__') else 0 for df in processed_data.values())} total rows")
        
        # Get statistics
        stats = {}
        for filename, df in processed_data.items():
            stats[filename] = {
                'total_entries': len(df),
                'unique_courses': df['Course'].nunique() if 'Course' in df.columns else 0,
                'unique_days': df['Day'].nunique() if 'Day' in df.columns else 0
            }
        
        return jsonify({
            'success': True,
            'message': 'Timetable uploaded successfully',
            'data': {
                'timetable_id': timetable_id,
                'files': [f['filename'] for f in uploaded_files],
                'statistics': stats
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to upload timetable',
            'message': str(e)
        }), 500


@timetable_bp.route('/test', methods=['GET'])
def get_test_timetables():
    """Get test timetables (no auth required for testing)"""
    try:
        # Return test data
        timetables_summary = [
            {
                'id': 'test_timetable',
                'files': ['test_timetable.xlsx'],
                'created_at': '2024-01-01T00:00:00'
            }
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'timetables': timetables_summary,
                'count': len(timetables_summary)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get test timetables',
            'message': str(e)
        }), 500


@timetable_bp.route('/', methods=['GET'])
@jwt_required()
def get_timetables():
    """Get all timetables for current user"""
    try:
        username = get_jwt_identity()
        
        timetables = user_timetables.get(username, {})
        
        # Return summary without full data
        timetables_summary = [
            {
                'id': tid,
                'files': [f['filename'] for f in t['files']],
                'created_at': t['created_at']
            }
            for tid, t in timetables.items()
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'timetables': timetables_summary,
                'count': len(timetables_summary)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get timetables',
            'message': str(e)
        }), 500


@timetable_bp.route('/debug', methods=['GET'])
def debug_timetables():
    """Debug endpoint to check stored timetables (no auth required)"""
    try:
        debug_info = {
            'user_timetables_keys': list(user_timetables.keys()),
            'user_timetables_count': len(user_timetables),
            'user_timetables_details': {}
        }
        
        for username, timetables in user_timetables.items():
            debug_info['user_timetables_details'][username] = {
                'timetable_ids': list(timetables.keys()),
                'timetable_count': len(timetables)
            }
            
            for tid, timetable in timetables.items():
                debug_info['user_timetables_details'][username][tid] = {
                    'files': [f['filename'] for f in timetable['files']],
                    'data_keys': list(timetable['processed_data'].keys()) if timetable['processed_data'] else [],
                    'data_count': sum(len(data) if isinstance(data, list) else 0 for data in timetable['processed_data'].values()) if timetable['processed_data'] else 0
                }
        
        return jsonify({
            'success': True,
            'debug_info': debug_info
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get debug info',
            'message': str(e)
        }), 500


@timetable_bp.route('/clear', methods=['POST'])
def clear_all_timetables():
    """Clear all timetable data (no auth required for testing)"""
    try:
        global user_timetables
        user_timetables = {}
        print("Cleared all timetable data")
        
        return jsonify({
            'success': True,
            'message': 'All timetable data cleared'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to clear timetable data',
            'message': str(e)
        }), 500


@timetable_bp.route('/test/<timetable_id>', methods=['GET'])
def get_test_timetable(timetable_id):
    """Get test timetable data (no auth required for testing)"""
    try:
        if timetable_id == 'test_timetable':
            timetable = test_timetable_data['test_user']['test_timetable']
            
            # Convert to JSON-serializable format
            processed_data_json = {}
            for filename, data in timetable['processed_data'].items():
                processed_data_json[filename] = data
            
            return jsonify({
                'success': True,
                'data': {
                    'id': timetable['id'],
                    'files': [f['filename'] for f in timetable['files']],
                    'data': processed_data_json,
                    'created_at': timetable['created_at']
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Test timetable not found'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get test timetable',
            'message': str(e)
        }), 500


@timetable_bp.route('/<timetable_id>', methods=['GET'])
@jwt_required()
def get_timetable(timetable_id):
    """Get specific timetable"""
    try:
        username = get_jwt_identity()
        
        if username not in user_timetables or timetable_id not in user_timetables[username]:
            return jsonify({
                'success': False,
                'error': 'Timetable not found'
            }), 404
        
        timetable = user_timetables[username][timetable_id]
        
        # Convert DataFrame to JSON-serializable format
        processed_data_json = {}
        for filename, df in timetable['processed_data'].items():
            processed_data_json[filename] = df.to_dict(orient='records')
        
        return jsonify({
            'success': True,
            'data': {
                'id': timetable['id'],
                'files': [f['filename'] for f in timetable['files']],
                'data': processed_data_json,
                'created_at': timetable['created_at']
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get timetable',
            'message': str(e)
        }), 500


@timetable_bp.route('/<timetable_id>/filter', methods=['POST'])
@jwt_required()
def filter_timetable(timetable_id):
    """
    Filter timetable by courses and departments
    
    Request Body:
    {
        "courses": ["CS101", "MATH201"],
        "departments": ["Computer Science", "Mathematics"]
    }
    """
    try:
        username = get_jwt_identity()
        
        if username not in user_timetables or timetable_id not in user_timetables[username]:
            return jsonify({
                'success': False,
                'error': 'Timetable not found'
            }), 404
        
        data = request.get_json()
        courses = data.get('courses', [])
        departments = data.get('departments', [])
        
        timetable = user_timetables[username][timetable_id]
        processor = TimetableProcessor()
        
        # Filter each processed file
        filtered_results = {}
        for filename, df in timetable['processed_data'].items():
            filtered_df = processor.filter_timetable(df, courses, departments)
            filtered_results[filename] = filtered_df.to_dict(orient='records')
        
        return jsonify({
            'success': True,
            'data': {
                'filtered_data': filtered_results,
                'filters_applied': {
                    'courses': courses,
                    'departments': departments
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to filter timetable',
            'message': str(e)
        }), 500


@timetable_bp.route('/<timetable_id>/conflicts', methods=['POST'])
@jwt_required()
def check_conflicts(timetable_id):
    """
    Check for time conflicts in selected courses
    
    Request Body:
    {
        "courses": ["CS101", "MATH201"]
    }
    """
    try:
        username = get_jwt_identity()
        
        if username not in user_timetables or timetable_id not in user_timetables[username]:
            return jsonify({
                'success': False,
                'error': 'Timetable not found'
            }), 404
        
        data = request.get_json()
        courses = data.get('courses', [])
        
        timetable = user_timetables[username][timetable_id]
        processor = TimetableProcessor()
        
        # Get first dataframe (assuming single source)
        df = list(timetable['processed_data'].values())[0]
        
        # Filter by selected courses
        filtered_df = processor.filter_timetable(df, courses, [])
        
        # Check conflicts
        conflicts = processor.check_time_conflicts(filtered_df)
        
        return jsonify({
            'success': True,
            'data': {
                'has_conflicts': len(conflicts) > 0,
                'conflicts': conflicts,
                'count': len(conflicts)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to check conflicts',
            'message': str(e)
        }), 500


@timetable_bp.route('/<timetable_id>/stats', methods=['GET'])
@jwt_required()
def get_statistics(timetable_id):
    """Get timetable statistics"""
    try:
        username = get_jwt_identity()
        
        if username not in user_timetables or timetable_id not in user_timetables[username]:
            return jsonify({
                'success': False,
                'error': 'Timetable not found'
            }), 404
        
        timetable = user_timetables[username][timetable_id]
        processor = TimetableProcessor()
        
        # Get statistics for each file
        all_stats = {}
        for filename, df in timetable['processed_data'].items():
            stats = processor.get_course_statistics(df)
            all_stats[filename] = stats
        
        return jsonify({
            'success': True,
            'data': all_stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get statistics',
            'message': str(e)
        }), 500




