"""
Books management tab
Handles book search, CRUD operations, and related queries
"""

import tkinter as tk
from tkinter import ttk, messagebox
from db import books_dao, publishers_dao, authors_dao
from ui.dialogs import AddBookDialog, EditBookDialog, BookDetailsDialog


class BooksTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, padding="10")
        self.setup_ui()
        self.load_books()
    
    def setup_ui(self):
        """Setup the UI components"""
        # Search frame
        search_frame = ttk.LabelFrame(self.frame, text="Search Books", padding="10")
        search_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Search fields
        ttk.Label(search_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.title_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.title_var, width=20).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(search_frame, text="Author:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.author_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.author_var, width=20).grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(search_frame, text="ISBN:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.isbn_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.isbn_var, width=15).grid(row=0, column=5, padx=(0, 10))
        
        ttk.Label(search_frame, text="Publisher:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.publisher_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.publisher_var, width=20).grid(row=1, column=1, padx=(0, 10), pady=(5, 0))
        
        ttk.Label(search_frame, text="Year:").grid(row=1, column=2, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.year_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.year_var, width=10).grid(row=1, column=3, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        
        # Search buttons
        ttk.Button(search_frame, text="Search", command=self.search_books).grid(row=1, column=4, padx=5, pady=(5, 0))
        ttk.Button(search_frame, text="Clear", command=self.clear_search).grid(row=1, column=5, padx=5, pady=(5, 0))
        
        # Books table frame
        table_frame = ttk.Frame(self.frame)
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        
        # Treeview
        columns = ("ISBN", "Title", "Authors", "Publisher", "Year", "Avg Rating")
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
        self.tree.heading("ISBN", text="ISBN")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Authors", text="Authors")
        self.tree.heading("Publisher", text="Publisher")
        self.tree.heading("Year", text="Year")
        self.tree.heading("Avg Rating", text="Avg Rating")
        
        self.tree.column("ISBN", width=100)
        self.tree.column("Title", width=250)
        self.tree.column("Authors", width=200)
        self.tree.column("Publisher", width=150)
        self.tree.column("Year", width=70)
        self.tree.column("Avg Rating", width=100)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Add Book", command=self.add_book).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Edit Book", command=self.edit_book).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete Book", command=self.delete_book).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="View Details", command=self.view_details).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Refresh", command=self.refresh).pack(side=tk.RIGHT, padx=5)
        
        # Bind double-click to view details
        self.tree.bind("<Double-1>", lambda e: self.view_details())

    def load_books(self, books=None):
        """Load books into the table"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if books is None:
            books = books_dao.search_books(limit=500)
        
        if books:
            for book in books:
                # Handle avg_rating - it could be None or a number
                avg_rating = book.get('avg_rating')
                if avg_rating is not None:
                    rating_display = f"{float(avg_rating):.2f}"
                else:
                    rating_display = "N/A"
                
                self.tree.insert("", tk.END, values=(
                    book.get('ISBN', ''),
                    book.get('title', ''),
                    book.get('authors', 'Unknown'),
                    book.get('publisher_name', 'Unknown'),
                    book.get('year_of_publication', ''),
                    rating_display
                ))
    
    def search_books(self):
        """Search books based on filters"""
        title = self.title_var.get().strip() or None
        author = self.author_var.get().strip() or None
        isbn = self.isbn_var.get().strip() or None
        publisher = self.publisher_var.get().strip() or None
        year = self.year_var.get().strip() or None
        
        if year:
            try:
                year = int(year)
            except ValueError:
                messagebox.showerror("Error", "Year must be a number")
                return
        
        books = books_dao.search_books(
            title=title,
            author=author,
            isbn=isbn,
            publisher=publisher,
            year=year,
            limit=500
        )
        
        self.load_books(books)
        messagebox.showinfo("Search Results", f"Found {len(books) if books else 0} books")
    
    def clear_search(self):
        """Clear search fields and reload all books"""
        self.title_var.set("")
        self.author_var.set("")
        self.isbn_var.set("")
        self.publisher_var.set("")
        self.year_var.set("")
        self.load_books()
    
    def add_book(self):
        """Open add book dialog"""
        dialog = AddBookDialog(self.frame)
        if dialog.result:
            self.refresh()
            messagebox.showinfo("Success", "Book added successfully!")
    
    def edit_book(self):
        """Open edit book dialog"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a book to edit")
            return
        
        item = self.tree.item(selection[0])
        isbn = item['values'][0]
        
        dialog = EditBookDialog(self.frame, isbn)
        if dialog.result:
            self.refresh()
            messagebox.showinfo("Success", "Book updated successfully!")
    
    def delete_book(self):
        """Delete selected book"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a book to delete")
            return
        
        item = self.tree.item(selection[0])
        isbn = item['values'][0]
        title = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Delete book '{title}'?\n\nThis will also delete all ratings and club references."):
            if books_dao.delete_book(isbn):
                self.refresh()
                messagebox.showinfo("Success", "Book deleted successfully!")
            else:
                messagebox.showerror("Error", "Failed to delete book")
    
    def view_details(self):
        """View detailed book information"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a book to view")
            return
        
        item = self.tree.item(selection[0])
        isbn = item['values'][0]
        
        BookDetailsDialog(self.frame, isbn)
    
    def refresh(self):
        """Refresh the books list"""
        self.clear_search()