from flask import Flask, render_template, request, redirect, flash, session
from sqlalchemy.sql import select, alias
# from flask_sqlalchemy import SQLAlchemy
from TicketDB import db, User, Team, TestTicket, Comment
# from urllib.request import urlopen
# from bs4 import BeautifulSoup
import itertools
import jinja2

app = Flask(__name__)

app.config['SECRET_KEY'] = "JohnKey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jMovie.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.before_first_request
def create_table():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/adduser', methods=['GET', 'POST'])
def addUser():
    if request.method == 'GET':
        return render_template('addUser.html')

    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        jobTitle = request.form['jobTitle']
        password = request.form['password']
        tasksComplete = request.form['tasksComplete']
        team_id = request.form['team_id']
        if username == "" or name == "" or email == "" or jobTitle == "" or password == "":
            return 'Please go back and enter values for all fields'
        else:
            newuser = User(username=username, name=name, email=email, jobTitle=jobTitle, password=password,
                           tasksComplete=tasksComplete, team_id=team_id)

            db.session.add(newuser)
            db.session.commit()
            return redirect('/admin_data')


@app.route('/addTeam', methods=['GET', 'POST'])
def addTeam():
    if request.method == 'GET':
        return render_template('addTeam.html')

    if request.method == 'POST':
        team_name = request.form['team_name']
        team_category = request.form['team_category']

        if team_name == "":
            return 'Please go back and enter Team Name'
        else:
            newTeam = Team(team_name=team_name, team_category=team_category)
            db.session.add(newTeam)
            db.session.commit()
            return redirect('/admin_data')


@app.route('/admin_data')
def retrieveUsers():
    teams = Team.query.all()
    users = User.query.all()

    return render_template('admin_data.html', users=users, teams=teams)

@app.route('/team/javadev')
def retrieveJava():
    javadevs = Team.query.with_entities(Team.team_id, Team.team_name, Team.team_category, User.user_id, User.name, User.
                                        email, User.jobTitle).join(User, Team.team_id == User.team_id).filter(Team.team_id ==
                                                                                                              '2').all()

    return render_template('javateam.html', javadevs=javadevs)

@app.route('/teams')
def AllTeams():

    teams = Team.query.all()
    return render_template('teamlist.html', teams=teams)


@app.route('/teams/<int:chosen_id>')
def Teaminfo(chosen_id):
    teaminfo = Team.query.filter_by(team_id=chosen_id).first()
    allMembers = User.query.with_entities(User.user_id, User.name, User.email, User.jobTitle).filter(User.team_id == chosen_id).all()
    if teaminfo:
        return render_template('team.html', teaminfo=teaminfo, allMembers=allMembers)
    return f"No Team with id {chosen_id} in system"



@app.route('/newticket', methods=['GET', 'POST'])
def addNewTicket():
    teamList = Team.query.all()
    #teamList = Team.query.with_entities(Team.team_id, Team.team_name).all()
    if request.method == 'GET':
        return render_template('newTicket.html', teamList=teamList)

    if request.method == 'POST':
        user_id = request.form['user_id']
        description = request.form['description']
        state = "Open"
        team_id = request.form['team_id']
        contact_num = request.form['contact_num']
        priority = request.form['priority']
        summary = request.form['summary']
        environment = request.form['environment']
        ticket_sp_instruction = request.form['ticket_sp_instruction']

        if user_id == "" or description == "" or team_id == "":
            return 'Please go back and enter values for fields'

        else:
            newTickets = TestTicket(user_id=user_id, description=description, state=state, team_id=team_id, contact_num=contact_num,
                           priority=priority, summary=summary, environment=environment, ticket_sp_instruction=ticket_sp_instruction)

            db.session.add(newTickets)
            db.session.commit()
            return redirect('/opentickets')


@app.route('/opentickets')
def allOpenTickets():
    tickets = TestTicket.query.all()

    openTickets = TestTicket.query.with_entities(TestTicket.ticket_id, TestTicket.user_id,  User.name, TestTicket.ticket_created, TestTicket.description,
                  TestTicket.state, TestTicket.team_id, Team.team_name, User.email, TestTicket.priority, TestTicket.summary,
                                                  TestTicket.environment, TestTicket.ticket_sp_instruction).join(Team,
                  TestTicket.team_id == Team.team_id).join(User, TestTicket.user_id == User.user_id).filter(TestTicket.state == 'Open').all()

    progTickets = TestTicket.query.with_entities(TestTicket.ticket_id, TestTicket.user_id,  User.name, TestTicket.ticket_created, TestTicket.description,
                  TestTicket.state, TestTicket.team_id, Team.team_name, User.email, TestTicket.priority, TestTicket.summary,
                                                  TestTicket.environment, TestTicket.ticket_sp_instruction).join(Team,
                  TestTicket.team_id == Team.team_id).join(User, TestTicket.user_id == User.user_id).filter(TestTicket.state == 'In Progress').all()

    return render_template('openTickets.html', openTickets=openTickets, progTickets=progTickets, tickets=tickets)


@app.route('/ticket/<int:chosen_ticket_id>', methods=['GET', 'POST'])
def viewTicket(chosen_ticket_id):
    ticketinfo = TestTicket.query.with_entities(TestTicket.ticket_id, TestTicket.user_id,  User.name, TestTicket.ticket_created, TestTicket.description,
                  TestTicket.state, TestTicket.team_id, Team.team_name, User.email, TestTicket.contact_num, TestTicket.priority, TestTicket.summary,
                                                  TestTicket.environment, TestTicket.ticket_sp_instruction).join(Team,
                  TestTicket.team_id == Team.team_id).join(User, TestTicket.user_id == User.user_id).filter(TestTicket.ticket_id == chosen_ticket_id).all()
    updatedescription = TestTicket.query.with_entities(TestTicket.description).filter(TestTicket.ticket_id == chosen_ticket_id).first()
    teamList = Team.query.all()

    if request.method == 'GET':
        if ticketinfo:
            return render_template('ticket.html', ticketinfo=ticketinfo, teamList=teamList)
    # return f"No Ticket with id {chosen_ticket_id} in system"

    if request.method == 'POST':
        # user_id = request.form['user_id']
        # description = request.form['description']
        state = request.form['state']
        # team_id = request.form['team_id']
        # contact_num = request.form['contact_num']
        #priority = request.form['priority']
        # summary = request.form['summary']
        # environment = request.form['environment']
        # ticket_sp_instruction = request.form['ticket_sp_instruction']

        # if user_id == "" or description == "" or team_id == "":
        #     return 'Please go back and enter values for fields'

        # else:
        #     updateTicket = TestTicket(user_id=user_id, description=description, state=state, team_id=team_id, contact_num=contact_num,
        #                    priority=priority, summary=summary, environment=environment, ticket_sp_instruction=ticket_sp_instruction)

        db.session.query(TestTicket).filter(TestTicket.ticket_id == chosen_ticket_id).update({TestTicket.state: state})
        db.session.commit()
        return redirect('/opentickets')


if __name__ == '__main__':
    app.run(debug=True)
