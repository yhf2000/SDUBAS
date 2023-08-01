from sqlalchemy import create_engine

from const import SQLALCHEMY_DATABASE_URL

# 这里需要引入所有使用 Base 的 Model
from model.project import Project, ProjectCredit, ProjectContentSubmission, ProjectContent, ProjectContentUserScore, \
    ProjectContentUserSubmission
from model.user import User, User_info, School, College, Major, Class, Operation, Session
from model.financial import Financial, Resource, Bill
create_table_list = [
    Project, ProjectCredit, ProjectContentSubmission, ProjectContent, ProjectContentUserScore,
    ProjectContentUserSubmission, User, User_info, School, College, Major, Class, Operation, Session,
    Financial, Resource, Bill

]

if __name__ == "__main__":
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    for tb in create_table_list:
        tb.__table__.create(bind=engine, checkfirst=True)
