from sqlalchemy import create_engine

from const import SQLALCHEMY_DATABASE_URL

# 这里需要引入所有使用 Base 的 Model
from model.project import Project

create_table_list = [
    Project
]


if __name__ == "__main__":
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    for tb in create_table_list:
        tb.__table__.create(bind=engine, checkfirst=True)
