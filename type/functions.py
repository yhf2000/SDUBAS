import copy
import datetime
import io
import json
import random
import time
import uuid
from docx import Document
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from fastapi import Request

from model.db import session_db, url_db
from service.file import UserFileModel, FileModel
from service.permissions import permissionModel
from service.user import SessionModel
from type.user import parameters_interface, session_interface

session_model = SessionModel()
user_file_model = UserFileModel()
file_model = FileModel()


async def make_parameters(request: Request):  # 生成操作表里的parameters
    url = request.url.path
    path = request.path_params
    para = ''
    body = ''
    if request.method == "GET":
        para = dict(request.query_params)
        if para == {}:
            para = ''
            if path != {}:
                para = path
        else:
            if path != {}:
                para.update(path)
    else:
        try:
            body = await request.body()
            if body == b'':
                body = ''
                if path != {}:
                    body = path
            else:
                body_str = body.decode('utf-8')  # 解码为字符串
                body = json.loads(body_str)
                if path != {}:
                    body.update(path)
        except Exception as e:
            body = ''
    parameters = parameters_interface(url='http://127.0.0.1:8000' + url, para=para, body=body)
    return json.dumps(parameters.__dict__, ensure_ascii=False)


def get_user_id(request: Request):  # 获取user_id
    token = request.cookies.get("SESSION")
    session = session_db.get(token)  # 有效session中没有
    if session is not None:
        return json.loads(session)['user_id']  # 登陆了就返回用户登录的session
    else:
        return session_model.get_user_id_by_token(token)[0]


def make_download_session(token, request, user_id, file_id, use_limit, hours):
    #  通过权限认证，判断是永久下载地址还是临时下载地址
    exp_dt = (datetime.datetime.now() + datetime.timedelta(hours=hours))
    new_session = session_interface(user_id=user_id, file_id=file_id, token=token,
                                    ip=request.client.host,
                                    func_type=2, user_agent=request.headers.get("user-agent"), use_limit=use_limit,
                                    exp_dt=exp_dt)  # 生成新session
    return new_session


def get_url(new_session, new_token):
    new_session.exp_dt = time.strptime(new_session.exp_dt.strftime(
        "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")  # 将datetime转化为字符串以便转为json
    new_session.create_dt = time.strptime(new_session.create_dt.strftime(
        "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")  # 将datetime转化为字符串以便转为json
    user_session = json.dumps(new_session.model_dump())
    session_db.set(new_token, user_session, ex=3600 * 72)  # 缓存有效session(时效72h)
    url = 'http://127.0.0.1:8000/files/download/' + new_token
    return url


def get_url_by_user_file_id(request, id_list):   # 得到下载链接
    user_file = user_file_model.get_user_file_id_by_id_list(id_list)
    urls = dict()
    if user_file is None:
        urls.update({id_list: None})
    else:
        if type(id_list) == int:
            if user_file[1] is None:
                urls.update({id_list: None})
            else:
                url = url_db.get(id_list)
                if url is not None:  # 有效url中有
                    urls.update({id_list: url.decode('utf-8')})
                else:
                    new_token = str(uuid.uuid4().hex)  # 生成token
                    new_session = make_download_session(new_token, request, user_file[1], id_list, 408, 72)
                    session_model.add_session(new_session)
                    url = get_url(new_session, new_token)
                    url_db.set(id_list, url)
                    urls.update({id_list: url})
        else:
            sessions = []
            for i in range(len(user_file)):
                if user_file[i][1] is None:
                    urls.update({id_list[i]: None})
                else:
                    url = url_db.get(id_list[i])
                    if url is not None:  # 有效url中有
                        urls.update({id_list[i]: url.decode('utf-8')})
                    else:
                        new_token = str(uuid.uuid4().hex)  # 生成token
                        new_session = make_download_session(new_token, request, user_file[i][1], id_list[i], 408, 72)
                        temp = copy.deepcopy(new_session)
                        sessions.append(temp)
                        url = get_url(new_session, new_token)
                        url_db.set(id_list[i], url)
                        urls.update({id_list[i]: url})
            if len(sessions) == 1:
                session_model.add_session(sessions[0])
            else:
                session_model.add_all_session(sessions)
            for i in range(len(id_list)):
                if id_list[i] not in urls.keys():
                    urls.update({id_list[i]: None})
    return urls


def get_locate_url_by_user_file_id(id_list):  # 得到本地路由
    urls = dict()
    file = file_model.get_file_by_user_file_id(id_list)
    if file is None:
        urls.update({id_list: None})
    else:
        if type(id_list) == int:
            url = "files" + '/' + file[0][:8] + '/' + file[1][-8:] + '/' + file[3]  # 找到路径
            urls.update({id_list: url})
        else:
            for i in range(len(file)):
                url = "files" + '/' + file[i][0][:8] + '/' + file[i][1][-8:] + '/' + file[i][3]  # 找到路径
                urls.update({file[i][2]: url})
            for i in range(len(id_list)):
                if id_list[i] not in urls.keys():
                    urls.update({id_list[i]: None})
    return urls
def search_son_user(request: Request):
    db = permissionModel()
    user_id = get_user_id(request)
    role_list = db.search_role_by_user(user_id)
    user_list = db.search_user_by_role(role_list)
    return user_list


def get_email_token():  # 生成email的验证码
    email_token = ''
    for i in range(6):
        email_token += str(random.randint(0, 9))  # 生成六位随机验证码
    return email_token


def get_video_time(user_file_id):  # 获取视频时间
    return user_file_model.get_video_time_by_id(user_file_id)[0]
def generate_rsa_key_pair():   # 获得一对公钥和私钥
    # 生成RSA私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    # 生成RSA公钥
    public_key = private_key.public_key()
    # 导出私钥和公钥到PEM格式
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    # 返回私钥和公钥的PEM格式字符串
    return private_pem, public_pem


def decrypt_file(file, private_key_pem):  # 使用私钥解密文件内容
    # 加载私钥
    with open(file, 'rb') as file:
        encrypted_content = file.read()
    private_key = serialization.load_pem_private_key(private_key_pem, password=None, backend=default_backend())
    # 使用私钥解密文件内容
    decrypted_content = private_key.decrypt(
        encrypted_content,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_content


def encrypt_file(file_content, public_key_pem):    #  加密文件（只能加密txt,其他类型需特殊处理）
    # 读取文件内容
    # 加载公钥
    public_key = serialization.load_pem_public_key(public_key_pem, backend=default_backend())

    # 使用公钥加密文件内容
    encrypted_content = public_key.encrypt(
        file_content,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return encrypted_content


def convert_word_to_bytes(file_path):
    doc = Document(file_path)
    # 将 Word 文档保存到内存中的字节流
    in_memory_file = io.BytesIO()
    doc.save(in_memory_file)
    in_memory_file.seek(0)
    # 读取字节流数据
    binary_data = in_memory_file.read()
    in_memory_file.close()
    return binary_data