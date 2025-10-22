"""
Database package
Contains all data access objects and connection management
"""

# Just import the connection - let other modules import what they need directly
from db.connection import db, DBConnection

__all__ = ['db', 'DBConnection']