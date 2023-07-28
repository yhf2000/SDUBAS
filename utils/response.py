import functools
from datetime import datetime
from typing import Callable, List

from starlette.responses import JSONResponse
from model.financial_Basemodel import page, pageResult
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


def obj2dict(obj):#添加的处理序列化
    m = obj.__dict__
    for k in m.keys():
        v = m[k]
        if hasattr(v, "__dict__"):
            m[k] = obj2dict(v)
        if type(v) == list:
            tp = []
            for it in v:
                if hasattr(it, "__dict__"):
                    tp.append(obj2dict(it))
                else:
                    tp.append(it)
            m[k] = tp
    return m


def makePageResult(pg: page, tn: int, data: List):#处理分页数据
    return obj2dict(pageResult(
        pageIndex=pg.pageNow,
        pageSize=pg.pageSize,
        totalNum=tn,
        rows=data
    ))
