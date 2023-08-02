import functools
from datetime import datetime
from typing import Callable, List

from starlette.responses import JSONResponse
from type.page import page, pageResult
from utils.times import getMsTime


def standard_response(func: Callable):
    @functools.wraps(func)
    async def decorator(*args, **kwargs):
        result = await func(*args, **kwargs)
        return JSONResponse({
            "code": 0,
            "message": "OK",
            "data": result,
            "timestamp": getMsTime(datetime.now())
        }, status_code=200)

    return decorator


def makePageResult(pg: page, tn: int, data: List):  # 处理分页数据
    return pageResult(
        pageIndex=pg.pageNow,
        pageSize=pg.pageSize,
        totalNum=tn,
        rows=data
    ).model_dump()

def user_standard_response(func: Callable):
    @functools.wraps(func)
    async def decorator(*args, **kwargs):
        result = await func(*args, **kwargs)
        response = JSONResponse({
            "code": 0,
            "message": result['message'],
            "data": result['data'],
            "timestamp": getMsTime(datetime.now())
        }, status_code=200)
        header = dict()
        if 'status' in result:  # 判断是否有status项，如果有就把它加入到header里
            header["status"] = str(result['status'])
        if 'token_header' in result:  # 判断是否有token_header项，如果有就把它加入到header里
            header["token"] = str(result['token_header'])
        if 'email_header' in result:  # 判断是否有email_header项，如果有就把它加入到header里
            header["email"] = str(result['email_header'])
        if 'token' in result:  # 判断是否有token项，如果有且不为-1就把它添加到cookie里
            if result['token'] == '-1':
                response.delete_cookie(key="SESSION")  # 删除cookie
            else:
                response.set_cookie(key="SESSION", value=str(result['token']))  # 添加cookie
        if header != {}:
            response.init_headers(header)
        return response

    return decorator


def page_response(func: Callable):
    @functools.wraps(func)
    async def decorator(*args, **kwargs):
        result = await func(*args, **kwargs)
        response = JSONResponse({
            "message": result['message'],
            "pageIndex": result['pageIndex'],
            "pageSize": result['pageSize'],
            "totalNum": result['totalNum'],
            "rows": result['rows'],
            "timestamp": getMsTime(datetime.now())
        }, status_code=200)
        return response

    return decorator
