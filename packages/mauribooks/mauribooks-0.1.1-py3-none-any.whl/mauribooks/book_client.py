import httpx
from typing import Optional, List, Literal, Union
import pandas as pd

from .schemas import (
    BookSimple,
    BookDetailed,
    RatingSimple,
    TagSimple,
    BookTagSimple,
    AnalyticsResponse,
)
from .book_config import BookConfig


class BookClient:
    def __init__(self, config: Optional[BookConfig] = None, timeout: float = 60.0):
        """
        Client SDK pour l'API Books.

        Args:
            config (BookConfig): Configuration avec l'URL de base.
            timeout (float): Timeout global pour les requêtes HTTP.
        """
        self.config = config or BookConfig()
        self.book_base_url = self.config.book_base_url
        self.client = httpx.Client(base_url=self.book_base_url, timeout=timeout)

    def _format_output(self, data, model, output_format: Literal["pydantic", "dict", "pandas"]):
        if output_format == "pydantic":
            return [model(**item) for item in data]
        elif output_format == "dict":
            return data
        elif output_format == "pandas":
            return pd.DataFrame(data)
        else:
            raise ValueError("Invalid output_format. Choose from 'pydantic', 'dict', or 'pandas'.")

    # --- Health Check ---
    def health_check(self) -> dict:
        response = self.client.get("/")
        response.raise_for_status()
        return response.json()

    # --- Books ---
    def get_book(self, book_id: int) -> BookDetailed:
        response = self.client.get(f"/books/{book_id}")
        response.raise_for_status()
        return BookDetailed(**response.json())

    def list_books(
        self,
        skip: int = 0,
        limit: int = 100,
        title: Optional[str] = None,
        authors: Optional[str] = None,
        output_format: Literal["pydantic", "dict", "pandas"] = "pydantic"
    ) -> Union[List[BookSimple], List[dict], "pd.DataFrame"]:
        params = {"skip": skip, "limit": limit}
        if title:
            params["title"] = title
        if authors:
            params["authors"] = authors
        response = self.client.get("/books", params=params)
        response.raise_for_status()
        return self._format_output(response.json(), BookSimple, output_format)

    # --- Ratings ---
    def get_rating(self, user_id: int, book_id: int) -> RatingSimple:
        response = self.client.get(f"/ratings/{user_id}/{book_id}")
        response.raise_for_status()
        return RatingSimple(**response.json())

    def list_ratings(
        self,
        skip: int = 0,
        limit: int = 100,
        book_id: Optional[int] = None,
        user_id: Optional[int] = None,
        min_rating: Optional[float] = None,
        output_format: Literal["pydantic", "dict", "pandas"] = "pydantic"
    ) -> Union[List[RatingSimple], List[dict], "pd.DataFrame"]:
        params = {"skip": skip, "limit": limit}
        if book_id:
            params["book_id"] = book_id
        if user_id:
            params["user_id"] = user_id
        if min_rating:
            params["min_rating"] = min_rating
        response = self.client.get("/ratings", params=params)
        response.raise_for_status()
        return self._format_output(response.json(), RatingSimple, output_format)

    # --- Tags ---
    def get_tag(self, tag_id: int) -> TagSimple:
        response = self.client.get(f"/tags/{tag_id}")
        response.raise_for_status()
        return TagSimple(**response.json())

    def list_tags(
        self,
        skip: int = 0,
        limit: int = 100,
        output_format: Literal["pydantic", "dict", "pandas"] = "pydantic"
    ) -> Union[List[TagSimple], List[dict], "pd.DataFrame"]:
        params = {"skip": skip, "limit": limit}
        response = self.client.get("/tags", params=params)
        response.raise_for_status()
        return self._format_output(response.json(), TagSimple, output_format)

    # --- Book Tags ---
    def list_book_tags(
        self,
        skip: int = 0,
        limit: int = 100,
        book_id: Optional[int] = None,
        tag_id: Optional[int] = None,
        output_format: Literal["pydantic", "dict", "pandas"] = "pydantic"
    ) -> Union[List[BookTagSimple], List[dict], "pd.DataFrame"]:
        params = {"skip": skip, "limit": limit}
        if book_id:
            params["book_id"] = book_id
        if tag_id:
            params["tag_id"] = tag_id
        response = self.client.get("/book_tags", params=params)
        response.raise_for_status()
        return self._format_output(response.json(), BookTagSimple, output_format)

    # --- Analytics ---
    def get_analytics(self) -> AnalyticsResponse:
        response = self.client.get("/statistics")
        response.raise_for_status()
        return AnalyticsResponse(**response.json())

    # --- Fermeture du client ---
    def close(self):
        self.client.close()