import json
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from model.permissions import Role, RolePrivilege, UserRole, Privilege, WorkRole
from model.user import User
from model.db import dbSession
from type.permissions import *


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


class roleModel(dbSession):

    def get_role_info_by_id(self, id):  # 获取角色表信息
        with self.get_db() as session:
            op = session.query(Role).filter(
                Role.id == id
            ).first()
            if op is None:
                raise HTTPException(detail="Problem not found",
                                    status_code=404)
            return op

    def get_user_role_info_by_id(self, id):  # 获取用户角色表信息
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
                                    status_code=404)
            temp_dict = json.loads(result.superiorListId)
            superiorListId = add_superiorId(temp_dict, role_superiorId)
            NewRole = Role(name=role_name, description=role_name,
                            superiorId=role_superiorId, superiorListId=superiorListId, template=0,
                            status=0,
                            has_delete=0)
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

    def attribute_user_role(self, data: attribute_role_base):  # 分配用户角色
        obj_dict = jsonable_encoder(data)
        with self.get_db() as session:
            query_result = session.query(Role).filter_by(name=obj_dict['role_name']).first()  # 依照role_name先查找角色
            if query_result:
                result_dict = RolePydantic.from_orm(query_result).dict()
                new_user_role = UserRole(role_id=result_dict['id'], user_id=obj_dict['user_id'], has_delete=0)
                session.add(new_user_role)
                session.commit()
                return new_user_role.id
            else:
                return '-1'

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
                UserRole.user_id == user_id
            ).all()
            role_ids = [row[0] for row in user_role]
            role_set = self.get_son_role(role_ids)
            role_list = list(role_set)
            return role_list

    def search_user_by_role(self, role_list: list):
        with self.get_db() as session:
            user_set = set()
            user = session.query(UserRole).filter(UserRole.role_id.in_(role_list)).all()
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

    def search_user_id_by_service(self, service_type: int, service_id: int):
        with self.get_db() as session:
            user_list = []
            query = session.query(WorkRole, UserRole).join(
                UserRole,
                WorkRole.role_id == UserRole.role_id,
            ).filter(
                WorkRole.service_type == service_type,
                WorkRole.service_id == service_id
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
            for item in role_list:
                role = session.query(Role).filter(
                    Role.id == item,
                    Role.name == 'default'
                ).first()
                if role is not None:
                    return role.id

    def add_role_for_work(self, service_id: int, service_type: int, user_id: int, role_name: str):
        superiorId = self.search_user_default_role(user_id)
        role_id = self.create_role(role_name, superiorId)  # 添加角色
        WorkRole_id = self.attribute_role_for_work(service_type, service_id, role_id)  # 连接业务角色
        return WorkRole_id

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
                    'id': item.id,
                    'name': item.name
                }
                privilege_list.append(temp)
            return privilege_list


    def add_role_for_user(self, user_id: int, role_id: int):
        with self.get_db() as session:
            user_role = UserRole(
                role_id=role_id, user_id=user_id, has_delete=0
            )
            session.add(user_role)
            session.commit()
            return user_role.id


    def add_default_role(self, user_id: int, superiorId: int):
        with self.get_db() as session:
            role_id = self.create_role('默认角色', superiorId)
            user_role_id = self.add_role_for_user(user_id,role_id)
            return user_role_id


    def test(self):
        with self.get_db() as session:
            query = session.query(Privilege).all()
            user_list = []
            for item in query:
                user_list.append(item[1].user_id)
            return user_list
