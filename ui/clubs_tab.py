"""
Clubs management tab
Handles club CRUD operations, members, queue, history, and discussions
"""

import tkinter as tk
from tkinter import ttk, messagebox
from db import clubs_dao
from ui.dialogs import (AddClubDialog, EditClubDialog, ClubDetailsDialog,
                        AddClubMemberDialog, AddToQueueDialog, AddDiscussionDialog)


class ClubsTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, padding="10")
        self.selected_club_id = None
        self.setup_ui()
        self.load_clubs()
    
    def setup_ui(self):
        """Setup the UI components"""
        # Create paned window (left: clubs list, right: club details)
        paned = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - clubs list
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="Book Clubs", font=('Helvetica', 12, 'bold')).pack(pady=(0, 5))
        
        # Clubs list
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        
        columns = ("ID", "Name", "Members", "Public")
        self.clubs_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            yscrollcommand=vsb.set
        )
        
        vsb.config(command=self.clubs_tree.yview)
        
        self.clubs_tree.heading("ID", text="ID")
        self.clubs_tree.heading("Name", text="Club Name")
        self.clubs_tree.heading("Members", text="Members")
        self.clubs_tree.heading("Public", text="Public")
        
        self.clubs_tree.column("ID", width=50)
        self.clubs_tree.column("Name", width=200)
        self.clubs_tree.column("Members", width=80)
        self.clubs_tree.column("Public", width=60)
        
        self.clubs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Clubs buttons
        clubs_buttons = ttk.Frame(left_frame)
        clubs_buttons.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(clubs_buttons, text="Create Club", command=self.create_club).pack(fill=tk.X, pady=2)
        ttk.Button(clubs_buttons, text="Edit Club", command=self.edit_club).pack(fill=tk.X, pady=2)
        ttk.Button(clubs_buttons, text="Delete Club", command=self.delete_club).pack(fill=tk.X, pady=2)
        ttk.Button(clubs_buttons, text="Refresh", command=self.load_clubs).pack(fill=tk.X, pady=2)
        
        # Right panel - club details
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)
        
        self.details_label = ttk.Label(right_frame, text="Select a club to view details", 
                                       font=('Helvetica', 12, 'bold'))
        self.details_label.pack(pady=(0, 10))
        
        # Create notebook for different club sections
        self.club_notebook = ttk.Notebook(right_frame)
        self.club_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Members tab
        self.members_frame = ttk.Frame(self.club_notebook)
        self.club_notebook.add(self.members_frame, text="Members")
        self.setup_members_tab()
        
        # Reading Queue tab
        self.queue_frame = ttk.Frame(self.club_notebook)
        self.club_notebook.add(self.queue_frame, text="Reading Queue")
        self.setup_queue_tab()
        
        # Reading History tab
        self.history_frame = ttk.Frame(self.club_notebook)
        self.club_notebook.add(self.history_frame, text="Reading History")
        self.setup_history_tab()
        
        # Discussions tab
        self.discussions_frame = ttk.Frame(self.club_notebook)
        self.club_notebook.add(self.discussions_frame, text="Discussions")
        self.setup_discussions_tab()
        
        # Bind selection event
        self.clubs_tree.bind("<<TreeviewSelect>>", self.on_club_selected)
    
    def setup_members_tab(self):
        """Setup members tab"""
        # Members list
        list_frame = ttk.Frame(self.members_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        
        columns = ("User ID", "Username", "Role", "Location")
        self.members_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            yscrollcommand=vsb.set
        )
        
        vsb.config(command=self.members_tree.yview)
        
        for col in columns:
            self.members_tree.heading(col, text=col)
        
        self.members_tree.column("User ID", width=80)
        self.members_tree.column("Username", width=120)
        self.members_tree.column("Role", width=100)
        self.members_tree.column("Location", width=200)
        
        self.members_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        buttons = ttk.Frame(self.members_frame)
        buttons.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(buttons, text="Add Member", command=self.add_member).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Remove Member", command=self.remove_member).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Change Role", command=self.change_role).pack(side=tk.LEFT, padx=5)
    
    def setup_queue_tab(self):
        """Setup reading queue tab"""
        # Queue list
        list_frame = ttk.Frame(self.queue_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        
        columns = ("Position", "Title", "Authors", "Added By", "Avg Rating")
        self.queue_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            yscrollcommand=vsb.set
        )
        
        vsb.config(command=self.queue_tree.yview)
        
        for col in columns:
            self.queue_tree.heading(col, text=col)
        
        self.queue_tree.column("Position", width=70)
        self.queue_tree.column("Title", width=250)
        self.queue_tree.column("Authors", width=180)
        self.queue_tree.column("Added By", width=100)
        self.queue_tree.column("Avg Rating", width=100)
        
        self.queue_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        buttons = ttk.Frame(self.queue_frame)
        buttons.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(buttons, text="Add to Queue", command=self.add_to_queue).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Remove from Queue", command=self.remove_from_queue).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Start Reading", command=self.start_reading).pack(side=tk.LEFT, padx=5)
    
    def setup_history_tab(self):
        """Setup reading history tab"""
        # History list
        list_frame = ttk.Frame(self.history_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        
        columns = ("Title", "Authors", "Start Date", "End Date", "Status", "Avg Rating")
        self.history_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            yscrollcommand=vsb.set
        )
        
        vsb.config(command=self.history_tree.yview)
        
        for col in columns:
            self.history_tree.heading(col, text=col)
        
        self.history_tree.column("Title", width=200)
        self.history_tree.column("Authors", width=150)
        self.history_tree.column("Start Date", width=100)
        self.history_tree.column("End Date", width=100)
        self.history_tree.column("Status", width=80)
        self.history_tree.column("Avg Rating", width=100)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        buttons = ttk.Frame(self.history_frame)
        buttons.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(buttons, text="Complete Current Book", command=self.complete_book).pack(side=tk.LEFT, padx=5)
    
    def setup_discussions_tab(self):
        """Setup discussions tab"""
        # Discussions list
        list_frame = ttk.Frame(self.discussions_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        hsb = ttk.Scrollbar(list_frame, orient="horizontal")
        
        columns = ("Type", "Title", "Username", "Date")
        self.discussions_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=self.discussions_tree.yview)
        hsb.config(command=self.discussions_tree.xview)
        
        for col in columns:
            self.discussions_tree.heading(col, text=col)
        
        self.discussions_tree.column("Type", width=80)
        self.discussions_tree.column("Title", width=300)
        self.discussions_tree.column("Username", width=120)
        self.discussions_tree.column("Date", width=150)
        
        self.discussions_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        # Bind double-click to view discussion
        self.discussions_tree.bind("<Double-1>", lambda e: self.view_discussion())
        
        # Buttons
        buttons = ttk.Frame(self.discussions_frame)
        buttons.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(buttons, text="View Discussion", command=self.view_discussion).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Add Discussion", command=self.add_discussion).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Delete Discussion", command=self.delete_discussion).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Refresh", command=self.load_discussions).pack(side=tk.LEFT, padx=5)
    
    def load_clubs(self):
        """Load clubs list"""
        # Clear existing items
        for item in self.clubs_tree.get_children():
            self.clubs_tree.delete(item)
        
        clubs = clubs_dao.get_all_clubs(limit=100)
        
        if clubs:
            for club in clubs:
                self.clubs_tree.insert("", tk.END, values=(
                    club.get('club_id', ''),
                    club.get('name', ''),
                    club.get('member_count', 0),
                    'Yes' if club.get('is_public') else 'No'
                ))
    
    def on_club_selected(self, event):
        """Handle club selection"""
        selection = self.clubs_tree.selection()
        if not selection:
            return
        
        item = self.clubs_tree.item(selection[0])
        self.selected_club_id = item['values'][0]
        club_name = item['values'][1]
        
        self.details_label.config(text=f"Club: {club_name}")
        
        # Load club details
        self.load_members()
        self.load_queue()
        self.load_history()
        self.load_discussions()
    
    def load_members(self):
        """Load club members"""
        if not self.selected_club_id:
            return
        
        # Clear existing items
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)
        
        members = clubs_dao.get_club_members(self.selected_club_id)
        
        if members:
            for member in members:
                self.members_tree.insert("", tk.END, values=(
                    member.get('user_id', ''),
                    member.get('username', ''),
                    member.get('role', ''),
                    member.get('location', '')
                ))
    
    def load_queue(self):
        """Load reading queue"""
        if not self.selected_club_id:
            return
        
        # Clear existing items
        for item in self.queue_tree.get_children():
            self.queue_tree.delete(item)
        
        queue = clubs_dao.get_club_reading_queue(self.selected_club_id)
        
        if queue:
            for item in queue:
                # Store queue_id as a tag or in values
                item_id = self.queue_tree.insert("", tk.END, values=(
                    item.get('queue_position', ''),
                    item.get('title', ''),
                    item.get('authors', 'Unknown'),
                    item.get('added_by_username', 'Unknown'),
                    f"{item.get('avg_rating', 0):.2f}" if item.get('avg_rating') else 'N/A'
                ))
                # Store queue_id as tag
                self.queue_tree.item(item_id, tags=(item.get('queue_id'),))

    def load_history(self):
        """Load reading history"""
        if not self.selected_club_id:
            return
        
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        history = clubs_dao.get_club_reading_history(self.selected_club_id)
        
        if history:
            for item in history:
                self.history_tree.insert("", tk.END, values=(
                    item.get('title', ''),
                    item.get('authors', 'Unknown'),
                    item.get('start_date', ''),
                    item.get('end_date', 'Current'),
                    item.get('status', ''),
                    f"{item.get('avg_rating', 0):.2f}" if item.get('avg_rating') else 'N/A'
                ))
    
    def load_discussions(self):
        """Load discussions with IDs stored in tags"""
        if not self.selected_club_id:
            return
        
        # Clear existing items
        for item in self.discussions_tree.get_children():
            self.discussions_tree.delete(item)
        
        discussions = clubs_dao.get_club_recent_discussions(self.selected_club_id, limit=50)
        
        if discussions:
            for disc in discussions:
                disc_type = disc.get('discussion_type', '').lower()
                disc_id = disc.get('discussion_id')
                
                # Insert row
                item_id = self.discussions_tree.insert("", tk.END, values=(
                    disc_type.title(),
                    disc.get('title', ''),
                    disc.get('username', ''),
                    disc.get('created_date', '')
                ))
                
                # Store discussion_id and type as tags (type, id)
                self.discussions_tree.item(item_id, tags=(disc_type, str(disc_id)))
    
    def create_club(self):
        """Create new club"""
        dialog = AddClubDialog(self.frame)
        if dialog.result:
            self.load_clubs()
            messagebox.showinfo("Success", "Club created successfully!")
    
    def edit_club(self):
        """Edit selected club"""
        selection = self.clubs_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a club to edit")
            return
        
        item = self.clubs_tree.item(selection[0])
        club_id = item['values'][0]
        
        dialog = EditClubDialog(self.frame, club_id)
        if dialog.result:
            self.load_clubs()
            messagebox.showinfo("Success", "Club updated successfully!")
    
    def delete_club(self):
        """Delete selected club"""
        selection = self.clubs_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a club to delete")
            return
        
        item = self.clubs_tree.item(selection[0])
        club_id = item['values'][0]
        club_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", 
                               f"Delete club '{club_name}'?\n\nThis will also delete all members, queue, history, and discussions."):
            if clubs_dao.delete_club(club_id):
                self.selected_club_id = None
                self.details_label.config(text="Select a club to view details")
                self.load_clubs()
                messagebox.showinfo("Success", "Club deleted successfully!")
            else:
                messagebox.showerror("Error", "Failed to delete club")
    
    def add_member(self):
        """Add member to club"""
        if not self.selected_club_id:
            messagebox.showwarning("Warning", "Please select a club first")
            return
        
        dialog = AddClubMemberDialog(self.frame, self.selected_club_id)
        if dialog.result:
            self.load_members()
            messagebox.showinfo("Success", "Member added successfully!")
    
    def remove_member(self):
        """Remove member from club"""
        if not self.selected_club_id:
            messagebox.showwarning("Warning", "Please select a club first")
            return
        
        selection = self.members_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a member to remove")
            return
        
        item = self.members_tree.item(selection[0])
        user_id = item['values'][0]
        username = item['values'][1]
        
        if messagebox.askyesno("Confirm Remove", f"Remove member '{username}' from club?"):
            if clubs_dao.remove_club_member(self.selected_club_id, user_id):
                self.load_members()
                messagebox.showinfo("Success", "Member removed successfully!")
            else:
                messagebox.showerror("Error", "Failed to remove member")
    
    def change_role(self):
        """Change member role"""
        if not self.selected_club_id:
            messagebox.showwarning("Warning", "Please select a club first")
            return
        
        selection = self.members_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a member")
            return
        
        item = self.members_tree.item(selection[0])
        user_id = item['values'][0]
        username = item['values'][1]
        current_role = item['values'][2]
        
        # Create dialog to select new role
        dialog = tk.Toplevel(self.frame)
        dialog.title("Change Member Role")
        dialog.geometry("300x150")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        ttk.Label(dialog, text=f"Change role for: {username}").pack(pady=10)
        ttk.Label(dialog, text=f"Current role: {current_role}").pack(pady=5)
        
        ttk.Label(dialog, text="New role:").pack(pady=5)
        role_var = tk.StringVar(value=current_role)
        ttk.Combobox(dialog, textvariable=role_var, values=['member', 'moderator', 'admin'], 
                    state='readonly').pack(pady=5)
        
        def save():
            new_role = role_var.get()
            if clubs_dao.update_member_role(self.selected_club_id, user_id, new_role):
                self.load_members()
                dialog.destroy()
                messagebox.showinfo("Success", "Role updated successfully!")
            else:
                messagebox.showerror("Error", "Failed to update role")
        
        ttk.Button(dialog, text="Save", command=save).pack(side=tk.LEFT, padx=20, pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=20, pady=10)
    
    def add_to_queue(self):
        """Add book to reading queue"""
        if not self.selected_club_id:
            messagebox.showwarning("Warning", "Please select a club first")
            return
        
        dialog = AddToQueueDialog(self.frame, self.selected_club_id)
        if dialog.result:
            self.load_queue()
            messagebox.showinfo("Success", "Book added to queue!")
    
    def remove_from_queue(self):
        """Remove book from reading queue"""
        if not self.selected_club_id:
            messagebox.showwarning("Warning", "Please select a club first")
            return
        
        selection = self.queue_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a book to remove from queue")
            return
        
        item = self.queue_tree.item(selection[0])
        queue_id = int(item['tags'][0]) if item['tags'] else None
        title = item['values'][1]
        
        if not queue_id:
            messagebox.showerror("Error", "Could not find queue ID")
            return
        
        if messagebox.askyesno("Confirm Remove", f"Remove '{title}' from reading queue?"):
            if clubs_dao.remove_from_reading_queue(queue_id):
                self.load_queue()
                messagebox.showinfo("Success", "Book removed from queue!")
            else:
                messagebox.showerror("Error", "Failed to remove book from queue")

    def start_reading(self):
        """Start reading first book in queue"""
        if not self.selected_club_id:
            messagebox.showwarning("Warning", "Please select a club first")
            return
        
        # Get first book from queue
        queue = clubs_dao.get_club_reading_queue(self.selected_club_id)
        if not queue:
            messagebox.showinfo("Info", "Queue is empty")
            return
        
        first_book = queue[0]
        isbn = first_book.get('ISBN')
        title = first_book.get('title')
        
        if messagebox.askyesno("Confirm", f"Start reading '{title}'?"):
            if clubs_dao.set_current_book(self.selected_club_id, isbn):
                # Remove from queue
                clubs_dao.remove_from_reading_queue(first_book.get('queue_id'))
                self.load_queue()
                self.load_history()
                messagebox.showinfo("Success", "Started reading book!")
            else:
                messagebox.showerror("Error", "Failed to start reading")
    
    def complete_book(self):
        """Complete current book"""
        if not self.selected_club_id:
            messagebox.showwarning("Warning", "Please select a club first")
            return
        
        if messagebox.askyesno("Confirm", "Mark current book as completed?"):
            if clubs_dao.complete_current_book(self.selected_club_id):
                self.load_history()
                messagebox.showinfo("Success", "Book marked as completed!")
            else:
                messagebox.showerror("Error", "Failed to complete book")
    
    def add_discussion(self):
        """Add new discussion"""
        if not self.selected_club_id:
            messagebox.showwarning("Warning", "Please select a club first")
            return
        
        dialog = AddDiscussionDialog(self.frame, self.selected_club_id)
        if dialog.result:
            self.load_discussions()
            messagebox.showinfo("Success", "Discussion added!")
    
    def delete_discussion(self):
        """Delete selected discussion"""
        if not self.selected_club_id:
            messagebox.showwarning("Warning", "Please select a club first")
            return
        
        selection = self.discussions_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a discussion to delete")
            return
        
        item = self.discussions_tree.item(selection[0])
        title = item['values'][1]
        
        # Extract type and ID from tags
        tags = item['tags']
        if not tags or len(tags) < 2:
            messagebox.showerror("Error", "Could not find discussion information")
            return
        
        discussion_type = tags[0]  # 'general' or 'chapter'
        discussion_id = int(tags[1])
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", 
                                f"Delete discussion '{title}'?\n\nThis action cannot be undone."):
            return
        
        # Delete based on type
        success = False
        try:
            if discussion_type == 'general':
                success = clubs_dao.delete_general_discussion(discussion_id)
            elif discussion_type == 'chapter':
                success = clubs_dao.delete_chapter_discussion(discussion_id)
            else:
                messagebox.showerror("Error", f"Unknown discussion type: {discussion_type}")
                return
            
            if success:
                self.load_discussions()
                messagebox.showinfo("Success", "Discussion deleted successfully!")
            else:
                messagebox.showerror("Error", "Failed to delete discussion")
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting discussion: {str(e)}")

    def view_discussion(self):
        """View discussion details with comments"""
        if not self.selected_club_id:
            messagebox.showwarning("Warning", "Please select a club first")
            return
        
        selection = self.discussions_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a discussion to view")
            return
        
        item = self.discussions_tree.item(selection[0])
        
        # Extract type and ID from tags
        tags = item['tags']
        if not tags or len(tags) < 2:
            messagebox.showerror("Error", "Could not find discussion information")
            return
        
        discussion_type = tags[0]  # 'general' or 'chapter'
        discussion_id = int(tags[1])
        
        # Open discussion viewer dialog
        from ui.dialogs import ViewDiscussionDialog
        ViewDiscussionDialog(self.frame, self.selected_club_id, discussion_type, discussion_id)
    
    def refresh(self):
        """Refresh clubs list"""
        self.load_clubs()