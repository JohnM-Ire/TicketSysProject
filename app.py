from flask import Flask, render_template, request, redirect, flash, session
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


@app.route('/admin/adduser', methods=['GET', 'POST'])
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
        if username == "" or name == "" or email == "" or jobTitle == "" or password == "":
            return 'Please go back and enter values for all fields'
        else:
            newuser = User(username=username, name=name, email=email, jobTitle=jobTitle, password=password,
                           tasksComplete=tasksComplete)

            db.session.add(newuser)
            db.session.commit()
            return redirect('/admin/userList')


@app.route('/admin/addTeam', methods=['GET', 'POST'])
def addTeam():
    if request.method == 'GET':
        return render_template('addTeam.html')

    if request.method == 'POST':
        team_name = request.form['team_name']

        if team_name == "":
            return 'Please go back and enter Team Name'
        else:
            newTeam = Team(team_name=team_name)
            db.session.add(newTeam)
            db.session.commit()
            return redirect('/userList')


@app.route('/admin/userList')
def retrieveUsers():
    teams = Team.query.all()
    users = User.query.all()
    return render_template('userList.html', users=users, teams=teams)


if __name__ == '__main__':
    app.run(debug=True)
