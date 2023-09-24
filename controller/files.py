import datetime
import json
import os
import time
import uuid
from urllib.parse import quote

from docx2pdf import convert
import docx
from docx import Document
from fastapi import APIRouter
from fastapi import File, UploadFile
from fastapi import Request, Header, Depends
from starlette.responses import FileResponse, JSONResponse, StreamingResponse
from Celery.add_operation import add_operation
from model.db import session_db
from service.file import FileModel, UserFileModel, RSAModel
from service.user import UserModel, SessionModel
from type.file import file_interface, user_file_interface, RSA_interface, user_file_all_interface
from type.page import page
from type.user import session_interface
from type.functions import make_parameters, generate_rsa_key_pair, decrypt_file, encrypt_file, remove_extension, \
    find_files_with_name_and_extension, ppt_to_pdf
from utils.auth_login import auth_login
from utils.response import user_standard_response, page_response, makePageResult

files_router = APIRouter()
file_model = FileModel()
user_file_model = UserFileModel()
session_model = SessionModel()
user_model = UserModel()
RSA_model = RSAModel()


# 文件存在验证，在上传文件之前先上传size和两个hash来判断文件是否存在：若文件存在则返回id，不存在则在cookie设置一个token
@files_router.post("/upload/valid")
@user_standard_response
async def file_upload_valid(request: Request, file: file_interface, user_agent: str = Header(None),
                            session=Depends(auth_login)):
    global user_file_id
    id = file_model.get_file_by_hash(file)  # 查询文件是否存在
    '''
    public_key = RSA_model.get_public_key_by_user_id(session['user_id'])
    if public_key is None:
        private_pem, public_pem = generate_rsa_key_pair()
        new_rsa= RSA_interface(private_key_pem = private_pem,public_key_pem=public_pem,user_id = session['user_id'])
        public_key = RSA_model.add_user_RSA(new_rsa)
    else:
        if public_key[1] < datetime.datetime.now():
            RSA_model.delete_user_RSA(session['user_id'])
        public_key = public_key[0]'''
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
        return {'message': '文件不存在', 'data': {'file_id': None, 'public_key': None}, 'token_header': new_token,
                'code': 0}
    else:  # 有该file
        user_file_id = user_file_model.get_user_file_id_by_file_id(id[0])[0]
        return {'message': '文件存在', 'data': {'file_id': user_file_id, 'public_key': None}, 'code': 0}


# 上传文件。文件存储位置：files/hash_md5前八位/hash_sha256的后八位/文件名
@files_router.post("/upload")
@user_standard_response
async def file_upload(request: Request, file: UploadFile = File(...), session=Depends(auth_login)):
    token = request.cookies.get("TOKEN")
    old_session = session_db.get(token)  # 有效session中没有，即session过期了
    if old_session is None:
        session_model.delete_session_by_token(token)
        return {'message': 'token已失效，请重新上传', 'data': None, 'code': 1}
    old_session = json.loads(old_session)
    id = user_file_model.get_user_file_by_file_name(file.filename)  # 查看文件名是否存在
    if id is not None:
        return {'message': '文件名已存在，请修改后重新上传', 'data': None, 'code': 2}
    contents = await file.read()
    file_id = user_file_model.get_file_id_by_id(old_session['file_id'])[0]
    get_file = file_model.get_file_by_id(file_id)
    folder = "files" + '/' + get_file.hash_md5[:8] + '/' + get_file.hash_sha256[-8:] + '/'  # 先创建文件夹
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(folder + file.filename,
              "wb") as f:  # 取hash_md5前八位与hash_sha256的后八位
        f.write(contents)  # 将获取的fileb文件内容，写入到新文件中
    session_model.update_session_use_by_token(token, 1)  # 将该session使用次数设为1
    session_model.delete_session_by_token(token)  # 将该session设为已失效
    session_db.delete(token)  # 将缓存删掉
    user_file_model.update_user_file_name_type(old_session['file_id'], file.filename,
                                               file.content_type)  # 添加一条user_file的记录
    file_model.update_file_is_save(file_id)  # 更新为已上传
    parameters = await make_parameters(request)
    add_operation.delay(8, old_session['file_id'], '用户上传了一个文件', parameters, old_session['user_id'])
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
    #  通过权限认证，判断是永久下载地址还是临时下载地址
    use_limit = 1
    exp_dt = (datetime.datetime.now() + datetime.timedelta(hours=6))
    #  通过权限认证，获取该session使用限制次数与过期时间
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
    if session['user_id'] != old_session['user_id']:
        return JSONResponse(content={'message': '您没有使用该链接的权限', 'code': 2, 'data': False})
    if old_session['use'] != old_session['use_limit']:  # 查看下载链接是否还有下载次数
        if old_session['use'] + 1 == old_session['use_limit']:  # 在下一次就失效
            session_model.delete_session_by_token(token)
            session_db.delete(token)
        else:
            session_model.update_session_use_by_token(token, 1)  # 将该session使用次数加1
        user_file = user_file_model.get_user_file_by_id(old_session['file_id'])
        file = file_model.get_file_by_id(user_file.file_id)
        pre_folder = "files" + '/' + file.hash_md5[:8] + '/' + file.hash_sha256[-8:]
        folder = pre_folder + '/' + user_file.name  # 先找到路径
        # private_key = RSA_model.get_private_key_by_user_id(session['user_id'])
        # decrypted_content = decrypt_file(folder,private_key[0].encode('utf-8'))
        filename = user_file.name
        if old_session['use_limit'] == -1:
            if user_file.type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' or user_file.type == 'application/msword':  # word转pdf
                file_name_without_extension = remove_extension(user_file.name)  # 除去后缀的文件名
                matching_files = find_files_with_name_and_extension(pre_folder, file_name_without_extension, 'pdf')
                filename = file_name_without_extension + '.pdf'
                if matching_files:  # 找到了匹配的文件
                    folder = matching_files[0]
                else:
                    word_file = folder
                    pdf_file = pre_folder + '/' + file_name_without_extension + '.pdf'
                    # 调用 convert 函数进行转换
                    new_file = user_file_all_interface(user_id=session['user_id'], file_id=user_file.file_id,
                                                       name=file_name_without_extension + '.pdf',
                                                       type='application/pdf')
                    user_file_model.add_user_file_all(new_file)
                    folder = pdf_file
                    convert(word_file, pdf_file)
                user_file.type = 'application/pdf'
            elif user_file.type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation' or user_file.type == 'application/vnd.ms-powerpoint':  # ppt转pdf
                file_name_without_extension = remove_extension(user_file.name)  # 除去后缀的文件名
                matching_files = find_files_with_name_and_extension(pre_folder, file_name_without_extension, 'pdf')
                filename = file_name_without_extension + '.pdf'
                if matching_files:  # 找到了匹配的文件
                    folder = matching_files[0]
                else:
                    current_path = __file__.replace("\\",
                                                    "/") + '/' + '..' + '/' + '..' + '/' + pre_folder  # 要获取全局路径！！！
                    ppt_file = current_path + '/' + user_file.name
                    pdf_file = current_path + '/' + filename
                    new_file = user_file_all_interface(user_id=session['user_id'], file_id=user_file.file_id,
                                                       name=file_name_without_extension + '.pdf',
                                                       type='application/pdf')
                    user_file_model.add_user_file_all(new_file)
                    folder = pdf_file
                    ppt_to_pdf(ppt_file, pdf_file)
                user_file.type = 'application/pdf'
            encoded_filename = quote(filename)
            headers = {
                "Content-Type": user_file.type,
                "Content-Disposition": f"inline; filename={encoded_filename}"
            }
            parameters = await make_parameters(request)
            add_operation.delay(8, old_session['file_id'], '用户预览了一个文件', parameters, old_session['user_id'])
            return FileResponse(folder, filename=filename, headers=headers)
            # return FileResponse(decrypted_content,headers=headers)
        else:
            parameters = await make_parameters(request)
            add_operation.delay(8, old_session['file_id'], '用户下载了一个文件', parameters, old_session['user_id'])
            '''
            headers = {
                "Content-Disposition": "attachment; filename="+user_file.name
            }
            def file_generator():
                yield decrypted_content
            return StreamingResponse(file_generator(), media_type="application/octet-stream",headers=headers)'''
            return FileResponse(folder, filename=user_file.name)
    return JSONResponse(content={'message': '链接已失效', 'code': 1, 'data': False})


# 文件预览,用户查看所有他可以进行下载的文件(目前是所有他上传的文件)
@files_router.get("/preview")
@page_response
async def file_preview(request: Request, pageNow: int, pageSize: int, session=Depends(auth_login)):
    Page = page(pageSize=pageSize, pageNow=pageNow)
    all_file = user_file_model.get_user_file_by_admin(Page, session['user_id'])  # 以分页形式返回
    result = {"rows": None}
    parameters = await make_parameters(request)
    add_operation.delay(8, session['user_id'], '用户查看他能下载的文件', parameters, session['user_id'])
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
    return {'message': '可下载文件如下', "data": result, 'code': 0}


'''
current_directory = os.path.dirname(os.path.abspath(__file__))
# 构建目标文件的绝对路径
target_directory = os.path.join(current_directory, '..', 'files/2/2/')
target_file_path = os.path.join(target_directory, '2023年奖学金、奖教金评选标准（华为建议）.docx')
doc = docx.Document(target_file_path)
file_content = b""
for paragraph in doc.paragraphs:
        file_content += paragraph.text.encode("utf-8")
pub = RSA_model.get_public_key_by_user_id(1)
e_cotents = encrypt_file(file_content, pub[0].encode('utf-8'))
with open(target_file_path, 'wb') as decrypted_file:
    decrypted_file.write(e_cotents)'''
