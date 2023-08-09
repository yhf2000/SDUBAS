from fastapi.encoders import jsonable_encoder

import model.user
from model.db import dbSession
from model.user import User, User_info, Session, School, College, Major, Class, Operation
from type.user import register_interface, user_info_interface, session_interface, \
    school_interface, college_interface, class_interface, major_interface, operation_interface, user_add_interface
import controller.users


class UserModel(dbSession):
    def register_user(self, obj: register_interface):  # 用户自己注册(在user表中添加一个用户)
        obj_dict = jsonable_encoder(obj)
        obj_add = User(**obj_dict)
        obj_add.password = controller.users.encrypted_password(obj_add.password, obj_add.registration_dt)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            return obj_add.id

    def add_user(self, obj: user_add_interface):  # 管理员添加一个用户(在user表中添加一个用户)
        obj_dict = jsonable_encoder(obj)
        obj_add = User(**obj_dict)
        obj_add.password = controller.users.encrypted_password(obj_add.password, obj_add.registration_dt)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            return obj_add.id

    def delete_user(self, id: int):  # 删除一个用户
        with self.get_db() as session:
            session.query(User).filter(User.id == id).update({"has_delete": 1})
            session.commit()
            return id

    def update_user_status(self, id: int, status: int):  # 更改用户账号状态
        with self.get_db() as session:
            session.query(User).filter(User.id == id).update({"status": status})
            session.commit()
            return id

    def update_user_storage_quota(self, id: int, storage_quota: int):  # 更改用户存储空间限制
        with self.get_db() as session:
            session.query(User).filter(User.id == id).update({"storage_quota": storage_quota})
            session.commit()
            return id

    def update_user_password(self, id: int, password: str):  # 更改用户名
        with self.get_db() as session:
            session.query(User).filter(User.id == id).update({"password": password})
            session.commit()
            return id

    def update_user_username(self, id: int, username: str):  # 更改用户名
        with self.get_db() as session:
            session.query(User).filter(User.id == id).update({"username": username})
            session.commit()
            return id

    def update_user_email(self, id: int, email: str):  # 更改绑定邮箱
        with self.get_db() as session:
            session.query(User).filter(User.id == id).update({"email": email})
            session.commit()
            return id

    def update_user_card_id(self, id: int, card_id: str):  # 更改学号
        with self.get_db() as session:
            session.query(User).filter(User.id == id).update({"card_id": card_id})
            session.commit()
            return id

    def get_user_by_username(self, username):  # 根据username查询user的基本信息
        with self.get_db() as session:
            user = session.query(User).filter(User.has_delete == 0, User.username == username).first()
            session.commit()
            return user

    def get_user_by_email(self, email):  # 根据email查询user的基本信息
        with self.get_db() as session:
            user = session.query(User).filter(User.has_delete == 0, User.email == email).first()
            session.commit()
            return user

    def get_user_by_user_id(self, user_id):  # 根据user_id查询user的基本信息
        with self.get_db() as session:
            user = session.query(User).filter(User.id == user_id, User.has_delete == 0).first()
            session.commit()
            return user


class SessionModel(dbSession):
    def add_session(self, obj: session_interface):  # 添加一个session
        obj_dict = jsonable_encoder(obj)
        obj_add = Session(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            return obj_add.id

    def delete_session(self, id: int):  # 删除一个session
        with self.get_db() as session:
            session.query(Session).filter(Session.id == id).update({"has_delete": 1})
            session.commit()
            return id

    def delete_session_by_token(self, token: str):  # 删除一个session
        with self.get_db() as session:
            session.query(Session).filter(Session.token == token).update({"has_delete": 1})
            session.commit()
            return 'ok'

    def get_session_by_token(self, token):  # 根据token查询session的基本信息
        with self.get_db() as session:
            ses = session.query(Session).filter(Session.has_delete == 0, Session.token == token).first()
            session.commit()
            return ses

    def get_session_by_token_force(self, token):  # 根据token查询session的基本信息（不论是否有效）
        with self.get_db() as session:
            ses = session.query(Session).filter(Session.token == token).first()
            session.commit()
            return ses

    def get_session_by_id(self, id):  # 根据id查询session的基本信息
        with self.get_db() as session:
            ses = session.query(Session).filter(Session.id == id, Session.has_delete == 0).first()
            session.commit()
            return ses

    def update_session_use(self, id: int, use_add: int):  # 更改session中的use
        with self.get_db() as session:
            old_session = self.get_session_by_id(id)
            old_session.use = old_session.use + use_add
            return self.add_new_something(old_session)

    def update_session_use_limit(self, id: int, use_limit: int):  # 更改session中的use_limit
        with self.get_db() as session:
            session.query(Session).filter(Session.id == id).update({"use_limit": use_limit})
            session.commit()
            return id

    def add_new_something(self, new):
        with self.get_db() as session:
            session.add(new)
            session.flush()
            session.commit()
            return new.id


class UserinfoModel(dbSession):
    def add_userinfo(self, obj: user_info_interface):  # 在user_info表中添加一条信息
        obj_dict = jsonable_encoder(obj)
        obj_dict.pop('card_id')
        new_user_info = model.user.User_info(**obj_dict)
        # 在user_info表中新建一个
        return self.add_new_something(new_user_info)

    def delete_userinfo(self, id: int):  # 删除一条信息
        with self.get_db() as session:
            session.query(User_info).filter(User_info.id == id).update({"has_delete": 1})
            session.commit()
            return id

    def update_userinfo_realname(self, id: int, realname: str):  # 更改用户真实名字
        with self.get_db() as session:
            session.query(User_info).filter(User_info.id == id).update({"realname": realname})
            session.commit()
            return id

    def update_userinfo_gender(self, id: int, gender: int):  # 更改用户性别
        with self.get_db() as session:
            session.query(User_info).filter(User_info.id == id).update({"gender": gender})
            session.commit()
            return id

    def update_userinfo_major(self, id: int, major_id: int):  # 更改用户专业
        with self.get_db() as session:
            session.query(User_info).filter(User_info.id == id).update({"major_id": major_id})
            session.commit()
            return id

    def update_userinfo_class(self, id: int, class_id: int):  # 更改用户班级
        with self.get_db() as session:
            session.query(User_info).filter(User_info.id == id).update({"class_id": class_id})
            session.commit()
            return id

    def get_userinfo_by_user_id(self, user_id):  # 根据user_id查询user的基本信息
        with self.get_db() as session:
            userinfo = session.query(User_info).filter(User_info.user_id == user_id, User_info.has_delete == 0).first()
            session.commit()
            return userinfo

    def get_userinfo_by_id(self, id):  # 根据id查询userinfo的基本信息
        with self.get_db() as session:
            userinfo = session.query(User).filter(User_info.id == id, User_info.has_delete == 0).first()
            session.commit()
            return userinfo

    def add_new_something(self, new):
        with self.get_db() as session:
            session.add(new)
            session.flush()
            session.commit()
            return new.id


class SchoolModel(dbSession):
    def add_school(self, obj: school_interface):  # 添加一个school
        obj_dict = jsonable_encoder(obj)
        obj_add = School(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            return obj_add.id

    def delete_school(self, id: int):  # 删除一个school
        with self.get_db() as session:
            session.query(School).filter(School.id == id).update({"has_delete": 1})
            session.commit()
            return id

    def get_school_by_name(self, name):  # 根据name查询school的基本信息
        with self.get_db() as session:
            school = session.query(School).filter(School.has_delete == 0, School.name == name).first()
            session.commit()
            return school

    def get_school_by_abbreviation(self, abbreviation):  # 根据学校简称查询school的基本信息
        with self.get_db() as session:
            school = session.query(School).filter(School.has_delete == 0, School.school_abbreviation == abbreviation
                                                  ).first()
            session.commit()
            return school

    def get_school_by_id(self, id):  # 根据id查询school的基本信息
        with self.get_db() as session:
            school = session.query(School).filter(School.id == id, School.has_delete == 0).first()
            session.commit()
            return school

    def get_school_by_admin(self, page):  # 查找某管理员能操作的所有学校
        with self.get_db() as session:
            school = session.query(School).filter(School.has_delete == 0).order_by(
                School.id).offset(
                page.offset()).limit(page.limit()).all()
            session.commit()
            return school

    def update_school_name(self, id, name):  # 更改school中的name
        with self.get_db() as session:
            session.query(School).filter(School.id == id).update({"name": name})
            session.commit()
            return id

    def update_school_abbreviation(self, id, abbreviation):  # 更改school中的abbreviation
        with self.get_db() as session:
            session.query(School).filter(School.id == id).update({"school_abbreviation": abbreviation})
            session.commit()
            return id


class CollegeModel(dbSession):
    def add_college(self, obj: college_interface):  # 添加一个college
        obj_dict = jsonable_encoder(obj)
        obj_add = College(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            return obj_add.id

    def delete_college(self, id: int):  # 删除一个college
        with self.get_db() as session:
            session.query(College).filter(College.id == id).update({"has_delete": 1})
            session.commit()
            return id

    def get_college_by_name(self, obj: college_interface):  # 根据school_id,name查询college的基本信息
        with self.get_db() as session:
            college = session.query(College).filter(College.has_delete == 0, College.school_id == obj.school_id,
                                                    College.name == obj.name).first()
            session.commit()
            return college

    def get_college_by_id(self, id):  # 根据id查询college的基本信息
        with self.get_db() as session:
            college = session.query(College).filter(College.has_delete == 0, College.id == id).first()
            session.commit()
            return college

    def get_college_by_admin(self, page):  # 查找某管理员能操作的所有college
        with self.get_db() as session:
            college = session.query(College).filter(College.has_delete == 0).order_by(
                College.id).offset(
                page.offset()).limit(page.limit()).all()
            session.commit()
            return college

    def update_college_school_id_name(self, id, school_id, name):  # 更改college中的school_id与name
        with self.get_db() as session:
            session.query(College).filter(College.id == id).update({"school_id": school_id, "name": name})
            session.commit()
            return id


class MajorModel(dbSession):
    def add_major(self, obj: major_interface):  # 添加一个major
        obj_dict = jsonable_encoder(obj)
        obj_dict.pop('school_id')
        obj_add = Major(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            return obj_add.id

    def delete_major(self, id: int):  # 删除一个major
        with self.get_db() as session:
            session.query(Major).filter(Major.id == id).update({"has_delete": 1})
            session.commit()
            return id

    def get_major_by_id(self, id):  # 根据id查询major的基本信息
        with self.get_db() as session:
            major = session.query(Major).filter(Major.has_delete == 0, Major.id == id).first()
            session.commit()
            return major

    def get_major_by_name(self, obj: major_interface):  # 根据专业名和学院id和学校id查询专业
        with self.get_db() as session:
            major = session.query(Major).outerjoin(College, Major.college_id == College.id).outerjoin(School,
                                                                                                      Major.has_delete == 0,
                                                                                                      College.school_id == School.id).filter(
                College.id == obj.college_id,
                Major.name == obj.name,
                School.id == obj.school_id

            ).first()
            session.commit()
            return major

    def get_major_by_admin(self, page):  # 查找某管理员能操作的所有major
        with self.get_db() as session:
            major = session.query(Major).filter(Major.has_delete == 0).order_by(
                Major.id).offset(
                page.offset()).limit(page.limit()).all()
            session.commit()
            return major

    def update_major_college_id_name(self, id, college_id, name):  # 更改college中的school_id与name
        with self.get_db() as session:
            session.query(Major).filter(Major.id == id).update({"college_id": college_id, "name": name})
            session.commit()
            return id


class ClassModel(dbSession):
    def add_class(self, obj: class_interface):  # 添加一个class
        obj_dict = jsonable_encoder(obj)
        obj_dict.pop('school_id')
        obj_add = Class(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            return obj_add.id

    def delete_class(self, id: int):  # 删除一个class
        with self.get_db() as session:
            session.query(Class).filter(Class.id == id).update({"has_delete": 1})
            session.commit()
            return id

    def get_class_by_id(self, id):  # 根据id查询class的基本信息
        with self.get_db() as session:
            clas = session.query(Class).filter(Class.has_delete == 0, Class.id == id).first()
            session.commit()
            return clas

    def get_class_by_name(self, obj: class_interface):  # 根据班级名和学院id和学校id查询班级
        with self.get_db() as session:
            clas = session.query(Class).outerjoin(College, Class.college_id == College.id).outerjoin(School,
                                                                                                     Class.has_delete == 0,
                                                                                                     College.school_id == School.id).filter(
                College.id == obj.college_id,
                Class.name == obj.name,
                School.id == obj.school_id

            ).first()
            session.commit()
            return clas

    def get_class_by_admin(self, page):  # 查找某管理员能操作的所有class
        with self.get_db() as session:
            clas = session.query(Class).filter(Class.has_delete == 0).order_by(
                Class.id).offset(
                page.offset()).limit(page.limit()).all()
            session.commit()
            return clas

    def update_major_college_id_name(self, id, college_id, name):  # 更改class中的college_id与name
        with self.get_db() as session:
            session.query(Class).filter(Class.id == id).update({"college_id": college_id, "name": name})
            session.commit()
            return id


class OperationModel(dbSession):
    def add_operation(self, obj: operation_interface):  # 添加一个操作(在operation表中添加一个操作)
        obj.oper_hash = obj.get_oper_hash()
        obj_dict = jsonable_encoder(obj)
        obj_add = Operation(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            return obj_add.id

    def get_operation_by_service_func(self, service_type, service_id, func):  # 根据service与func查询operation的基本信息
        with self.get_db() as session:
            operation = session.query(Operation).filter(Operation.service_type == service_type,
                                                        Operation.service_id == service_id,
                                                        Operation.func == func).first()
            session.commit()
            return operation

    def get_operation_by_oper_user_id(self, oper_user_id):  # 根据user_id查询operation的基本信息
        with self.get_db() as session:
            operation = session.query(Operation).filter(Operation.oper_user_id == oper_user_id).first()
            session.commit()
            return operation

    def get_operation_by_id(self, id):  # 根据id查询operation的基本信息
        with self.get_db() as session:
            operation = session.query(Operation).filter(Operation.id == id).first()
            session.commit()
            return operation
