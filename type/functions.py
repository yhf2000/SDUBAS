import copy
import datetime
import io
import json
import random
import re
import uuid

from Crypto.Cipher import AES
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Request
from minio import S3Error
from starlette.responses import JSONResponse

from model.db import session_db, url_db, user_information_db, minio_client
from service.file import UserFileModel, FileModel
from service.permissions import permissionModel
from service.user import SessionModel, UserModel, UserinfoModel, EducationProgramModel
from type.user import parameters_interface, session_interface

session_model = SessionModel()
user_file_model = UserFileModel()
file_model = FileModel()
user_model = UserModel()
user_info_model = UserinfoModel()
education_program_model = EducationProgramModel()


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
    exp_dt = (datetime.datetime.now() + datetime.timedelta(hours=hours))
    new_session = session_interface(user_id=user_id, file_id=file_id, token=token,
                                    ip=request.client.host,
                                    func_type=2, user_agent=request.headers.get("user-agent"), use_limit=use_limit,
                                    exp_dt=exp_dt)  # 生成新session
    return new_session


def get_url(new_session, new_token):
    new_session.exp_dt = new_session.exp_dt.strftime("%Y-%m-%d %H:%M:%S")  # 将datetime转化为字符串以便转为json
    user_session = json.dumps(new_session.model_dump())
    session_db.set(new_token, user_session, ex=3600 * 72)  # 缓存有效session(时效72h)
    url = 'http://127.0.0.1:8000/files/download/' + new_token
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
                    url = get_url(new_session, new_token)
                    temp = dict({"url": url, "file_type": user_file[2]})
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
                    url = get_url(new_session, new_token)
                    temp = dict({"url": url, "file_type": user_file[i][2]})
                    url_db.set(user_file[i][0], json.dumps(temp))
                    urls.update({user_file[i][0]: json.dumps(temp)})
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
    return user_file_model.get_video_time_by_id(user_file_id)[0]


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


def decrypt_aes_key_with_rsa(encrypted_aes_key: bytes, private_key_pem: bytes):  # 使用私钥解密AES密钥
    private_key = serialization.load_pem_private_key(private_key_pem, password=None, backend=default_backend())
    decrypted_aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_aes_key


def decrypt_file(file_path: str, encrypt_aes_key: bytes, private_key: bytes) -> bytes:  # 解密文件
    aes_key = decrypt_aes_key_with_rsa(encrypt_aes_key, private_key)
    with open(file_path, 'rb') as file:
        nonce = file.read(16)
        tag = file.read(16)
        encrypted_data = file.read()
    aes_cipher = AES.new(aes_key, AES.MODE_EAX, nonce)
    decrypted_data = aes_cipher.decrypt_and_verify(encrypted_data, tag)
    return decrypted_data


def get_user_information(user_id):  # 根据user_id查询用户基本信息
    user_information = user_information_db.get(user_id)  # 缓存中中没有
    if user_information is None:
        information = user_model.get_user_all_information_by_user_id(user_id)
        res = dict({'username': information[0], 'email': information[1], 'card_id': information[2],
                    'registration_dt': information[3], 'realname': information[4], 'gender': information[5],
                    'school_name': information[6], 'college_name': information[7], 'major_name': information[8],
                    'class_name': information[9], 'enrollment_dt': information[10], 'graduation_dt': information[11]})
        res['registration_dt'] = res['registration_dt'].strftime("%Y-%m-%d %H:%M:%S")
        res['enrollment_dt'] = res['enrollment_dt'].strftime("%Y-%m-%d")
        res['graduation_dt'] = res['graduation_dt'].strftime("%Y-%m-%d")
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


'''
def judge_private_file(user_file_id,user_id):   # 判断某个文件是否是该用户的私有文件
    return project_service_model.judge_private_file(user_id,user_file_id)
'''
