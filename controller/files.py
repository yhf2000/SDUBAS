import datetime
import json
import os
import time
import uuid

from fastapi import APIRouter
from fastapi import File, UploadFile
from fastapi import Request, Header, HTTPException, Depends
from starlette.responses import FileResponse

from controller.users import add_operation
from model.db import session_db
from service.file import FileModel, UserFileModel
from service.user import UserModel, SessionModel
from type.file import file_interface, user_file_interface
from type.page import page
from type.user import session_interface
from utils.auth_login import auth_login
from utils.response import user_standard_response, page_response,makePageResult

files_router = APIRouter()
file_model = FileModel()
user_file_model = UserFileModel()
session_model = SessionModel()
user_model = UserModel()


@files_router.post("/upload/valid")  # 文件存在验证
@user_standard_response
async def file_upload_valid(request: Request, file: file_interface, user_agent: str = Header(None),
                            session=Depends(auth_login)):
    id = file_model.get_file_by_hash(file)  # 查询文件是否存在
    if id is None:  # 没有该file
        user_id = session['user_id']  # 得到user_id
        file_id = file_model.add_file(file)  # 新建一个file
        new_token = str(uuid.uuid4().hex)  # 生成token
        new_session = session_interface(user_id=user_id, file_id=file_id, token=new_token, ip=request.client.host,
                                        func_type=3, user_agent=user_agent, use_limit=1, exp_dt=(
                    datetime.datetime.now() + datetime.timedelta(hours=6)))  # 生成新session
        session_model.add_session(new_session)
        new_session.exp_dt = time.strptime(new_session.exp_dt.strftime(
            "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")  # 将datetime转化为字符串以便转为json
        user_session = json.dumps(new_session.model_dump())
        session_db.set(new_token, user_session, ex=21600)  # 缓存有效session(时效6h)

        return {'message': '文件不存在', 'data': True, 'token_header': new_token}
    else:  # 有该file
        return {'message': '文件存在', 'data': {'file_id': id[0]}}


@files_router.post("/upload")  # 上传文件
@user_standard_response
async def file_upload(request: Request, file: UploadFile = File(...)):
    token = request.cookies.get("TOKEN")
    old_session = session_db.get(token) # 有效session中没有
    if old_session is None:
        raise HTTPException(
            status_code=401,
            detail="token已失效，请重新上传"
        )
    old_session = json.loads(old_session)
    contents = await file.read()
    get_file = file_model.get_file_by_id(old_session['file_id'])
    folder = "files" + '/' + get_file.hash_md5[:8] + '/' + get_file.hash_sha256[-8:] + '/'  # 先创建文件夹
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(folder + file.filename,
              "wb") as f:  # 取hash_md5前八位与hash_sha256的后八位
        f.write(contents)  # 将获取的fileb文件内容，写入到新文件中
    session_model.update_session_use_by_token(token, 1)  # 将该session使用次数设为1
    session_model.delete_session_by_token(token)  # 将该session设为已失效
    session_db.delete(token)  # 将缓存删掉
    file_model.update_file_is_save(old_session['file_id'])  # 更新为已上传
    file_information = user_file_interface(file_id=old_session['file_id'], user_id=old_session['user_id'],
                                           name=file.filename, type=file.content_type)
    id = user_file_model.add_user_file(file_information)  # 添加一条user_file的记录
    current_path = request.url.path
    add_operation.delay(service_type=7, service_id=id, func='上传文件', parameters='用户上传了一个文件',
                  oper_user_id=file_information.user_id, url=current_path)  # 添加一个文件上传的操作
    data = dict()
    data['file_size'] = file.size
    data['file_name'] = file.filename,
    data['file_content_type'] = file.content_type
    data['file_id'] = id
    return {'message': '上传成功', 'data': data}


@files_router.get("/download")  # 下载文件
@user_standard_response
async def file_download(id: int, request: Request, user_agent: str = Header(None)):
    user_file = user_file_model.get_user_file_by_id(id)
    new_token = str(uuid.uuid4().hex)  # 生成token
    #  通过权限认证，判断是永久下载地址还是临时下载地址
    use_limit = 1
    exp_dt = (datetime.datetime.now() + datetime.timedelta(hours=6))
    #  通过权限认证，获取该session使用限制次数与过期时间
    new_session = session_interface(user_id=user_file.user_id, file_id=id, token=new_token,
                                    ip=request.client.host,
                                    func_type=2, user_agent=user_agent, use_limit=use_limit,
                                    exp_dt=exp_dt)  # 生成新session
    session_model.add_session(new_session)
    new_session.exp_dt = time.strptime(new_session.exp_dt.strftime(
        "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")  # 将datetime转化为字符串以便转为json
    user_session = json.dumps(new_session.model_dump())
    session_db.set(new_token, user_session, ex=21600)  # 缓存有效session(时效6h)
    return {'message': '请前往下载', 'data': {'url': 'http://127.0.0.1:8000/files/download/' + new_token}}


@files_router.get("/download/{token}")  # 下载文件
async def file_download_files(request: Request, token: str):
    old_session = session_db.get(token)  # 有效session中没有
    if old_session is None:
        raise HTTPException(
            status_code=401,
            detail="链接已失效"
        )
    old_session = json.loads(old_session)
    if old_session['use'] != old_session['use_limit']:
        if old_session['use'] + 1 == old_session['use_limit']:
            session_model.delete_session_by_token(token)
            session_db.delete(token)
        else:
            session_model.update_session_use_by_token(token, 1)  # 将该session使用次数加1
        user_file = user_file_model.get_user_file_by_id(old_session['file_id'])
        file = file_model.get_file_by_id(user_file.file_id)
        folder = "files" + '/' + file.hash_md5[:8] + '/' + file.hash_sha256[-8:] + '/' + user_file.name  # 先找到路径
        current_path = request.url.path
        add_operation.delay(service_type=7, service_id=old_session['file_id'], func='下载文件', parameters='用户下载了一个文件',
                      oper_user_id=old_session['user_id'], url=current_path)
        return FileResponse(folder, filename=user_file.name)
    raise HTTPException(
        status_code=401,
        detail="链接已失效"
    )


@files_router.get("/preview")  # 文件预览,用户查看所有他可以进行下载的文件
@page_response
async def file_preview(request:Request,pageNow: int, pageSize: int, session=Depends(auth_login)):
    # 判断是否有权限
    # 如果有权限
    Page = page(pageSize=pageSize, pageNow=pageNow)
    all_file = user_file_model.get_user_file_by_admin(Page, session['user_id'])  # 以分页形式返回
    result = None
    current_path = request.url.path
    add_operation.delay(service_type=7, service_id=session['user_id'], func='查看文件', parameters='用户查看他能下载的文件',
                        oper_user_id=session['user_id'], url=current_path)
    if all_file != []:
        file_data = []
        for file in all_file:  # 遍历查询结果
            temp = user_file_interface()
            temp_dict = temp.model_validate(file).model_dump()  # 查询出来的结果转字典
            temp_dict['user_name'] = user_model.get_user_by_user_id(session['user_id']).username  # 查出name
            file_data.append(temp_dict)
        result = makePageResult(Page, len(all_file), file_data)
    return {'message': '可下载文件如下', "data": result}
