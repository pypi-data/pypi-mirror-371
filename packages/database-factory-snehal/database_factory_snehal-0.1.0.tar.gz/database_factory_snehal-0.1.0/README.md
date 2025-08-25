# Database Factory

A robust, self-cleaning factory for creating isolated temporary SQLite databases. Perfect for pytest fixtures, automated testing, and any scenario requiring a clean database state. Built on SQLAlchemy.

## Features

-   **🧹 Guaranteed Cleanup:** Uses a context manager to automatically delete temporary database files, even if your code throws an error.
-   **💾 System Safe:** Creates databases in the system's temp directory, avoiding permission issues and leftover files.
-   **🔌 SQLAlchemy Ready:** Returns a standard SQLAlchemy `Engine` object, ready for use with both Core and ORM.
-   **⚡ Zero Config:** No setup needed. Works out of the box with a single import.
-   **🧪 Testing Focused:** The ideal tool for creating isolated database fixtures for your test suite.

## Installation

```bash
pip install database-factory-snehal
```

## Quickstart

The `temporary_database` context manager is the easiest way to get started.

```python
from database_factory import temporary_database
from sqlalchemy import text

# The database is created when you enter the `with` block...
with temporary_database() as engine:
    # ...and is automatically deleted when you leave it.
    with engine.connect() as conn:
        # Use SQLAlchemy Core for raw SQL operations
        conn.execute(text("CREATE TABLE test (id INTEGER, name TEXT);"))
        conn.execute(text("INSERT INTO test (name) VALUES ('My Data');"))
        
        # Read the data back
        result = conn.execute(text("SELECT * FROM test;"))
        for row in result:
            print(row)  # Output: (1, 'My Data')
# The temporary database file is now gone.
```

## Advanced Usage

### For Full Control: `create_isolated_engine()`

If you need to manage the lifecycle yourself, use the lower-level function.

```python
from database_factory import create_isolated_engine
import os

# Create the engine and get its path
engine, db_path = create_isolated_engine()

try:
    # ... do your work with the engine ...
    print(f"Database is active at: {db_path}")
finally:
    # You are responsible for cleanup!
    engine.dispose()
    if os.path.exists(db_path):
        os.remove(db_path)
```

### With SQLAlchemy ORM

The factory works seamlessly with the SQLAlchemy ORM.

```python
from database_factory import temporary_database
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)

with temporary_database() as engine:
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Use the ORM session
    with Session(engine) as session:
        new_user = User(name="Snehal")
        session.add(new_user)
        session.commit()
        
        user = session.get(User, 1)
        print(user.name)  # Output: Snehal
```

## API Reference

### `temporary_database()`
The main context manager.
-   **Yields:** `sqlalchemy.engine.Engine` - A SQLAlchemy engine connected to the temporary database.
-   **Guarantee:** The temporary file is deleted upon exit, regardless of success or failure.

### `create_isolated_engine()`
The lower-level function for manual lifecycle management.
-   **Returns:** `tuple` - `(engine, db_path)` The SQLAlchemy engine and the absolute path to the temporary file.
-   **Note:** You are responsible for calling `engine.dispose()` and `os.remove(db_path)`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the repository
2.  Create your feature branch (`git checkout -b feature/amazing-feature`)
3.  Commit your changes (`git commit -m 'Add some amazing feature'`)
4.  Push to the branch (`git push origin feature/amazing-feature`)
5.  Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

-   Built with the fantastic [SQLAlchemy](https://www.sqlalchemy.org/) library.