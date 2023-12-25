import asyncio
import base64
import copy
import io
import json
import os
import random
import re
import time
import uuid
import requests
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import unpad
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Request, HTTPException
from minio import S3Error

from starlette.responses import JSONResponse
from const import base_url, server_ip
from model.db import session_db, url_db, user_information_db, minio_client, block_chain_db
from service.file import UserFileModel, FileModel, RSAModel
from service.permissions import permissionModel
from service.user import SessionModel, UserModel, UserinfoModel, EducationProgramModel, OperationModel
from type.user import parameters_interface, session_interface

session_model = SessionModel()
user_file_model = UserFileModel()
file_model = FileModel()
user_model = UserModel()
user_info_model = UserinfoModel()
education_program_model = EducationProgramModel()
operation_model = OperationModel()
RSA_model = RSAModel()
mimetype_to_format = {
    'image/jpeg': 'image',
    'image/png': 'image',
    'audio/mpeg': 'MP3',
    'application/msword': 'office_word',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'office_word',
    'application/vnd.ms-powerpoint': 'office_word',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'office_word',
    'video/mp4': 'video',
    'video/mpeg': 'video',
    'video/quicktime': 'video',
    'video/x-msvideo': 'video',
    'video/x-flv': 'video',
    'video/webm': 'video',
    'video/x-ms-wmv': 'video',
    'video/x-matroska': 'video',
    'video/3gpp': 'video',
    'video/x-ms-asf': 'video',
    'video/x-m4v': 'video',
    'video/x-mng': 'video',
    'video/ogg': 'video',
    'video/vnd.rn-realvideo': 'video'
}

server_id_to_ip = {
    1: '111.15.182.56:41011',
    2: '111.15.182.56:41012',
    3: '111.15.182.56:41013',
    4: '111.15.182.56:41014',
    5: '111.15.182.56:41015',
    6: '111.15.182.56:41016',
    7: '111.15.182.56:41017',
    8: '111.15.182.56:41018',
    9: '111.15.182.56:41019',
    10: '111.15.182.56:41020',
    11: '43.138.34.119'
}


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
    parameters = parameters_interface(url=f'http://{server_ip}' + url, para=para, body=body)
    return parameters.__dict__


def get_user_name(user_id):
    return user_model.get_user_name_by_user_id(user_id)[0]


def get_user_id(request: Request):  # 获取user_id
    token = request.cookies.get("SESSION")
    session = session_db.get(token)  # 有效session中没有
    if session is not None:
        return json.loads(session)['user_id']  # 登陆了就返回用户登录的session
    else:
        session_model.delete_session_by_token(token)
        return session_model.get_user_id_by_token(token)[0]


def make_download_session(token, request, user_id, file_id, use_limit, hours):
    #  通过权限认证，判断是永久下载地址还是临时下载地址
    new_session = session_interface(user_id=user_id, file_id=file_id, token=token,
                                    ip=request.client.host,
                                    func_type=2, user_agent=request.headers.get("user-agent"), use_limit=use_limit,
                                    exp_dt=get_time_now('hours', hours))  # 生成新session
    return new_session


def get_url(new_session, new_token, use_file_id):
    user_session = json.dumps(new_session.model_dump())
    session_db.set(new_token, user_session, ex=3600 * 72)  # 缓存有效session(时效72h)
    server_id = file_model.get_server_id_by_user_file_id(use_file_id)[0]
    url = f'http://{server_id_to_ip[server_id]}/api/files/download/' + new_token
    return url


def get_url_by_user_file_id(request, id_list):  # 得到下载链接
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
                    urls.update({id_list: json.loads(url)})
                else:
                    new_token = str(uuid.uuid4().hex)  # 生成token
                    new_session = make_download_session(new_token, request, user_file[1], id_list, -1, 72)
                    session_model.add_session(new_session)
                    url = get_url(new_session, new_token, id_list)
                    types = user_file[2]
                    if user_file[2] in mimetype_to_format:
                        types = mimetype_to_format[user_file[2]]
                    temp = dict({"url": url, "file_type": types, "file_name": user_file[3]})
                    url_db.set(id_list, json.dumps(temp))
                    urls.update({id_list: temp})
        else:
            sessions = []
            for i in range(len(user_file)):
                url = url_db.get(user_file[i][0])
                if url is not None:  # 有效url中有
                    urls.update({user_file[i][0]: json.loads(url)})
                else:
                    new_token = str(uuid.uuid4().hex)  # 生成token
                    new_session = make_download_session(new_token, request, user_file[i][1], user_file[i][0], -1, 72)
                    temp = copy.deepcopy(new_session)
                    sessions.append(temp)
                    url = get_url(new_session, new_token, user_file[i][0])
                    types = user_file[i][2]
                    if user_file[i][2] in mimetype_to_format:
                        types = mimetype_to_format[user_file[i][2]]
                    temp = dict({"url": url, "file_type": types, "file_name": user_file[i][3]})
                    url_db.set(user_file[i][0], json.dumps(temp))
                    urls[user_file[i][0]] = temp
            if len(sessions) == 1:
                session_model.add_session(sessions[0])
            else:
                session_model.add_all_session(sessions)
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
    time = user_file_model.get_video_time_by_id(user_file_id)
    return time[0] if time is not None else None


def generate_rsa_key_pair():  # 获得一对公钥和私钥
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


def decrypt_aes_key_with_rsa(encrypted_aes_key, private_key):  # 使用私钥解密AES密钥
    rsakey = RSA.importKey(private_key)  # 导入私钥
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    text = cipher.decrypt(base64.b64decode(encrypted_aes_key), None)
    return text


class DeAesCrypt:
    """
    AES-128-CBC解密
    """

    def __init__(self, data, key, pad='zero'):
        """
        :param data: 加密后的字符串
        :param key: 随机的16位字符
        :param pad: 填充方式
        """
        self.key = key
        self.data = data
        self.pad = pad.lower()

    def decrypt_aes(self):
        """AES-128-CBC解密"""
        real_data = base64.b64decode(self.data)
        my_aes = AES.new(self.key, AES.MODE_ECB)
        decrypt_data = my_aes.decrypt(real_data)
        decrypted_data = unpad(decrypt_data, 16)
        return decrypt_data

    def get_str(self, bd):
        """解密后的数据去除加密前添加的数据"""
        if self.pad == "zero":  # 去掉数据在转化前不足16位长度时添加的ASCII码为0编号的二进制字符
            return ''.join([chr(i) for i in bd if i != 0])

        elif self.pad == "pkcs7":  # 去掉pkcs7模式中添加后面的字符
            return ''.join([chr(i) for i in bd if i > 32])

        else:
            return "不存在此种数据填充方式"


def get_user_information(user_id):  # 根据user_id查询用户基本信息
    user_information = user_information_db.get(user_id)  # 缓存中中没有
    if user_information is None:
        information = user_model.get_user_all_information_by_user_id(user_id)
        res = dict({'username': information[0], 'email': information[1], 'oj_username': information[2], 'oj_bind': 0})
        user_information_db.set(user_id, json.dumps(res), ex=1209600)
    else:
        res = json.loads(user_information)
    return res


programs_translation = {
    "思想政治理论课": "thought_political_theory",
    "大学体育": "college_sports",
    "大学英语": "college_english",
    "国学修养": "chinese_culture",
    "艺术审美": "art_aesthetics",
    "创新创业": "innovation_entrepreneurship",
    "人文学科": "humanities",
    "社会科学": "social_sciences",
    "科学素养": "scientific_literacy",
    "信息技术": "information_technology",
    "通识教育选修课程": "general_education_elective",
    "专业必修课程": "major_compulsory_courses",
    "专业选修课程": "major_elective_courses",
    "重点提升必修课程": "key_improvement_courses",
    "齐鲁创业": "qilu_entrepreneurship",
    "稷下创新": "jixia_innovation"
}


def get_education_programs(user_id):  # 根据用户id查询培养方案的内容
    programs = education_program_model.get_education_program_by_user_id(user_id)
    if programs is not None:
        programs.pop('major_id')
        programs.pop('id')
        programs.pop('has_delete')
    return programs


def get_files(object_key):  # 根据桶名称与文件名从Minio上下载文件
    try:
        object_data = minio_client.get_object('main', object_key)
        content = io.BytesIO(object_data.read())
        return content
    except S3Error as e:
        return JSONResponse(content={'message': e, 'code': 3, 'data': False})


def extract_word_between(text, word1, word2):  # 提取出两单词间的单词
    pattern = r'{}(.*?){}'.format(re.escape(word1), re.escape(word2))
    matches = re.findall(pattern, text)
    return matches


def get_time_now(unit="seconds", value=0):
    current_timestamp = int(time.time())
    if unit == "seconds":
        new_timestamp = current_timestamp + value
    elif unit == "minutes":
        new_timestamp = current_timestamp + (value * 60)
    elif unit == "hours":
        new_timestamp = current_timestamp + (value * 3600)
    elif unit == "days":
        new_timestamp = current_timestamp + (value * 86400)
    else:
        raise ValueError("Unsupported time unit")
    return new_timestamp


def block_chains_login():
    username = 'admin'
    password = 'admin'
    response = requests.post(f"{base_url}/api/auth/user/current/")
    token = None
    if response.status_code == 200:
        token = block_chain_db.get(get_server_info())  # 从缓存中得到token
        if token is not None:
            token = token.decode('utf-8')
    if response.status_code != 200 or token is None:
        user_info = {
            "username": username,
            "password": password
        }
        response = requests.post(f"{base_url}/api/auth/login/token/", json=user_info)
        if response.status_code == 200:
            data = response.json()
            token = data['data']['token']
            block_chain_db.set(get_server_info(), token, ex=12096000)  # 缓存有效session
        else:
            raise HTTPException(
                status_code=404,
                detail="登录失败",
            )
    headers = {
        "Authorization": f"Token 228358886993fb99d2afabdec74f139dcc872eea"
    }
    return headers


def block_chains_upload(tx_hash, optional_message, headers):
    data = {
        "tx_hash": tx_hash,
        "optional_message": optional_message
    }
    response = requests.post(f"{base_url}/api/chain/logmanager/create/", json=data, headers=headers)  # 执行上链操作
    if response.status_code == 200:
        data = response.json()
        if data['data'] is None:
            raise HTTPException(
                status_code=404,
                detail="数据已在链上",
            )
        receipt = data['data']['receipt']
    print(response.json())
    return receipt


async def block_chains_judge_complete(receipt, headers):
    receipts = {
        "receipt": receipt
    }
    while True:
        response = requests.post(f"{base_url}/api/chain/smartcontract/receipt/", json=receipts, headers=headers)
        if response.status_code == 200:
            data = response.json().get('data')
            if data is not None:
                break
        else:
            raise HTTPException(
                status_code=404,
                detail="上链失败",
            )
        await asyncio.sleep(0.2)  # 等待0.2秒后再继续检查


def block_chains_get(tx_hash, headers):
    txhash = {
        "tx_hash": tx_hash
    }
    response = requests.post(f"{base_url}/api/chain/logmanager/get/", json=txhash, headers=headers)  # 查询在链上的数据
    if response.status_code == 200:
        data = response.json()
        on_chain = data['data']
        return on_chain


def block_chains_information(headers, oj_headers):
    response = requests.post(f"{base_url}/api/chain/tendermint/status/", headers=headers)  # 查询区块链基本信息
    if response.status_code == 200:
        data = response.json()
        chain_information = data['data']
        results = {}
        if chain_information:
            results['id'] = chain_information['status']['node_info']['id']
            results['latest_block_height'] = chain_information['status']['sync_info']['latest_block_height']
            results['latest_block_time'] = chain_information['status']['sync_info']['latest_block_time']
            results['address'] = chain_information['status']['validator_info']['address']
            results['earliest_block_time'] = chain_information['status']['sync_info']['earliest_block_time']
            results['num_cnt'] = get_user_num(oj_headers)
            results['deal_cnt'] = get_operation_num() + 12345
            return results
    else:
        raise HTTPException(
            status_code=404,
            detail="获取区块链信息失败",
        )


def get_server_info():
    host_ip = os.environ.get("host_ip")
    return host_ip


def get_user_num(oj_headers):
    try_num = 3
    while try_num >= 0:
        try_num -= 1
        try:
            response = requests.get(f"https://43.143.149.67:7359/api/manage/user/list?pageNow=1&pageSize=1",
                                    verify=False,
                                    headers=oj_headers)
            break
        except Exception as e:
            time.sleep(0.5)
    return response.json()['data']['totalNum']


def get_operation_num():
    return operation_model.get_operation_num()


def oj_bind_func(username, password):
    private_key = RSA_model.get_private_key_by_user_id(1)[0]
    user_info = {
        "username": username,
        "password": decrypt_aes_key_with_rsa(password, private_key)
    }
    response = requests.post(f"https://43.143.149.67:7359/api/user/login", json=user_info, verify=False)
    if response.status_code == 200:
        data = response.headers
        token = data['Set-Cookie'].split(';')[0]
        headers = {
            "Cookie": token
        }
    else:
        raise HTTPException(
            status_code=404,
            detail="登录失败",
        )
    return headers
