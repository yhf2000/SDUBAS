from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, Float, Text
from sqlalchemy.sql import func
from model.db import Base


class Project(Base):
    __tablename__ = 'project'
    __table_args__ = (
        Index('ix_project_type_tag', "type", "tag"),  # 非唯一的联合索引
        Index('ix_project_tag', "tag"),  # 非唯一的索引
    )

    id = Column(Integer, primary_key=True, unique=True, index=True)  # 主键，唯一，有索引
    name = Column(String(64), nullable=False)  # 项目名，不能为空
    type = Column(String(64), nullable=False)  # 项目类型：课程，竞赛，实验，课题，活动，不能为空
    tag = Column(String(64), nullable=False)  # 标签，不能为空
    img_id = Column(Integer, ForeignKey('user_file.id'), nullable=False)  # 用户文件id，外键，不能为空
    active = Column(Integer, nullable=False)  # 0 未开始：创建人可看，1 进行中，2 归档：只读，不能为空
    create_dt = Column(DateTime, default=func.now(), nullable=False)  # 创建时间，自动设置，不能为空
    has_delete = Column(Integer, nullable=False)  # 是否已删除，不能为空


class ProjectCredit(Base):
    __tablename__ = 'project_credit'
    __table_args__ = (
        Index('ix_project_credit_project_id', "project_id"),  # 非唯一的索引
    )

    id = Column(Integer, primary_key=True, unique=True, index=True)  # 主键，唯一，有索引
    project_id = Column(Integer, ForeignKey('project.id'), nullable=False)  # 项目id，外键，不能为空
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False)  # 角色id，外键，不能为空
    credit = Column(Float, nullable=True)  # 角色学分设定，可以为空


class ProjectContent(Base):
    __tablename__ = 'project_content'
    __table_args__ = (
        Index('ix_project_content_project_id', "project_id"),  # 非唯一的索引
        Index('ix_project_content_type', "type"),  # 非唯一的索引
        Index('ix_project_content_fa_id', "fa_id"),  # 非唯一的索引
    )

    id = Column(Integer, primary_key=True, unique=True, index=True)  # 主键，唯一，有索引
    project_id = Column(Integer, ForeignKey('project.id'), nullable=False)  # 项目id，外键，不能为空
    type = Column(Integer, nullable=False)  # 项目类别，不能为空，0 通知/规则, 1 学习资料, 2 作业/实验/考试
    fa_id = Column(Integer, ForeignKey('project_content.id'), nullable=True)  # 多级内容的父级项目id，可以为空
    name = Column(String(64), nullable=False)  # 项目名称，不能为空
    file_id = Column(Integer, ForeignKey('user_file.id'), nullable=True)  # 文件id，外键，可以为空
    content = Column(Text, nullable=True)  # 项目内容，可以为空，最大4Kb
    weight = Column(Float, nullable=False)  # 项目权重，不能为空
    feature = Column(Text, nullable=True)  # 额外信息，可以为空，最大4Kb


class ProjectContentSubmission(Base):
    __tablename__ = 'project_content_submission'
    __table_args__ = (
        Index('ix_project_content_submission_pro_content_id', "pro_content_id"),  # 非唯一的索引
        Index('ix_project_content_submission_type', "type"),  # 非唯一的索引
    )

    id = Column(Integer, primary_key=True, unique=True, index=True)  # 主键，唯一，有索引
    pro_content_id = Column(Integer, ForeignKey('project_content.id'), nullable=False)  # 项目内容id，外键，不能为空
    type = Column(Integer, nullable=False)  # 提交内容类型，不能为空，0 文件, 1 文本
    count_limit = Column(Integer, nullable=True)  # 字数限制，可以为空
    size_limit = Column(Integer, nullable=True)  # 大小限制，可以为空
    type_limit = Column(String(64), nullable=True)  # 文件类型限制，可以为空，如 pdf, zip, docx, pptx


class ProjectContentUserSubmission(Base):
    __tablename__ = 'project_content_user_submission'
    __table_args__ = (
        Index('ix_project_content_user_submission_pc_submit_id', "pc_submit_id"),  # 非唯一的索引
        Index('ix_project_content_user_submission_user_id', "user_id"),  # 非唯一的索引
    )

    id = Column(Integer, primary_key=True, unique=True, index=True)  # 主键，唯一，有索引
    pc_submit_id = Column(Integer, ForeignKey('project_content_submission.id'), nullable=False)  # 项目内容提交id，外键，不能为空
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)  # 用户id，外键，不能为空
    file_id = Column(Integer, ForeignKey('user_file.id'), nullable=True)  # 文件id，外键，可以为空
    content = Column(Text, nullable=True)  # 提交内容，可以为空，最大32Kb
    submit_dt = Column(DateTime, default=func.now(), nullable=False)  # 提交时间，不能为空


class ProjectContentUserScore(Base):
    __tablename__ = 'project_content_user_score'
    __table_args__ = (
        Index('ix_project_content_user_score_user_pcs_id', "user_pcs_id"),  # 非唯一的索引
        Index('ix_project_content_user_score_user_id', "user_id"),  # 非唯一的索引
        Index('ix_project_content_user_score_pass', "is_pass"),  # 非唯一的索引
    )

    id = Column(Integer, primary_key=True, unique=True, index=True)  # 主键，唯一，有索引
    user_pcs_id = Column(Integer, ForeignKey('project_content_user_submission.id'), nullable=False)  # 用户提交id，外键，不能为空
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)  # 批阅用户id，外键，不能为空
    honesty = Column(String(4096), nullable=False)  # 诚信数据，不能为空
    honesty_weight = Column(Float, nullable=False)  # 诚信扣分权重，不能为空
    is_pass = Column(Integer, nullable=False)  # 是否通过，不能为空，-1 待确定, 0 通过, 1 不通过
    score = Column(Float, nullable=True)  # 百分制分数，可以为空
    comment = Column(Text, nullable=False)  # 评测评论，不能为空，最大4Kb
    judge_dt = Column(DateTime, default=func.now(), nullable=False)  # 打分时间，不能为空
