from utils.auth_permission import auth_permission
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Request, HTTPException
from db import deps
from Basemodel import financial_Basemodel
from crudapi import Resourcecrud, amountcrud
from crudapi import accountcrud
from utils.response import standard_response

financial_router = APIRouter()


@financial_router.post("/resource/add")  # 添加资源项目
@standard_response
async def save_api(apiSchema: financial_Basemodel.ResourceAdd, user=Depends(auth_permission),
                   session=Depends(deps.get_session)):
    return Resourcecrud.api.save_resource(obj_in=apiSchema, db=session)


@financial_router.post("/resource/delete")  # 删除资源项目
@standard_response
async def delete(apiSchema: financial_Basemodel.ResourceDelete, user=Depends(auth_permission),
                 session=Depends(deps.get_session)):
    check_result = Resourcecrud.api.check_by_id(Id=apiSchema.id, db=session)
    if check_result is not None:
        Resourcecrud.api.delete(Id=apiSchema.id, db=session)
        return {"message": "delete success"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@financial_router.post("/financial/add")  # 添加资金项目
@standard_response
async def save_financial(apiSchema: financial_Basemodel.FinancialAdd, user=Depends(auth_permission),
                         session=Depends(deps.get_session)):
    apiSchema.create_dt = datetime.now()
    return accountcrud.api.save_financial(obj_in=apiSchema, db=session)


@financial_router.post("/financial/account")  # 添加收支记录
@standard_response
async def save_financial(apiSchema: financial_Basemodel.AmountAdd, user=Depends(auth_permission),
                         session=Depends(deps.get_session)):
    if apiSchema.state == 0:
        count = str(apiSchema.amount)
        apiSchema.log_content = "收入" + count
    else:
        count = str(apiSchema.amount)
        apiSchema.log_content = "支出" + count
    apiSchema.oper_dt = datetime.now()
    return amountcrud.api.save_amount(obj_in=apiSchema, db=session)


@financial_router.post("/financial/total")  # 计算总额
@standard_response
async def query_total(apiSchema: financial_Basemodel.ResourceDelete, user=Depends(auth_permission),
                      session=Depends(deps.get_session)):
    num = accountcrud.api.check_byId(Id=apiSchema.id, db=session)
    if num == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    else:
        summ = amountcrud.api.query_total(Id=apiSchema.id, db=session)
        return {"message": "资金总额", "count": str(float(summ))}


@financial_router.post("/financial/accountbook")  # 查看账单
@standard_response
async def query_page(apiSchema: financial_Basemodel.pageRequest, user=Depends(auth_permission),
                     session=Depends(deps.get_session)):
    num = accountcrud.api.check_byId(Id=apiSchema.id, db=session)
    if num == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    else:
        return amountcrud.api.query_amount(ID=apiSchema.id, pn=apiSchema.pn, pg=apiSchema.pg, db=session)


@financial_router.post("/financial/delete")  # 删除资金项目
@standard_response
async def delete_financial(apiSchema: financial_Basemodel.ResourceDelete, user=Depends(auth_permission),
                           session=Depends(deps.get_session)):
    check_result = accountcrud.api.check_byId(Id=apiSchema.id, db=session)
    if check_result is not None:
        accountcrud.api.delete(Id=apiSchema.id, db=session)
        amountcrud.api.delete_by_financial(Id=apiSchema.id, db=session)
        #此处应该删除权限
        return {"message": "delete success"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@financial_router.post("/financial/account/delete")  # 删除资金流水项目
@standard_response
async def delete_account(apiSchema: financial_Basemodel.ResourceDelete, user=Depends(auth_permission),
                         session=Depends(deps.get_session)):
    check_result = amountcrud.api.check_byId(Id=apiSchema.id, db=session)
    if check_result is not None:
        amountcrud.api.delete_by_id(Id=apiSchema.id, db=session)
        return {"message": "delete success"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")
