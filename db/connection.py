import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG


class DBConnection:
    """Singleton database connection manager"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.config = DB_CONFIG
    
    def get_connection(self):
        """Create and return a new database connection"""
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except Error as e:
            print(f"Error connecting to database: {e}")
            raise
    
    def execute_query(self, query, params=None, fetch_one=False):
        """
        Execute a SELECT query and return results
        
        Args:
            query: SQL query string
            params: Query parameters (tuple or dict)
            fetch_one: If True, return single row; else return all rows
            
        Returns:
            List of tuples (or single tuple if fetch_one=True), or None on error
        """
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch_one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
            
            return result
            
        except Error as e:
            print(f"Error executing query: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            return None
            
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def execute_update(self, query, params=None, return_lastrowid=False):
        """
        Execute INSERT, UPDATE, or DELETE query
        
        Args:
            query: SQL query string
            params: Query parameters
            return_lastrowid: If True, return last inserted ID
            
        Returns:
            Number of affected rows (or last inserted ID), or None on error
        """
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params or ())
            connection.commit()
            
            if return_lastrowid:
                return cursor.lastrowid
            else:
                return cursor.rowcount
                
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error executing update: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            return None
            
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def execute_many(self, query, params_list):
        """
        Execute batch INSERT/UPDATE/DELETE
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Total affected rows, or None on error
        """
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.executemany(query, params_list)
            connection.commit()
            return cursor.rowcount
            
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error executing batch: {e}")
            return None
            
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def execute_transaction(self, operations):
        """
        Execute multiple operations in a transaction
        
        Args:
            operations: List of (query, params) tuples
            
        Returns:
            True on success, False on error
        """
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Start transaction
            connection.start_transaction()
            
            # Execute all operations
            for query, params in operations:
                cursor.execute(query, params or ())
            
            # Commit transaction
            connection.commit()
            return True
            
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Transaction error: {e}")
            return False
            
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()


# Create singleton instance
db = DBConnection()