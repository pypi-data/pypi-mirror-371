import pytest
from sqlalchemy import text
from database_factory.engine_factory import temporary_database,create_isolated_engine
import os



def test_database_is_usable():
    """Test that the temporary database can be used for basic SQL operations."""
    with temporary_database() as engine:
        with engine.connect() as conn:
            # Create a table and insert data
            conn.execute(text("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)"))
            conn.execute(text("INSERT INTO test (value) VALUES ('success')"))
            conn.commit()

            # Read the data back
            result = conn.execute(text("SELECT value FROM test")).scalar()
            assert result == 'success'


def test_file_is_deleted_after_context():
    """
    Test that the context manager deletes the database file IT CREATED.
    """
    # We need to capture the file path that the context manager creates INSIDE the block.
    captured_db_path = None

    # Use the context manager
    with temporary_database() as engine:
        # Extract the file path from the engine's URL that the context manager created
        # The engine.url will be a string like 'sqlite:////tmp/somefile.db'
        # We need to remove the 'sqlite:///' prefix to get the system file path
        captured_db_path = str(engine.url).replace('sqlite:///', '')
        # Verify the file actually exists on disk at this moment
        assert os.path.exists(captured_db_path), f"File should exist during the context block: {captured_db_path}"

    # Now that the 'with' block has exited, the context manager's cleanup should have run.
    # The file it created should now be gone.
    assert not os.path.exists(captured_db_path), f"File should have been deleted after the context block: {captured_db_path}"

# tests/test_factory.py

def test_cleanup_on_exception():
    """Test that the database is cleaned up even if an error occurs inside the block."""
    with pytest.raises(RuntimeError):  # This test expects an error to be raised
        with temporary_database() as engine:
            db_path = str(engine.url).replace('sqlite:///', '')
            assert os.path.exists(db_path)  # File exists before error
            raise RuntimeError("Simulated catastrophic failure!")  # Boom!

    # The 'with' block has exited (due to the error). Now check if file was cleaned up.
    assert not os.path.exists(db_path), "File was not cleaned up after an exception!"