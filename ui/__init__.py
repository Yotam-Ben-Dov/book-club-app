"""
UI package
Contains all user interface components
"""

from ui.main_window import MainWindow
from ui.books_tab import BooksTab
from ui.users_tab import UsersTab
from ui.ratings_tab import RatingsTab
from ui.clubs_tab import ClubsTab
from ui.analytics_tab import AnalyticsTab
from ui.dialogs import ViewDiscussionDialog

__all__ = [
    'MainWindow',
    'BooksTab',
    'UsersTab',
    'RatingsTab',
    'ClubsTab',
    'AnalyticsTab',
    'ViewDiscussionDialog'
]