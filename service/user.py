from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, join
import model.user
from model.db import dbSession, dbSessionread
from model.user import User, User_info, Session, Operation, Captcha, Major, Class, School, College, Education_Program
from type.user import user_info_interface, session_interface, \
    operation_interface, user_add_interface, education_program_interface

programs_translation1 = {
    "thought_political_theory": "思想政治理论课",
    "college_sports": "大学体育",
    "college_english": "大学英语",
    "chinese_culture": "国学修养",
    "art_aesthetics": "艺术审美",
    "innovation_entrepreneurship": "创新创业",
    "humanities": "人文学科",
    "social_sciences": "社会科学",
    "scientific_literacy": "科学素养",
    "information_technology": "信息技术",
    "general_education_elective": "通识教育选修课程",
    "major_compulsory_courses": "专业必修课程",
    "major_elective_courses": "专业选修课程",
    "key_improvement_courses": "重点提升必修课程",
    "qilu_entrepreneurship": "齐鲁创业",
    "jixia_innovation": "稷下创新"
}


class UserModel(dbSession, dbSessionread):

    def add_user(self, obj: user_add_interface):  # 管理员添加一个用户(在user表中添加一个用户)
        obj_dict = jsonable_encoder(obj)
        obj_add = User(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.commit()
            return obj_add.id

    def add_all_user(self, user_list):  # 管理员批量添加用户
        objects = [User(**jsonable_encoder(user_list[i])) for i in range(len(user_list))]
        with self.get_db() as session:
            session.add_all(objects)
            session.commit()
            return objects

    def update_user_status(self, id: int, status: int):  # 更改用户账号状态
        with self.get_db() as session:
            session.query(User).filter(User.id == id).update({"status": status})
            session.commit()
            return id

    def update_user_password(self, id: int, password: str):  # 更改用户密码
        with self.get_db() as session:
            session.query(User).filter(User.id == id).update({"password": password})
            session.commit()
            return id

    def update_user_email(self, id: int, email: str):  # 更改绑定邮箱
        with self.get_db() as session:
            session.query(User).filter(User.id == id).update({"email": email})
            session.commit()
            return id

    def get_user_by_username(self, username):  # 根据username查询user的基本信息
        with self.get_db_read() as session:
            user = session.query(User).filter(User.has_delete == 0, User.username == username).first()
            session.commit()
            return user

    def get_user_some_by_username(self, username):  # 根据username查询user的部分信息
        with self.get_db_read() as session:
            user = session.query(User.email, User.password, User.username, User.id).filter(User.has_delete == 0,
                                                                                           User.username == username).first()
            session.commit()
            return user

    def get_user_email_by_username(self, username):  # 根据username查询id,email
        with self.get_db_read() as session:
            email = session.query(User.id, User.email).filter(User.username == username).first()
            session.commit()
            return email

    def get_user_status_by_username(self, username):  # 根据username查询user的帐号状态
        with self.get_db_read() as session:
            user = session.query(User.status).filter(User.has_delete == 0, User.username == username).first()
            session.commit()
            return user

    def get_user_status_by_email(self, email):  # 根据email查询user的帐号状态
        with self.get_db_read() as session:
            user = session.query(User.status).filter(User.has_delete == 0, User.email == email).first()
            session.commit()
            return user

    def get_user_status_by_card_id(self, card_id):  # 根据card_id查询user的帐号状态
        with self.get_db_read() as session:
            user = session.query(User.status).filter(User.has_delete == 0, User.card_id == card_id).first()
            session.commit()
            return user

    def get_user_id_by_email(self, email):  # 根据email查询user_id
        with self.get_db_read() as session:
            user = session.query(User.id).filter(User.has_delete == 0, User.email == email).first()
            session.commit()
            return user

    def get_user_by_user_id(self, user_id):  # 根据user_id查询user的基本信息
        with self.get_db_read() as session:
            user = session.query(User).filter(User.id == user_id, User.has_delete == 0).first()
            session.commit()
            return user

    def get_user_all_information_by_user_id(self, user_id):  # 根据user_id查询user的所有信息
        with self.get_db_read() as session:
            informations = session.query(User.username, User.email,
                                         User_info.oj_username). \
                outerjoin(User_info, User_info.user_id == User.id). \
                filter(User.id == user_id, User.has_delete == 0). \
                first()
            session.commit()
            return informations

    def get_user_status_by_user_id(self, user_id):  # 根据user_id查询user的帐号状态
        with self.get_db_read() as session:
            status = session.query(User.status).filter(User.id == user_id, User.has_delete == 0).first()
            session.commit()
            return status

    def get_name_by_user_id(self, user_id):  # 根据user_id查询username,realname
        with self.get_db_read() as session:
            names = session.query(User.username, User_info.realname).outerjoin(User_info,
                                                                               User_info.user_id == user_id).filter(
                User.id == user_id, User.has_delete == 0).first()
            session.commit()
            return names

    def get_user_name_by_user_id(self, user_id):  # 根据user_id查询username
        with self.get_db_read() as session:
            name = session.query(User.username).filter(
                User.id == user_id, User.has_delete == 0).first()
            session.commit()
            return name

    def get_user_information_by_name_school(self, name, school, pg):
        with self.get_db_read() as session:
            res_list = []
            join_tables = join(User, User_info, User.id == User_info.user_id)
            join_tables = join(join_tables, Class, User_info.class_id == Class.id)
            join_tables = join(join_tables, Major, User_info.major_id == Major.id)
            join_tables = join(join_tables, College, Major.college_id == College.id)
            join_tables = join(join_tables, School, College.school_id == School.id)
            user = session.query(User.id, User.username, User.card_id, User_info.realname, School.name, Major.name,
                                 Class.name).select_from(join_tables).filter(
                User.has_delete == 0,
                User_info.has_delete == 0,
                School.has_delete == 0,
                College.has_delete == 0,
                Major.has_delete == 0,
                Class.has_delete == 0,
                (User.username == name if name is not None else True),  # 使用 True 来表示不过滤
                (School.name == school if school is not None else True)
            )
            data = user.offset(pg.offset()).limit(pg.limit())
            for item in data:
                temp = {
                    "user_id": item[0],
                    "user_name": item[1],
                    "card_id": item[2],
                    "real_name": item[3],
                    "school": item[4],
                    "major": item[5],
                    "class": item[6],
                }
                res_list.append(temp)
            total_count = user.count()
            return total_count, res_list


class SessionModel(dbSession, dbSessionread):
    def add_session(self, obj: session_interface):  # 添加一个session
        obj_dict = jsonable_encoder(obj)
        obj_dict['exp_dt'] = func.from_unixtime(obj_dict['exp_dt'])
        obj_add = Session(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.commit()
            return obj_add.id

    def add_all_session(self, sessions):  # 批量添加session
        objects = []
        for i in range(len(sessions)):
            sessions[i] = jsonable_encoder(sessions[i])
            sessions[i]['exp_dt'] = func.from_unixtime(sessions[i]['exp_dt'])
            objects.append(Session(**sessions[i]))
        with self.get_db() as session:
            session.add_all(objects)
            session.commit()
            return 'ok'

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
        with self.get_db_read() as session:
            ses = session.query(Session).filter(Session.has_delete == 0, Session.token == token).first()
            session.commit()
            return ses

    def get_user_id_by_token(self, token):  # 根据token查询user_id
        with self.get_db_read() as session:
            user_id = session.query(Session.user_id).filter(Session.has_delete == 0, Session.token == token).first()
            session.commit()
            return user_id

    def get_user_name_by_token(self, token):  # 根据token查询user_name
        with self.get_db_read() as session:
            user_name = session.query(User.username).outerjoin(Session, Session.user_id == User.id).filter(
                Session.has_delete == 0, Session.token == token).first()
            session.commit()
            return user_name

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


class UserinfoModel(dbSession, dbSessionread):
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
            session.commit()
            return 'ok'

    def get_major_id_by_user_id(self, user_id):  # 根据user_id查询user的major_id
        with self.get_db_read() as session:
            userinfo = session.query(User_info.major_id).filter(User_info.user_id == user_id,
                                                                User_info.has_delete == 0).first()
            session.commit()
            return userinfo

    def get_oj_exist_by_user_id(self, user_id):  # 根据user_id查询oj账号是否绑定
        with self.get_db_read() as session:
            exist = session.query(User_info.oj_username).filter(User_info.user_id == user_id,
                                                                User_info.has_delete == 0).first()
            session.commit()
            return exist

    def add_new_something(self, new):
        with self.get_db() as session:
            session.add(new)
            session.commit()
            return new.id


class OperationModel(dbSession, dbSessionread):
    def add_operation(self, obj: operation_interface):  # 添加一个操作(在operation表中添加一个操作)
        obj_dict = jsonable_encoder(obj)
        obj_add = Operation(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.commit()
            return 'ok'

    def get_operation_hash_by_id_list(self, id_list):  # 根据id_list查询operation的hash
        with self.get_db_read() as session:
            hash_list = session.query(Operation.id, Operation.oper_hash).filter(Operation.id.in_(id_list)).all()
            session.commit()
            return hash_list

    def get_func_and_time_by_admin(self, page, user_id):  # 查找某操作人的所有操作和时间
        with self.get_db_read() as session:
            query = session.query(Operation.func, Operation.oper_dt, Operation.id).filter(
                Operation.oper_user_id == user_id)
            counts = query.count()
            operations = query.order_by(
                Operation.id).offset(
                page.offset()).limit(page.limit()).all()
            session.commit()
            return operations, counts

    def get_operation_by_service_type(self, service_type, service_id, type):  # 根据service与type查询operation的基本信息
        with self.get_db_read() as session:
            reason = session.query(Operation.func, Operation.oper_user_id).filter(
                Operation.service_type == service_type,
                Operation.service_id == service_id, Operation.operation_type == type).first()
            session.commit()
            return reason


class CaptchaModel(dbSession, dbSessionread):
    def add_captcha(self, value):  # 添加一个验证码
        obj_add = Captcha(value=value, has_delete=0)
        with self.get_db() as session:
            session.add(obj_add)
            session.commit()
            return obj_add.id

    def delete_captcha(self, id: int):  # 删除一个captcha
        with self.get_db() as session:
            session.query(Captcha).filter(Captcha.id == id).update({"has_delete": 1})
            session.commit()
            return id

    def get_captcha_by_id(self, id):  # 根据id查询captcha的值
        with self.get_db_read() as session:
            value = session.query(Captcha.value).filter(Captcha.id == id, Captcha.has_delete == 0).first()
            session.commit()
            return value


class EducationProgramModel(dbSession, dbSessionread):
    def add_education_program(self, obj: education_program_interface):  # 添加一个培养方案
        obj_dict = jsonable_encoder(obj)
        obj_add = Education_Program(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.commit()
            return obj_add.id

    def delete_education_program(self, id: int):  # 删除一个education_program
        with self.get_db() as session:
            session.query(Education_Program).filter(Education_Program.id == id).update({"has_delete": 1})
            session.commit()
            return id

    def delete_education_program_by_major_id(self, major_id: int):  # 删除一个education_program
        with self.get_db() as session:
            session.query(Education_Program).filter(Education_Program.major_id == major_id).update({"has_delete": 1})
            session.commit()
            return 'ok'

    def get_education_program_by_user_id(self, user_id):  # 根据user_id查询education_program
        with self.get_db_read() as session:
            user_info = UserinfoModel()
            major_id = user_info.get_major_id_by_user_id(user_id)
            if major_id is None:
                return 0
            value = session.query(Education_Program).filter(
                Education_Program.has_delete == 0,
                Education_Program.major_id == major_id[0]).first()
            session.commit()
            if value:
                # 使用字典推导式创建带有属性名的字典
                result_dict = {key: getattr(value, key) for key in value.__dict__ if
                               not key.startswith('_') and getattr(value, key) is not None}
                translated_result = {programs_translation1.get(key, key): value for key, value in result_dict.items()}
                session.commit()
                return translated_result
            else:
                return None

    def update_education_program_exist(self, major_id: int):  # 更改education_program存在状态
        with self.get_db() as session:
            session.query(Education_Program).filter(Education_Program.major_id == major_id).update({"has_delete": 0})
            session.commit()
            return 'ok'
