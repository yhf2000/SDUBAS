import datetime
import json
import uuid
from hashlib import sha256, md5
from urllib.parse import quote
from fastapi import APIRouter, Form
from fastapi import File, UploadFile
from fastapi import Request, Header, Depends
from starlette.responses import JSONResponse, StreamingResponse
from Celery.add_operation import add_operation
from Celery.upload_file import upload_file
from model.db import session_db
from service.file import FileModel, UserFileModel, RSAModel, ASEModel
from service.user import UserModel, SessionModel
from type.file import file_interface, user_file_interface, RSA_interface, ASE_interface
from type.functions import get_files, generate_rsa_key_pair, make_parameters, get_user_name
from type.page import page
from type.user import session_interface
from utils.auth_login import auth_login
from utils.response import user_standard_response, page_response, makePageResult

files_router = APIRouter()
file_model = FileModel()
user_file_model = UserFileModel()
session_model = SessionModel()
user_model = UserModel()
RSA_model = RSAModel()
ASE_model = ASEModel()

# 文件存在验证，在上传文件之前先上传size和两个hash来判断文件是否存在：若文件存在则返回id，不存在则在cookie设置一个token
@files_router.post("/upload/valid")
@user_standard_response
async def file_upload_valid(request: Request, file: file_interface, user_agent: str = Header(None),
                            session=Depends(auth_login)):
    global user_file_id
    id = file_model.get_file_by_hash(file)  # 查询文件是否存在
    public_key = None
    if file.type == 1:
        public_key = RSA_model.get_public_key_by_user_id(session['user_id'])
        if public_key is None:
            private_pem, public_pem = generate_rsa_key_pair()
            new_rsa= RSA_interface(private_key_pem = private_pem,public_key_pem=public_pem,user_id = session['user_id'])
            public_key =RSA_model.add_user_RSA(new_rsa)
        else:
            public_key = public_key[0]
    if id is None or id[1] is False:  # 没有该file或者有但是还未上传
        user_id = session['user_id']  # 得到user_id
        if id is None:
            file_id = file_model.add_file(file)  # 新建一个file
            if file.time is None:
                user_file_id = user_file_model.add_user_file(
                    user_file_interface(file_id=file_id, user_id=session['user_id']))
            else:
                user_file_id = user_file_model.add_user_file(
                    user_file_interface(file_id=file_id, user_id=session['user_id'], video_time=file.time))
        else:
            user_file_id = user_file_model.get_user_file_id_by_file_id(id[0])[0]
        new_token = str(uuid.uuid4().hex)  # 生成token
        new_session = session_interface(user_id=user_id, file_id=user_file_id, token=new_token, ip=request.client.host,
                                        func_type=3, user_agent=user_agent, use_limit=1, exp_dt=(
                    datetime.datetime.now() + datetime.timedelta(hours=6)))  # 生成新session
        session_model.add_session(new_session)
        new_session = new_session.model_dump()
        new_session['exp_dt'] = new_session['exp_dt'].strftime("%Y-%m-%d %H:%M:%S")
        user_session = json.dumps(new_session)
        session_db.set(new_token, user_session, ex=21600)  # 缓存有效session(时效6h)
        return {'message': '文件不存在', 'data': {'file_id': None, 'public_key': public_key}, 'token_header': new_token,
                'code': 0}
    else:  # 有该file
        user_file_id = user_file_model.get_user_file_id_by_file_id(id[0])[0]
        return {'message': '文件存在', 'data': {'file_id': user_file_id, 'public_key': public_key}, 'code': 0}


# 上传文件。文件存储位置：files/hash_md5前八位/hash_sha256的后八位/文件名
@files_router.post("/upload")
@user_standard_response
async def file_upload(request: Request, file: UploadFile = File(...), ase_key: str = Form(...), session=Depends(auth_login)):
    token = request.cookies.get("TOKEN")
    old_session = session_db.get(token)  # 有效session中没有，即session过期了
    if old_session is None:
        session_model.delete_session_by_token(token)
        return {'message': 'token已失效，请重新上传', 'data': None, 'code': 1}
    old_session = json.loads(old_session)
    id = user_file_model.get_user_file_by_file_name(file.filename)  # 查看文件名是否存在
    if id is not None:
        return {'message': '文件名已存在，请修改后重新上传', 'data': None, 'code': 2}
    file_content = await file.read()
    file_id = user_file_model.get_file_id_by_id(old_session['file_id'])[0]
    get_file = file_model.get_file_by_id(file_id)
    size = file.size
    if size != get_file.size:
        return {'message': '文件size不正确', 'data': None, 'code': 3}
    md5_hash = md5()
    md5_hash.update(file_content)
    md5_hexdigest = md5_hash.hexdigest()
    if md5_hexdigest != get_file.hash_md5:
        return {'message': '文件MD5不正确', 'data': None, 'code': 4}
    sha256_hash = sha256()
    sha256_hash.update(file_content)
    sha256_hexdigest = sha256_hash.hexdigest()
    if sha256_hexdigest != get_file.hash_sha256:
        return {'message': '文件sha256不正确', 'data': None, 'code': 5}
    if ase_key is not None:
        new_ase = ASE_interface(file_id = old_session['file_id'],ase_key = ase_key)
        id = ASE_model.add_file_ASE(new_ase)
    folder = get_file.hash_md5[:8] + '/' + get_file.hash_sha256[-8:] + '/'  # 先创建路由
    contents = await file.read()
    upload_file.delay(folder,file.filename,contents)
    session_model.update_session_use_by_token(token, 1)  # 将该session使用次数设为1
    session_model.delete_session_by_token(token)  # 将该session设为已失效
    session_db.delete(token)  # 将缓存删掉
    user_file_model.update_user_file_name_type(old_session['file_id'], file.filename,
                                               file.content_type)  # 添加一条user_file的记录
    file_model.update_file_is_save(file_id)  # 更新为已上传
    parameters = await make_parameters(request)
    username = get_user_name(session['user_id'])
    add_operation.delay(8, old_session['file_id'], '上传文件',f'用户{username}于qpzm7913上传了一个名为{file.filename}的文件', parameters, old_session['user_id'])
    data = dict()
    data['file_size'] = file.size
    data['file_name'] = file.filename,
    data['file_content_type'] = file.content_type
    data['file_id'] = old_session['file_id']
    return {'message': '上传成功', 'data': data, 'code': 0}


# 下载文件，即返回一个下载链接
@files_router.get("/download")
@user_standard_response
async def file_download(id: int, request: Request, user_agent: str = Header(None), session=Depends(auth_login)):
    user_file = user_file_model.get_user_file_by_id(id)
    new_token = str(uuid.uuid4().hex)  # 生成token
    use_limit = 1
    exp_dt = (datetime.datetime.now() + datetime.timedelta(hours=6))
    new_session = session_interface(user_id=user_file.user_id, file_id=id, token=new_token,
                                    ip=request.client.host,
                                    func_type=2, user_agent=user_agent, use_limit=use_limit,
                                    exp_dt=exp_dt)  # 生成新session
    session_model.add_session(new_session)
    new_session = new_session.model_dump()
    new_session['exp_dt'] = new_session['exp_dt'].strftime("%Y-%m-%d %H:%M:%S")
    user_session = json.dumps(new_session)
    session_db.set(new_token, user_session, ex=21600)  # 缓存有效session(时效6h)
    return {'message': '请前往下载', 'data': {'url': 'http://127.0.0.1:8000/files/download/' + new_token}, 'code': 0}


# 根据下载链接下载文件
@files_router.get("/download/{token}")
async def file_download_files(request: Request, token: str, session=Depends(auth_login)):
    old_session = session_db.get(token)  # 有效session中没有
    if old_session is None:
        session_model.delete_session_by_token(token)
        return JSONResponse(content={'message': '链接已失效', 'code': 1, 'data': False})
    old_session = json.loads(old_session)
    '''
    is_private = judge_private_file(old_session['file_id'],old_session['user_id'])
    if is_private:
        if session['user_id'] != old_session['user_id']:
            return JSONResponse(content={'message': '您没有使用该链接的权限', 'code': 2, 'data': False})
    '''
    if old_session['use'] != old_session['use_limit']:  # 查看下载链接是否还有下载次数
        if old_session['use'] + 1 == old_session['use_limit']:  # 在下一次就失效
            session_model.delete_session_by_token(token)
            session_db.delete(token)
        else:
            session_model.update_session_use_by_token(token, 1)  # 将该session使用次数加1
            old_session['use'] = old_session['use'] + 1
            session_db.set(token,json.dumps(old_session),ex=21600)
        user_file = user_file_model.get_user_file_by_id(old_session['file_id'])
        file = file_model.get_file_by_id(user_file.file_id)
        pre_folder =  file.hash_md5[:8] + '/' + file.hash_sha256[-8:]
        folder = pre_folder + '/' + user_file.name  # 先找到路径
        # private_key = RSA_model.get_private_key_by_user_id(session['user_id'])
        # decrypted_content = decrypt_file(folder,private_key[0].encode('utf-8'))
        filename = user_file.name
        parameters = await make_parameters(request)
        username = get_user_name(session['user_id'])
        if old_session['use_limit'] == -1:
            data = get_files(folder)
            encoded_filename = quote(filename)
            headers = {
                "Content-Type":user_file.type,
                "Content-Disposition": f"inline; filename={encoded_filename}"
            }
            add_operation.delay(8, old_session['file_id'], '预览文件',f'用户{username}于qpzm7913预览了一个名为{user_file.name}的文件', parameters, old_session['user_id'])
            return StreamingResponse(data, headers=headers)
        else:
            content = get_files(folder)
            add_operation.delay(8, old_session['file_id'], '下载文件',f'用户{username}于qpzm791下载了一个名为{user_file.name}的文件', parameters, old_session['user_id'])
            encoded_filename = quote(user_file.name, safe='')
            return StreamingResponse(content, media_type=user_file.type,headers={
                    "Content-Disposition": f'attachment; filename="{encoded_filename}"'
                })
    return JSONResponse(content={'message': '链接已失效', 'code': 1, 'data': False})


# 文件预览,用户查看所有他可以进行下载的文件(目前是所有他上传的文件)
@files_router.get("/preview")
@page_response
async def file_preview(request: Request, pageNow: int, pageSize: int, session=Depends(auth_login)):
    Page = page(pageSize=pageSize, pageNow=pageNow)
    all_file = user_file_model.get_user_file_by_admin(Page, session['user_id'])  # 以分页形式返回
    result = {"rows": None}
    if all_file != []:
        file_data = []
        for file in all_file:  # 遍历查询结果
            if file.video_time is not None:
                temp = user_file_interface(file_id=file.file_id, video_time=file.video_time, user_id=file.user_id)
            else:
                temp = user_file_interface(file_id=file.file_id, user_id=file.user_id)
            temp_dict = temp.model_dump()  # 查询出来的结果转字典
            temp_dict['user_name'] = user_model.get_user_by_user_id(session['user_id']).username  # 查出name
            file_data.append(temp_dict)
        result = makePageResult(Page, len(all_file), file_data)
    parameters = await make_parameters(request)
    username = get_user_name(session['user_id'])
    add_operation.delay(8, session['user_id'], '查看文件',
                        f'用户{username}于qpzm7913查看了他能下载的所有文件', parameters,
                        session['user_id'])
    return {'message': '可下载文件如下', "data": result, 'code': 0}
