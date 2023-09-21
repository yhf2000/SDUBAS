import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey, Boolean, String, Index, func, LargeBinary, text
)

from model.db import Base


class File(Base):  # 文件表
    __tablename__ = 'file'
    __table_args__ = (
        Index('ix_file_has_delete_size_hash', "has_delete", "size", "hash_md5", "hash_sha256"),  # 非唯一的索引
    )
    id = Column(Integer, primary_key=True)  # 文件 id
    size = Column(Integer, nullable=False)  # 文件大小（字节）
    is_save = Column(Boolean, nullable=False)  # 文件是否已上传
    hash_md5 = Column(String(128), nullable=False)  # 文件哈希md5
    hash_sha256 = Column(String(128), nullable=False)  # 文件哈希sha256
    create_dt = Column(DateTime)  # 文件创建时间
    has_delete = Column(Boolean)  # 是否已经删除



class User_File(Base):  # 文件用户表
    __tablename__ = 'user_file'
    id = Column(Integer, primary_key=True)  # 主键
    file_id = Column(Integer, ForeignKey('file.id'), nullable=False)  # 文件id，外键
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)  # 用户id，外键
    name = Column(String(128), nullable=True)  # 文件名
    type = Column(String(128), nullable=True)  # 文件类型
    video_time = Column(Integer, nullable=True)  # 视频类型的文件的播放时长
    has_delete = Column(Boolean, index=True)  # 是否已经删除

class RSAKeys(Base):  #用户RSA公私钥表
    __tablename__ = 'RSA_keys'
    id = Column(Integer, primary_key=True)# 主键
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)  # 用户id，外键
    private_key_pem = Column(String(2048),nullable=False)
    public_key_pem = Column(String(2048),nullable=False)
    created_at = Column(DateTime, default=func.now(),nullable=False)
    expires_at = Column(DateTime,server_default=text("(CURRENT_TIMESTAMP + INTERVAL 14 DAY)"),nullable=False)
    has_delete = Column(Boolean, index=True,default=0,nullable=False)  # 是否已经删除
