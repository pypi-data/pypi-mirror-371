import os
from dotenv import load_dotenv

load_dotenv()

class BookConfig:
    """Classe de configuration pour le SDK BookClient.

    Contient la configuration de l'URL de base.
    """

    book_base_url: str

    def __init__(self, book_base_url: str = None):
        """
        Initialise la configuration du client BookClient.

        Args:
            book_base_url (str, optional): URL de base de l'API.
                Si non fourni, sera lu depuis la variable d'environnement BOOK_API_BASE_URL.
        """
        self.book_base_url = book_base_url or os.getenv("BOOK_API_BASE_URL")
        print(f"BOOK_API_BASE_URL in BookConfig init: {self.book_base_url}")

        if not self.book_base_url:
            raise ValueError(
                "L'URL de base est requise. Définissez la variable d'environnement BOOK_API_BASE_URL ou fournissez-la au constructeur."
            )

    def __str__(self):
        """Représentation de l'objet pour le logging."""
        return f"BookConfig(book_base_url='{self.book_base_url}')"