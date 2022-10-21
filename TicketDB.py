from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy import sql
db = SQLAlchemy()


class Team(db.Model):
    __tablename__ = "teamtable"
    team_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    team_name = db.Column(db.String(50), unique=True)
    team_category = db.Column(db.String(50))

    def __init__(self, team_name, team_category):
        self.team_name = team_name
        self.team_category = team_category

    def __repr__(self):
        return f"{self.team_name}:{self.team_name}"


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
    team_id = db.Column(db.Integer, db.ForeignKey(Team.team_id))
    team_user = db.relationship("Team", backref='User')

    def __init__(self, username, name, email, jobTitle, password, tasksComplete, team_id):
        self.username = username
        self.name = name
        self.email = email
        self.jobTitle = jobTitle
        self.password = password
        self.tasksComplete = tasksComplete
        self.team_id = team_id

    def __repr__(self):
        return f"{self.username}:{self.username}"


# Consider a Ticket update field, where when we update the ticket state, the current DAteTime() is entered/Updated
class TestTicket(db.Model):
    __tablename__ = "tickettable"

    ticket_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.user_id))
    ticket_user = db.relationship("User", backref='TestTicket')
    ticket_created = db.Column(db.String(50), default=func.now())
    description = db.Column(db.String(300))
    state = db.Column(db.String(30), default="Open")
    team_id = db.Column(db.Integer, db.ForeignKey(Team.team_id))
    ticket_team = db.relationship("Team", backref='TestTicket')
    contact_num = db.Column(db.String(20))
    priority = db.Column(db.Integer)
    summary = db.Column(db.String(80))
    environment = db.Column(db.String(50))
    ticket_sp_instruction = db.Column(db.String(200))


    def __init__(self, user_id, description, state, team_id, contact_num, priority, summary, environment, ticket_sp_instruction):
        self.user_id = user_id
        self.description = description
        self.state = state
        self.team_id = team_id
        self.contact_num = contact_num
        self.priority = priority
        self.summary = summary
        self.environment = environment
        self.ticket_sp_instruction = ticket_sp_instruction


    def __repr__(self):
        return f"{self.ticket_id}:{self.ticket_id}"


class TComment(db.Model):
    __tablename__ = "ticketcommenttable"
    comm_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    comment = db.Column(db.String(240))
    user_id = db.Column(db.Integer, db.ForeignKey(User.user_id))
    commuserrel = db.relationship("User", backref='TComment')
    timecreated = db.Column(db.String(50), default=func.now(), index=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey(TestTicket.ticket_id))
    commentticketrel = db.relationship("TestTicket", backref='TComment')

    def __init__(self, comment, user_id, ticket_id):
        self.comment = comment
        self.user_id = user_id
        self.ticket_id = ticket_id

    def __repr__(self):
        return f"{self.comm_id}:{self.comm_id}"


class LoginUser(db.Model):
    __tablename__ = "loggedintable"
    login_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.user_id))
    login_user = db.relationship("User", backref='LoginUser')
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(12))
    loginTime = db.Column(db.DATETIME, default=func.now())

    def __init__(self, email, password):

        self.email = email
        self.password = password

    def __repr__(self):
        return f"{self.login_id}:{self.login_id}"
