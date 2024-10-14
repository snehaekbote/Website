# import mysql.connector
# from mysql.connector import Error

# def create_connection():
#     """ Create a database connection to a MySQL database """
#     connection = None
#     try:
#         connection = mysql.connector.connect(
#             host='13.234.113.49',
#             user='admin',
#             password='Admin#235',
#             database='turtu_website'
#         )
#         if connection.is_connected():
#             print("Connection successful!")
#     except Error as e:
#         print(f"The error '{e}' occurred")
#     finally:
#         if connection:
#             connection.close()

# if __name__ == "__main__":
#     create_connection()
