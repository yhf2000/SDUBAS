import json
from datetime import datetime

from fastapi import HTTPException, Request
from sqlalchemy import func, or_, distinct, case
from utils.times import getMsTime
from model.db import dbSession

from sqlalchemy.orm import Session, aliased
from typing import List, Any, Optional
from model.project import Project, ProjectContent, ProjectCredit, ProjectContentSubmission, \
    ProjectContentUserSubmission, ProjectContentUserScore
from type.project import ProjectBase, ProjectUpdate, CreditCreate, SubmissionCreate, ScoreCreate, ProjectBase_Opt, \
    ProjectContentBaseOpt, user_submission, user_submission_Opt, Submission_Opt, SubmissionListCreate, \
    project_content_renew, content_score, User_Opt, ProjectCreate, video_finish_progress, Credit_Opt
from type.page import page, dealDataList
from sqlalchemy import and_
from service.permissions import permissionModel
from model.permissions import UserRole
from model.user import User
from type.functions import get_url_by_user_file_id, get_video_time
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
                if content.file_id is not None:
                    content.file_time = get_video_time(content.file_id)
                db_content = ProjectContent(**content.model_dump())
                session.add(db_content)
                session.commit()
            role_model = permissionModel()
            for role in project.roles:
                role_id = role_model.add_role_for_work(service_id=db_project.id,
                                                       service_type=7, user_id=user_id, role_name=role.role_name)
                role_model.attribute_privilege_for_role(role.privilege_list, role_id)
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

    def list_projects(self, request: Request, pg: page, user_id: int):
        with self.get_db() as session:
            role_model = permissionModel()
            role_list = role_model.search_role_by_user(user_id)
            service_ids = role_model.search_service_id(role_list, service_type=7, name="查看项目")
            query = session.query(Project).filter(Project.has_delete == 0, Project.id.in_(service_ids))
            total_count = query.count()  # 总共
            # 执行分页查询
            data = query.offset(pg.offset()).limit(pg.limit())  # .all()
            # 序列化结
            results = dealDataList(data, ProjectBase_Opt, {'has_delete'})
            for result in results:
                result['url'] = get_url_by_user_file_id(request, result['img_id'])
            return total_count, results

    def get_project(self, request: Request, project_id: int, user_id: int):
        with self.get_db() as session:
            project = session.query(Project).filter(Project.id == project_id).first()
            project = ProjectBase_Opt.model_validate(project)
            date = project.model_dump(exclude={'has_delete'})
            file_url = get_url_by_user_file_id(request, date['img_id'])
            date['url'] = file_url[date['img_id']]
            date['contents'] = self.list_projects_content(project_id=project_id, user_id=user_id)
            return date

    def list_projects_content(self, request: Request, project_id: int, user_id: int):
        with self.get_db() as session:
            subquery = session.query(ProjectContentUserScore). \
                filter(ProjectContentUserScore.user_id == user_id).subquery()
            query = session.query(ProjectContent, subquery.c.is_pass). \
                outerjoin(subquery,
                          ProjectContent.id == subquery.c.user_pcs_id). \
                filter(ProjectContent.project_id == project_id,
                       ProjectContent.has_delete == 0).all()
            results = []
            for re in query:
                result = ProjectContentBaseOpt.model_validate(re[0])
                result = result.model_dump(exclude={'has_delete'})
                if re[1] is None:
                    result['is_pass'] = 0
                else:
                    result['is_pass'] = re[1]
                results.append(result)
            file_id_list = []
            for result in results:
                file_id_list.append(result['file_id'])
            file_url_list = get_url_by_user_file_id(request, file_id_list)
            for result in results:
                if result['file_id'] is not None:
                    result['url'] = file_url_list[result['file_id']]
            return results

    def get_projects_content(self, request: Request, content_id: int, project_id: int, user_id: int):
        with self.get_db() as session:
            project_content = session.query(ProjectContent).filter_by(id=content_id, project_id=project_id,
                                                                      has_delete=0).first()
            project_content = ProjectContentBaseOpt.model_validate(project_content)
            result = project_content.model_dump()
            if result['file_id'] is not None:
                file_url_list = get_url_by_user_file_id(request, result['file_id'])
                result['url'] = file_url_list[result['file_id']]
            return result

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

    def get_user_submission_list(self, request: Request, project_id: int, content_id: int, user_id: int):
        with self.get_db() as session:
            list_user_submission = session.query(ProjectContentUserSubmission) \
                .join(ProjectContentSubmission,
                      ProjectContentUserSubmission.pc_submit_id == ProjectContentSubmission.id) \
                .filter(ProjectContentSubmission.pro_content_id == content_id,
                        ProjectContentUserSubmission.user_id == user_id).all()
            results = dealDataList(list_user_submission, user_submission_Opt)
            file_id_list = []
            for result in results:
                file_id_list.append(result['file_id'])
            file_url_list = get_url_by_user_file_id(request, file_id_list)
            for result in results:
                if result['file_id'] is not None:
                    result['url'] = file_url_list[result['file_id']]
            return results

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
            total_score = session.query(
                func.sum(func.coalesce(ProjectContentUserScore.score, 0) * ProjectContent.weight)
            ).outerjoin(ProjectContentUserScore,
                        ProjectContentUserScore.user_pcs_id == ProjectContent.id) \
                .filter(ProjectContent.project_id == project_id,
                        ProjectContent.has_delete == 0,
                        ProjectContentUserScore.user_id == user_id) \
                .scalar()

            if total_score is None:
                total_score = 0

            return total_score

    def get_projects_by_type(self, request: Request, project_type: str, pg: page, tags: str, user_id: int):
        with self.get_db() as session:
            role_model = permissionModel()
            role_list = role_model.search_role_by_user(user_id)
            service_ids = role_model.search_service_id(role_list, service_type=7, name="查看项目")
            # service_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9]
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
            results = dealDataList(data, ProjectBase_Opt, {'has_delete'})
            file_id_list = []
            for result in results:
                file_id_list.append(result['img_id'])
            file_url_list = get_url_by_user_file_id(request, file_id_list)
            for result in results:
                result['url'] = file_url_list[result['img_id']]
            return total_count, results

    def get_content_by_projectcontentid_userid(self, user_id: int, content_id: int, pg: page, project_id: int):
        with self.get_db() as session:
            subquery = session.query(distinct(ProjectContentUserSubmission.pc_submit_id).label('pc_submit_id')). \
                filter(ProjectContentUserSubmission.user_id == user_id).subquery()
            query = session.query(ProjectContentSubmission, subquery.c.pc_submit_id). \
                filter(ProjectContentSubmission.pro_content_id == content_id). \
                outerjoin(subquery, ProjectContentSubmission.id == subquery.c.pc_submit_id). \
                add_columns(case((subquery.c.pc_submit_id.is_(None), 0), else_=1).label('commit'))

            total_count = query.count()  # 总共
            # 执行分页查询
            datas = query.offset(pg.offset()).limit(pg.limit()).all()
            finial_dates = []
            for data, pc_submit_id, commit in datas:
                finial_date = {
                    "name": data.name,
                    "pro_content_id": data.pro_content_id,
                    "type": data.type,
                    "count_limit": data.count_limit,
                    "size_limit": data.size_limit,
                    "type_limit": data.type_limit,
                    "id": data.id,
                    "commit": commit
                }
                finial_dates.append(finial_date)
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
        role_model = permissionModel()
        query = role_model.search_user_id_by_service(service_type=7, service_id=project_id)
        query = query.join(User, User.id == UserRole.user_id)
        query = query.add_entity(User)
        total_count = query.distinct(Project.id).count()  # 总共
        print(total_count)
        # 执行分页查询
        data = query.offset(pg.offset()).limit(pg.limit())  # .all()
        lis = []
        for d in data:
            user = d[1]
            print(type(user))
            lis.append(user)
        return total_count, dealDataList(lis, User_Opt, {'has_delete'})

    def get_credits_user_get(self, user_id: int):
        with self.get_db() as session:
            role_model = permissionModel()
            role_list = role_model.search_role_by_user(user_id)
            service_ids = role_model.search_service_id(role_list, service_type=7, name="提交项目内容")
            credit_role_id = 1
            service_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9]

            subquery = session.query(Project). \
                select_from(Project). \
                join(ProjectContent,
                     ProjectContent.project_id == Project.id). \
                outerjoin(ProjectContentUserScore,
                          (ProjectContentUserScore.user_pcs_id == ProjectContent.id) &
                          (ProjectContentUserScore.user_id == user_id)). \
                filter(ProjectContent.project_id.in_(service_ids),
                       Project.has_delete == 0). \
                group_by(Project.id). \
                having(func.sum(ProjectContentUserScore.is_pass) == func.count(ProjectContent.id)).subquery()
            query = session.query(ProjectCredit.type, func.sum(ProjectCredit.credit)). \
                join(subquery, ProjectCredit.project_id == subquery.c.id). \
                filter(ProjectCredit.role_id == credit_role_id). \
                group_by(ProjectCredit.type). \
                add_columns(func.sum(ProjectCredit.credit).label("credit_count"))

            results = query.all()
            total_count = []
            for project in results:
                count = {'credit_type': project[0],
                         'credit_count': project[1]}
                total_count.append(count)

        return total_count

    def get_all_project_score(self, project_id: int, user_id: int, pg: page):
        with self.get_db() as session:
            subquery = session.query(
                ProjectContentUserScore
            ).filter(
                ProjectContentUserScore.user_id == user_id
            ).subquery()

            scores = session.query(
                ProjectContent, subquery
            ).outerjoin(subquery,
                        subquery.c.user_pcs_id == ProjectContent.id) \
                .filter(ProjectContent.project_id == project_id,
                        ProjectContent.has_delete == 0)
            lis = []
            total_num = scores.count()
            scores_list = scores.offset(pg.offset()).limit(pg.limit())
            for score in scores_list:
                now_score = {'content_name': score[0].name, 'score': score[8]}
                lis.append(now_score)
            return total_num, lis

    def get_content_user_score_all(self, project_id: int, content_id: int, pg: page, user_id: int):
        with self.get_db() as session:
            role_model = permissionModel()
            query = role_model.search_user_id_by_service(service_type=7, service_id=project_id)
            query = query.join(User, User.id == UserRole.user_id)
            query = query.add_entity(User)
            subquery = session.query(ProjectContentUserScore).filter(ProjectContentUserScore.user_pcs_id == content_id) \
                .subquery()
            query = query.outerjoin(subquery, subquery.c.user_id == User.id)
            query = query.add_entity(subquery)
            total_count = query.count()  # 总共
            # 执行分页查询
            data = query.offset(pg.offset()).limit(pg.limit())  # .all()
            lis = []
            for d in data:
                user = d[1]
                score = d[9]
                user_name = user.username
                user_id = user.id
                lis.append({'user_id': user_id, 'user_name': user_name, 'score': score})
            return total_count, lis

    def get_user_credit_all(self, user_id: int, pg: page):
        with self.get_db() as session:
            credit_role_id = 1
            subquery = session.query(ProjectCredit).filter(
                ProjectCredit.role_id == credit_role_id).subquery()
            query = session.query(Project, subquery.c.credit, subquery.c.type). \
                select_from(Project). \
                join(subquery, subquery.c.project_id == Project.id). \
                join(ProjectContent, ProjectContent.project_id == Project.id). \
                outerjoin(ProjectContentUserScore,
                          (ProjectContentUserScore.user_pcs_id == ProjectContent.id) &
                          (ProjectContentUserScore.user_id == user_id)). \
                filter(Project.has_delete == 0,
                       ProjectContent.has_delete == 0). \
                group_by(Project.id)

            query = query.add_columns(
                case((func.sum(ProjectContentUserScore.is_pass) == func.count(ProjectContent.id), 1), else_=0).label(
                    "is_pass")
            )
            total_count = query.count()
            projects = query.offset(pg.offset()).limit(pg.limit())
            results = []
            for project, project_credit, credit_type, is_pass in projects:
                result = {'project_id': project.id, 'project_name': project.name, 'credit': project_credit,
                          'type': credit_type,
                          'is_pass': is_pass}
                results.append(result)
        return total_count, results

    def video_content_progress_renew(self, content_renew: video_finish_progress, user_id: int):
        with self.get_db() as session:
            time1 = datetime.now()
            time = time1.timestamp()
            content_user_score_check = session.query(ProjectContentUserScore). \
                filter(ProjectContentUserScore.user_id == user_id,
                       ProjectContentUserScore.user_pcs_id == content_renew.content_id).first()
            content = session.query(ProjectContent). \
                filter(ProjectContent.id == content_renew.content_id,
                       ProjectContent.has_delete == 0).first()
            if content_user_score_check is None:
                db_score = ProjectContentUserScore(id=None,
                                                   user_pcs_id=content_renew.content_id, user_id=user_id,
                                                   judger=1, honesty='', honesty_weight=0,
                                                   is_pass=-1, score=None, comment='',
                                                   judge_dt=time1, viewed_time=0,
                                                   last_check_time=time1)
                session.add(db_score)
                session.commit()
                session.refresh(db_score)
                return 'renew_finish'
            elif content_user_score_check.is_pass == -1:
                last_check = content_user_score_check.last_check_time.timestamp()
                if time - last_check >= 30:
                    has_view_time = content_user_score_check.viewed_time + 30
                    is_pass = -1
                    if has_view_time >= content.file_time:
                        is_pass = 1
                    session.query(ProjectContentUserScore). \
                        filter(ProjectContentUserScore.user_id == user_id,
                               ProjectContentUserScore.user_pcs_id == content_renew.content_id).update(
                        {'viewed_time': has_view_time,
                         'last_check_time': time1,
                         'is_pass': is_pass})
                    session.commit()
                    if is_pass == 1:
                        return 'video_finish'
                    else:
                        return 'renew_finish'
            return 'renew_failure'

    def get_project_credits_all(self, project_id: int):
        with self.get_db() as session:
            query = session.query(ProjectCredit).filter(ProjectCredit.project_id == project_id)
            results = query.all()
            results = dealDataList(results, Credit_Opt, {})
            return results

    def renew_project_content_special(self, project_id: int, content_id: int, user_id: int):
        with self.get_db() as session:
            content = session.query(ProjectContent).filter(ProjectContent.id == content_id,
                                                           ProjectContent.project_id == project_id,
                                                           ProjectContent.has_delete == 0).first()
            description = content.feature
            result = {}
            pairs = description.split(';')
            for pair in pairs:
                key_value = pair.split(':')
                if len(key_value) == 2:
                    key = key_value[0]
                    values = [int(num) for num in key_value[1].split(',')]
                    result[key] = values  # 对字符串进行处理
            count = len(result['c'])

            # 获取所有符合条件的 ProjectContentUserScore 的 is_pass 的和
            total_pass = session.query(func.sum(ProjectContentUserScore.is_pass)).filter(
                ProjectContentUserScore.user_pcs_id.in_(result['c']),
                ProjectContentUserScore.user_id == user_id).scalar()
            if total_pass == count:
                query = session.query(ProjectContentUserScore).filter(ProjectContentUserScore.user_pcs_id == content_id,
                                                                      ProjectContentUserScore.user_id == user_id)
                check_score = query.first()
                if check_score is None:
                    db_score = ProjectContentUserScore(id=None,
                                                       user_pcs_id=content_id, user_id=user_id,
                                                       judger=1, honesty='', honesty_weight=0,
                                                       is_pass=1, score=None, comment='')
                    session.add(db_score)
                    session.commit()
                    session.refresh(db_score)
                else:
                    session.query(ProjectContentUserScore). \
                        filter(ProjectContentUserScore.user_id == user_id,
                               ProjectContentUserScore.user_pcs_id == content_id).update(
                        {'is_pass': 1})
                return 1
            return 0

    def get_user_personal_file_by_user_id(self, user_id):
        with self.get_db() as session:
            role_model = permissionModel()
            role_list = role_model.search_role_by_user(user_id)
            service_ids = role_model.search_service_id(role_list, service_type=7, name="查看项目")
            # service_ids = [1, 2, 3, 4, 5, 6, 7]
            query = session.query(Project).filter(Project.has_delete == 0, Project.id.in_(service_ids))
            # 执行分页查询
            data = query.all()  # .all()
            # 序列化结
            results = dealDataList(data, ProjectBase_Opt, {'has_delete'})
            return {'project': results}
