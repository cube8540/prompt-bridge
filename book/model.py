import datetime
import typing

class Series:
    def __init__(self,
                 series_id: int,
                 name: str,
                 isbn: str = None,
                 registered_at: datetime.datetime = None,
                 modified_at: datetime.datetime = None,
                 vec: typing.List[float] = None):
        self.id = series_id
        self.name = name
        self.isbn = isbn
        self.registered_at = registered_at
        self.modified_at = modified_at
        self.vec = vec

class Book:
    def __init__(self,
                 book_id: int,
                 isbn: str,
                 title: str,
                 publisher_id: int,
                 scheduled_pub_date: datetime.date = None,
                 actual_pub_date: datetime.date = None,
                 series_id: int = None,
                 registered_at: datetime.datetime = None,
                 modified_at:datetime.datetime = None):
        self.id = book_id
        self.isbn = isbn
        self.title = title
        self.publisher_id = publisher_id
        self.scheduled_pub_date = scheduled_pub_date
        self.actual_pub_date = actual_pub_date
        self.series_id = series_id
        self.registered_at = registered_at
        self.modified_at = modified_at