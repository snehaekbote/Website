from flask import Blueprint, jsonify, send_file
from config.config import Config
from sqlalchemy import create_engine
import pandas as pd
import openpyxl

data_bp = Blueprint('data', __name__)

def create_engine_from_config():
    try:
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        print("Successfully connected to the database")
        return engine
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Function to export multiple tables to an Excel file
def export_multiple_tables_to_excel(engine, tables, output_file):
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            for table_name in tables:
                query = f"SELECT * FROM {table_name}"
                data_frame = pd.read_sql(query, engine)
                data_frame.to_excel(writer, sheet_name=table_name, index=False)
        print(f"Data from all tables successfully exported to {output_file}")
        return output_file
    except Exception as e:
        print(f"Error exporting data: {e}")
        return None
    
@data_bp.route('/export-data', methods=['GET'])
def export_data_route():
    try:
        # Create SQLAlchemy engine
        engine = create_engine_from_config()
        if engine is None:
            return jsonify({'error': 'Failed to connect to the database'}), 500

        # Define tables to export
        tables = ["career_applications", "contacts", "users"]  # Replace with actual table names
        excel_file = "api_export_automated.xlsx"

        # Export the data
        file_path = export_multiple_tables_to_excel(engine, tables, excel_file)
        if file_path:
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({"error": "Failed to export data"}), 500

    except Exception as e:
        return jsonify({'error': str(e)})