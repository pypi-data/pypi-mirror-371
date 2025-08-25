from sqlalchemy import create_engine
import os
import tempfile
from contextlib import contextmanager



def create_isolated_engine():
    file_descriptor, file_path = tempfile.mkstemp(suffix='.db')
    os.close(file_descriptor)
    db_url = f"sqlite:///{file_path}"
    engine = create_engine(db_url)
    print(f"[FACTORY] Engine created for temporary database: {file_path}")
    return engine,file_path


@contextmanager
def temporary_database():
    try:
        engine = None
        db_path = None

        engine,db_path = create_isolated_engine()

        yield engine
    finally:
        print("[FACTORY] Cleanup initiated.") 
        if engine is not None:
            engine.dispose()
            print("[FACTORY] Engine connections disposed.")

        if db_path is not None and os.path.exists(db_path):
            os.remove(db_path)
            print(f"[FACTORY] Database file deleted: {db_path}")

