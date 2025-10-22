"""
Ratings management tab
Handles rating CRUD operations and filtering
"""

import tkinter as tk
from tkinter import ttk, messagebox
from db import ratings_dao, users_dao, books_dao
from ui.dialogs import AddRatingDialog, EditRatingDialog


class RatingsTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, padding="10")
        self.setup_ui()
        self.load_ratings()
    
    def setup_ui(self):
        """Setup the UI components"""
        # Filter frame
        filter_frame = ttk.LabelFrame(self.frame, text="Filter Ratings", padding="10")
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Filter fields
        ttk.Label(filter_frame, text="User ID:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.user_id_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.user_id_var, width=15).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(filter_frame, text="ISBN:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.isbn_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.isbn_var, width=15).grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(filter_frame, text="Min Rating:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.min_rating_var = tk.StringVar()
        ttk.Combobox(filter_frame, textvariable=self.min_rating_var, width=5, 
                    values=[''] + list(range(1, 11))).grid(row=0, column=5, padx=(0, 10))
        
        # Filter buttons
        ttk.Button(filter_frame, text="Filter", command=self.filter_ratings).grid(row=0, column=6, padx=5)
        ttk.Button(filter_frame, text="Clear", command=self.clear_filter).grid(row=0, column=7, padx=5)
        
        # Ratings table frame
        table_frame = ttk.Frame(self.frame)
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        
        # Treeview
        columns = ("Rating ID", "User ID", "Username", "ISBN", "Book Title", "Rating")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Configure columns
        self.tree.heading("Rating ID", text="Rating ID")
        self.tree.heading("User ID", text="User ID")
        self.tree.heading("Username", text="Username")
        self.tree.heading("ISBN", text="ISBN")
        self.tree.heading("Book Title", text="Book Title")
        self.tree.heading("Rating", text="Rating")
        
        self.tree.column("Rating ID", width=80)
        self.tree.column("User ID", width=80)
        self.tree.column("Username", width=120)
        self.tree.column("ISBN", width=100)
        self.tree.column("Book Title", width=300)
        self.tree.column("Rating", width=80)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Add Rating", command=self.add_rating).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Edit Rating", command=self.edit_rating).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete Rating", command=self.delete_rating).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Refresh", command=self.refresh).pack(side=tk.RIGHT, padx=5)
    
    def load_ratings(self, ratings=None):
        """Load ratings into the table"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if ratings is None:
            ratings = ratings_dao.get_ratings(limit=500)
        
        if ratings:
            for rating in ratings:
                self.tree.insert("", tk.END, values=(
                    rating.get('rating_id', ''),
                    rating.get('user_id', ''),
                    rating.get('username', ''),
                    rating.get('ISBN', ''),
                    rating.get('book_title', ''),
                    rating.get('rating', '')
                ))
    
    def filter_ratings(self):
        """Filter ratings based on criteria"""
        user_id = self.user_id_var.get().strip()
        isbn = self.isbn_var.get().strip()
        min_rating = self.min_rating_var.get().strip()
        
        # Validate inputs
        if user_id:
            try:
                user_id = int(user_id)
            except ValueError:
                messagebox.showerror("Error", "User ID must be a number")
                return
        else:
            user_id = None
        
        if isbn:
            isbn = isbn
        else:
            isbn = None
        
        if min_rating:
            try:
                min_rating = int(min_rating)
            except ValueError:
                messagebox.showerror("Error", "Min rating must be a number")
                return
        else:
            min_rating = None
        
        ratings = ratings_dao.get_ratings(
            user_id=user_id,
            isbn=isbn,
            min_rating=min_rating,
            limit=500
        )
        
        self.load_ratings(ratings)
        messagebox.showinfo("Filter Results", f"Found {len(ratings) if ratings else 0} ratings")
    
    def clear_filter(self):
        """Clear filter fields and reload all ratings"""
        self.user_id_var.set("")
        self.isbn_var.set("")
        self.min_rating_var.set("")
        self.load_ratings()
    
    def add_rating(self):
        """Open add rating dialog"""
        dialog = AddRatingDialog(self.frame)
        if dialog.result:
            self.refresh()
            messagebox.showinfo("Success", "Rating added successfully!")
    
    def edit_rating(self):
        """Open edit rating dialog"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a rating to edit")
            return
        
        item = self.tree.item(selection[0])
        rating_id = item['values'][0]
        
        dialog = EditRatingDialog(self.frame, rating_id)
        if dialog.result:
            self.refresh()
            messagebox.showinfo("Success", "Rating updated successfully!")
    
    def delete_rating(self):
        """Delete selected rating"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a rating to delete")
            return
        
        item = self.tree.item(selection[0])
        rating_id = item['values'][0]
        username = item['values'][2]
        book_title = item['values'][4]
        
        if messagebox.askyesno("Confirm Delete", 
                               f"Delete rating by '{username}' for '{book_title}'?"):
            if ratings_dao.delete_rating(rating_id):
                self.refresh()
                messagebox.showinfo("Success", "Rating deleted successfully!")
            else:
                messagebox.showerror("Error", "Failed to delete rating")
    
    def refresh(self):
        """Refresh the ratings list"""
        self.clear_filter()