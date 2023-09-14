import json
import re
from fastapi import Depends, Security, HTTPException
from fastapi import Request


from model.user import User
from model.permissions import UserRole, RolePrivilege, Role
from model.db import dbSession
from service.permissions import roleModel
from utils.auth_login import auth_login
from utils.privilege_dict import *


def extract_type_from_string(input_string):
    if input_string.startswith('/projects'):
        return 7
    if input_string.startswith('/resources'):
        return 5
    if input_string.startswith('/resources/financial'):
        return 6
    if input_string.startswith('/users'):
        return 0
    if input_string.startswith('/educations'):
        return 1
    if input_string.startswith('/permissions'):  # 记得删除
        return 7
    return -1

def extract_id_from_string(input_string):
    if input_string.startswith('/projects'):
        match = re.search(r'\d+', input_string)
        if match:
            number = match.group()
            return number
    if input_string.startswith('/resources'):
        match = re.search(r'\d+', input_string)
        if match:
            number = match.group()
            return number
    if input_string.startswith('/resources/financial'):
        match = re.search(r'\d+', input_string)
        if match:
            number = match.group()
            return number
    if input_string.startswith('/users'):
        match = re.search(r'\d+', input_string)
        if match:
            number = match.group()
            return number
    if input_string.startswith('/educations'):
        match = re.search(r'\d+', input_string)
        if match:
            number = match.group()
            return number
    return 0

def remove_numbers(input_string):
    return re.sub(r'\d', '', input_string)

def find_common_role(list1, list2):
    set1 = set(list1)
    set2 = set(list2)
    common_role = list(set1 & set2)
    return common_role


def auth_permission(request: Request):
    # session = auth_login(request)
    user_id = int(request.headers.get("user_id"))
    session = {
        "user_id": user_id
    }
    # user_id = session['user_id']
    db = roleModel()
    url = request.url.path
    permission_key = remove_numbers(url)
    service_id = extract_id_from_string(url)
    service_type = extract_type_from_string(url)
    user_role_list = db.search_role_by_user(user_id)
    if 1 in user_role_list:
        return session
    service_role_list = db.search_role_by_service(service_id, service_type)
    common_role_list = find_common_role(user_role_list, service_role_list)

    privilege = privilege_dict[permission_key]
    privilege_id = db.search_privilege_name_by_privilege_id(privilege)
    privilege_set = db.search_privilege_by_role(common_role_list)
    if privilege_id in privilege_set:
        return session
    else:
        raise HTTPException(
            status_code=403,
            detail="No permission",
        )


def auth_permission_default(request: Request):
    session = auth_login(request)
    # user_id = int(request.headers.get("user_id"))
    # session = {
    #     "user_id": user_id
    # }
    user_id = session['user_id']
    db = roleModel()
    url = request.url.path
    permission_key = remove_numbers(url)
    user_role_list = db.search_role_by_user(user_id)
    if 1 in user_role_list:
        return session
    privilege = privilege_dict[permission_key]
    privilege_id = db.search_privilege_name_by_privilege_id(privilege)
    privilege_set = db.search_privilege_by_role(user_role_list)
    if privilege_id in privilege_set:
        return session
    else:
        raise HTTPException(
            status_code=403,
            detail="No permission",
        )
