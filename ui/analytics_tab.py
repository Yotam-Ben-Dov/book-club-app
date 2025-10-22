"""
Analytics tab
Displays complex analytical queries and simple queries
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from db import analytics_dao, simple_queries_dao


class AnalyticsTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, padding="10")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components"""
        # Title
        ttk.Label(self.frame, text="Analytics Dashboard", 
                 font=('Helvetica', 14, 'bold')).pack(pady=(0, 10))
        
        # Create notebook for different analytics
        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Complex Queries Tab
        complex_frame = ttk.Frame(notebook, padding="10")
        notebook.add(complex_frame, text="Complex Queries")
        self.setup_complex_queries(complex_frame)
        
        # Simple Queries Tab
        simple_frame = ttk.Frame(notebook, padding="10")
        notebook.add(simple_frame, text="Simple Queries")
        self.setup_simple_queries(simple_frame)
    
    def setup_complex_queries(self, parent):
        """Setup complex queries section"""
        # Query 1: Top Publishers
        query1_frame = ttk.LabelFrame(parent, text="Top Publishers by Rating", padding="10")
        query1_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(query1_frame, text="Analyzes publishers by average rating and book count. "
                "Shows publishers with at least a minimum number of books and ratings.").pack(pady=5)
        
        param_frame1 = ttk.Frame(query1_frame)
        param_frame1.pack(pady=5)
        
        ttk.Label(param_frame1, text="Min Books:").pack(side=tk.LEFT, padx=5)
        self.min_books_var = tk.StringVar(value="5")
        ttk.Entry(param_frame1, textvariable=self.min_books_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(param_frame1, text="Min Ratings:").pack(side=tk.LEFT, padx=5)
        self.min_pub_ratings_var = tk.StringVar(value="50")
        ttk.Entry(param_frame1, textvariable=self.min_pub_ratings_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(query1_frame, text="Run Publisher Analysis", 
                command=self.run_top_publishers).pack(pady=5)
        
        # Query 2: Top Rated Books by Age Group
        query2_frame = ttk.LabelFrame(parent, text="Top Rated Books by Age Group", 
                                    padding="10")
        query2_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(query2_frame, text="Shows which books are most popular in different generations: "
                "Gen Z (18-25), Millennials (26-40), Gen X (41-55), Boomers+ (56+).").pack(pady=5)
        
        param_frame2 = ttk.Frame(query2_frame)
        param_frame2.pack(pady=5)
        ttk.Label(param_frame2, text="Min Ratings:").pack(side=tk.LEFT, padx=5)
        self.min_ratings_var = tk.StringVar(value="10")
        ttk.Entry(param_frame2, textvariable=self.min_ratings_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(query2_frame, text="Run Age Group Analysis", 
                command=self.run_age_group_books).pack(pady=5)
        
        # Query 3: Most Active Book Clubs
        query3_frame = ttk.LabelFrame(parent, text="Most Active Book Clubs", 
                                    padding="10")
        query3_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(query3_frame, text="Analyzes club engagement: member count, books read, "
                "discussions, comments, and discussions per member ratio.").pack(pady=5)
        
        param_frame3 = ttk.Frame(query3_frame)
        param_frame3.pack(pady=5)
        ttk.Label(param_frame3, text="Min Members:").pack(side=tk.LEFT, padx=5)
        self.min_members_var = tk.StringVar(value="3")
        ttk.Entry(param_frame3, textvariable=self.min_members_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(query3_frame, text="Run Club Engagement Analysis", 
                command=self.run_active_clubs).pack(pady=5)


    # Update the query methods:

    def run_top_publishers(self):
        """Run top publishers query"""
        try:
            min_books = int(self.min_books_var.get())
            min_ratings = int(self.min_pub_ratings_var.get())
        except ValueError:
            messagebox.showerror("Error", "Parameters must be numbers")
            return
        
        results = analytics_dao.get_top_publishers_by_rating(min_books, min_ratings)
        
        if not results:
            messagebox.showinfo("Results", "No data available")
            return
        
        self.show_results_table(
            "Top Publishers by Rating",
            ["Publisher Name", "Total Books", "Avg Rating", "Total Ratings"],
            results,
            lambda r: (
                r.get('publisher_name'),
                r.get('total_books'),
                f"{r.get('avg_rating', 0):.2f}",
                r.get('total_ratings')
            )
        )


    def run_age_group_books(self):
        """Run age group books query"""
        try:
            min_ratings = int(self.min_ratings_var.get())
        except ValueError:
            messagebox.showerror("Error", "Min ratings must be a number")
            return
        
        results = analytics_dao.get_top_rated_books_by_age_group(min_ratings)
        
        if not results:
            messagebox.showinfo("Results", "No data available")
            return
        
        self.show_results_table(
            "Top Rated Books by Age Group",
            ["Age Group", "ISBN", "Title", "Num Ratings", "Avg Rating"],
            results,
            lambda r: (
                r.get('age_group'),
                r.get('ISBN'),
                r.get('title'),
                r.get('num_ratings'),
                f"{r.get('avg_rating', 0):.2f}"
            )
        )


    def run_active_clubs(self):
        """Run active clubs query"""
        try:
            min_members = int(self.min_members_var.get())
        except ValueError:
            messagebox.showerror("Error", "Min members must be a number")
            return
        
        results = analytics_dao.get_most_active_book_clubs(min_members)
        
        if not results:
            messagebox.showinfo("Results", "No data available")
            return
        
        self.show_results_table(
            "Most Active Book Clubs",
            ["Club ID", "Club Name", "Members", "Books Read", "Discussions", "Comments", "Disc/Member"],
            results,
            lambda r: (
                r.get('club_id'),
                r.get('club_name'),
                r.get('member_count'),
                r.get('books_read'),
                r.get('total_discussions'),
                r.get('total_comments'),
                f"{r.get('discussions_per_member', 0):.2f}"
            )
        )
    
    def setup_simple_queries(self, parent):
        """Setup simple queries section"""
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Simple queries buttons
        queries = [
            ("Books Trending in Clubs", self.run_trending_books, 
             "Books most frequently added to club reading queues"),
            ("Most Discussed Books", self.run_discussed_books,
             "Books with most chapter discussions across clubs"),
            ("Publisher Comparison", self.run_publisher_comparison,
             "Publishers ranked by book count, ratings, and club selections"),
            ("Most Prolific Authors", self.run_prolific_authors,
             "Authors with most books published and their ratings"),
            ("Location-Based Statistics", self.run_location_stats,
             "User distribution and popular books by location"),
            ("Top Rated Books", self.run_top_rated,
             "Highest rated books with minimum rating threshold"),
            ("Club Activity Metrics", self.run_club_activity,
             "Activity metrics for all clubs")
        ]
        
        for title, command, description in queries:
            frame = ttk.LabelFrame(scrollable_frame, text=title, padding="10")
            frame.pack(fill=tk.X, pady=5, padx=10)
            
            ttk.Label(frame, text=description, wraplength=500).pack(pady=5)
            ttk.Button(frame, text=f"Run Query", command=command).pack(pady=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    # Complex Query Methods
    
    def run_club_analytics(self):
        """Run club analytics query"""
        results = analytics_dao.get_club_analytics()
        
        if not results:
            messagebox.showinfo("Results", "No data available")
            return
        
        # Create results window
        self.show_results_table(
            "Club Analytics Results",
            ["Club ID", "Name", "Public", "Members", "Avg Age", "Discussions", 
             "Current Book", "Book Rating", "Completed", "In Queue"],
            results,
            lambda r: (
                r.get('club_id'),
                r.get('club_name'),
                'Yes' if r.get('is_public') else 'No',
                r.get('member_count'),
                r.get('avg_member_age'),
                r.get('total_discussions'),
                r.get('current_book_title', 'None'),
                f"{r.get('current_book_avg_rating', 0):.2f}" if r.get('current_book_avg_rating') else 'N/A',
                r.get('books_completed'),
                r.get('books_in_queue')
            )
        )
    
    def run_cross_generational(self):
        """Run cross-generational reading patterns query"""
        try:
            min_ratings = int(self.min_ratings_var.get())
        except ValueError:
            messagebox.showerror("Error", "Min ratings must be a number")
            return
        
        results = analytics_dao.get_cross_generational_reading_patterns(min_ratings)
        
        if not results:
            messagebox.showinfo("Results", "No data available")
            return
        
        self.show_results_table(
            "Cross-Generational Reading Patterns",
            ["Age Group", "ISBN", "Title", "Authors", "Publisher", "Readers", "Avg Rating", "Count"],
            results,
            lambda r: (
                r.get('age_group'),
                r.get('ISBN'),
                r.get('book_title'),
                r.get('authors', 'Unknown'),
                r.get('publisher', 'Unknown'),
                r.get('readers_in_group'),
                f"{r.get('avg_rating', 0):.2f}",
                r.get('rating_count')
            )
        )
    
    def run_publisher_analysis(self):
        """Run publisher success analysis query"""
        try:
            min_books = int(self.min_books_var.get())
        except ValueError:
            messagebox.showerror("Error", "Min books must be a number")
            return
        
        results = analytics_dao.get_publisher_success_analysis(min_books)
        
        if not results:
            messagebox.showinfo("Results", "No data available")
            return
        
        self.show_results_table(
            "Publisher Success Analysis",
            ["Publisher", "Books", "Avg Rating", "Ratings", "Club Selections", "In Queue",
             "High %", "Top Book"],
            results,
            lambda r: (
                r.get('publisher_name'),
                r.get('total_books'),
                f"{r.get('avg_rating', 0):.2f}",
                r.get('total_ratings'),
                r.get('club_selections'),
                r.get('times_in_queue'),
                f"{r.get('high_rating_percentage', 0):.1f}%",
                r.get('top_rated_book', 'N/A')
            )
        )
    
    # Simple Query Methods
    
    def run_trending_books(self):
        """Run trending books query"""
        results = simple_queries_dao.get_books_trending_in_clubs(limit=30)
        
        if not results:
            messagebox.showinfo("Results", "No data available")
            return
        
        self.show_results_table(
            "Books Trending in Clubs",
            ["ISBN", "Title", "Authors", "Publisher", "Clubs", "Avg Rating", "Ratings"],
            results,
            lambda r: (
                r.get('ISBN'),
                r.get('title'),
                r.get('authors', 'Unknown'),
                r.get('publisher', 'Unknown'),
                r.get('clubs_count'),
                f"{r.get('avg_rating', 0):.2f}" if r.get('avg_rating') else 'N/A',
                r.get('rating_count', 0)
            )
        )
    
    def run_discussed_books(self):
        """Run most discussed books query"""
        results = simple_queries_dao.get_most_discussed_books(limit=30)
        
        if not results:
            messagebox.showinfo("Results", "No data available")
            return
        
        self.show_results_table(
            "Most Discussed Books",
            ["ISBN", "Title", "Authors", "Discussions", "Clubs", "Avg Rating"],
            results,
            lambda r: (
                r.get('ISBN'),
                r.get('title'),
                r.get('authors', 'Unknown'),
                r.get('discussion_count'),
                r.get('clubs_discussing'),
                f"{r.get('avg_rating', 0):.2f}" if r.get('avg_rating') else 'N/A'
            )
        )
    
    def run_publisher_comparison(self):
        """Run publisher comparison query"""
        results = simple_queries_dao.get_publisher_comparison()
        
        if not results:
            messagebox.showinfo("Results", "No data available")
            return
        
        self.show_results_table(
            "Publisher Comparison",
            ["Publisher ID", "Publisher Name", "Books", "Avg Rating", "Ratings", "Club Selections"],
            results,
            lambda r: (
                r.get('publisher_id'),
                r.get('publisher_name'),
                r.get('total_books'),
                f"{r.get('avg_rating', 0):.2f}" if r.get('avg_rating') else 'N/A',
                r.get('total_ratings', 0),
                r.get('club_selections', 0)
            )
        )
    
    def run_prolific_authors(self):
        """Run most prolific authors query"""
        results = simple_queries_dao.get_most_prolific_authors(limit=30)
        
        if not results:
            messagebox.showinfo("Results", "No data available")
            return
        
        self.show_results_table(
            "Most Prolific Authors",
            ["Author ID", "Author Name", "Books", "Avg Rating", "Ratings"],
            results,
            lambda r: (
                r.get('author_id'),
                r.get('author_name'),
                r.get('book_count'),
                f"{r.get('avg_rating', 0):.2f}" if r.get('avg_rating') else 'N/A',
                r.get('total_ratings', 0)
            )
        )
    
    def run_location_stats(self):
        """Run location-based statistics query"""
        results = simple_queries_dao.get_location_based_stats()
        
        if not results:
            messagebox.showinfo("Results", "No data available")
            return
        
        self.show_results_table(
            "Location-Based Statistics",
            ["Location", "Users", "Ratings", "Avg Rating", "Most Popular Book"],
            results,
            lambda r: (
                r.get('location'),
                r.get('user_count'),
                r.get('total_ratings', 0),
                f"{r.get('avg_rating_given', 0):.2f}" if r.get('avg_rating_given') else 'N/A',
                r.get('most_popular_book', 'N/A')
            )
        )
    
    def run_top_rated(self):
        """Run top rated books query"""
        results = simple_queries_dao.get_top_rated_books(min_ratings=10, limit=50)
        
        if not results:
            messagebox.showinfo("Results", "No data available")
            return
        
        self.show_results_table(
            "Top Rated Books",
            ["ISBN", "Title", "Authors", "Publisher", "Year", "Avg Rating", "Ratings"],
            results,
            lambda r: (
                r.get('ISBN'),
                r.get('title'),
                r.get('authors', 'Unknown'),
                r.get('publisher', 'Unknown'),
                r.get('year_of_publication', 'N/A'),
                f"{r.get('avg_rating', 0):.2f}",
                r.get('rating_count')
            )
        )
    
    def run_club_activity(self):
        """Run club activity metrics query"""
        results = simple_queries_dao.get_club_activity_metrics()
        
        if not results:
            messagebox.showinfo("Results", "No data available")
            return
        
        self.show_results_table(
            "Club Activity Metrics",
            ["Club ID", "Club Name", "Members", "Discussions", "Completed", "In Queue"],
            results,
            lambda r: (
                r.get('club_id'),
                r.get('club_name'),
                r.get('member_count'),
                r.get('total_discussions'),
                r.get('books_completed'),
                r.get('books_in_queue')
            )
        )
    
    def show_results_table(self, title, columns, results, row_mapper):
        """Show results in a table dialog"""
        # Create results window
        dialog = tk.Toplevel(self.frame)
        dialog.title(title)
        dialog.geometry("1000x600")
        
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text=title, font=('Helvetica', 12, 'bold')).pack(pady=(0, 10))
        
        # Create treeview
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        
        # Load data
        for result in results:
            tree.insert("", tk.END, values=row_mapper(result))
        
        # Info label
        info_label = ttk.Label(frame, text=f"Total Results: {len(results)}")
        info_label.pack(pady=(10, 0))

        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=(10, 0))
        
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side=tk.LEFT, padx=5)