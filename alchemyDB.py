from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()
db = SQLAlchemy()

# user_team = Table(
#     "user_team",
#     Base.metadata,
#     db.Column("user_id", INTEGER, ForeignKey("user.id")),
#     db.Column("team_id", INTEGER, ForeignKey("team.team_id")),
# )


class User(db.Model):
    __tablename__ = "user"

    user_id = db.Column(INTEGER, primary_key=True, unique=True, autoincrement=True)
    username = db.Column(VARCHAR(50), unique=True)
    name = db.Column(VARCHAR(50))
    email = db.Column(VARCHAR(50), unique=True)
    jobTitle = db.Column(VARCHAR(60))
    password = db.Column(VARCHAR(12))
    dateCreated = db.Column(DATETIME)
    tasksComplete = db.Column(INTEGER)

    def __init__(self, username, name, email, jobTitle, password, tasksComplete):
        self.username = username
        self.name = name
        self.email = email
        self.jobTitle = jobTitle
        self.password = password
        self.tasksComplete = tasksComplete

    def __repr__(self):
        return f"{self.username}:{self.username}"

class Team(db.Model):
    __tablename__ = "team"

    team_id = db.Column(INTEGER, primary_key=True, unique=True, autoincrement=True)
    team_name = db.Column(VARCHAR(60))
    team_info = db.Column(VARCHAR(250))

    def __init__(self, team_name, team_info):
        self.team_name = team_name
        self.team_info = team_info

    def __repr__(self):
        return f"{self.team_id}:{self.team_name}"
#
# class TeamMembers(Base):
#     __tablename__ = "teamMembers"
#     user_id = Column(Integer, ForeignKey("user.user_id"))
#     team_id = Column(Integer, ForeignKey("team.team_id"))

    # def __repr__(self):
    #     return f"{self.movie_name}:{self.signature}"








    # def __init__(self, id, username, name, email, jobTitle, password, dateCreated, tasksComplete):
    #     self.id = id
    #     self.username = username
    #     self.name = name
    #     self.email = email
    #     self.jobTitle = jobTitle
    #     self.password = password
    #     self.dateCreated = dateCreated
    #     self.tasksComplete = tasksComplete
    #
    # def __repr__(self):
    #     return f"{self.id}:{self.username}"
