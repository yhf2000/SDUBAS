from typing import List
import time
from pydantic import BaseModel, Field, validator, constr, ConfigDict, BaseConfig
from datetime import datetime
from typing import get_type_hints


def convert_datetime_to_timestamp(dt: datetime) -> int:#datetime换时间戳函数
    return int(dt.timestamp())


def convert_result_to_model(result, model_class):#base转换成basemodel函数,参数查询结果，basemodel类
    model_fields = model_class.__annotations__
    model_kwargs = {}

    for field, annotation in model_fields.items():
        if field == 'Config':
            continue
        if getattr(result, field) is None:#对None的处理，如果有例外再增加，已有对int和str的判断
            if annotation == int:
                model_kwargs[field] = 0
            elif annotation == str:
                model_kwargs[field] = ""
            # 如果字段类型是 int，且结果值为 datetime 类型，则转换为时间戳
        elif annotation == int and isinstance(getattr(result, field), datetime):
            model_kwargs[field] = convert_datetime_to_timestamp(getattr(result, field))
        else:
            model_kwargs[field] = getattr(result, field)

    return model_class(**model_kwargs)


def dealDataList(data, model_class, popKeys=None):#参数：查询结果list,basemodel类，移除属性
    dicts = []
    print(type(model_class))
    for d in data:
        base_model = convert_result_to_model(d, model_class=model_class)
        print(type(base_model))
        dicts.append(base_model.model_dump(exclude=popKeys))
    return dicts


class page(BaseModel):  # 定义的分页类
    pageSize: int = Field(..., gt=0)
    pageNow: int = Field(..., gt=0)

    def offset(self):
        return (max(1, self.pageNow) - 1) * self.pageSize

    def limit(self):
        return self.pageSize


class pageResult(BaseModel):  # 分页结果类
    pageIndex: int
    pageSize: int
    totalNum: int
    rows: List
