from model.db import dbSession

from sqlalchemy.orm import Session
from typing import List
from model.project import Project, ProjectContent
from type.project import ProjectBase, ProjectUpdate, CreditCreate, SubmissionCreate, ScoreCreate


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
                db_content = ProjectContent(project_id=db_project.id, **content.model_dump())
                session.add(db_content)
            session.commit()

            return db_project.id

    def update_project(self, project: ProjectUpdate) -> int:
        with self.get_db() as session:
            # 实现具体的业务逻辑
            # ...
            project_id = 0
            return project_id

    def delete_project(self, project_id: int) -> int:
        with self.get_db() as session:
            # 实现具体的业务逻辑
            # ...
            return project_id

    def list_projects(self) -> List[Project]:
        with self.get_db() as session:
            # 实现具体的业务逻辑
            # ...
            projects = []
            return projects

    def get_project(self, project_id: int) -> Project:
        with self.get_db() as session:
            # 实现具体的业务逻辑
            # ...
            project = Project()
            return project

    def create_credit(self, credit: CreditCreate) -> int:
        with self.get_db() as session:
            # 实现具体的业务逻辑
            # ...
            credit_id = 0
            return credit_id

    def create_submission(self, submission: SubmissionCreate) -> int:
        with self.get_db() as session:
            # 实现具体的业务逻辑
            # ...
            submission_id = 0
            return submission_id

    def create_score(self, score: ScoreCreate) -> int:
        with self.get_db() as session:
            # 实现具体的业务逻辑
            # ...
            score_id = 0
            return score_id
