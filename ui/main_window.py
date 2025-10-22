"""
Main application window
Contains notebook with tabs for different sections
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ui.books_tab import BooksTab
from ui.users_tab import UsersTab
from ui.ratings_tab import RatingsTab
from ui.clubs_tab import ClubsTab
from ui.analytics_tab import AnalyticsTab


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Club Management App")
        self.root.geometry("1200x800")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Book Club Management App",
            font=('Helvetica', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self.books_tab = BooksTab(self.notebook)
        self.users_tab = UsersTab(self.notebook)
        self.ratings_tab = RatingsTab(self.notebook)
        self.clubs_tab = ClubsTab(self.notebook)
        self.analytics_tab = AnalyticsTab(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.books_tab.frame, text=" Books")
        self.notebook.add(self.users_tab.frame, text=" Users")
        self.notebook.add(self.ratings_tab.frame, text=" Ratings")
        self.notebook.add(self.clubs_tab.frame, text=" Clubs")
        self.notebook.add(self.analytics_tab.frame, text=" Analytics")
        
    
    def refresh_all(self):
        """Refresh all tabs"""
        try:
            self.books_tab.refresh()
            self.users_tab.refresh()
            self.ratings_tab.refresh()
            self.clubs_tab.refresh()
            messagebox.showinfo("Success", "All data refreshed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh data:\n{str(e)}")
