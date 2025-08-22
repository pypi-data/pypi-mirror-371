from pydantic import BaseModel
from typing import Optional, List


# --- Schémas secondaires ---

class RatingBase(BaseModel):
    user_id: int
    book_id: int
    rating: float

    class Config:
        orm_mode = True


class BookTagBase(BaseModel):
    goodreads_book_id: int
    tag_id: int
    count: int

    class Config:
        orm_mode = True


class TagBase(BaseModel):
    tag_id: int
    tag_name: str

    class Config:
        orm_mode = True


class ToReadBase(BaseModel):
    user_id: int
    book_id: int

    class Config:
        orm_mode = True


# --- Schéma principal pour Book ---
class BookBase(BaseModel):
    book_id: int
    goodreads_book_id: int
    best_book_id: int
    work_id: int
    books_count: int
    isbn: Optional[str]
    isbn13: Optional[str]
    authors: str
    original_publication_year: Optional[int]
    original_title: Optional[str]
    title: str
    language_code: Optional[str]
    average_rating: Optional[float]
    ratings_count: Optional[int]
    work_ratings_count: Optional[int]
    work_text_reviews_count: Optional[int]
    ratings_1: Optional[int]
    ratings_2: Optional[int]
    ratings_3: Optional[int]
    ratings_4: Optional[int]
    ratings_5: Optional[int]
    image_url: Optional[str]
    small_image_url: Optional[str]

    class Config:
        orm_mode = True


class BookDetailed(BookBase):
    ratings: List[RatingBase] = []
    tags: List[TagBase] = []
    to_read: List[ToReadBase] = []


# --- Schéma pour liste de livres (sans détails imbriqués) ---
class BookSimple(BaseModel):
    book_id: int
    title: str
    authors: str
    average_rating: Optional[float]

    class Config:
        orm_mode = True


# --- Pour les endpoints individuels ---
class RatingSimple(BaseModel):
    user_id: int
    book_id: int
    rating: float

    class Config:
        orm_mode = True


class TagSimple(BaseModel):
    tag_id: int
    tag_name: str

    class Config:
        orm_mode = True


class BookTagSimple(BaseModel):
    goodreads_book_id: int
    tag_id: int
    count: int

    class Config:
        orm_mode = True


class ToReadSimple(BaseModel):
    user_id: int
    book_id: int

    class Config:
        orm_mode = True


class AnalyticsResponse(BaseModel):
    book_count: int
    rating_count: int
    tag_count: int
    to_read_count: int
    book_tag_count: int  

    class Config:
        from_attributes = True  



# Schéma détaillé pour Book, incluant les relations
# class BookDetailed(BaseModel):
#     book_id: int
#     goodreads_book_id: int
#     title: str
#     authors: Optional[str] = None
#     original_publication_year: Optional[int]
#     original_title: Optional[str]
#     language_code: Optional[str]
#     average_rating: Optional[float]
#     ratings_count: Optional[int]

#     ratings: List[RatingSimple] = []
#     book_tags: List[BookTagSimple] = []

#     class Config:
#         orm_mode = True