# from flask import Blueprint, jsonify, send_file, send_from_directory, abort
# from config.config import Config
# from sqlalchemy import create_engine
# import pandas as pd
# import openpyxl
# import os

# data_bp = Blueprint('data', __name__)

# def create_engine_from_config():
#     try:
#         engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
#         print("Successfully connected to the database")
#         return engine
#     except Exception as e:
#         print(f"Error connecting to database: {e}")
#         return None

# def export_multiple_tables_to_excel(engine, tables, output_file):
#     try:
#         # Base URL for downloading resumes (adjust as per your app's URL)
#         base_url = "http://localhost:5000/download_resume/"  # Change this to your actual domain

#         with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
#             for table_name in tables:
#                 query = f"SELECT * FROM {table_name}"
#                 data_frame = pd.read_sql(query, engine)

#                 # Modify resume_filename column to include clickable links (for career_applications table)
#                 if table_name == "career_applications" and 'resume_filename' in data_frame.columns:
#                     data_frame['resume_filename'] = data_frame['resume_filename'].apply(
#                         lambda filename: f'=HYPERLINK("{base_url}{filename}", "{filename}")'
#                     )

#                 # Write the dataframe to Excel
#                 data_frame.to_excel(writer, sheet_name=table_name, index=False)

#         print(f"Data from all tables successfully exported to {output_file}")
#         return output_file
#     except Exception as e:
#         print(f"Error exporting data: {e}")
#         return None

# UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
# print(f"Upload folder set to: {UPLOAD_FOLDER}")

# @data_bp.route('/download_resume/<filename>', methods=['GET'])
# def download_resume(filename):
#     print(f"Hyperlink for filename: {filename}")

#     try:
#         file_path = os.path.join(UPLOAD_FOLDER, filename)
#         print(f"Looking for file at: {file_path}")  # Debugging line
#         if os.path.exists(file_path):
#             return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
#         else:
#             abort(404, description="File not found")
#     except Exception as e:
#         abort(500, description=f"Error while trying to download file: {str(e)}")

# @data_bp.route('/export-data', methods=['GET'])
# def export_data_route():
#     try:
#         engine = create_engine_from_config()
#         if engine is None:
#             return jsonify({'error': 'Failed to connect to the database'}), 500

#         tables = ["career_applications", "contacts", "users"]
#         excel_file = "api_export_automated.xlsx"

#         # Ensure the output file is created in a writable directory
#         file_path = export_multiple_tables_to_excel(engine, tables, excel_file)
#         if file_path:
#             return send_file(file_path, as_attachment=True)
#         else:
#             return jsonify({"error": "Failed to export data"}), 500

#     except Exception as e:
#         return jsonify({'error': str(e)})
