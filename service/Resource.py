import datetime
from typing import Any
from fastapi import HTTPException, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from model.db import dbSession
from model.financial import Bill
from model.financial import Resource, Financial
from model.permissions import *
from model.user import *
from service.permissions import permissionModel
from type.financial import Financial_ModelOpt, BillModelOpt, Resource_Basemodel
from type.financial import ResourceAdd, ApplyBody, AmountAdd, FinancialAdd
from type.functions import get_url_by_user_file_id,get_time_now
from type.page import dealDataList
from utils.response import page


class ResourceModel(dbSession):
    def save_resource(self, obj_in: ResourceAdd, user_id: int):  # 增加
        obj_dict = obj_in.model_dump(exclude={"roles"})
        obj_add = Resource(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            role_model = permissionModel()
            superiorId = role_model.search_user_default_role(user_id)
            for role in obj_in.roles:
                role_id = role_model.add_role_for_work(service_id=obj_add.Id,
                                                       service_type=5, user_id=user_id, role_name=role.role_name)
                role_model.attribute_privilege_for_role(role.privilege_list, role_id)
            self_role = role_model.add_role_for_work(service_id=obj_add.Id,
                                                     service_type=5, user_id=user_id, role_name=obj_add.name)
            all_privilege = role_model.search_privilege_id_list(5)
            role_model.attribute_privilege_for_role(all_privilege, self_role)
            role_model.attribute_user_role(user_id, self_role)
            return obj_add.Id

    def delete(self, Id: int, user_id: int):  # 删除
        with self.get_db() as session:
            session.query(Resource).filter(Resource.Id == Id).update({"has_delete": 1})
            session.commit()
            return Id

    def check_by_id(self, Id: int, user_id: int):  # 通过主键获取
        with self.get_db() as session:
            Resource_template = session.query(Resource).filter(Resource.Id == Id, Resource.has_delete == 0).first()
        if Resource_template is not None:
            Resource_dict = Resource_Basemodel.model_validate(Resource_template)
            return Resource_dict.model_dump(exclude={'has_delete'})
        else:
            raise HTTPException(status_code=408, detail="Item not found")

    def get_view_resource_by_user(self, user: Any, pg: page, user_id: int):  # 获取当前用户所有可用资源
        with self.get_db() as session:
            role_model = permissionModel()
            role_list = role_model.search_role_by_user(user)
            new_role_list = role_model.search_specific_role(role_list, '资源查看')
            service_id = role_model.search_service_id(new_role_list, service_type=5, name="查看资源")
            query = session.query(Resource).filter(Resource.has_delete == 0, Resource.Id.in_(service_id))
            total_count = query.count()  # 总共
            # 执行分页查询
            data = query.offset(pg.offset()).limit(pg.limit())  # .all()
            # 序列化结
            return total_count, dealDataList(data, Resource_Basemodel, {'has_delete'})

    def get_applied_resource_by_user(self, user: Any, pg: page, user_id: int):  # 获取当前用户所有可审批资源
        with self.get_db() as session:
            role_model = permissionModel()
            role_list = role_model.search_role_by_user(user)
            new_role_list = role_model.search_specific_role(role_list, '资源审批')
            service_ids = role_model.search_service_id(new_role_list, service_type=5, name="资源审批")
            query = session.query(Resource).filter(Resource.has_delete == 0, Resource.Id.in_(service_ids))
            total_count = query.count()  # 总共
            # 执行分页查询
            data = query.offset(pg.offset()).limit(pg.limit())  # .all()
            # 序列化结
            return total_count, dealDataList(data, Resource_Basemodel, {'has_delete'})

    def apply_resource(self, user_id: int, resource_id: int, data: ApplyBody):
        # 权限查询相关的业务类型，业务Id,角色类型，查询模板角色id
        # 输入模板角色ID，与相关参数，添加接口
        # 返回成功或者失败
        with self.get_db() as session:
            role_model = permissionModel()
            current_datetime = get_time_now('days',data.day)
            time_range = {
                "year": current_datetime.year,
                "month": current_datetime.month,
                "day": current_datetime.day,
                "start_time": data.time_range[0],
                "end_time": data.time_range[1],
            }
            time_range_json = json.dumps(time_range)
            superiorId = role_model.search_user_default_role(user_id)
            role_id = role_model.create_template_role('资源使用', superiorId, time_range_json)
            role_model.attribute_user_role(user_id, role_id)
            role_model.attribute_role_for_work(5, resource_id, role_id)
            return 'OK'

    def get_resource_application(self, resource_id: int, day: int):
        with self.get_db() as session:
            query = session.query(Role).join(
                WorkRole,
                WorkRole.role_id == Role.id
            ).filter(
                WorkRole.service_type == 5,
                WorkRole.service_id == resource_id,
                Role.has_delete == 0,
                WorkRole.has_delete == 0,
                Role.name == '资源使用'
            ).all()
            res = []
            current_date_only = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            for item in query:
                time_range = json.loads(item.template_val)
                date_obj = datetime.datetime(time_range['year'], time_range['month'], time_range['day'])
                time_difference = date_obj - current_date_only
                days_difference = time_difference.days
                if days_difference == day:
                    temp_list = []
                    temp_list.append(time_range['start_time'])
                    temp_list.append(time_range['end_time'])
                    res.append(temp_list)
            return res



    def get_specific_applied_resources(self, user_id: int, resource_id: int):
        with self.get_db() as session:
            result = []
            role_model = permissionModel()
            query = session.query(Role).join(
                WorkRole,
                WorkRole.role_id == Role.id
            ).join(
                Resource,
                Resource.Id == WorkRole.service_id
            ).filter(
                Resource.Id == resource_id
            ).all()
            if query is None:
                return
            else:
                for item in query:
                    if item.template == 1 and item.status == 1 and item.has_delete == 0:
                        time_range = json.loads(item.template_val)
                        role_id = item.id
                        user = session.query(User).join(
                            UserRole,
                            UserRole.user_id == User.id
                        ).filter(
                            UserRole.role_id == role_id
                        ).first()
                        temp_res = {
                            "user_id": user.id,
                            "user_name": user.username,
                            "start_time": time_range['start_time'],
                            "end_time": time_range['end_time'],
                        }
                        result.append(temp_res)
                return result

    def get_ifapply_resources(self, user_id: int, resource_id: int, pg: page):
        with self.get_db() as session:
            result = []
            role_model = permissionModel()
            query = session.query(Role).join(
                WorkRole,
                WorkRole.role_id == Role.id
            ).join(
                Resource,
                Resource.Id == WorkRole.service_id
            ).filter(
                Resource.Id == resource_id
            )
            if query is None:
                return
            else:
                for item in query:
                    if item.name == '资源使用':
                        time_range = json.loads(item.template_val)
                        role_id = item.id
                        user = session.query(User).join(
                            UserRole,
                            UserRole.user_id == User.id
                        ).filter(
                            UserRole.role_id == role_id
                        ).first()
                        apply_time = str(time_range['year']) + '-' + str(time_range['month']) + '-' + str(time_range['day'])
                        temp_res = {
                            "user_name": user.username,
                            "time": apply_time,
                            "start_time": time_range['start_time'],
                            "end_time": time_range['end_time'],
                        }
                        result.append(temp_res)
                total_count = len(result)
                return total_count, result





    def count_Update(self, Id: int, count: int, user_id: int):  # 修改Note
        with self.get_db() as session:
            session.query(Resource).filter(Resource.Id == Id).update({"count": count})
            session.commit()
            return Id

    def get_resource_apply_by_id(self, Id: int):  # 获取某项资源的所有申请
        # 权限查询相关的业务类型，业务Id,角色类型，查询模板角色id
        # 输入模板角色ID，查询所有非模板角色，的模板id为XXX的申请中的角色，与userid表格联合一下返回
        # 返回成功或者失败
        return

    def approve_apply(self, resource_id: int, user_id: int):
        role_model = permissionModel()
        role_list = role_model.search_role_by_user(user_id)
        new_role_list = role_model.search_specific_role(role_list, '资源审批')
        service_ids = role_model.search_service_id(new_role_list, service_type=5, name="资源审批")
        return

    def refuse_apply_by_roleid(self, Id: int):
        # 直接修改角色id，修改为不可用
        return


class BillModel(dbSession):
    def save_amount(self, obj_in: AmountAdd, user_id: int):  # 增加
        obj_dict = jsonable_encoder(obj_in)
        obj_add = Bill(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            return jsonable_encoder(obj_add.Id)

    def query_total(self, Id: int, user_id: int):  # 查询全部金额
        with self.get_db() as session:
            # 查询收入，未删除的和
            result = session.query(func.sum(Bill.amount)).filter(Bill.finance_id == Id,
                                                                 Bill.state == 0,
                                                                 Bill.has_delete == 0).scalar()
            # 查询支出，未删除的和
            result2 = session.query(func.sum(Bill.amount)).filter(Bill.finance_id == Id,
                                                                  Bill.state == 1,
                                                                  Bill.has_delete == 0).scalar()
        # 收入或支出没有赋值0
        if result is None:
            result = 0
        if result2 is None:
            result2 = 0
        return result - result2

    def query_amount(self, request: Request, ID: int, pg: page, user_id: int):  # 查询分页流水
        with self.get_db() as session:
            query = session.query(Bill).filter_by(finance_id=ID, has_delete=0)
            total_count = query.count()  # 总共
            # 执行分页查询
            data = query.offset(pg.offset()).limit(pg.limit())  # .all()
            # 序列化结
            results = dealDataList(data, BillModelOpt, {'has_delete'})
            file_id_list = []
            for result in results:
                file_id_list.append(result['log_file_id'])
            file_url_list = get_url_by_user_file_id(request, file_id_list)
            for result in results:
                if result['log_file_id'] is not None:
                    result['url'] = file_url_list[result['log_file_id']]['url']
                    result['file_type'] = file_url_list[result['log_file_id']]['file_type']
            return total_count, results

    def delete_by_id(self, Id: int, user_id: int, financial_id: int):
        with self.get_db() as session:
            session.query(Bill).filter(Bill.Id == Id).update({"has_delete": 1})
            session.commit()
            return Id

    def delete_by_financial(self, Id: int, user_id: int):  # 通过外键删除
        with self.get_db() as session:
            session.query(Bill).filter(Bill.finance_id == Id).update({"has_delete": 1})
            session.commit()
            return Id

    def check_by_id(self, Id: int, user_id: int):  # 通过主键获取
        with self.get_db() as session:
            return session.query(Bill).filter(Bill.Id == Id, Bill.has_delete == 0).first()


class FinancialModel(dbSession):
    def save_financial(self, obj_in: FinancialAdd, user_id: int):  # 增加
        obj_dict = obj_in.model_dump(exclude={"roles"})
        obj_add = Financial(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            role_model = permissionModel()
            for role in obj_in.roles:
                role_model.add_role_for_work(service_type=6, service_id=obj_add.Id, user_id=user_id,
                                             role_name=role.role_name)
            return obj_add.Id

    def check_by_id(self, Id: int, user_id: int):  # 获取，通过主键
        with self.get_db() as session:
            Financial_list = session.query(Financial).filter(Financial.Id == Id, Financial.has_delete == 0).first()
        if Financial_list is None:
            raise HTTPException(status_code=404, detail="Item not found")
        Financial_list3 = Financial_ModelOpt.model_validate(Financial_list)
        return Financial_list3.model_dump(exclude={'has_delete'})

    def delete(self, Id: int, user_id: int):  # 删除，通过主键
        with self.get_db() as session:
            session.query(Financial).filter(Financial.Id == Id).update({"has_delete": 1})
            session.commit()
            return Id

    def note_Update(self, Id: int, note: str, user_id: int):  # 修改Note
        with self.get_db() as session:
            session.query(Financial).filter(Financial.Id == Id).update({"note": note})
            session.commit()
            return Id

    def get_financial_by_user(self, user: Any, pg: page, user_id: int):  # 获取当前用户所有可用资金
        with self.get_db() as session:
            role_model = permissionModel()
            role_list = role_model.search_role_by_user(user)
            service_id = role_model.search_service_id(role_list, service_type=6, name="查看资金")
            query = session.query(Financial).filter(Financial.has_delete == 0, Financial.Id.in_(service_id))
            total_count = query.count()  # 总共
            # 执行分页查询
            data = query.offset(pg.offset()).limit(pg.limit())  # .all()
            return total_count, dealDataList(data, Financial_ModelOpt, {'has_delete'})
