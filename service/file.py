from fastapi.encoders import jsonable_encoder

from model.db import dbSession
from model.file import File, User_File, RSAKeys, ASEKey
from type.file import file_interface, user_file_interface, RSA_interface, user_file_all_interface, ASE_interface


class FileModel(dbSession):
    def add_file(self, obj: file_interface):  # 用户上传文件(在file表中添加一个记录)
        obj_dict = jsonable_encoder(obj)
        obj_dict.pop('time')
        obj_dict.pop('type')
        obj_add = File(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            return obj_add.id

    def delete_file(self, id: int):  # 删除一个文件
        with self.get_db() as session:
            session.query(File).filter(File.id == id).update({"has_delete": 1})
            session.commit()
            return id

    def get_file_by_hash(self, obj: file_interface):  # 根据size与两个hash查询file的id
        with self.get_db() as session:
            id = session.query(File.id, File.is_save).filter(
                File.has_delete == 0,
                File.size == obj.size,
                File.hash_md5 == obj.hash_md5,
                File.hash_sha256 == obj.hash_sha256).first()
            session.commit()
            return id

    def update_file_is_save(self, id: int):  # 更改文件上传状态
        with self.get_db() as session:
            session.query(File).filter(File.id == id).update({"is_save": 1})
            session.commit()
            return id

    def get_file_by_id(self, id):  # 根据id查询file的基本信息
        with self.get_db() as session:
            file = session.query(File).filter(File.id == id, File.has_delete == 0).first()
            session.commit()
            return file

    def get_file_by_user_file_id(self, user_file_id_list):  # 根据user_file_id_list查询file的基本信息
        with self.get_db() as session:
            if type(user_file_id_list) is list:
                file = session.query(File.hash_md5, File.hash_sha256, User_File.id,
                                     User_File.name).outerjoin(User_File, User_File.file_id == File.id).filter(
                    User_File.id.in_(user_file_id_list),
                    File.has_delete == 0
                ).all()
            else:
                file = session.query(File.hash_md5, File.hash_sha256, User_File.id,
                                     User_File.name).outerjoin(User_File,
                                                               User_File.file_id == File.id).filter(
                    User_File.id == user_file_id_list,
                    File.has_delete == 0
                ).first()
            session.commit()
            return file


class UserFileModel(dbSession):
    def add_user_file(self, obj: user_file_interface):  # 用户上传文件(在user_file表中添加一个记录)（不完全版）
        obj_dict = jsonable_encoder(obj)
        obj_add = User_File(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            return obj_add.id

    def add_user_file_all(self, obj: user_file_all_interface):  # 用户上传文件(在user_file表中添加一个记录)(完全版)
        obj_dict = jsonable_encoder(obj)
        obj_add = User_File(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            return obj_add.id

    def delete_user_file(self, id: int):  # 删除一个文件
        with self.get_db() as session:
            session.query(User_File).filter(User_File.id == id).update({"has_delete": 1})
            session.commit()
            return id

    def update_user_file_name(self, id: int, name: str):  # 更改文件名
        with self.get_db() as session:
            session.query(User_File).filter(User_File.id == id).update({"name": name})
            session.commit()
            return id

    def update_user_file_name_type(self, id: int, name: str, type: str):  # 更改文件名与type
        with self.get_db() as session:
            session.query(User_File).filter(User_File.id == id).update({"name": name, "type": type})
            session.commit()
            return id

    def update_user_file_type(self, id: int, type: str):  # 更改文件类型
        with self.get_db() as session:
            session.query(User_File).filter(User_File.id == id).update({"type": type})
            session.commit()
            return id

    def get_user_file_by_id(self, id: int):  # 根据id查询user_file的基本信息
        with self.get_db() as session:
            user_file = session.query(User_File).filter(User_File.has_delete == 0, User_File.id == id).first()
            session.commit()
            return user_file

    def get_user_file_id_by_id_list(self, id_list):  # 根据id_list查询user_file的file_id
        with self.get_db() as session:
            if type(id_list) is list:
                user_file = session.query(User_File.id, User_File.user_id, User_File.type).filter(
                    User_File.id.in_(id_list),
                    User_File.has_delete == 0).all()
                session.commit()
            else:
                user_file = session.query(User_File.id, User_File.user_id, User_File.type).filter(
                    User_File.id == id_list,
                    User_File.has_delete == 0).first()
                session.commit()
            return user_file

    def get_file_id_by_id(self, id: int):  # 根据id查询user_file的file_id
        with self.get_db() as session:
            user_file = session.query(User_File.file_id).filter(User_File.has_delete == 0, User_File.id == id).first()
            session.commit()
            return user_file

    def get_file_name_by_id(self, id: int):  # 根据id查询user_file的file_name
        with self.get_db() as session:
            name = session.query(User_File.name).filter(User_File.has_delete == 0, User_File.id == id).first()
            session.commit()
            return name

    def get_video_time_by_id(self, id: int):  # 根据id查询user_file的time
        with self.get_db() as session:
            time = session.query(User_File.video_time).filter(User_File.has_delete == 0, User_File.id == id).first()
            session.commit()
            return time

    def get_type_by_id(self, id: int):  # 根据id查询user_file的type
        with self.get_db() as session:
            type = session.query(User_File.type).filter(User_File.has_delete == 0, User_File.id == id).first()
            session.commit()
            return type

    def get_user_file_id_by_file_id(self, file_id: int):  # 根据file_id查询user_file的id
        with self.get_db() as session:
            id = session.query(User_File.id).filter(User_File.has_delete == 0, User_File.file_id == file_id).first()
            session.commit()
            return id

    def get_user_file_by_file_name(self, file_name: str):  # 根据file_name查询user_file的基本信息
        with self.get_db() as session:
            id = session.query(User_File.id).filter(User_File.has_delete == 0, User_File.name == file_name).first()
            session.commit()
            return id

    def get_user_file_by_admin(self, page, user_id):  # 查找某用户能操作的所有文件
        with self.get_db() as session:
            files = session.query(User_File).filter(User_File.has_delete == 0, User_File.user_id == user_id).order_by(
                User_File.id).offset(
                page.offset()).limit(page.limit()).all()
            session.commit()
            return files


class RSAModel(dbSession):
    def add_user_RSA(self, obj: RSA_interface):  # 给用户生成RSA公钥和密钥
        obj_dict = jsonable_encoder(obj)
        obj_add = RSAKeys(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            return obj_add.public_key_pem

    def delete_user_RSA(self, user_id: int):  # 删除一对公钥密钥
        with self.get_db() as session:
            session.query(RSAKeys).filter(RSAKeys.user_id == user_id).update({"has_delete": 1})
            session.commit()
            return id

    def get_public_key_by_user_id(self, user_id: int):  # 根据user_id查询公钥
        with self.get_db() as session:
            public_key = session.query(RSAKeys.public_key_pem).filter(RSAKeys.has_delete == 0,
                                                                      RSAKeys.user_id == user_id).first()
            session.commit()
            return public_key

    def get_private_key_by_user_id(self, user_id: int):  # 根据user_id查询私钥
        with self.get_db() as session:
            private_key = session.query(RSAKeys.private_key_pem).filter(RSAKeys.has_delete == 0,
                                                                        RSAKeys.user_id == user_id).first()
            session.commit()
            return private_key


class ASEModel(dbSession):
    def add_file_ASE(self, obj: ASE_interface):  # 生成ASE的记录
        obj_dict = jsonable_encoder(obj)
        obj_add = ASEKey(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            return obj_add.id

    def delete_file_ASE(self, file_id: int):  # 删除一条ASE密钥的记录
        with self.get_db() as session:
            session.query(ASEKey).filter(ASEKey.file_id == file_id).update({"has_delete": 1})
            session.commit()
            return 'ok'

    def get_ase_key_by_file_id(self, file_id: int):  # 根据file_id查询密钥
        with self.get_db() as session:
            key = session.query(ASEKey.ase_key).filter(ASEKey.has_delete == 0, ASEKey.file_id == file_id).first()
            session.commit()
            return key
