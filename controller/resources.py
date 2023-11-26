from type.financial import User_Name_Add
from utils.auth_login import auth_login
from utils.auth_permission import auth_permission, auth_permission_default
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from utils.response import standard_response, makePageResult
from service.Resource import ResourceModel, FinancialModel, BillModel
from type.page import page
from type import financial as financial_Basemodel
from type.functions import make_parameters, get_user_name
from Celery.add_operation import add_operation
from service.permissions import permissionModel

resources_router = APIRouter()


@resources_router.post("/resource")  # 添加资源项目
@standard_response
async def save_api(request: Request, apiSchema: financial_Basemodel.ResourceAdd, user=Depends(auth_permission_default)):
    db = ResourceModel()  # 判断后直接添加
    results = db.save_resource(obj_in=apiSchema, user_id=user['user_id'])
    parameters = await make_parameters(request)
    add_operation.delay(5, results, "添加资源", f"用户{user['user_id']}于xxx添加资源{apiSchema.name}", parameters, user['user_id'])
    return results


@resources_router.get("/resource/view")  # 查看所有资源项目,可能需要分页数据
@standard_response
async def get_resource_by_user(request: Request, pageNow: int = Query(description="页码", gt=0),
                               pageSize: int = Query(description="每页数量", gt=0),
                               user=Depends(auth_permission_default)):
    Page = page(pageNow=pageNow, pageSize=pageSize)
    db = ResourceModel()
    tn, res = db.get_view_resource_by_user(user=user['user_id'], pg=Page, user_id=user['user_id'])
    parameters = await make_parameters(request)
    add_operation.delay(5, 0, "查看所有资源", f"用户{user['user_id']}于xxx查看所有资源", parameters, user['user_id'])
    return makePageResult(pg=Page, tn=tn, data=res)


@resources_router.put("/resource/{resource_id}")  # 修改资源数目
@standard_response
async def Update_resource_by_count(request: Request, resource_id: int,
                                   apiSchema: financial_Basemodel.resource_count_update,
                                   user=Depends(auth_permission)):
    db = ResourceModel()  # 判断后直接添加
    Resource = db.check_by_id(Id=resource_id, user_id=user['user_id'])
    if Resource is not None:
        results = db.count_Update(Id=resource_id, count=apiSchema.count, user_id=user['user_id'])
        parameters = await make_parameters(request)
        name = db.get_resource_by_id(resource_id)[0]
        add_operation.delay(5, resource_id, "修改资源数目", f"用户{user['user_id']}于xxx修改资源{name}", parameters,
                            user['user_id'])
        return results
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@resources_router.get("/resource/get/{resource_id}")  # 查看一个具体的资源
@standard_response
async def Update_resource_by_count(request: Request, resource_id: int,
                                   user=Depends(auth_permission)):
    db = ResourceModel()
    results = db.check_by_id(Id=resource_id, user_id=user['user_id'])
    parameters = await make_parameters(request)
    name = db.get_resource_by_id(resource_id)[0]
    add_operation.delay(5, resource_id, "查看一个具体资源", f"用户{user['user_id']}于xxx查看资源{name}", parameters,
                        user['user_id'])
    return results


@resources_router.post("/resource/apply/{resource_id}")  # 申请一个具体的资源(不需要审批版)
@standard_response
async def apply_Resource(resource_id: int, apiSchema: financial_Basemodel.ApplyBody,
                         user=Depends(auth_permission)):
    db = ResourceModel()
    return db.apply_resource(user_id=user['user_id'], resource_id=resource_id, data=apiSchema)


@resources_router.get("/resource/application/{resource_id}/{day}")  # 查看资源被占用时间
@standard_response
async def get_application(resource_id: int, day: int,
                          user=Depends(auth_permission)):
    db = ResourceModel()
    return db.get_resource_application(resource_id, day)


@resources_router.get("/resource/apply/get")  # 获取所有可以审批的资源
@standard_response
async def get_applied_resource(request: Request, pageNow: int = Query(description="页码", gt=0),
                               pageSize: int = Query(description="每页数量", gt=0),
                               user=Depends(auth_permission_default)):
    Page = page(pageNow=pageNow, pageSize=pageSize)
    db = ResourceModel()
    tn, res = db.get_applied_resource_by_user(user=user['user_id'], pg=Page, user_id=user['user_id'])
    parameters = await make_parameters(request)
    add_operation.delay(5, 0, "查看可审批资源", f"用户{user['user_id']}于xxx查看所有可审批资源", parameters, user['user_id'])
    return makePageResult(pg=Page, tn=tn, data=res)


@resources_router.get("/resource/ifapply/{resource_id}")  # 查看某一个资源的申请记录
@standard_response
async def get_specific_applied_resource(request: Request, resource_id: int,
                                        pageNow: int = Query(description="页码", gt=0),
                                        pageSize: int = Query(description="每页数量", gt=0),
                                        user=Depends(auth_permission)):
    Page = page(pageNow=pageNow, pageSize=pageSize)
    db = ResourceModel()
    tn, res = db.get_ifapply_resources(user['user_id'], resource_id, Page)
    name = db.get_resource_by_id(resource_id)[0]
    parameters = await make_parameters(request)
    add_operation.delay(5, 0, "查看资源申请记录", f"用户{user['user_id']}于xxx查看资源{name}申请记录", parameters, user['user_id'])
    return makePageResult(pg=Page, tn=tn, data=res)


@resources_router.put("/resource/approve/{resource_id}")  # 通过一个资源的申请,不可用
@standard_response
async def get_Resource_apply_by_user(role_id: int, resource_id: int,
                                     user=Depends(auth_permission)):
    db = ResourceModel()
    return db.approve_apply(resource_id)


@resources_router.put("/resource/{resource_id}/{role_id}/refuse")  # 拒绝一个资源的申请,不可用
@standard_response
async def get_Resource_apply_by_user(role_id: int,
                                     user=Depends(auth_permission)):
    db = ResourceModel()
    return db.refuse_apply_by_roleid(Id=role_id)


# 可能需要查询申请结果的url，但可以复用查询权限

@resources_router.delete("/resource/{resource_id}/delete")  # 删除资源项目
@standard_response
async def delete(request: Request, resource_id: int, user=Depends(auth_permission)):
    db = ResourceModel()
    check_result = db.check_by_id(Id=resource_id, user_id=user['user_id'])  # 判断有无资源，是否被删除
    if check_result is not None:  # 有，删除
        name = db.get_resource_by_id(resource_id)[0]
        return_id = db.delete(Id=resource_id, user_id=user['user_id'])
        parameters = await make_parameters(request)
        add_operation.delay(5, return_id, "删除资源", f"用户{user['user_id']}于xxx删除资源{name}", parameters, user['user_id'])
        return return_id
    else:  # 无，项目找不到
        raise HTTPException(status_code=404, detail="Item not found")


@resources_router.post("/resource/delete_user_in_resources/{resource_id}/{role_id}/{delete_user}")  # 删除资源用户
@standard_response
async def delete_user_in_project(request: Request, role_id: int, delete_user: int,
                                 user=Depends(auth_permission)):
    db = permissionModel()
    db.delete_work_user(delete_user, role_id)
    return 'OK'


@resources_router.post("/resource/add_user_in_resources/{resource_id}")  # 添加资源用户
@standard_response
async def add_user_in_resources(request: Request, data: User_Name_Add):
    db = permissionModel()
    db.add_work_user(data.username, data.role_id)
    return 'OK'


@resources_router.post("/financial")  # 添加资金项目
@standard_response
async def save_financial(request: Request, apiSchema: financial_Basemodel.FinancialAdd, user=Depends(auth_permission)):
    db = FinancialModel()
    results = db.save_financial(obj_in=apiSchema, user_id=user['user_id'])
    parameters = await make_parameters(request)
    add_operation.delay(6, results, "添加资金", f"用户{user['user_id']}于xxx添加资金{apiSchema.name}", parameters, user['user_id'])
    return results


@resources_router.post("/financial/{financial_id}/account")  # 添加收支记录
@standard_response
async def save_financial(request: Request, financial_id: int, apiSchema: financial_Basemodel.AmountAdd,
                         user=Depends(auth_permission)):
    db = BillModel()
    FinancialModel_db = FinancialModel()
    num = FinancialModel_db.check_by_id(Id=financial_id, user_id=user['user_id'])  # 所有信息，处理总额之外所有信息
    if num is None:
        raise HTTPException(status_code=404, detail="Item not found")
    else:
        apiSchema.finance_id = financial_id
        results = db.save_amount(obj_in=apiSchema, user_id=user['user_id'])
        parameters = await make_parameters(request)
        name = FinancialModel_db.get_financial_by_id(financial_id)[0]
        add_operation.delay(6, financial_id, "添加资金收支", f"用户{user['user_id']}于xxx添加资金收支{name}", parameters,
                            user['user_id'])
        return results


@resources_router.get("/financial/{financial_id}/amount")  # 计算总额,外加额外信息
@standard_response
async def query_total(request: Request, financial_id: int, user=Depends(auth_permission)):
    FinancialModel_db = FinancialModel()
    BillModel_db = BillModel()
    num = FinancialModel_db.check_by_id(Id=financial_id, user_id=user['user_id'])  # 所有信息，处理总额之外所有信息
    if num is None:
        raise HTTPException(status_code=404, detail="Item not found")
    else:
        summ = BillModel_db.query_total(Id=financial_id, user_id=user['user_id'])  # 获取可用流水，总额
        num['count'] = str(float(summ))
        # 或许可增加创建人信息
        parameters = await make_parameters(request)
        name = FinancialModel_db.get_financial_by_id(financial_id)[0]
        add_operation.delay(6, financial_id, "计算资金总额", f"用户{user['user_id']}于xxx计算资金{name}总额", parameters,
                            user['user_id'])
        return num


@resources_router.get("/financial/{financial_id}/accountbook")  # 查看账单
@standard_response
async def query_page(request: Request, financial_id: int, pageNow: int = Query(description="页码", gt=0),
                     pageSize: int = Query(description="每页数量", gt=0), user=Depends(auth_permission)):
    Page = page(pageNow=pageNow, pageSize=pageSize)
    FinancialModel_db = FinancialModel()
    BillModel_db = BillModel()
    num = FinancialModel_db.check_by_id(Id=financial_id, user_id=user['user_id'])  # 检查资金项目有无
    if num is None:
        raise HTTPException(status_code=404, detail="Item not found")
    else:
        tn, res = BillModel_db.query_amount(request=request, ID=financial_id, pg=Page,
                                            user_id=user['user_id'])  # 返回总额，分页数据
        parameters = await make_parameters(request)
        add_operation.delay(6, financial_id, "查看账单", f"用户{user['user_id']}于xxx查看账单", parameters, user['user_id'])
        return makePageResult(pg=Page, tn=tn, data=res)  # 封装的函数


@resources_router.delete("/financial/{financial_id}/delete")  # 删除资金项目
@standard_response
async def delete_financial(request: Request, financial_id: int, user=Depends(auth_permission)):
    FinancialModel_db = FinancialModel()
    BillModel_db = BillModel()
    check_result = FinancialModel_db.check_by_id(Id=financial_id, user_id=user['user_id'])
    if check_result is not None:
        name = FinancialModel_db.get_financial_by_id(financial_id)[0]
        return_id = FinancialModel_db.delete(Id=financial_id, user_id=user['user_id'])
        BillModel_db.delete_by_financial(Id=financial_id, user_id=user['user_id'])  # 同步删除所有资金流水
        parameters = await make_parameters(request)
        add_operation.delay(6, return_id, "删除资金", f"用户{user['user_id']}于xxx删除资金{name}", parameters, user['user_id'])
        # 此处应该删除权限
        return return_id
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@resources_router.delete("/financial/{financial_id}/{account_id}")  # 删除资金流水项目
@standard_response
async def delete_account(request: Request, financial_id: int, account_id: int, user=Depends(auth_permission)):
    BillModel_db = BillModel()
    check_result = BillModel_db.check_by_id(Id=account_id, user_id=user['user_id'])
    if check_result is not None:
        return_id = BillModel_db.delete_by_id(Id=account_id, user_id=user['user_id'], financial_id=financial_id)
        parameters = await make_parameters(request)
        add_operation.delay(6, return_id, "删除资金流水", f"用户{user['user_id']}于xxx删除资金流水", parameters, user['user_id'])
        return return_id
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@resources_router.put("/financial/{financial_id}/revise")  # 修改资金项目
@standard_response
async def delete_financial(request: Request, financial_id: int, apiSchme: financial_Basemodel.FinancialUpdate,
                           user=Depends(auth_permission)):
    FinancialModel_db = FinancialModel()
    check_result = FinancialModel_db.check_by_id(Id=financial_id, user_id=user['user_id'])
    if check_result is not None:
        returnId = FinancialModel_db.note_Update(Id=financial_id, note=apiSchme.note, user_id=user['user_id'])
        name = FinancialModel_db.get_financial_by_id(financial_id)[0]
        parameters = await make_parameters(request)
        add_operation.delay(6, financial_id, "修改资金项目", f"用户{user['user_id']}于xxx修改资金项目{name}", parameters,
                            user['user_id'])
        return returnId
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@resources_router.get("/financial/search")  # 查询资金，需要权限，不可用
@standard_response
async def get_financial_by_user(request: Request, pageNow: int = Query(description="页码", gt=0),
                                pageSize: int = Query(description="每页数量", gt=0), user=Depends(auth_login)):
    Page = page(pageNow=pageNow, pageSize=pageSize)
    db = FinancialModel()
    # 调用函数
    tn, result = db.get_financial_by_user(user=user['user_id'], pg=Page, user_id=user['user_id'])
    parameters = await make_parameters(request)
    name = get_user_name(user['user_id'])
    add_operation.delay(6, 0, "查询资金列表", f"用户{name}于xxx查询资金列表", parameters, user['user_id'])
    return makePageResult(pg=Page, tn=tn, data=result)
