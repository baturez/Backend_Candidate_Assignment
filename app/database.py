from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus
from .config import settings




engine = create_engine(settings.DATABASE_URL, echo=True, fast_executemany=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()



# odbc_str = (
#     f"DRIVER={{{settings.DB_DRIVER}}};"
#     f"SERVER={settings.DB_SERVER};"
#     f"DATABASE={settings.DB_NAME};"
#     f"UID={settings.DB_USER};"
#     f"PWD={settings.DB_PASSWORD};"
#     "TrustServerCertificate=yes;"
#     "Trusted_Connection=yes;"
#
#
# )
#
#
# params = quote_plus(odbc_str)
# SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"
# engine = create_engine(SQLALCHEMY_DATABASE_URL, fast_executemany=True)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()