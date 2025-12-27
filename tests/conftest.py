import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from arbitrage_os.db.database import Base

@pytest.fixture(scope="function", autouse=True)
def test_db_setup_and_teardown(monkeypatch):
    """
    Central fixture to set up and tear down a test database for each test function.
    This fixture will automatically apply to all tests.
    """
    # 1. Define the test database URL (in-memory SQLite)
    TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

    # 2. Create the test engine
    test_engine = create_engine(
        TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    
    # 3. Create a test session maker
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # 4. Monkeypatch the original engine and SessionLocal in the database module
    monkeypatch.setattr("arbitrage_os.db.database.engine", test_engine)
    monkeypatch.setattr("arbitrage_os.db.database.SessionLocal", TestSessionLocal)

    # 5. Create all tables on the test engine
    from arbitrage_os.db import models
    Base.metadata.create_all(bind=test_engine)

    # 6. Yield control to the test function
    yield

    # 7. Drop all tables after the test function completes
    Base.metadata.drop_all(bind=test_engine)
