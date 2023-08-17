from sqlalchemy import func, or_

from model.db import dbSession

from sqlalchemy.orm import Session
from typing import List
from model.project import Project, ProjectContent, ProjectCredit, ProjectContentSubmission, \
    ProjectContentUserSubmission, ProjectContentUserScore
from type.project import ProjectBase, ProjectUpdate, CreditCreate, SubmissionCreate, ScoreCreate, ProjectBase_Opt, \
    ProjectContentBaseOpt, user_submission, user_submission_Opt, Submission_Opt, SubmissionListCreate, \
    project_content_renew
from type.page import page, dealDataList
from sqlalchemy import and_


class ProjectService(dbSession):
    def create_project(self, project: ProjectBase) -> int:
        with self.get_db() as session:
            # Create a new Project instance
            db_project = Project(**project.model_dump(exclude={"contents"}))
            # Add the new project to the session
            session.add(db_project)
            # Commit the transaction
            session.commit()
            # Refresh the instance
            session.refresh(db_project)
            # Create the project contents
            for content in project.contents:
                content.project_id = db_project.id
                db_content = ProjectContent(**content.model_dump())
                session.add(db_content)
                session.commit()
            return db_project.id

    def update_project(self, project_id: int, newproject: ProjectUpdate) -> int:
        with self.get_db() as session:
            session.query(Project).filter(Project.id == project_id).update({"name": newproject.name,
                                                                            "tag": newproject.tag,
                                                                            "active": newproject.active})
            session.commit()
            return project_id

    def delete_project(self, project_id: int) -> int:
        with self.get_db() as session:
            session.query(Project).filter(Project.id == project_id).update({'has_delete': 1})
            session.query(ProjectContent).filter(ProjectContent.project_id == project_id).update({'has_delete': 1})
            session.commit()
            # session.query(ProjectContent).filter_by(ProjectContent.project_id == project_id).update({'has_delete': 1})
            return project_id

    def list_projects(self, pg: page):
        with self.get_db() as session:
            query = session.query(Project).filter_by(has_delete=0)
            total_count = query.count()  # 总共
            # 执行分页查询
            data = query.offset(pg.offset()).limit(pg.limit())  # .all()
            # 序列化结
            return total_count, dealDataList(data, ProjectBase_Opt, {'has_delete', 'img_id'})

    def get_project(self, project_id: int):
        with self.get_db() as session:
            project = session.query(Project).filter(Project.id == project_id).first()
            project = ProjectBase_Opt.model_validate(project)
            date = project.model_dump(exclude={'has_delete'})
            date['content'] = self.list_projects_content(project_id=project_id)
            return date

    def list_projects_content(self, project_id: int, ):
        with self.get_db() as session:
            query = session.query(ProjectContent).filter_by(project_id=project_id,
                                                            has_delete=0).all()
            return dealDataList(query, ProjectContentBaseOpt, {})

    def get_projects_content(self, content_id: int, project_id: int):
        with self.get_db() as session:
            project_content = session.query(ProjectContent).filter_by(id=content_id, project_id=project_id).first()
            project_content = ProjectContentBaseOpt.model_validate(project_content)
            return project_content.model_dump()

    def create_credit(self, credit: CreditCreate) -> int:
        with self.get_db() as session:
            db_credit = ProjectCredit(**credit.model_dump())
            session.add(db_credit)
            session.commit()
            session.refresh(db_credit)
            return db_credit.id

    def create_submission(self, submission: SubmissionListCreate) -> int:
        with self.get_db() as session:
            for sub in submission.addSubmissions:
                db_submission = ProjectContentSubmission(**sub.model_dump())
                session.add(db_submission)
                session.commit()
                session.refresh(db_submission)
            return db_submission.id

    def create_score(self, score: ScoreCreate) -> int:
        with self.get_db() as session:
            db_score = ProjectContentUserScore(**score.model_dump())
            session.add(db_score)
            session.commit()
            session.refresh(db_score)
            return db_score.id

    def create_user_submission(self, uer_submission: user_submission):
        with self.get_db() as session:
            db_user_submission = ProjectContentUserSubmission(**uer_submission.model_dump())
            session.add(db_user_submission)
            session.commit()
            session.refresh(db_user_submission)
            return db_user_submission.id

    def get_user_submission_list(self, project_id: int, content_id: int, user_id: int):
        with self.get_db() as session:
            list_user_submission = session.query(ProjectContentUserSubmission) \
                .join(ProjectContentSubmission,
                      ProjectContentUserSubmission.pc_submit_id == ProjectContentSubmission.id) \
                .filter(ProjectContentSubmission.pro_content_id == content_id,
                        ProjectContentUserSubmission.user_id == user_id).all()
            return dealDataList(list_user_submission, user_submission_Opt)

    def get_project_progress(self, project_id: int, user_id: int):
        with self.get_db() as session:
            total_count = session.query(func.count()).select_from(ProjectContentSubmission) \
                .join(ProjectContent,
                      ProjectContentSubmission.pro_content_id == ProjectContent.id) \
                .filter(ProjectContent.project_id == project_id) \
                .scalar()
            finish_count = session.query(func.count(ProjectContentSubmission.id)) \
                .join(ProjectContent,
                      ProjectContentSubmission.pro_content_id == ProjectContent.id) \
                .join(ProjectContentUserSubmission,
                      ProjectContentUserSubmission.pc_submit_id == ProjectContentSubmission.id) \
                .filter(ProjectContent.project_id == project_id,
                        ProjectContentUserSubmission.user_id == user_id) \
                .scalar()

            return {"finish_count": finish_count, "total_count": total_count}

    def get_user_project_score(self, project_id: int, user_id: int):
        with self.get_db() as session:
            def calculate_content_score(pcs_id: int, content_weight: float):
                # 查询当前项目内容
                content_score = session.query(ProjectContentUserScore.score) \
                    .filter(ProjectContentUserScore.user_id == user_id,
                            ProjectContentUserScore.user_pcs_id == pcs_id).scalar()
                if content_score is None:
                    content_score = 0
                content_score = content_score * content_weight
                return content_score

            total_score = 0

            # 查询该项目下的所有项目内容
            project_contents = session.query(ProjectContent).filter(ProjectContent.project_id == project_id,
                                                                    ProjectContent.has_delete == 0).all()

            # 遍历项目内容并计算总分
            for project_content in project_contents:
                total_score += calculate_content_score(project_content.id, project_content.weight)

            return total_score

    def get_projects_by_type(self, project_type: str, pg: page, tags: str):
        with self.get_db() as session:
            query = session.query(Project).filter(Project.type == project_type, Project.has_delete == 0)
            if tags:
                tag_list = tags.split(',')
                print(tag_list)
                conditions = [Project.tag.like(f"%{tag}%") for tag in tag_list]
                query = query.filter(and_(*conditions))
            total_count = query.count()  # 总共
            # 执行分页查询
            data = query.offset(pg.offset()).limit(pg.limit())  # .all()
            # 序列化结
            return total_count, dealDataList(data, ProjectBase_Opt, {'has_delete', 'img_id'})

    def get_content_by_projectcontentid_userid(self, user_id: int, content_id: int, pg: page):
        with self.get_db() as session:
            query = session.query(ProjectContentSubmission) \
                .filter(ProjectContentSubmission.pro_content_id == content_id)
            total_count = query.count()  # 总共
            # 执行分页查询
            data = query.offset(pg.offset()).limit(pg.limit())  # .all()
            finial_dates = dealDataList(data, Submission_Opt, {})
            for finial_date in finial_dates:
                flag_commit = session.query(ProjectContentUserSubmission) \
                    .filter(ProjectContentUserSubmission.pc_submit_id == finial_date['id'],
                            ProjectContentUserSubmission.user_id == user_id).first()
                if flag_commit is None:
                    finial_date['commit'] = 0
                else:
                    finial_date['commit'] = 1
            return total_count, finial_dates

    def renew_project_content(self, project_id: int, project_contents: project_content_renew):
        with self.get_db() as session:
            data = session.query(ProjectContent).filter(ProjectContent.project_id == project_id,
                                                        ProjectContent.has_delete == 0).all()
            data = dealDataList(data, ProjectContentBaseOpt, {})
            contents = []
            for da in project_contents.contents:
                da = da.model_dump()
                contents.append(da)
            delete_list = []
            add_list = []
            for content in contents:
                if content['id'] is None:
                    add_list.append(content)
                    db_submission = ProjectContent(**content)
                    session.add(db_submission)
                    session.commit()
                    session.refresh(db_submission)
            for da in data:
                if da not in contents:
                    delete_list.append(da)
                    session.query(ProjectContent).filter(ProjectContent.id == da['id']).update({'has_delete': 1})
                    session.commit()
        return project_id
