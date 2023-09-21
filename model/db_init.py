from sqlalchemy import create_engine

from const import SQLALCHEMY_DATABASE_URL

# 这里需要引入所有使用 Base 的 Model
from model.project import Project, ProjectCredit, ProjectContentSubmission, ProjectContent, ProjectContentUserScore, \
    ProjectContentUserSubmission
from model.user import User, User_info, School, College, Major, Class, Operation, Session, Captcha
from model.financial import Financial, Resource, Bill
from model.file import File, User_File,RSAKeys
from model.permissions import UserRole, WorkRole, Role, RolePrivilege, Privilege

create_table_list = [Role,
                     Captcha, User, School, College, Major, Class, User_info, File, User_File, Operation, Session,
                     Financial, Resource, Bill, UserRole, WorkRole, Privilege, RolePrivilege,
                     Project, ProjectCredit, ProjectContent, ProjectContentSubmission, ProjectContentUserScore,
                     ProjectContentUserSubmission,RSAKeys
                     ]

if __name__ == "__main__":
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    for tb in create_table_list:
        tb.__table__.create(bind=engine, checkfirst=True)
