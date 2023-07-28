from utils.auth_permission import auth_permission
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Request, HTTPException
from model import financial_Basemodel
from service import accountcrud
from utils.response import standard_response, makePageResult
from service.Resourcecrud import ResourceModel
from service.accountcrud import FinancialModel
from service.billcrud import BillModel

financial_router = APIRouter()


@financial_router.post("/resource")  # 添加资源项目
@standard_response
async def save_api(apiSchema: financial_Basemodel.ResourceAdd, user=Depends(auth_permission)):
    db = ResourceModel()#判断后直接添加
    return db.save_resource(obj_in=apiSchema)


@financial_router.delete("/resource/{resource_id}")  # 删除资源项目
@standard_response
async def delete(resource_id: int, user=Depends(auth_permission)):
    db = ResourceModel()
    check_result = db.check_by_id(Id=resource_id)#判断有无资源，是否被删除
    if check_result is not None:#有，删除
        return_id = db.delete(Id=resource_id)
        return return_id
    else:#无，项目找不到
        raise HTTPException(status_code=404, detail="Item not found")


@financial_router.post("/financial")  # 添加资金项目
@standard_response
async def save_financial(apiSchema: financial_Basemodel.FinancialAdd, user=Depends(auth_permission)):
    db = FinancialModel()
    return db.save_financial(obj_in=apiSchema)


@financial_router.post("/financial/{financial_id}/account")  # 添加收支记录
@standard_response
async def save_financial(financial_id: int, apiSchema: financial_Basemodel.AmountAdd, user=Depends(auth_permission)):
    db = BillModel()
    apiSchema.finance_id = financial_id
    return db.save_amount(obj_in=apiSchema)


@financial_router.get("/financial/{financial_id}")  # 计算总额,外加额外信息
@standard_response
async def query_total(financial_id: int, user=Depends(auth_permission)):
    FinancialModel_db = FinancialModel()
    BillModel_db = BillModel()
    num = FinancialModel_db.check_by_id(Id=financial_id)  # 所有信息，处理总额之外所有信息
    if num is None:
        raise HTTPException(status_code=404, detail="Item not found")
    else:
        summ = BillModel_db.query_total(Id=financial_id)#获取可用流水，总额
        num['count'] = str(float(summ))
        #或许可增加创建人信息
        return num


@financial_router.post("/financial/{financial_id}/accountbook")  # 查看账单
@standard_response
async def query_page(financial_id: int, apiSchema: financial_Basemodel.page, user=Depends(auth_permission)):
    FinancialModel_db = FinancialModel()
    BillModel_db = BillModel()
    num = FinancialModel_db.check_by_id(Id=financial_id)#检查资金项目有无
    if num is None:
        raise HTTPException(status_code=404, detail="Item not found")
    else:
        tn, res = BillModel_db.query_amount(ID=financial_id, pg=apiSchema)#返回总额，分页数据
        return makePageResult(pg=apiSchema, tn=tn, data=res)#封装的函数


@financial_router.delete("/financial/{financial_id}")  # 删除资金项目
@standard_response
async def delete_financial(financial_id: int, user=Depends(auth_permission)):
    FinancialModel_db = FinancialModel()
    BillModel_db = BillModel()
    check_result = FinancialModel_db.check_by_id(Id=financial_id)
    if check_result is not None:
        return_id = FinancialModel_db.delete(Id=financial_id)
        BillModel_db.delete_by_financial(Id=financial_id)#同步删除所有资金流水
        # 此处应该删除权限
        return return_id
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@financial_router.delete("/financial/{financial_id}/{account_id}")  # 删除资金流水项目
@standard_response
async def delete_account(account_id: int, user=Depends(auth_permission)):
    BillModel_db = BillModel()
    check_result = BillModel_db.check_by_id(Id=account_id)
    if check_result is not None:
        return_id = BillModel_db.delete_by_id(Id=account_id)
        return return_id
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@financial_router.put("/financial/{financial_id}")  # 修改资金项目
@standard_response
async def delete_financial(financial_id: int, apiSchme:financial_Basemodel.FinancialUpdate, user=Depends(auth_permission)):
    FinancialModel_db = FinancialModel()
    check_result = FinancialModel_db.check_by_id(Id=financial_id)
    if check_result is not None:
        returnId = FinancialModel_db.note_Update(Id=financial_id, note=apiSchme.note)
        return returnId
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@financial_router.get("/financial")  # 查询资金
@standard_response
async def get_financial_by_user(user=Depends(auth_permission)):
    db = FinancialModel()
    # 调用函数
    # tn, result = db.get_financial_list_by_user(user)获取分页
    return 0  # makepage()
