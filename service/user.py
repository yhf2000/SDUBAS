import hashlib

from fastapi.encoders import jsonable_encoder

import model.user
from model.db import dbSession
from model.user import User, User_info, Session, Operation, Captcha
from type.user import register_interface, user_info_interface, session_interface, \
    operation_interface, user_add_interface


def encrypted_password(password, salt):  # 对密码进行加密
    res = hashlib.sha256()
    password += salt
    res.update(password.encode())
    return res.hexdigest()


class UserModel(dbSession):
    def register_user(self, obj: register_interface):  # 用户自己注册(在user表中添加一个用户)
        obj.registration_dt = obj.registration_dt.strftime(
            "%Y-%m-%d %H:%M:%S")
        obj_dict = jsonable_encoder(obj)
        obj_add = User(**obj_dict)
        obj_add.password = encrypted_password(obj_add.password, obj_add.registration_dt)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            return obj_add.id

    def add_user(self, obj: user_add_interface):  # 管理员添加一个用户(在user表中添加一个用户)
        obj.registration_dt = obj.registration_dt.strftime(
            "%Y-%m-%d %H:%M:%S")
        obj_dict = jsonable_encoder(obj)
        obj_add = User(**obj_dict)
        obj_add.password = encrypted_password(obj_add.password, obj_add.registration_dt)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            return obj_add.id

    def add_all_user(self, user_list):  # 管理员批量添加用户
        objects = [User(**jsonable_encoder(user_list[i])) for i in range(len(user_list))]
        with self.get_db() as session:
            session.add_all(objects)
            session.flush()
            session.commit()
            return objects

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

    def update_user_password(self, id: int, password: str):  # 更改用户密码
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

    def get_user_email_by_username(self, username):  # 根据username查询id,email
        with self.get_db() as session:
            email = session.query(User.id, User.email).filter(User.username == username).first()
            session.commit()
            return email

    def get_user_status_by_username(self, username):  # 根据username查询user的帐号状态
        with self.get_db() as session:
            user = session.query(User.status).filter(User.has_delete == 0, User.username == username).first()
            session.commit()
            return user

    def get_user_by_email(self, email):  # 根据email查询user的基本信息
        with self.get_db() as session:
            user = session.query(User).filter(User.has_delete == 0, User.email == email).first()
            session.commit()
            return user

    def get_user_status_by_email(self, email):  # 根据email查询user的帐号状态
        with self.get_db() as session:
            user = session.query(User.status).filter(User.has_delete == 0, User.email == email).first()
            session.commit()
            return user

    def get_user_status_by_card_id(self, card_id):  # 根据card_id查询user的帐号状态
        with self.get_db() as session:
            user = session.query(User.status).filter(User.has_delete == 0, User.card_id == card_id).first()
            session.commit()
            return user

    def get_user_id_by_email(self, email):  # 根据email查询user_id
        with self.get_db() as session:
            user = session.query(User.id).filter(User.has_delete == 0, User.email == email).first()
            session.commit()
            return user

    def get_user_by_user_id(self, user_id):  # 根据user_id查询user的基本信息
        with self.get_db() as session:
            user = session.query(User).filter(User.id == user_id, User.has_delete == 0).first()
            session.commit()
            return user

    def get_user_information_by_id(self, user_id):  # 根据user_id查询user的所有信息
        with self.get_db() as session:
            user = session.query(User, User_info).outerjoin(User_info, User_info.user_id == User.id).filter(
                User.id == user_id,
                User.has_delete == 0
            ).first()
            session.commit()
            return user

    def get_user_status_by_user_id(self, user_id):  # 根据user_id查询user的帐号状态
        with self.get_db() as session:
            status = session.query(User.status).filter(User.id == user_id, User.has_delete == 0).first()
            session.commit()
            return status

    def get_name_by_user_id(self, user_id):  # 根据user_id查询username,realname
        with self.get_db() as session:
            names = session.query(User.username, User_info.realname).outerjoin(User_info,
                                                                               User_info.user_id == user_id).filter(
                User.id == user_id, User.has_delete == 0).first()
            session.commit()
            return names


class SessionModel(dbSession):
    def add_session(self, obj: session_interface):  # 添加一个session
        obj_dict = jsonable_encoder(obj)
        obj_add = Session(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            return obj_add.id

    def delete_session(self, id: int):  # 根据id删除一个session
        with self.get_db() as session:
            session.query(Session).filter(Session.id == id).update({"has_delete": 1})
            session.commit()
            return id

    def delete_session_by_token(self, token: str):  # 根据token删除一个session
        with self.get_db() as session:
            session.query(Session).filter(Session.token == token).update({"has_delete": 1})
            session.commit()
            return 'ok'

    def get_session_by_token(self, token):  # 根据token查询session的基本信息
        with self.get_db() as session:
            ses = session.query(Session).filter(Session.has_delete == 0, Session.token == token).first()
            session.commit()
            return ses

    def get_user_id_by_token(self, token):  # 根据token查询user_id
        with self.get_db() as session:
            user_id = session.query(Session.user_id).filter(Session.has_delete == 0, Session.token == token).first()
            session.commit()
            return user_id


    def get_session_by_id(self, id):  # 根据id查询session的基本信息
        with self.get_db() as session:
            ses = session.query(Session).filter(Session.id == id, Session.has_delete == 0).first()
            session.commit()
            return ses

    def update_session_use(self, id: int, use_add: int):  # 根据id更改session中的use
        with self.get_db() as session:
            session.query(Session).filter(Session.id == id).update({"use": Session.use + use_add})
            session.commit()
            return id

    def update_session_use_by_token(self, token: str, use_add: int):  # 根据token更改session中的use by token
        with self.get_db() as session:
            session.query(Session).filter(Session.token == token).update({"use": Session.use + use_add})
            session.commit()
            return "ok"

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

    def add_all_user_info(self, user_info_list, user_id_list):  # 管理员批量添加user_info
        objects = []
        for i in range(len(user_info_list)):
            obj_dict = jsonable_encoder(user_info_list[i])
            obj_dict.pop('card_id')
            obj_dict['user_id'] = user_id_list[i].id
            objects.append(User_info(**obj_dict))
        with self.get_db() as session:
            session.add_all(objects)
            session.flush()
            session.commit()
            return 'ok'

    def delete_userinfo(self, id: int):  # 删除一条信息
        with self.get_db() as session:
            session.query(User_info).filter(User_info.id == id).update({"has_delete": 1})
            session.commit()
            return id

    def delete_userinfo_by_user_id(self, user_id: int):  # 删除一条信息
        with self.get_db() as session:
            session.query(User_info).filter(User_info.user_id == user_id).update({"has_delete": 1})
            session.commit()
            return 'ok'

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

    def get_major_id_by_user_id(self, user_id):  # 根据user_id查询user的major_id
        with self.get_db() as session:
            userinfo = session.query(User_info.major_id).filter(User_info.user_id == user_id,
                                                                                    User_info.has_delete == 0).first()
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
                                                        Operation.func[0:4] == func).first()
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


class CaptchaModel(dbSession):
    def add_captcha(self, value):  # 添加一个验证码
        obj_add = Captcha(value=value)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            return obj_add.id

    def delete_captcha(self, id: int):  # 删除一个captcha
        with self.get_db() as session:
            session.query(Captcha).filter(Captcha.id == id).update({"has_delete": 1})
            session.commit()
            return id

    def get_captcha_by_id(self, id):  # 根据id查询captcha的值
        with self.get_db() as session:
            value = session.query(Captcha.value).filter(Captcha.id == id, Captcha.has_delete == 0).first()
            session.commit()
            return value
