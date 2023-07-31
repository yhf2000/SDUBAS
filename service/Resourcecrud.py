from typing import Any, Type, List
from fastapi.encoders import jsonable_encoder
from model.financial_dbmodel import Resource
from model.financial_Basemodel import ResourceAdd, ApplyBody
from model.financial_dbmodel import dbSession
from utils.response import page
from fastapi import HTTPException


class ResourceModel(dbSession):
    def save_resource(self, obj_in: ResourceAdd):  # 增加
        obj_dict = jsonable_encoder(obj_in)
        obj_add = Resource(**obj_dict)
        self.session.add(obj_add)
        self.session.flush()
        self.session.commit()
        return obj_add.Id

    def delete(self, Id: int):  # 删除
        self.session.query(Resource).filter(Resource.Id == Id).update({"has_delete": 1})
        self.session.commit()
        return Id

    def check_by_id(self, Id: int):  # 通过主键获取
        Resource_template = self.session.query(Resource).filter(Resource.Id == Id, Resource.has_delete == 0).first()
        if Resource_template is not None:
            return jsonable_encoder(Resource_template)
        else:
            raise HTTPException(status_code=404, detail="Item not found")

    def get_resource_by_user(self, user: Any, pg: page):  # 获取当前用户所有可用资源
        # query=调用权限函数   返回一个query,可用
        # 分页相关 result=query.offset(pg.offset).limit(pg.limit())  使用直接获取
        # 整理函数  返回结果
        return

    def apply_resource(self, user: Any, Id: int, date: ApplyBody):
        # 权限查询相关的业务类型，业务Id,角色类型，查询模板角色id
        # 输入模板角色ID，与相关参数，添加接口
        # 返回成功或者失败
        return

    def count_Update(self, Id: int, count: int):  # 修改Note
        self.session.query(Resource).filter(Resource.Id == Id).update({"count": count})
        self.session.commit()
        return Id

    def get_resource_apply_by_id(self, Id: int):  # 获取某项资源的所有申请
        # 权限查询相关的业务类型，业务Id,角色类型，查询模板角色id
        # 输入模板角色ID，查询所有非模板角色，的模板id为XXX的申请中的角色，与userid表格联合一下返回
        # 返回成功或者失败
        return

    def approve_apply_by_roleid(self, Id: int):
        # 直接修改角色id，修改为可用
        return

    def refuse_apply_by_roleid(self, Id: int):
        # 直接修改角色id，修改为不可用
        return
