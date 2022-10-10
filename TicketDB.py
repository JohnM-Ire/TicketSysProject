from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy import sql
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "usertable"
    user_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    jobTitle = db.Column(db.String(60))
    password = db.Column(db.String(12))
    dateCreated = db.Column(db.DATETIME, default=func.now())
    tasksComplete = db.Column(db.Integer)

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
    __tablename__ = "teamtable"
    team_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    team_name = db.Column(db.String(50), unique=True)

    def __init__(self, team_name):
        self.team_name = team_name

    def __repr__(self):
        return f"{self.team_name}:{self.team_name}"

class Ticket(db.Model):
    __tablename__ = "tickettable"
    ticket_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    item_type = db.Column(db.String(50))
    requested_by = db.Column(db.String(50)) #reference user.user_id foreignKey
    ticket_created = db.Column(db.String(50), default=func.now())
    description = db.Column(db.String(300))
    state = db.Column(db.String(20), default="Open")
    assign_to_group = db.Column(db.String(50)) #drop down with list of viable teams
    assign_to_person = db.Column() #reference user.user.id, drop down should only show team members from above
    email = db.Column(db.String(60))
    contact_num = db.Column(db.Varchar(20))
    priority = db.Column(db.String())
    summary = db.Column(db.String(50))
    ticket_env = db.Column(db.String(50)) #dropdown to have the env's DEV, QA, REL, PROD, OTHER
    ticket_sp_instruction = db.Column(db.String(200))

