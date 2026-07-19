from app.database import Base, engine
from app import models  # noqa: F401  (ensures model classes are registered on Base.metadata)


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created.")
