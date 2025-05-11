import datetime
import typing
from enum import Enum

class Site(Enum):
    NLGO = "nlgo"
    ALADIN = "aladin"
    NAVER = "naver"
    KYOBO = "kyobo"

class Series:
    def __init__(self,
                 series_id: int = 0,
                 name: str = None,
                 isbn: str = None,
                 registered_at: datetime.datetime = None,
                 modified_at: datetime.datetime = None,
                 main_title_vec: typing.List[float] = None,):
        self.id = series_id
        self.name = name
        self.isbn = isbn
        self.registered_at = registered_at
        self.modified_at = modified_at
        self.main_title_vec = main_title_vec

    def __str__(self):
        return f"({self.id}) {self.name}"

class BookOriginData:
    def __init__(self,
                 book_id: int,
                 site: Site,
                 property_name: str,
                 value: str):
        self.book_id = book_id
        self.site = site
        self.property_name = property_name
        self.value = value

class Book:
    _cached_series_isbn: str | None = None

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
        self.origin_data: typing.Dict[Site, list[BookOriginData]] = {}

    def add_origin_data(self, origin_data: BookOriginData):
        if origin_data.site not in self.origin_data:
            self.origin_data[origin_data.site] = []
        self.origin_data[origin_data.site].append(origin_data)

    def retrieve_series_isbn(self) -> str | None:
        if self._cached_series_isbn is not None:
            return self._cached_series_isbn

        nlgo_origin = self.origin_data.get(Site.NLGO)
        if nlgo_origin is not None:
            series_isbn_origin = next((o for o in nlgo_origin if o.property_name == "set_isbn"), None)
            if series_isbn_origin is not None:
                self._cached_series_isbn = series_isbn_origin.value
                return self._cached_series_isbn
            else:
                return None
        else:
            return None

    def __str__(self):
        return f"({self.id}/{self.isbn}){self.title}"