from app.database.database import engine, Base

from app.models import *

print("creating database tables...")

Base.metadata.create_all(bind=engine)

print("tables created succesfully")
