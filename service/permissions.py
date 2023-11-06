import json
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import distinct, join
from sqlalchemy.sql import select

from model.permissions import Role, RolePrivilege, UserRole, Privilege, WorkRole
from model.user import User
from model.db import dbSession
from type.permissions import *
from type.page import page


def add_superiorId(data: dict, super_id: int):  # 在superiorListId中添加父节点
    temp_list = data['ids']
    temp_list.append(super_id)
    newdata = {"ids": temp_list}
    json_string = json.dumps(newdata)
    return json_string


def delete_superiorId(data: dict, super_id: int):  # 在superiorListId中删除父节点
    temp_list = data['ids']
    temp_list.remove(super_id)
    newdata = {"ids": temp_list}
    json_string = json.dumps(newdata)
    return json_string


class permissionModel(dbSession):

    def get_role_info_by_id(self, id):  # 获取角色表信息
        with self.get_db() as session:
            op = session.query(Role).filter(
                Role.id == id
            ).first()
            if op is None:
                raise HTTPException(detail="Problem not found",
                                    status_code=404)
            return op

    def create_role(self, role_name: str, role_superiorId: int):  # 创建角色
        with self.get_db() as session:
            result = session.query(Role).filter(Role.id == role_superiorId).first()  # 处理父节点
            if result is None:
                raise HTTPException(detail="父节点无效",
                                    status_code=408)
            temp_dict = json.loads(result.superiorListId)
            superiorListId = add_superiorId(temp_dict, role_superiorId)
            NewRole = Role(name=role_name, description=role_name,
                           superiorId=role_superiorId, superiorListId=superiorListId, template=0,
                           status=0,
                           has_delete=0)
            session.add(NewRole)
            session.commit()
            return NewRole.id

    def create_template_role(self, role_name: str, role_superiorId: int, template_val: str):  # 创建角色
        with self.get_db() as session:
            result = session.query(Role).filter(Role.id == role_superiorId).first()  # 处理父节点
            if result is None:
                raise HTTPException(detail="父节点无效",
                                    status_code=408)
            temp_dict = json.loads(result.superiorListId)
            superiorListId = add_superiorId(temp_dict, role_superiorId)
            NewRole = Role(name=role_name, description=role_name,
                           superiorId=role_superiorId, superiorListId=superiorListId, template=0,
                           template_val=template_val, status=0,
                           has_delete=0)
            session.add(NewRole)
            session.commit()
            return NewRole.id

    def create_real_template_role(self, role_name: str, role_superiorId: int):  # 创建角色
        with self.get_db() as session:
            result = session.query(Role).filter(Role.id == role_superiorId).first()  # 处理父节点
            if result is None:
                raise HTTPException(detail="父节点无效",
                                    status_code=408)
            temp_dict = json.loads(result.superiorListId)
            superiorListId = add_superiorId(temp_dict, role_superiorId)
            NewRole = Role(name=role_name, description=role_name,
                           superiorId=role_superiorId, superiorListId=superiorListId, template=1,
                           status=0,has_delete=0)
            session.add(NewRole)
            session.commit()
            return NewRole.id


    def add_user_role(self, obj: create_user_role_base):
        obj_dict = jsonable_encoder(obj)
        obj_add = UserRole(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            return obj_add.id

    def add_all_user_role(self, role_id, user_id_list):  # 管理员批量添加user_role
        objects = []
        for i in range(len(user_id_list)):
            obj = create_user_role_base(role_id=role_id, user_id=user_id_list[i].id)
            obj_dict = jsonable_encoder(obj)
            objects.append(UserRole(**obj_dict))
        with self.get_db() as session:
            session.add_all(objects)
            session.flush()
            session.commit()
            return 'ok'

    def delete_role(self, role_name: delete_role_base):  # 删除角色
        with self.get_db() as session:
            role_list = []
            role = session.query(Role).filter(Role.name == role_name).first()  # 查找当前角色
            role_list.append(role.id)
            son_sole = session.query(Role).filter(Role.superiorId == role.id).all()
            role_set = self.get_son_role(role_list)
            role_set.remove(role.id)
            if role_set is not None:
                query = session.query(Role).filter(Role.id.in_(role_set))
                for item in query:
                    temp_dict = json.loads(item.superiorListId)
                    new_superiorListId = delete_superiorId(temp_dict, role.id)
                    item.superiorListId = new_superiorListId  # 更改孩子角色父节点列表
                    session.add(item)
            session.commit()
            role.has_delete = 1  # 删除当前角色
            session.add(role)
            session.commit()
            if son_sole is not None:
                for item in son_sole:
                    item.superiorId = role.superiorId  # 更改孩子角色父节点
                    session.add(item)
            session.commit()
            return 'OK'

    def attribute_user_role(self, user_id: int, role_id: int):  # 分配用户角色
        with self.get_db() as session:
            query = session.query(UserRole).filter(
                UserRole.role_id == role_id,
                UserRole.user_id == user_id,
                UserRole.has_delete == 0
            ).first()
            if query is not None:
                raise HTTPException(
                    status_code=402,
                    detail="重复添加",
                )
            new_user_role = UserRole(role_id=role_id, user_id=user_id, has_delete=0)
            session.add(new_user_role)
            session.commit()
            return new_user_role.id

    def attribute_privilege_for_role(self, privilege_list: list, role_id: int):
        with self.get_db() as session:
            for item in privilege_list:
                new_role_privilege = RolePrivilege(
                    role_id=role_id, privilege_id=item, has_delete=0
                )
                session.add(new_role_privilege)
            session.commit()
            return 'OK'

    def attribute_role_for_work(self, service_type: int, service_id: int, role_id: int):
        with self.get_db() as session:
            Role_query_result = session.query(Role).filter(Role.id == role_id).first()
            if Role_query_result is not None:
                new_work_role = WorkRole(role_id=Role_query_result.id, service_type=service_type,
                                         service_id=service_id, has_delete=0)
                session.add(new_work_role)
                session.commit()
                return new_work_role.id

    def get_son_role(self, role_list: list):
        with self.get_db() as session:
            role_set = set()
            while len(role_list) != 0:
                role_set.add(role_list[0])
                son = session.query(Role).filter(
                    Role.superiorId == role_list[0],
                    Role.has_delete == 0
                ).all()
                for item in son:
                    role_list.append(item.id)
                del role_list[0]
            return role_set

    def search_role_by_user(self, user_id: int):
        with self.get_db() as session:
            user_role = session.query(UserRole.role_id).filter(
                UserRole.user_id == user_id,
                UserRole.has_delete == 0
            ).all()
            role_ids = [row[0] for row in user_role]
            role_set = self.get_son_role(role_ids)
            role_list = list(role_set)
            return role_list

    def search_user_by_role(self, role_list: list):
        with self.get_db() as session:
            user_set = set()
            user = session.query(UserRole).filter(
                UserRole.role_id.in_(role_list),
                UserRole.has_delete == 0
            ).all()
            for item in user:
                user_set.add(item.user_id)
            user_list = list(user_set)
            return user_list

    def search_privilege_by_role(self, role_list: list):
        with self.get_db() as session:
            privilege_set = set()
            for i in role_list:
                role_privilege = session.query(RolePrivilege).filter(
                    RolePrivilege.role_id == i
                ).all()
                for item in role_privilege:
                    privilege_set.add(item.privilege_id)
            return privilege_set

    def search_privilege_name_by_privilege_id(self, privilege_name: str):
        with self.get_db() as session:
            privilege_id = session.query(Privilege).filter(
                Privilege.name == privilege_name
            ).first()
            return privilege_id.id

    def search_work_by_role(self, role_list: list):
        with self.get_db() as session:
            work_list = []
            for i in role_list:
                work = session.query(WorkRole).filter(
                    WorkRole.role_id == i
                ).all()
                for item in work:
                    work_list.append(item.id)
            return work_list

    def check_permission(self, permission_key: str, privilege_set: set):
        with self.get_db() as session:
            for item in privilege_set:
                privilege = session.query(Privilege).filter(
                    item == Privilege.id
                ).first()
                if privilege.key == permission_key:
                    return True
            return False

    def search_service_id(self, role_list: list, service_type: int, name: str):
        with self.get_db() as session:
            service_ids = []
            for i in role_list:
                work_role = session.query(WorkRole).filter(
                    WorkRole.role_id == i,
                    WorkRole.service_type == service_type
                ).all()
                for item in work_role:
                    service_ids.append(item.service_id)
            return service_ids

    def search_user_id_by_service(self, service_type: int, service_id: int): #userrolehasdelete有改动
        with self.get_db() as session:
            user_list = []
            query = session.query(distinct(UserRole.user_id)).join(
                WorkRole,
                WorkRole.role_id == UserRole.role_id,
            ).filter(
                WorkRole.service_type == service_type,
                WorkRole.service_id == service_id,
                UserRole.has_delete == 0
            )
            return query

    def search_college_default_role_id(self, role_list: list):
        with self.get_db() as session:
            query = session.query(WorkRole).filter(
                WorkRole.role_id.in_(role_list),
                WorkRole.service_type == 2,
                WorkRole.service_id == None
            ).one()
            return query.role_id

    def search_user_default_role(self, user_id: int):
        with self.get_db() as session:
            role_list = self.search_role_by_user(user_id)
            query = session.query(WorkRole).filter(
                WorkRole.service_type == 0
            ).all()
            for item in query:
                if item.role_id in role_list:
                    return item.role_id

    def add_role_for_work(self, service_id: int, service_type: int, user_id: int, role_name: str):
        superiorId = self.search_user_default_role(user_id)
        role_id = self.create_role(role_name, superiorId)  # 添加角色
        WorkRole_id = self.attribute_role_for_work(service_type, service_id, role_id)  # 连接业务角色
        return role_id

    def search_role_by_service(self, service_id: int, service_type: int):
        with self.get_db() as session:
            role_list = []
            query = session.query(WorkRole).filter(
                WorkRole.service_id == service_id,
                WorkRole.service_type == service_type
            ).all()
            for item in query:
                role_list.append(item.role_id)
            return role_list

    def search_privilege_list(self, service_type: int):
        with self.get_db() as session:
            privilege_list = []
            privilege = session.query(Privilege).filter(
                Privilege.service_type == service_type
            ).all()
            for item in privilege:
                temp = {
                    'value': item.id,
                    'label': item.name
                }
                privilege_list.append(temp)
            return privilege_list

    def search_privilege_id_list(self, service_type: int):
        with self.get_db() as session:
            privilege_list = []
            privilege = session.query(Privilege).filter(
                Privilege.service_type == service_type
            ).all()
            for item in privilege:
                privilege_list.append(item.id)
            return privilege_list

    def add_default_work_role(self, user_id: int, role_id: int):
        with self.get_db() as session:
            work_role = WorkRole(role_id=role_id, service_type=0, service_id=user_id, has_delete=0)
            session.add(work_role)
            session.commit()
            return 'OK'

    def search_created_user_id(self, user_id: int, pg: page): #改userrole的hasdelete
        with self.get_db() as session:
            user = session.query(distinct(UserRole.user_id)).join(
                WorkRole,
                WorkRole.role_id == UserRole.role_id,
            ).filter(
                WorkRole.service_type == 0,
                WorkRole.service_id == user_id
            )
            total_count = user.count()
            data = user.offset(pg.offset()).limit(pg.limit()).all()
            dicts = []
            for item in data:
                dicts.append(item[0])
            return total_count, dicts

    def search_role_by_user_2(self, user_id: int, pg: page):
        with self.get_db() as session:
            res_list = []
            user_role = session.query(UserRole.role_id).filter(
                UserRole.user_id == user_id,
                UserRole.has_delete == 0
            )
            role_ids = [row[0] for row in user_role.all()]
            role_set = self.get_son_role(role_ids)
            role_list = list(role_set)
            role = session.query(Role).filter(
                Role.id.in_(role_list)
            ).all()
            for item in role:
                temp = {
                    "role_id": item.id,
                    "role_name": item.name
                }
                res_list.append(temp)
            total_count = user_role.count()
            return total_count, res_list

    def get_user_info_by_role(self, role_id: int):
        with self.get_db() as session:
            res_list = []
            join_tables = join(UserRole, User, UserRole.user_id == User.id)
            query = session.query(UserRole, User).select_from(join_tables).filter(
                UserRole.role_id == role_id,
                UserRole.has_delete == 0
            )
            query = query.all()
            for item in query:
                temp = {
                    "user_id": item[1].id,
                    "user_name": item[1].username
                }
                res_list.append(temp)
            total_count = len(res_list)
            return total_count, res_list

    def get_role_by_work(self, service_type: int, service_id: int):
        with self.get_db() as session:
            role_list = []
            res_list = []
            query = session.query(WorkRole).filter(
                WorkRole.service_type == service_type,
                WorkRole.service_id == service_id
            ).all()
            for item in query:
                role_list.append(item.role_id)
            role = session.query(Role).filter(
                Role.id.in_(role_list)
            ).all()
            for item in role:
                temp = {
                    "role_id": item.id,
                    "role_name": item.name
                }
                res_list.append(temp)
            total_count = len(res_list)
            return total_count, res_list

    def delete_work_user(self, user_id: int, role_id: int):
        with self.get_db() as session:
            query = session.query(UserRole).filter(
                UserRole.role_id == role_id,
                UserRole.user_id == user_id
            ).first()
            if query is not None:
                query.has_delete = 1
                session.add(query)
            session.commit()
            return 'OK'

    def add_work_user(self, name_list: list, role_id: int):
        with self.get_db() as session:
            user_ids = []
            query = session.query(User).filter(
                User.username.in_(name_list)
            ).all()
            for item in query:
                user_ids.append(item.id)
            for item in user_ids:
                self.attribute_user_role(item, role_id)
            return 'OK'


    def search_created_user_info(self, user_id: int):
        with self.get_db() as session:
            role_list = []
            res_list = []
            query = session.query(WorkRole).filter(
                WorkRole.service_type == 0,
                WorkRole.service_id == user_id
            ).all()
            for item in query:
                role_list.append(item.role_id)
            join_tables = join(UserRole, User, UserRole.user_id == User.id)
            user = session.query(UserRole, User).select_from(join_tables).filter(
                UserRole.role_id.in_(role_list),
                UserRole.has_delete == 0
            ).all()
            for item in user:
                temp = {
                    "user_id": item[1].id,
                    "user_name": item[1].username
                }
                res_list.append(temp)
            total_count = len(res_list)
            return total_count, res_list

    def search_specific_role(self, role_list: list, privilege_name: str):
        with self.get_db() as session:
            new_role_list = []
            privilege = session.query(Privilege).filter(
                Privilege.name == privilege_name
            ).first()
            query = session.query(RolePrivilege).filter(
                RolePrivilege.role_id.in_(role_list),
                RolePrivilege.privilege_id == privilege.id
            ).all()
            for item in query:
                new_role_list.append(item.role_id)
            return new_role_list

    def search_role_info_by_service(self, service_id: int, service_type: int):
        with self.get_db() as session:
            role_list = []
            query = session.query(Role).join(
                WorkRole,
                WorkRole.role_id == Role.id
            ).filter(
                WorkRole.service_type == service_type,
                WorkRole.service_id == service_id
            ).all()
            for item in query:
                temp = {
                    "role_id": item.id,
                    "role_name": item.name
                }
                role_list.append(temp)
            return role_list

    def return_student_role(self, service_id: int, service_type: int):
        with self.get_db() as session:
            query = session.query(WorkRole).join(
                RolePrivilege,
                RolePrivilege.role_id == WorkRole.role_id
            ).filter(
                WorkRole.service_type == service_type,
                WorkRole.service_id == service_id,
                RolePrivilege.privilege_id == 2
            ).all()
            role_list = []
            user_list = []
            for item in query:
                role_list.append(item.role_id)
            user = session.query(UserRole).filter(UserRole.role_id.in_(role_list)).all()
            for item in user:
                user_list.append(item.user_id)
            return user_list

    def return_user_major_role(self, user_id: int):
        with self.get_db() as session:
            query = session.query(UserRole).join(
                User,
                UserRole.user_id == User.id
            ).filter(
                User.id == user_id
            ).all()
            test_list = []
            for item in query:
                work_role = session.query(WorkRole).join(
                    Role,
                    WorkRole.role_id == Role.id
                ).filter(
                    WorkRole.service_type == 3,
                    WorkRole.role_id == item.role_id
                ).first()
                if work_role is not None:
                    test_list.append(work_role.service_id)
            return test_list[0]


    def create_work_role(self, user_id: int, role_name: str, service_type: int, service_id: int):
        with self.get_db() as session:
            superiorId = self.search_user_default_role(user_id)
            role_id = self.create_role(role_name, superiorId)
            self.attribute_user_role(user_id, role_id)
            self.attribute_role_for_work(service_type, service_id, role_id)
            return 'OK'

    def test(self, role_id: int):
        with self.get_db() as session:
            user_list = []
            query = session.query(User).join(
                UserRole,
                UserRole.user_id == User.id
            ).join(
                Role,
                UserRole.role_id == Role.id
            ).filter(
                Role.id == 69
            ).all()
            print(query[0].id)
            return'OK'



