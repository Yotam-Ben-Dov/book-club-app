"""
Users management tab
Handles user search, CRUD operations, and user statistics
"""

import tkinter as tk
from tkinter import ttk, messagebox
from db import users_dao
from ui.dialogs import AddUserDialog, EditUserDialog, UserStatisticsDialog


class UsersTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, padding="10")
        self.setup_ui()
        self.load_users()
    
    def setup_ui(self):
        """Setup the UI components"""
        # Search frame
        search_frame = ttk.LabelFrame(self.frame, text="Search Users", padding="10")
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Search fields
        ttk.Label(search_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.username_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.username_var, width=20).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(search_frame, text="Location:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.location_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.location_var, width=30).grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(search_frame, text="Birth Year:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.birth_year_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.birth_year_var, width=10).grid(row=0, column=5, padx=(0, 10))
        
        # Search buttons
        ttk.Button(search_frame, text="Search", command=self.search_users).grid(row=0, column=6, padx=5)
        ttk.Button(search_frame, text="Clear", command=self.clear_search).grid(row=0, column=7, padx=5)
        
        # Users table frame
        table_frame = ttk.Frame(self.frame)
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        
        # Treeview
        columns = ("User ID", "Username", "Location", "Birth Year", "Age")
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
        self.tree.heading("User ID", text="User ID")
        self.tree.heading("Username", text="Username")
        self.tree.heading("Location", text="Location")
        self.tree.heading("Birth Year", text="Birth Year")
        self.tree.heading("Age", text="Age")
        
        self.tree.column("User ID", width=80)
        self.tree.column("Username", width=150)
        self.tree.column("Location", width=300)
        self.tree.column("Birth Year", width=100)
        self.tree.column("Age", width=80)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Add User", command=self.add_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Edit User", command=self.edit_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete User", command=self.delete_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="View Statistics", command=self.view_statistics).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Refresh", command=self.refresh).pack(side=tk.RIGHT, padx=5)
        
        # Bind double-click
        self.tree.bind("<Double-1>", lambda e: self.view_statistics())
    
    def load_users(self, users=None):
        """Load users into the table"""
        from datetime import datetime
        current_year = datetime.now().year
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if users is None:
            users = users_dao.search_users(limit=500)
        
        if users:
            for user in users:
                birth_year = user.get('birth_year')
                age = current_year - birth_year if birth_year else 'N/A'
                
                self.tree.insert("", tk.END, values=(
                    user.get('user_id', ''),
                    user.get('username', ''),
                    user.get('location', ''),
                    birth_year or 'N/A',
                    age
                ))
    
    def search_users(self):
        """Search users based on filters"""
        username = self.username_var.get().strip() or None
        location = self.location_var.get().strip() or None
        birth_year = self.birth_year_var.get().strip()
        
        min_birth_year = None
        max_birth_year = None
        
        if birth_year:
            try:
                min_birth_year = int(birth_year)
                max_birth_year = int(birth_year)
            except ValueError:
                messagebox.showerror("Error", "Birth year must be a number")
                return
        
        users = users_dao.search_users(
            username=username,
            location=location,
            min_birth_year=min_birth_year,
            max_birth_year=max_birth_year,
            limit=500
        )
        
        self.load_users(users)
        messagebox.showinfo("Search Results", f"Found {len(users) if users else 0} users")
    
    def clear_search(self):
        """Clear search fields and reload all users"""
        self.username_var.set("")
        self.location_var.set("")
        self.birth_year_var.set("")
        self.load_users()
    
    def add_user(self):
        """Open add user dialog"""
        dialog = AddUserDialog(self.frame)
        if dialog.result:
            self.refresh()
            messagebox.showinfo("Success", "User added successfully!")
    
    def edit_user(self):
        """Open edit user dialog"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user to edit")
            return
        
        item = self.tree.item(selection[0])
        user_id = item['values'][0]
        
        dialog = EditUserDialog(self.frame, user_id)
        if dialog.result:
            self.refresh()
            messagebox.showinfo("Success", "User updated successfully!")
    
    def delete_user(self):
        """Delete selected user"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user to delete")
            return
        
        item = self.tree.item(selection[0])
        user_id = item['values'][0]
        username = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", 
                               f"Delete user '{username}'?\n\nThis will also delete all ratings and club memberships."):
            if users_dao.delete_user(user_id):
                self.refresh()
                messagebox.showinfo("Success", "User deleted successfully!")
            else:
                messagebox.showerror("Error", "Failed to delete user")
    
    def view_statistics(self):
        """View user statistics"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user to view statistics")
            return
        
        item = self.tree.item(selection[0])
        user_id = item['values'][0]
        
        UserStatisticsDialog(self.frame, user_id)
    
    def refresh(self):
        """Refresh the users list"""
        self.clear_search()