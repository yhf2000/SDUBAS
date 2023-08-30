from fastapi.encoders import jsonable_encoder

from model.db import dbSession
from model.file import File, User_File
from type.file import file_interface, user_file_interface


class FileModel(dbSession):
    def add_file(self, obj: file_interface):  # 用户上传文件(在file表中添加一个记录)
        obj_dict = jsonable_encoder(obj)
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

    def get_file_by_hash(self, obj: file_interface):  # 根据size与hash查询file的id
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


class UserFileModel(dbSession):
    def add_user_file(self, obj: user_file_interface):  # 用户上传文件(在user_file表中添加一个记录)
        obj_dict = jsonable_encoder(obj)
        obj_add = User_File(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            return obj_add.id

    def add_user_file_id(self, obj: user_file_interface):  # 用户上传文件(在user_file表中添加一个记录)
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

    def get_file_id_by_id(self, id: int):  # 根据id查询user_file的基本信息
        with self.get_db() as session:
            user_file = session.query(User_File.file_id).filter(User_File.has_delete == 0, User_File.id == id).first()
            session.commit()
            return user_file

    def get_user_file_id_by_file_id(self, file_id: int):  # 根据id查询user_file的基本信息
        with self.get_db() as session:
            id = session.query(User_File.id).filter(User_File.has_delete == 0, User_File.file_id == file_id).first()
            session.commit()
            return id

    def get_user_file_by_admin(self, page, user_id):  # 查找某用户能操作的所有文件
        with self.get_db() as session:
            files = session.query(User_File).filter(User_File.has_delete == 0, User_File.user_id == user_id).order_by(
                User_File.id).offset(
                page.offset()).limit(page.limit()).all()
            session.commit()
            return files
