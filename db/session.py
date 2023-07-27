from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.orm import declarative_base

engine = create_engine("mysql+pymysql://root:123456@127.0.0.1:3306/demo47", echo=True)
SessionLocal = sessionmaker(autocommit=False, expire_on_commit=False, bind=engine)

Base = declarative_base()


