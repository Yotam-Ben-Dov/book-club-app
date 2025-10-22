#!/usr/bin/env python3
"""
Book Club Management System
Main application entry point
"""

import tkinter as tk
from tkinter import messagebox
import sys
import traceback

# Test database connection first
try:
    from db.connection import db
    # Test connection
    result = db.execute_query("SELECT DATABASE()", fetch_one=True)
    if result:
        print(f"✓ Connected to database: {result.get('DATABASE()')}")
    else:
        print("✗ Database connection failed")
        sys.exit(1)
except Exception as e:
    print(f"✗ Error connecting to database: {e}")
    traceback.print_exc()
    sys.exit(1)

from ui.main_window import MainWindow


def main():
    """Main application entry point"""
    try:
        root = tk.Tk()
        app = MainWindow(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application error:\n{str(e)}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()