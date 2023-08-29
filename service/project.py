from fastapi import HTTPException
from sqlalchemy import func, or_, distinct

from model.db import dbSession

from sqlalchemy.orm import Session
from typing import List, Any, Optional
from model.project import Project, ProjectContent, ProjectCredit, ProjectContentSubmission, \
    ProjectContentUserSubmission, ProjectContentUserScore
from type.project import ProjectBase, ProjectUpdate, CreditCreate, SubmissionCreate, ScoreCreate, ProjectBase_Opt, \
    ProjectContentBaseOpt, user_submission, user_submission_Opt, Submission_Opt, SubmissionListCreate, \
    project_content_renew, content_score, User_Opt, ProjectCreate
from type.page import page, dealDataList
from sqlalchemy import and_
from service.permissions import roleModel
from model.permissions import UserRole
from model.user import User
from type.user import operation_interface
from service.user import OperationModel


class ProjectService(dbSession):
    def create_project(self, project: ProjectCreate, user_id: int) -> int:
        with self.get_db() as session:
            # Create a new Project instance
            db_project = Project(**project.model_dump(exclude={"contents", "roles"}))
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
            role_model = roleModel()
            for role in project.roles:
                role_model.add_role_for_work(service_id=db_project.id,
                                             service_type=7, user_id=user_id, role_name=role.role_name)
            return db_project.id

    def update_project(self, project_id: int, newproject: ProjectUpdate, user_id: int) -> int:
        with self.get_db() as session:
            session.query(Project).filter(Project.id == project_id).update({"name": newproject.name,
                                                                            "tag": newproject.tag,
                                                                            "active": newproject.active})
            session.commit()
            return project_id

    def delete_project(self, project_id: int, user_id: int) -> int:
        with self.get_db() as session:
            session.query(Project).filter(Project.id == project_id).update({'has_delete': 1})
            session.query(ProjectContent).filter(ProjectContent.project_id == project_id).update({'has_delete': 1})
            session.commit()
            # session.query(ProjectContent).filter_by(ProjectContent.project_id == project_id).update({'has_delete': 1})
            return project_id

    def list_projects(self, pg: page, user_id: int):
        with self.get_db() as session:
            role_model = roleModel()
            role_list = role_model.search_role_by_user(user_id)
            service_ids = role_model.search_service_id(role_list, service_type=7, name="查看项目")
            query = session.query(Project).filter(Project.has_delete == 0, Project.id.in_(service_ids))
            total_count = query.count()  # 总共
            # 执行分页查询
            data = query.offset(pg.offset()).limit(pg.limit())  # .all()
            # 序列化结
            return total_count, dealDataList(data, ProjectBase_Opt, {'has_delete', 'img_id'})

    def get_project(self, project_id: int, user_id: int):
        with self.get_db() as session:
            project = session.query(Project).filter(Project.id == project_id).first()
            project = ProjectBase_Opt.model_validate(project)
            date = project.model_dump(exclude={'has_delete'})
            date['contents'] = self.list_projects_content(project_id=project_id, user_id=user_id)
            return date

    def list_projects_content(self, project_id: int, user_id: int):
        with self.get_db() as session:
            query = session.query(ProjectContent).filter_by(project_id=project_id,
                                                            has_delete=0).all()
            return dealDataList(query, ProjectContentBaseOpt, {})

    def get_projects_content(self, content_id: int, project_id: int, user_id: int):
        with self.get_db() as session:
            project_content = session.query(ProjectContent).filter_by(id=content_id, project_id=project_id,
                                                                      has_delete=0).first()
            project_content = ProjectContentBaseOpt.model_validate(project_content)
            return project_content.model_dump()

    def create_credit(self, credit: CreditCreate, user_id: int) -> int:
        with self.get_db() as session:
            db_check = session.query(ProjectCredit).filter(ProjectCredit.project_id == credit.project_id,
                                                           ProjectCredit.role_id == credit.role_id).first()
            if db_check is None:
                db_credit = ProjectCredit(**credit.model_dump())
                session.add(db_credit)
                session.commit()
                session.refresh(db_credit)
                return db_credit.id
            else:
                session.query(ProjectCredit).filter(ProjectCredit.project_id == credit.project_id,
                                                    ProjectCredit.role_id == credit.role_id) \
                    .update({'credit': credit.credit})
                session.commit()
                return db_check.id

    def create_submission(self, submission: SubmissionListCreate, user_id: int, project_id: int) -> int:
        with self.get_db() as session:
            for sub in submission.addSubmissions:
                db_submission = ProjectContentSubmission(**sub.model_dump())
                session.add(db_submission)
                session.commit()
                session.refresh(db_submission)
            return db_submission.id

    def create_score(self, scoremodel: ScoreCreate, user_id: int, project_id: int) -> int:
        with self.get_db() as session:
            db_check = session.query(ProjectContentUserScore). \
                filter(ProjectContentUserScore.user_id == scoremodel.user_id,
                       ProjectContentUserScore.user_pcs_id == scoremodel.user_pcs_id).first()
            if db_check is None:
                db_score = ProjectContentUserScore(**scoremodel.model_dump())
                session.add(db_score)
                session.commit()
                session.refresh(db_score)
                return db_score.id
            else:
                db_score = session.query(ProjectContentUserScore). \
                    filter(ProjectContentUserScore.user_id == scoremodel.user_id,
                           ProjectContentUserScore.user_pcs_id == scoremodel.user_pcs_id) \
                    .update({'score': scoremodel.score, 'is_pass': scoremodel.is_pass})
                session.commit()
                return db_check.id

    def create_user_submission(self, uer_submission: user_submission, user_id: int, project_id: int):
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
            finish_count = session.query(func.count(distinct(ProjectContentSubmission.id))) \
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
            xd = 1

            def calculate_content_score(pcs_id: int, content_weight: float):
                # 查询当前项目内容
                content_scores = session.query(ProjectContentUserScore.score) \
                    .filter(ProjectContentUserScore.user_id == user_id,
                            ProjectContentUserScore.user_pcs_id == pcs_id).scalar()
                if content_scores is None:
                    content_scores = 0
                content_scores = content_scores * content_weight
                return content_scores

            total_score = 0

            # 查询该项目下的所有项目内容
            project_contents = session.query(ProjectContent).filter(ProjectContent.project_id == project_id,
                                                                    ProjectContent.has_delete == 0).all()

            # 遍历项目内容并计算总分
            for project_content in project_contents:
                total_score += calculate_content_score(project_content.id, project_content.weight)
            return total_score

    def get_projects_by_type(self, project_type: str, pg: page, tags: str, user_id: int):
        with self.get_db() as session:
            role_model = roleModel()
            role_list = role_model.search_role_by_user(user_id)
            service_ids = role_model.search_service_id(role_list, service_type=7, name="查看项目")
            query = session.query(Project).filter(Project.type == project_type, Project.has_delete == 0,
                                                  Project.id.in_(service_ids))
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

    def get_content_by_projectcontentid_userid(self, user_id: int, content_id: int, pg: page, project_id: int):
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

    def renew_project_content(self, project_id: int, project_contents: project_content_renew, user_id: int):
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

    def check_project_exist(self, project_id: int):
        with self.get_db() as session:
            project_model = session.query(Project).filter(Project.id == project_id, Project.has_delete == 0).first()
            if project_model is None:
                raise HTTPException(status_code=404, detail="Item not found")
            else:
                return project_model

    def check_projectContent_exist(self, project_id: int, content_id: int):
        with self.get_db() as session:
            projectCount_model = session.query(ProjectContent).filter(ProjectContent.id == content_id,
                                                                      ProjectContent.has_delete == 0,
                                                                      ProjectContent.project_id == project_id).first()
            if projectCount_model is None:
                raise HTTPException(status_code=404, detail="Item not found")
            else:
                return projectCount_model

    def get_user_by_project_id(self, project_id: int, pg: page, user_id: int):
        role_model = roleModel()
        query = role_model.search_user_id_by_service(service_type=7, service_id=project_id)
        query = query.join(User, User.id == UserRole.user_id)
        query = query.add_entity(User)
        total_count = query.distinct(Project.id).count()  # 总共
        print(total_count)
        # 执行分页查询
        data = query.offset(pg.offset()).limit(pg.limit())  # .all()
        lis = []
        for d in data:
            user = d[2]
            print(type(user))
            lis.append(user)
        return total_count, dealDataList(lis, User_Opt, {'has_delete'})

    def get_credits_user_get(self, user_id: int):
        with self.get_db() as session:
            def check_content_finish(project_id: int):
                contents = session.query(ProjectContent).filter(ProjectContent.project_id == project_id).all()
                for content in contents:
                    score = session.query(ProjectContentUserScore).filter(
                        ProjectContentUserScore.user_pcs_id == content.id,
                        ProjectContentUserScore.user_id == user_id).first()
                    if score is None:
                        return 0
                    elif score.is_pass != 0:
                        return 0
                return 1

            role_model = roleModel()
            role_list = role_model.search_role_by_user(user_id)
            service_ids = role_model.search_service_id(role_list, service_type=7, name="提交项目内容")
            projects = session.query(Project).filter(Project.has_delete == 0, Project.id.in_(service_ids)).all()
            # 获取角色ID
            credit_role_id = 1
            total_credits = 0
            for project in projects:
                if check_content_finish(project_id=project.id):
                    current_credit = session.query(ProjectCredit).filter(ProjectCredit.project_id == project.id,
                                                                         ProjectCredit.role_id == credit_role_id).first()
                    total_credits += current_credit.credit
        return total_credits

    def get_all_project_score(self, project_id: int, user_id: int):
        with self.get_db() as session:
            scores = session.query(ProjectContent, ProjectContentUserScore).outerjoin(ProjectContentUserScore,
                                                                                      ProjectContent.id == ProjectContentUserScore.user_pcs_id) \
                .filter(ProjectContent.project_id == project_id,
                        or_(ProjectContentUserScore.user_id == user_id,
                            ProjectContentUserScore.user_id.is_(None))).all()
            lis = []
            for score in scores:
                if score[1] is None:
                    score_value = 0
                else:
                    score_value = score[1].score
                print(score[0].id)
                now_score = {'content_name': score[0].name, 'score': score_value}
                lis.append(now_score)
            return lis

    def get_content_user_score_all(self, project_id: int, content_id: int, pg: page, user_id: int):
        with self.get_db() as session:
            role_model = roleModel()
            query = role_model.search_user_id_by_service(service_type=7, service_id=project_id)
            query = query.join(User, User.id == UserRole.user_id)
            query = query.add_entity(User)
            query = query.outerjoin(ProjectContentUserScore, ProjectContentUserScore.user_id == UserRole.user_id)
            query = query.add_entity(ProjectContentUserScore)
            query = query.filter(or_(ProjectContentUserScore.user_pcs_id == content_id,
                                     ProjectContentUserScore.user_pcs_id.is_(None)))
            total_count = query.distinct(User.id).count()  # 总共
            print(total_count)
            # 执行分页查询
            data = query.offset(pg.offset()).limit(pg.limit())  # .all()
            lis = []
            for d in data:
                user = d[2]
                score = d[3]
                user_name = user.username
                if score is None:
                    score_now = 0
                else:
                    score_now = score.score
                lis.append({'user_name': user_name, 'score': score_now})
            return total_count, lis
