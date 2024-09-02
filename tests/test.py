from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://admin:Admin#235@13.234.113.49/turtu_website')

try:
    connection = engine.connect()
    print("Connected to MySQL using SQLAlchemy")
except Exception as e:
    print(f"SQLAlchemy connection error: {e}")
finally:
    connection.close()
