"""
Dialog windows for add/edit operations
All CRUD dialogs for the application
"""

import tkinter as tk
from tkinter import ttk, messagebox
from db import (books_dao, users_dao, ratings_dao, clubs_dao)
from core.validators import *


# ==================== BOOK DIALOGS ====================

class AddBookDialog:
    def __init__(self, parent):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Book")
        self.dialog.geometry("500x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.dialog.wait_window()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Add New Book", font=('Helvetica', 12, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=(0, 20))
        
        # ISBN
        ttk.Label(frame, text="*ISBN:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.isbn_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.isbn_var, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Title
        ttk.Label(frame, text="*Title:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.title_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.title_var, width=30).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Authors (comma-separated)
        ttk.Label(frame, text="*Authors:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.authors_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.authors_var, width=30).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(frame, text="(comma-separated for multiple)", font=('Helvetica', 8)).grid(
            row=4, column=1, sticky=tk.W)
        
        # Publisher
        ttk.Label(frame, text="Publisher:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.publisher_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.publisher_var, width=30).grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Year
        ttk.Label(frame, text="Year:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.year_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.year_var, width=30).grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Image URL
        ttk.Label(frame, text="Image URL:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.image_url_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.image_url_var, width=30).grid(row=7, column=1, sticky=(tk.W, tk.E), pady=5)
        
        frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        isbn = self.isbn_var.get().strip()
        title = self.title_var.get().strip()
        authors_str = self.authors_var.get().strip()
        publisher = self.publisher_var.get().strip() or None
        year = self.year_var.get().strip() or None
        image_url = self.image_url_var.get().strip() or None
        
        # Validate
        valid, msg = validate_isbn(isbn)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return
        
        valid, msg = validate_title(title)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return
        
        if not authors_str:
            messagebox.showerror("Validation Error", "At least one author is required")
            return
        
        # Parse authors
        authors = [a.strip() for a in authors_str.split(',') if a.strip()]
        
        if year:
            valid, msg = validate_year(year)
            if not valid:
                messagebox.showerror("Validation Error", msg)
                return
            year = int(year)
        
        # Add book
        if books_dao.add_book(isbn, title, authors, publisher, year, image_url):
            self.result = True
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to add book. ISBN may already exist.")


class EditBookDialog:
    def __init__(self, parent, isbn):
        self.result = None
        self.isbn = isbn
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Book")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Load book data
        self.book = books_dao.get_book_by_isbn(isbn)
        if not self.book:
            messagebox.showerror("Error", "Book not found")
            self.dialog.destroy()
            return
        
        self.setup_ui()
        self.dialog.wait_window()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text=f"Edit Book", font=('Helvetica', 12, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=(0, 10))
        ttk.Label(frame, text=f"ISBN: {self.isbn}").grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Title
        ttk.Label(frame, text="Title:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.title_var = tk.StringVar(value=self.book.get('title', ''))
        ttk.Entry(frame, textvariable=self.title_var, width=30).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Publisher
        ttk.Label(frame, text="Publisher:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.publisher_var = tk.StringVar(value=self.book.get('publisher_name', ''))
        ttk.Entry(frame, textvariable=self.publisher_var, width=30).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Year
        ttk.Label(frame, text="Year:").grid(row=4, column=0, sticky=tk.W, pady=5)
        year_val = self.book.get('year_of_publication')
        self.year_var = tk.StringVar(value=str(year_val) if year_val else '')
        ttk.Entry(frame, textvariable=self.year_var, width=30).grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Image URL
        ttk.Label(frame, text="Image URL:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.image_url_var = tk.StringVar(value=self.book.get('image_url', ''))
        ttk.Entry(frame, textvariable=self.image_url_var, width=30).grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        
        frame.columnconfigure(1, weight=1)
        
        # Note about authors
        ttk.Label(frame, text="Note: Authors cannot be edited here", 
                 font=('Helvetica', 8, 'italic')).grid(row=6, column=0, columnspan=2, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        title = self.title_var.get().strip()
        publisher = self.publisher_var.get().strip() or None
        year = self.year_var.get().strip() or None
        image_url = self.image_url_var.get().strip() or None
        
        # Validate
        valid, msg = validate_title(title)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return
        
        if year:
            valid, msg = validate_year(year)
            if not valid:
                messagebox.showerror("Validation Error", msg)
                return
            year = int(year)
        
        # Update book
        if books_dao.update_book(self.isbn, title, year, publisher, image_url):
            self.result = True
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to update book")


class BookDetailsDialog:
    def __init__(self, parent, isbn):
        self.isbn = isbn
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Book Details")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        
        # Load book data
        self.book = books_dao.get_book_by_isbn(isbn)
        if not self.book:
            messagebox.showerror("Error", "Book not found")
            self.dialog.destroy()
            return
        
        self.setup_ui()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(frame, text=self.book.get('title', 'Unknown'), 
                 font=('Helvetica', 14, 'bold'), wraplength=550).pack(pady=(0, 10))
        
        # Details
        details_frame = ttk.LabelFrame(frame, text="Book Information", padding="10")
        details_frame.pack(fill=tk.X, pady=10)
        
        info = [
            ("ISBN:", self.book.get('ISBN', 'N/A')),
            ("Authors:", self.book.get('authors', 'Unknown')),
            ("Publisher:", self.book.get('publisher_name', 'Unknown')),
            ("Year:", str(self.book.get('year_of_publication', 'N/A'))),
            ("Average Rating:", f"{self.book.get('avg_rating', 0):.2f}" if self.book.get('avg_rating') else 'No ratings'),
            ("Total Ratings:", str(self.book.get('rating_count', 0)))
        ]
        
        for i, (label, value) in enumerate(info):
            ttk.Label(details_frame, text=label, font=('Helvetica', 10, 'bold')).grid(
                row=i, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            ttk.Label(details_frame, text=value, wraplength=400).grid(row=i, column=1, sticky=tk.W, pady=5)
        
        # Rating distribution
        ratings_frame = ttk.LabelFrame(frame, text="Rating Distribution", padding="10")
        ratings_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        from db import simple_queries_dao
        distribution = simple_queries_dao.get_rating_distribution_for_book(self.isbn)
        
        if distribution:
            for item in distribution:
                rating = item.get('rating')
                count = item.get('count')
                bar = "█" * int(count / 2)  # Simple bar chart
                ttk.Label(ratings_frame, text=f"{rating:2d} ⭐: {bar} ({count})").pack(anchor=tk.W, pady=2)
        else:
            ttk.Label(ratings_frame, text="No ratings yet").pack()
        
        # Close button
        ttk.Button(frame, text="Close", command=self.dialog.destroy).pack(pady=10)


# ==================== USER DIALOGS ====================

class AddUserDialog:
    def __init__(self, parent):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add User")
        self.dialog.geometry("450x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.dialog.wait_window()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Add New User", font=('Helvetica', 12, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=(0, 20))
        
        # User ID
        ttk.Label(frame, text="*User ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.user_id_var = tk.StringVar()
        # Auto-suggest next ID
        next_id = users_dao.get_next_user_id()
        self.user_id_var.set(str(next_id))
        ttk.Entry(frame, textvariable=self.user_id_var, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Username
        ttk.Label(frame, text="*Username:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.username_var, width=30).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Password
        ttk.Label(frame, text="*Password:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.password_var, width=30, show="*").grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Location
        ttk.Label(frame, text="*Location:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.location_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.location_var, width=30).grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(frame, text="(e.g., City, State, Country)", font=('Helvetica', 8)).grid(
            row=5, column=1, sticky=tk.W)
        
        # Birth Year
        ttk.Label(frame, text="*Birth Year:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.birth_year_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.birth_year_var, width=30).grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5)
        
        frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        user_id = self.user_id_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        location = self.location_var.get().strip()
        birth_year = self.birth_year_var.get().strip()
        
        # Validate
        valid, msg = validate_user_id(user_id)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return
        user_id = int(user_id)
        
        valid, msg = validate_username(username)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return
        
        valid, msg = validate_password(password)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return
        
        valid, msg = validate_location(location)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return
        
        valid, msg = validate_birth_year(birth_year)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return
        birth_year = int(birth_year)
        
        # Add user
        if users_dao.add_user(user_id, username, password, location, birth_year):
            self.result = True
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to add user. User ID or username may already exist.")


class EditUserDialog:
    def __init__(self, parent, user_id):
        self.result = None
        self.user_id = user_id
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit User")
        self.dialog.geometry("450x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Load user data
        self.user = users_dao.get_user_by_id(user_id)
        if not self.user:
            messagebox.showerror("Error", "User not found")
            self.dialog.destroy()
            return
        
        self.setup_ui()
        self.dialog.wait_window()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text=f"Edit User: {self.user.get('username')}", 
                 font=('Helvetica', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Username
        ttk.Label(frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar(value=self.user.get('username', ''))
        ttk.Entry(frame, textvariable=self.username_var, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Password
        ttk.Label(frame, text="New Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.password_var, width=30, show="*").grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(frame, text="(leave empty to keep current)", font=('Helvetica', 8)).grid(
            row=3, column=1, sticky=tk.W)
        
        # Location
        ttk.Label(frame, text="Location:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.location_var = tk.StringVar(value=self.user.get('location', ''))
        ttk.Entry(frame, textvariable=self.location_var, width=30).grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Birth Year
        ttk.Label(frame, text="Birth Year:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.birth_year_var = tk.StringVar(value=str(self.user.get('birth_year', '')))
        ttk.Entry(frame, textvariable=self.birth_year_var, width=30).grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        
        frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip() or None
        location = self.location_var.get().strip()
        birth_year = self.birth_year_var.get().strip()
        
        # Validate
        valid, msg = validate_username(username)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return
        
        if password:
            valid, msg = validate_password(password)
            if not valid:
                messagebox.showerror("Validation Error", msg)
                return
        
        valid, msg = validate_location(location)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return
        
        valid, msg = validate_birth_year(birth_year)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return
        birth_year = int(birth_year)
        
        # Update user
        if users_dao.update_user(self.user_id, username, password, location, birth_year):
            self.result = True
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to update user")


class UserStatisticsDialog:
    def __init__(self, parent, user_id):
        self.user_id = user_id
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("User Statistics")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        
        # Load statistics
        self.stats = users_dao.get_user_reading_statistics(user_id)
        if not self.stats:
            messagebox.showerror("Error", "Could not load user statistics")
            self.dialog.destroy()
            return
        
        self.setup_ui()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(frame, text=f"Statistics for: {self.stats.get('username')}", 
                 font=('Helvetica', 14, 'bold')).pack(pady=(0, 20))
        
        # Statistics
        stats_frame = ttk.LabelFrame(frame, text="Reading Statistics", padding="10")
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        stats_info = [
            ("Books Rated:", str(self.stats.get('books_rated', 0))),
            ("Average Rating Given:", f"{self.stats.get('avg_rating_given', 0):.2f}" if self.stats.get('avg_rating_given') else 'N/A'),
            ("Unique Authors Read:", str(self.stats.get('unique_authors_rated', 0))),
            ("Favorite Author:", self.stats.get('favorite_author', 'N/A'))
        ]
        
        for i, (label, value) in enumerate(stats_info):
            ttk.Label(stats_frame, text=label, font=('Helvetica', 10, 'bold')).grid(
                row=i, column=0, sticky=tk.W, pady=10, padx=(0, 20))
            ttk.Label(stats_frame, text=value, font=('Helvetica', 10)).grid(
                row=i, column=1, sticky=tk.W, pady=10)
        
        # Get clubs
        clubs = clubs_dao.get_user_clubs(self.user_id)
        
        clubs_frame = ttk.LabelFrame(frame, text="Club Memberships", padding="10")
        clubs_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        if clubs:
            for club in clubs:
                club_text = f"• {club.get('name')} ({club.get('role')})"
                ttk.Label(clubs_frame, text=club_text).pack(anchor=tk.W, pady=2)
        else:
            ttk.Label(clubs_frame, text="Not a member of any clubs").pack()
        
        # Close button
        ttk.Button(frame, text="Close", command=self.dialog.destroy).pack(pady=(10, 0))


# ==================== RATING DIALOGS ====================

class AddRatingDialog:
    def __init__(self, parent):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Rating")
        self.dialog.geometry("450x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.dialog.wait_window()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Add New Rating", font=('Helvetica', 12, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=(0, 20))
        
        # User ID
        ttk.Label(frame, text="*User ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.user_id_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.user_id_var, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # ISBN
        ttk.Label(frame, text="*ISBN:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.isbn_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.isbn_var, width=30).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Rating
        ttk.Label(frame, text="*Rating (0-10):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.rating_var = tk.StringVar()
        ttk.Combobox(frame, textvariable=self.rating_var, width=28, 
                    values=list(range(0, 11)), state='readonly').grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        user_id = self.user_id_var.get().strip()
        isbn = self.isbn_var.get().strip()
        rating = self.rating_var.get().strip()
        
        # Validate
        valid, msg = validate_user_id(user_id)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return
        user_id = int(user_id)
        
        valid, msg = validate_isbn(isbn)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return
        
        valid, msg = validate_rating(rating)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return
        rating = int(rating)
        
        # Check if user exists
        if not users_dao.get_user_by_id(user_id):
            messagebox.showerror("Error", "User ID does not exist")
            return
        
        # Check if book exists
        if not books_dao.get_book_by_isbn(isbn):
            messagebox.showerror("Error", "ISBN does not exist")
            return
        
        # Add rating
        if ratings_dao.add_rating(user_id, isbn, rating):
            self.result = True
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to add rating")


class EditRatingDialog:
    def __init__(self, parent, rating_id):
        self.result = None
        self.rating_id = rating_id
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Rating")
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Load rating data
        self.rating = ratings_dao.get_rating_by_id(rating_id)
        if not self.rating:
            messagebox.showerror("Error", "Rating not found")
            self.dialog.destroy()
            return
        
        self.setup_ui()
        self.dialog.wait_window()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Edit Rating", font=('Helvetica', 12, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Display info
        ttk.Label(frame, text=f"User: {self.rating.get('username')}").grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        ttk.Label(frame, text=f"Book: {self.rating.get('book_title')}").grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Rating
        ttk.Label(frame, text="New Rating (0-10):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.rating_var = tk.StringVar(value=str(self.rating.get('rating', '')))
        ttk.Combobox(frame, textvariable=self.rating_var, width=28, 
                    values=list(range(0, 11)), state='readonly').grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        rating = self.rating_var.get().strip()
        
        # Validate
        valid, msg = validate_rating(rating)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return
        rating = int(rating)
        
        # Update rating
        if ratings_dao.update_rating(self.rating_id, rating):
            self.result = True
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to update rating")


# ==================== CLUB DIALOGS ====================

class AddClubDialog:
    def __init__(self, parent):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create Book Club")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.dialog.wait_window()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Create New Book Club", font=('Helvetica', 12, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Club Name
        ttk.Label(frame, text="*Club Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var, width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Description
        ttk.Label(frame, text="Description:").grid(row=2, column=0, sticky=tk.NW, pady=5)
        self.description_text = tk.Text(frame, width=40, height=5)
        self.description_text.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Public/Private
        ttk.Label(frame, text="Club Type:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.is_public_var = tk.BooleanVar(value=True)
        public_frame = ttk.Frame(frame)
        public_frame.grid(row=3, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(public_frame, text="Public", variable=self.is_public_var, value=True).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(public_frame, text="Private", variable=self.is_public_var, value=False).pack(side=tk.LEFT, padx=5)
        
        # Creator User ID
        ttk.Label(frame, text="*Creator User ID:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.creator_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.creator_var, width=40).grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Max Members
        ttk.Label(frame, text="Max Members:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.max_members_var = tk.StringVar(value="50")
        ttk.Entry(frame, textvariable=self.max_members_var, width=40).grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        
        frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Create", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        name = self.name_var.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()
        is_public = self.is_public_var.get()
        creator = self.creator_var.get().strip()
        max_members = self.max_members_var.get().strip()
        
        # Validate
        valid, msg = validate_club_name(name)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return
        
        valid, msg = validate_user_id(creator)
        if not valid:
            messagebox.showerror("Validation Error", "Creator " + msg)
            return
        creator = int(creator)
        
        # Check if creator exists
        if not users_dao.get_user_by_id(creator):
            messagebox.showerror("Error", "Creator user ID does not exist")
            return
        
        if max_members:
            valid, msg = validate_max_members(max_members)
            if not valid:
                messagebox.showerror("Validation Error", msg)
                return
            max_members = int(max_members)
        else:
            max_members = 50
        
        # Create club
        club_id = clubs_dao.create_club(name, description, is_public, creator, max_members)
        if club_id:
            self.result = True
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to create club")


class EditClubDialog:
    def __init__(self, parent, club_id):
        self.result = None
        self.club_id = club_id
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Book Club")
        self.dialog.geometry("500x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Load club data
        self.club = clubs_dao.get_club_by_id(club_id)
        if not self.club:
            messagebox.showerror("Error", "Club not found")
            self.dialog.destroy()
            return
        
        self.setup_ui()
        self.dialog.wait_window()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text=f"Edit Club: {self.club.get('name')}", 
                 font=('Helvetica', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Club Name
        ttk.Label(frame, text="Club Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value=self.club.get('name', ''))
        ttk.Entry(frame, textvariable=self.name_var, width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Description
        ttk.Label(frame, text="Description:").grid(row=2, column=0, sticky=tk.NW, pady=5)
        self.description_text = tk.Text(frame, width=40, height=5)
        self.description_text.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        self.description_text.insert("1.0", self.club.get('description', ''))
        
        # Public/Private
        ttk.Label(frame, text="Club Type:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.is_public_var = tk.BooleanVar(value=self.club.get('is_public', True))
        public_frame = ttk.Frame(frame)
        public_frame.grid(row=3, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(public_frame, text="Public", variable=self.is_public_var, value=True).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(public_frame, text="Private", variable=self.is_public_var, value=False).pack(side=tk.LEFT, padx=5)
        
        # Max Members
        ttk.Label(frame, text="Max Members:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.max_members_var = tk.StringVar(value=str(self.club.get('max_members', 50)))
        ttk.Entry(frame, textvariable=self.max_members_var, width=40).grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        name = self.name_var.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()
        is_public = self.is_public_var.get()
        max_members = self.max_members_var.get().strip()
        
        # Validate
        valid, msg = validate_club_name(name)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return
        
        if max_members:
            valid, msg = validate_max_members(max_members)
            if not valid:
                messagebox.showerror("Validation Error", msg)
                return
            max_members = int(max_members)
        
        # Update club
        if clubs_dao.update_club(self.club_id, name, description, is_public, max_members):
            self.result = True
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to update club")


class ClubDetailsDialog:
    def __init__(self, parent, club_id):
        self.club_id = club_id
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Club Details")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        
        # Load club data
        self.club = clubs_dao.get_club_by_id(club_id)
        if not self.club:
            messagebox.showerror("Error", "Club not found")
            self.dialog.destroy()
            return
        
        self.setup_ui()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(frame, text=self.club.get('name', 'Unknown'), 
                 font=('Helvetica', 14, 'bold')).pack(pady=(0, 10))
        
        # Details
        details_frame = ttk.LabelFrame(frame, text="Club Information", padding="10")
        details_frame.pack(fill=tk.X, pady=10)
        
        info = [
            ("Club ID:", str(self.club.get('club_id', ''))),
            ("Creator:", self.club.get('creator_username', 'Unknown')),
            ("Type:", "Public" if self.club.get('is_public') else "Private"),
            ("Members:", str(self.club.get('member_count', 0))),
            ("Max Members:", str(self.club.get('max_members', 50))),
            ("Description:", self.club.get('description', 'No description'))
        ]
        
        for i, (label, value) in enumerate(info):
            ttk.Label(details_frame, text=label, font=('Helvetica', 10, 'bold')).grid(
                row=i, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            ttk.Label(details_frame, text=value, wraplength=400).grid(row=i, column=1, sticky=tk.W, pady=5)
        
        # Close button
        ttk.Button(frame, text="Close", command=self.dialog.destroy).pack(pady=10)


class AddClubMemberDialog:
    def __init__(self, parent, club_id):
        self.result = None
        self.club_id = club_id
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Club Member")
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.dialog.wait_window()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Add Member to Club", font=('Helvetica', 12, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=(0, 20))
        
        # User ID
        ttk.Label(frame, text="*User ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.user_id_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.user_id_var, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Role
        ttk.Label(frame, text="Role:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.role_var = tk.StringVar(value="member")
        ttk.Combobox(frame, textvariable=self.role_var, width=28, 
                    values=['member', 'moderator', 'admin'], state='readonly').grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Add", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        user_id = self.user_id_var.get().strip()
        role = self.role_var.get()
        
        # Validate
        valid, msg = validate_user_id(user_id)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return
        user_id = int(user_id)
        
        # Check if user exists
        if not users_dao.get_user_by_id(user_id):
            messagebox.showerror("Error", "User ID does not exist")
            return
        
        # Check if already member
        if clubs_dao.is_user_in_club(self.club_id, user_id):
            messagebox.showerror("Error", "User is already a member of this club")
            return
        
        # Add member
        if clubs_dao.add_club_member(self.club_id, user_id, role):
            self.result = True
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to add member")


class AddToQueueDialog:
    def __init__(self, parent, club_id):
        self.result = None
        self.club_id = club_id
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Book to Queue")
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.dialog.wait_window()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Add Book to Reading Queue", font=('Helvetica', 12, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=(0, 20))
        
        # ISBN
        ttk.Label(frame, text="*ISBN:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.isbn_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.isbn_var, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Added by User ID
        ttk.Label(frame, text="*Added By (User ID):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.added_by_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.added_by_var, width=30).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Add", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        isbn = self.isbn_var.get().strip()
        added_by = self.added_by_var.get().strip()
        
        # Validate
        valid, msg = validate_isbn(isbn)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return
        
        valid, msg = validate_user_id(added_by)
        if not valid:
            messagebox.showerror("Validation Error", "Added by " + msg)
            return
        added_by = int(added_by)
        
        # Check if book exists
        if not books_dao.get_book_by_isbn(isbn):
            messagebox.showerror("Error", "ISBN does not exist")
            return
        
        # Check if user exists
        if not users_dao.get_user_by_id(added_by):
            messagebox.showerror("Error", "User ID does not exist")
            return
        
        # Add to queue
        if clubs_dao.add_to_reading_queue(self.club_id, isbn, added_by):
            self.result = True
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to add book to queue. It may already be in the queue.")


class AddDiscussionDialog:
    def __init__(self, parent, club_id):
        self.result = None
        self.club_id = club_id
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Discussion")
        self.dialog.geometry("500x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.dialog.wait_window()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Create New Discussion", font=('Helvetica', 12, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Discussion Type
        ttk.Label(frame, text="*Discussion Type:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.type_var = tk.StringVar(value="general")
        type_frame = ttk.Frame(frame)
        type_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(type_frame, text="General", variable=self.type_var, value="general",
                       command=self.on_type_change).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="Chapter", variable=self.type_var, value="chapter",
                       command=self.on_type_change).pack(side=tk.LEFT, padx=5)
        
        # User ID
        ttk.Label(frame, text="*Posted By (User ID):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.user_id_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.user_id_var, width=30).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Title
        ttk.Label(frame, text="*Title:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.title_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.title_var, width=30).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # ISBN (for chapter discussions)
        self.isbn_label = ttk.Label(frame, text="*ISBN:")
        self.isbn_var = tk.StringVar()
        self.isbn_entry = ttk.Entry(frame, textvariable=self.isbn_var, width=30)
        
        # Chapter Number (for chapter discussions)
        self.chapter_label = ttk.Label(frame, text="*Chapter Number:")
        self.chapter_var = tk.StringVar()
        self.chapter_entry = ttk.Entry(frame, textvariable=self.chapter_var, width=30)
        
        # Content
        ttk.Label(frame, text="*Content:").grid(row=6, column=0, sticky=tk.NW, pady=5)
        self.content_text = tk.Text(frame, width=30, height=8)
        self.content_text.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5)
        
        frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Create", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Initial state
        self.on_type_change()
    
    def on_type_change(self):
        """Show/hide chapter-specific fields"""
        if self.type_var.get() == "chapter":
            self.isbn_label.grid(row=4, column=0, sticky=tk.W, pady=5)
            self.isbn_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
            self.chapter_label.grid(row=5, column=0, sticky=tk.W, pady=5)
            self.chapter_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        else:
            self.isbn_label.grid_remove()
            self.isbn_entry.grid_remove()
            self.chapter_label.grid_remove()
            self.chapter_entry.grid_remove()
    
    def save(self):
        discussion_type = self.type_var.get()
        user_id = self.user_id_var.get().strip()
        title = self.title_var.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        
        # Validate common fields
        valid, msg = validate_user_id(user_id)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return
        user_id = int(user_id)
        
        if not title:
            messagebox.showerror("Validation Error", "Title is required")
            return
        
        if not content:
            messagebox.showerror("Validation Error", "Content is required")
            return
        
        # Check if user exists
        if not users_dao.get_user_by_id(user_id):
            messagebox.showerror("Error", "User ID does not exist")
            return
        
        # Check if user is member of club
        if not clubs_dao.is_user_in_club(self.club_id, user_id):
            messagebox.showerror("Error", "User is not a member of this club")
            return
        
        if discussion_type == "general":
            # Create general discussion
            discussion_id = clubs_dao.add_general_discussion(self.club_id, user_id, title, content)
            if discussion_id:
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to create discussion")
        else:
            # Chapter discussion
            isbn = self.isbn_var.get().strip()
            chapter = self.chapter_var.get().strip()
            
            # Validate
            valid, msg = validate_isbn(isbn)
            if not valid:
                messagebox.showerror("Validation Error", msg)
                return
            
            valid, msg = validate_chapter_number(chapter)
            if not valid:
                messagebox.showerror("Validation Error", msg)
                return
            chapter = int(chapter)
            
            # Check if book exists
            if not books_dao.get_book_by_isbn(isbn):
                messagebox.showerror("Error", "ISBN does not exist")
                return
            
            # Create chapter discussion
            discussion_id = clubs_dao.add_chapter_discussion(self.club_id, isbn, chapter, user_id, title, content)
            if discussion_id:
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to create discussion")

# ==================== DISCUSSION VIEWER DIALOG ====================

class ViewDiscussionDialog:
    def __init__(self, parent, club_id, discussion_type, discussion_id):
        self.club_id = club_id
        self.discussion_type = discussion_type  # 'general' or 'chapter'
        self.discussion_id = discussion_id
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("View Discussion")
        self.dialog.geometry("800x700")
        self.dialog.transient(parent)
        
        # Load discussion data
        self.load_discussion_data()
        
        if not self.discussion:
            messagebox.showerror("Error", "Discussion not found")
            self.dialog.destroy()
            return
        
        self.setup_ui()
        self.load_comments()
    
    def load_discussion_data(self):
        """Load discussion details"""
        from db.connection import db
        
        if self.discussion_type == 'general':
            query = """
                SELECT 
                    gd.discussion_id,
                    gd.title,
                    gd.content,
                    gd.created_date,
                    u.user_id,
                    u.username
                FROM General_Discussions gd
                JOIN Users u ON gd.user_id = u.user_id
                WHERE gd.discussion_id = %s
            """
        else:  # chapter
            query = """
                SELECT 
                    cd.discussion_id,
                    cd.title,
                    cd.content,
                    cd.created_date,
                    cd.ISBN,
                    cd.chapter_number,
                    b.title as book_title,
                    u.user_id,
                    u.username
                FROM Chapter_Discussions cd
                JOIN Users u ON cd.user_id = u.user_id
                JOIN Books b ON cd.ISBN = b.ISBN
                WHERE cd.discussion_id = %s
            """
        
        self.discussion = db.execute_query(query, (self.discussion_id,), fetch_one=True)
    
    def setup_ui(self):
        """Setup the UI"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Title
        title_text = self.discussion.get('title', 'Untitled')
        ttk.Label(header_frame, text=title_text, 
                 font=('Helvetica', 14, 'bold'), wraplength=750).pack(anchor=tk.W)
        
        # Metadata
        meta_frame = ttk.Frame(header_frame)
        meta_frame.pack(anchor=tk.W, pady=(5, 0))
        
        author = self.discussion.get('username', 'Unknown')
        date = self.discussion.get('created_date', '')
        meta_text = f"Posted by: {author} | Date: {date}"
        
        if self.discussion_type == 'chapter':
            book_title = self.discussion.get('book_title', 'Unknown')
            chapter = self.discussion.get('chapter_number', '?')
            meta_text += f" | Book: {book_title} | Chapter: {chapter}"
        
        ttk.Label(meta_frame, text=meta_text, font=('Helvetica', 9, 'italic')).pack()
        
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Content
        content_frame = ttk.LabelFrame(main_frame, text="Discussion Content", padding="10")
        content_frame.pack(fill=tk.X, pady=(0, 15))
        
        content_text = tk.Text(content_frame, height=6, wrap=tk.WORD, 
                              font=('Helvetica', 10), relief=tk.FLAT, bg='#f0f0f0')
        content_text.pack(fill=tk.BOTH, expand=True)
        content_text.insert("1.0", self.discussion.get('content', ''))
        content_text.config(state=tk.DISABLED)
        
        # Comments section
        comments_frame = ttk.LabelFrame(main_frame, text="Comments", padding="10")
        comments_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Comments list with scrollbar
        list_frame = ttk.Frame(comments_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.comments_canvas = tk.Canvas(list_frame, yscrollcommand=scrollbar.set, 
                                        bg='white', highlightthickness=0)
        self.comments_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.comments_canvas.yview)
        
        self.comments_inner_frame = ttk.Frame(self.comments_canvas)
        self.comments_canvas.create_window((0, 0), window=self.comments_inner_frame, anchor='nw')
        
        self.comments_inner_frame.bind(
            '<Configure>',
            lambda e: self.comments_canvas.configure(scrollregion=self.comments_canvas.bbox('all'))
        )
        
        # Add comment section
        add_comment_frame = ttk.Frame(comments_frame)
        add_comment_frame.pack(fill=tk.X)
        
        ttk.Label(add_comment_frame, text="Add Comment:").pack(anchor=tk.W, pady=(0, 5))
        
        input_frame = ttk.Frame(add_comment_frame)
        input_frame.pack(fill=tk.X)
        
        self.comment_text = tk.Text(input_frame, height=3, wrap=tk.WORD)
        self.comment_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Label(button_frame, text="User ID:").pack(pady=(0, 5))
        self.user_id_var = tk.StringVar()
        ttk.Entry(button_frame, textvariable=self.user_id_var, width=10).pack(pady=(0, 5))
        ttk.Button(button_frame, text="Post Comment", command=self.add_comment).pack()
        
        # Close button
        ttk.Button(main_frame, text="Close", command=self.dialog.destroy).pack(pady=(10, 0))
    
    def load_comments(self):
        """Load and display all comments"""
        from db.connection import db
        
        # Clear existing comments
        for widget in self.comments_inner_frame.winfo_children():
            widget.destroy()
        
        # Load comments based on type
        if self.discussion_type == 'general':
            query = """
                SELECT 
                    c.comment_id,
                    c.title,
                    c.content,
                    c.created_date,
                    u.user_id,
                    u.username
                FROM General_Discussion_Comments c
                JOIN Users u ON c.user_id = u.user_id
                WHERE c.discussion_id = %s
                ORDER BY c.created_date ASC
            """
        else:  # chapter
            query = """
                SELECT 
                    c.comment_id,
                    c.content,
                    c.created_date,
                    u.user_id,
                    u.username
                FROM Chapter_Discussion_Comments c
                JOIN Users u ON c.user_id = u.user_id
                WHERE c.discussion_id = %s
                ORDER BY c.created_date ASC
            """
        
        comments = db.execute_query(query, (self.discussion_id,))
        
        if not comments:
            ttk.Label(self.comments_inner_frame, 
                     text="No comments yet. Be the first to comment!",
                     font=('Helvetica', 10, 'italic')).pack(pady=20)
            return
        
        # Display each comment
        for comment in comments:
            self.create_comment_widget(comment)
    
    def create_comment_widget(self, comment):
        """Create a widget for displaying a single comment"""
        comment_frame = ttk.Frame(self.comments_inner_frame, relief=tk.SOLID, borderwidth=1)
        comment_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Header with author and date
        header = ttk.Frame(comment_frame, style='Comment.TFrame')
        header.pack(fill=tk.X, padx=10, pady=(5, 0))
        
        author_text = f"👤 {comment.get('username', 'Unknown')}"
        ttk.Label(header, text=author_text, font=('Helvetica', 9, 'bold')).pack(side=tk.LEFT)
        
        date_text = str(comment.get('created_date', ''))
        ttk.Label(header, text=date_text, font=('Helvetica', 8), 
                 foreground='gray').pack(side=tk.RIGHT)
        
        # Comment title (only for general discussions)
        if self.discussion_type == 'general' and comment.get('title'):
            title_label = ttk.Label(comment_frame, 
                                   text=comment.get('title'),
                                   font=('Helvetica', 10, 'bold'))
            title_label.pack(anchor=tk.W, padx=10, pady=(5, 0))
        
        # Comment content
        content = comment.get('content', '')
        content_label = tk.Label(comment_frame, text=content, 
                               font=('Helvetica', 10), wraplength=700,
                               justify=tk.LEFT, anchor='w', bg='white')
        content_label.pack(fill=tk.X, padx=10, pady=10)
        
        # Delete button (optional - could check if user is author or admin)
        delete_btn = ttk.Button(comment_frame, text="Delete", 
                               command=lambda: self.delete_comment(comment.get('comment_id')))
        delete_btn.pack(anchor=tk.E, padx=10, pady=(0, 5))
    
    def add_comment(self):
        """Add a new comment"""
        from db.connection import db
        from core.validators import validate_user_id
        
        user_id = self.user_id_var.get().strip()
        content = self.comment_text.get("1.0", tk.END).strip()
        
        # Validate
        valid, msg = validate_user_id(user_id)
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return
        user_id = int(user_id)
        
        if not content:
            messagebox.showerror("Validation Error", "Comment content cannot be empty")
            return
        
        # Check if user exists
        from db import users_dao
        if not users_dao.get_user_by_id(user_id):
            messagebox.showerror("Error", "User ID does not exist")
            return
        
        # Insert comment
        try:
            if self.discussion_type == 'general':
                # For general discussions, we need a title too
                query = """
                    INSERT INTO General_Discussion_Comments(discussion_id, user_id, title, content)
                    VALUES (%s, %s, %s, %s)
                """
                title = "Re: " + self.discussion.get('title', '')[:50]
                db.execute_update(query, (self.discussion_id, user_id, title, content))
            else:  # chapter
                query = """
                    INSERT INTO Chapter_Discussion_Comments(discussion_id, user_id, content)
                    VALUES (%s, %s, %s)
                """
                db.execute_update(query, (self.discussion_id, user_id, content))
            
            # Clear input and reload
            self.comment_text.delete("1.0", tk.END)
            self.user_id_var.set("")
            self.load_comments()
            messagebox.showinfo("Success", "Comment posted successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to post comment: {str(e)}")
    
    def delete_comment(self, comment_id):
        """Delete a comment"""
        from db.connection import db
        
        if not messagebox.askyesno("Confirm Delete", "Delete this comment?"):
            return
        
        try:
            if self.discussion_type == 'general':
                query = "DELETE FROM General_Discussion_Comments WHERE comment_id = %s"
            else:  # chapter
                query = "DELETE FROM Chapter_Discussion_Comments WHERE comment_id = %s"
            
            db.execute_update(query, (comment_id,))
            self.load_comments()
            messagebox.showinfo("Success", "Comment deleted!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete comment: {str(e)}")