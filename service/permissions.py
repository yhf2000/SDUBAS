import json
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from model.permissions import Role, RolePrivilege, UserRole, Privilege
from model.db import dbSession
from type.permissions import *


def handle_superiorId(data: dict, superid: int):  # 处理父节点列表JSON
    temp_list = data['ids']
    temp_list.append(superid)
    newdata = {"ids": temp_list}
    json_string = json.dumps(newdata)
    return json_string


class roleModel(dbSession):

    def get_role_info_by_id(self, id):  # 获取角色表信息
        op = self.session.query(Role).filter(
            Role.id == id
        ).first()
        if op is None:
            raise HTTPException(detail="Problem not found",
                                status_code=404)
        return op

    def get_user_role_info_by_id(self, id):  # 获取用户角色表信息
        op = self.session.query(Role).filter(
            Role.id == id
        ).first()
        if op is None:
            raise HTTPException(detail="Problem not found",
                                status_code=404)
        return op

    def create(self, data: role_base):  # 创建角色
        obj_dict = jsonable_encoder(data)
        # obj_add = Role(**obj_dict)
        result = self.session.query(Role).filter_by(id=obj_dict['role_superiorId']).first()  # 处理父节点
        if result is None:
            return "-1"
        temp_dict = json.loads(result.superiorListId)
        superiorListId = handle_superiorId(temp_dict, obj_dict['role_superiorId'])
        NewRole = Role(name=obj_dict['role_name'], description=obj_dict['role_name'],
                       superiorId=obj_dict['role_superiorId'], superiorListId=superiorListId, template=1, status=0,
                       has_delete=0)
        self.session.add(NewRole)
        self.session.commit()
        return NewRole.id

    def delete(self, role_name: str):  # 删除角色
        result = self.session.query(Role).filter_by(name=role_name).first()
        result.has_delete = 1
        self.session.add(result)
        self.session.commit()
        return 'OK'

    def attribute_user_role(self, data: attribute_role_base):  # 分配用户角色
        obj_dict = jsonable_encoder(data)
        query_result = self.session.query(Role).filter_by(name=obj_dict['role_name']).first()  # 依照role_name先查找角色
        if query_result:
            result_dict = RolePydantic.from_orm(query_result).dict()
            new_user_role = UserRole(role_id=result_dict['id'], user_id=obj_dict['user_id'], has_delete=0)
            self.session.add(new_user_role)
            self.session.commit()
            return new_user_role.id
        else:
            return '-1'

    def attribute_privilege(self, data: attribute_privilege_base):
        obj_dict = jsonable_encoder(data)
        UserRole_query_result = self.session.query(UserRole).filter_by(user_id=obj_dict['user_id']).first()  # 先从用户查到角色
        now_role_id = UserRole_query_result.role_id
        Privilege_query_result = self.session.query(Privilege).filter_by(name=obj_dict['privilege_name']).first()  # 再从角色查到权限
        if Privilege_query_result is not None:
            new_role_privilege = RolePrivilege(role_id=now_role_id, privilege_id=Privilege_query_result.id, has_delete=0)
            self.session.add(new_role_privilege)
            self.session.commit()
            return 'OK'
