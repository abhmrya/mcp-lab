import sqlite3
from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database location
DB_PATH = BASE_DIR / "data" / "shop.db"


def create_database():
    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL
        )
    """)

    products = [
        ("Laptop", 50000, "Electronics"),
        ("Mouse", 500, "Accessories"),
        ("Keyboard", 1200, "Accessories"),
    ]

    cursor.executemany(
        """
        INSERT INTO products (name, price, category)
        VALUES (?, ?, ?)
        """,
        products,
    )

    connection.commit()
    connection.close()

    print("Database created successfully!")


if __name__ == "__main__":
    create_database()