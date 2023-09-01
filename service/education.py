from fastapi.encoders import jsonable_encoder

from model.db import dbSession
from model.user import School, College, Major, Class
from type.user import school_interface, college_interface, class_interface, major_interface


class SchoolModel(dbSession):  # 学校model
    def add_school(self, obj: school_interface):  # 添加一个school
        obj_dict = jsonable_encoder(obj)
        obj_dict.pop('file_id')
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

    def get_school_id_by_name(self, name):  # 根据name查询school的id
        with self.get_db() as session:
            school = session.query(School.id).filter(School.has_delete == 0, School.name == name).first()
            session.commit()
            return school

    def get_school_information_by_name(self, name):  # 根据name查询school的基本信息
        with self.get_db() as session:
            school = session.query(School).filter(School.name == name).first()
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

    def get_school_logo_by_id(self, id):  # 根据id查询school的logo
        with self.get_db() as session:
            logo = session.query(School.school_logo).filter(School.id == id, School.has_delete == 0).first()
            session.commit()
            return logo

    def get_school_exist_by_id(self, id):  # 根据id查询school的id
        with self.get_db() as session:
            id = session.query(School.id).filter(School.id == id, School.has_delete == 0).first()
            session.commit()
            return id

    def get_school_id_by_major_id(self, major_id):  # 根据专业id查询学校id
        with self.get_db() as session:
            id = session.query(School.id).outerjoin(College, School.id == College.school_id).outerjoin(Major,
                                                                                                       Major.college_id == College.id).filter(
                Major.id == major_id,
                Major.has_delete == 0,
            ).first()
            session.commit()
            return id

    def get_school_by_admin(self, page):  # 查找管理员能操作的所有学校
        with self.get_db() as session:
            school = session.query(School).filter(School.has_delete == 0).order_by(
                School.id).offset(
                page.offset()).limit(page.limit()).all()
            session.commit()
            return school

    def update_school_information(self, id, name, abbreviation):  # 更改school中的name与abbreviation
        with self.get_db() as session:
            session.query(School).filter(School.id == id).update({"name": name, "school_abbreviation": abbreviation})
            session.commit()
            return id

    def update_school_logo(self, id, logo):  # 更改school中的school_logo
        with self.get_db() as session:
            session.query(School).filter(School.id == id).update({"school_logo": logo})
            session.commit()
            return id

    def update_school_status_by_id(self, id):  # 更改school中的name
        with self.get_db() as session:
            session.query(School).filter(School.id == id).update({"has_delete": 0})
            session.commit()
            return 'ok'


class CollegeModel(dbSession):
    def add_college(self, obj: college_interface):  # 添加一个college
        obj_dict = jsonable_encoder(obj)
        obj_dict.pop('file_id')
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

    def get_college_by_name(self, obj: college_interface):  # 根据school_id,name查询college的id
        with self.get_db() as session:
            college = session.query(College.id).filter(College.has_delete == 0, College.school_id == obj.school_id,
                                                       College.name == obj.name).first()
            session.commit()
            return college

    def get_college_logo_by_id(self, id):  # 根据id查询college的logo
        with self.get_db() as session:
            logo = session.query(College.college_logo).filter(College.id == id, College.has_delete == 0).first()
            session.commit()
            return logo

    def get_college_status_by_name(self, obj: college_interface):  # 根据school_id,name查询college的状态
        with self.get_db() as session:
            college = session.query(College.has_delete, College.id).filter(
                College.school_id == obj.school_id,
                College.name == obj.name).first()
            session.commit()
            return college

    def get_college_exist_by_id(self, id):  # 根据id查询college的id
        with self.get_db() as session:
            id = session.query(College.id).filter(College.id == id, College.has_delete == 0).first()
            session.commit()
            return id

    def get_college_by_id(self, id):  # 根据id查询college的基本信息
        with self.get_db() as session:
            college = session.query(College).filter(College.has_delete == 0, College.id == id).first()
            session.commit()
            return college

    def get_college_by_school_id(self, school_id, page):  # 根据college的school_id查询college的基本信息
        with self.get_db() as session:
            college = session.query(College).filter(College.has_delete == 0, College.school_id == school_id).order_by(
                College.id).offset(
                page.offset()).limit(page.limit()).all()
            session.commit()
            return college

    def get_school_id_by_college_id(self, college_id):  # 根据college_id查询school_id
        with self.get_db() as session:
            school_id = session.query(College.school_id).filter(College.has_delete == 0,
                                                                College.id == college_id).first()
            session.commit()
            return school_id

    def get_college_by_admin(self, page):  # 查找某管理员能操作的所有college
        with self.get_db() as session:
            college = session.query(College).filter(College.has_delete == 0).order_by(
                College.id).offset(
                page.offset()).limit(page.limit()).all()
            session.commit()
            return college

    def update_college_school_id_name(self, id, name):  # 更改college中的name
        with self.get_db() as session:
            session.query(College).filter(College.id == id).update({"name": name})
            session.commit()
            return id

    def update_college_status_by_id(self, id):  # 更改college中的status
        with self.get_db() as session:
            session.query(College).filter(College.id == id).update(
                {"has_delete": 0})
            session.commit()
            return 'ok'


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

    def get_college_id_by_id(self, id):  # 根据id查询college_id
        with self.get_db() as session:
            college_id = session.query(Major.college_id).filter(Major.has_delete == 0, Major.id == id).first()
            session.commit()
            return college_id

    def get_major_exist_by_id(self, id):  # 根据id查询major是否存在
        with self.get_db() as session:
            id = session.query(Major.id).filter(Major.id == id, Major.has_delete == 0).first()
            session.commit()
            return id

    def get_major_by_college_id(self, college_id, page):  # 根据college_id查询major的基本信息
        with self.get_db() as session:
            major = session.query(Major).filter(Major.has_delete == 0, Major.college_id == college_id).order_by(
                Major.id).offset(
                page.offset()).limit(page.limit()).all()
            session.commit()
            return major

    def get_major_status_by_name(self, obj: major_interface):  # 根据专业名和学院id和学校id查询专业
        with self.get_db() as session:
            major = session.query(Major.has_delete, Major.id).outerjoin(College,
                                                                        Major.college_id == College.id).outerjoin(
                School,
                College.school_id == School.id).filter(
                College.id == obj.college_id,
                Major.name == obj.name,
                School.id == obj.school_id
            ).first()
            session.commit()
            return major

    def get_major_by_name(self, obj: major_interface):  # 根据专业名和学院id和学校id查询专业的id
        with self.get_db() as session:
            major = session.query(Major.id).outerjoin(College, Major.college_id == College.id).outerjoin(School,
                                                                                                         College.school_id == School.id).filter(
                College.id == obj.college_id,
                Major.name == obj.name,
                School.id == obj.school_id,
                Major.has_delete == 0

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

    def update_major_information(self, id, name):  # 更改college中的name
        with self.get_db() as session:
            session.query(Major).filter(Major.id == id).update({"name": name})
            session.commit()
            return id

    def update_major_status_by_id(self, id):  # 更改major中的status
        with self.get_db() as session:
            session.query(Major).filter(Major.id == id).update(
                {"has_delete": 0})
            session.commit()
            return 'ok'


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

    def get_class_exist_by_id(self, id):  # 根据id查询class是否存在
        with self.get_db() as session:
            id = session.query(Class.id).filter(Class.id == id, Class.has_delete == 0).first()
            session.commit()
            return id

    def get_class_by_college_id(self, college_id, page):  # 根据college_id查询class的基本信息
        with self.get_db() as session:
            clas = session.query(Class).filter(Class.has_delete == 0, Class.college_id == college_id).order_by(
                Class.id).offset(
                page.offset()).limit(page.limit()).all()
            session.commit()
            return clas

    def get_class_by_name(self, obj: class_interface):  # 根据班级名和学院id和学校id查询班级的id
        with self.get_db() as session:
            clas = session.query(Class.id).outerjoin(College, Class.college_id == College.id).outerjoin(School,

                                                                                                        College.school_id == School.id).filter(
                College.id == obj.college_id,
                Class.name == obj.name,
                School.id == obj.school_id,
                Class.has_delete == 0

            ).first()
            session.commit()
            return clas

    def get_class_status_by_name(self, obj: class_interface):  # 根据班级名和学院id和学校id查询班级
        with self.get_db() as session:
            clas = session.query(Class.has_delete, Class.id).outerjoin(College,
                                                                       Class.college_id == College.id).outerjoin(School,
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

    def update_class_status_by_id(self, id):  # 更改class中的status
        with self.get_db() as session:
            session.query(Class).filter(Class.id == id).update(
                {"has_delete": 0})
            session.commit()
            return 'ok'

    def update_class_information(self, id, name):  # 更改class中的name
        with self.get_db() as session:
            session.query(Class).filter(Class.id == id).update({"name": name})
            session.commit()
            return id