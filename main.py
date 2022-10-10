from flask import Flask, render_template, request, redirect, flash, session
from sqlalchemy.sql import select, alias
# from flask_sqlalchemy import SQLAlchemy
from TicketDB import db, User, Team
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
    return 'Home Page'


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
    return f"No Team with id {id} in system"




if __name__ == '__main__':
    app.run(debug=True)
