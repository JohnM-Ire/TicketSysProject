from flask import Flask, render_template, request, redirect, flash, session, sessions
from sqlalchemy.sql import select, alias, desc, or_, and_

import ssl
from email.message import EmailMessage
import smtplib
# from flask_sqlalchemy import SQLAlchemy
from TicketDB import db, User, Team, Ticket, TComment, TeamChat

import itertools
import jinja2

app = Flask(__name__)
app.secret_key = "bbrm36hy"

# app.config['SECRET_KEY'] = "JohnKey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jMovie.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TicketDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.before_first_request
def create_table():
    # db.session.query(Ticket).delete()
    # db.session.commit()
    # db.drop_all()
    db.create_all()



@app.route('/', methods=['GET', 'POST'])
def home():
    if "user" not in session:
        return redirect('/login')
    else:
        user = session["user"]

        loggedteam = User.query.with_entities(User.team_id).filter(User.user_id == user).all()
        loggedteam = str(loggedteam)
        loggedteam = loggedteam.strip("[ ] , ( )")
        username = User.query.with_entities(User.name).filter(User.user_id == user).all()
        username = str(username)
        username = username.strip("[ ] , ( ) '")

        openTickets = Ticket.query.with_entities(Ticket.ticket_id, Ticket.user_id, User.name, Ticket.
                                                 ticket_created, Ticket.description, Ticket.state, Ticket.team_id,
                                                 Team.team_name, User.
                                                 email, Ticket.priority, Ticket.summary, Ticket.environment,
                                                 Ticket.ticket_sp_instruction).join(Team, Ticket.team_id == Team.team_id)\
                                                .join(User, Ticket.user_id == User.user_id).filter(
                                                and_(Ticket.state == 'Open', Ticket.team_id == loggedteam)).limit(3).all()

        openTicketsCount = Ticket.query.with_entities(Ticket.ticket_id, Ticket.user_id, Ticket.team_id).join(Team,
                                                Ticket.team_id == Team.team_id).join(User, Ticket.user_id == User.
                                                user_id).filter(and_(Ticket.state == 'Open', Ticket.team_id ==
                                                loggedteam)).count()

        progTickets = Ticket.query.with_entities(Ticket.ticket_id, Ticket.user_id, User.name, Ticket
                                                 .ticket_created, Ticket.description, Ticket.state, Ticket.team_id,
                                                 Team.team_name, User.email, Ticket.priority, Ticket.summary,
                                                 Ticket.environment, Ticket.ticket_sp_instruction).join(Team,
                                                Ticket.team_id == Team.team_id).join(User, Ticket.user_id == User.
                                                user_id).filter(and_(Ticket.state == 'In Progress'), (Ticket.team_id
                                                == loggedteam)).limit(2).all()

        progTicketsCount = Ticket.query.with_entities(Ticket.ticket_id, Ticket.user_id, Ticket.team_id).join(Team,
                                                Ticket.team_id == Team.team_id).join(User, Ticket.user_id == User.
                                                user_id).filter(and_(Ticket.state == 'In Progress'), (Ticket.
                                                team_id == loggedteam)).count()

        # waitTickets = Ticket.query.with_entities(Ticket.ticket_id, Ticket.user_id, User.name, Ticket
        #                                          .ticket_created, Ticket.description, Ticket.state, Ticket.team_id,
        #                                          Team.team_name, User.email, Ticket.priority, Ticket.summary, Ticket.environment, Ticket
        #                                          .ticket_sp_instruction).join(Team,Ticket.team_id == Team.team_id).join(User,
        #                                         Ticket.user_id == User.user_id).filter(and_(Ticket.state == 'Waiting'),
        #                                         (Ticket.team_id == loggedteam)).limit(2).all()

        closedTicketsCount = Ticket.query.with_entities(Ticket.ticket_id, Ticket.user_id, Ticket.team_id).join(Team,
                                                   Ticket.team_id == Team.team_id).join(User, Ticket.user_id == User.
                                                   user_id).filter(and_(or_(Ticket.state == 'Fulfilled', Ticket.state ==
                                                   'Closed Incomplete'), Ticket.team_id == loggedteam)).count()

        myClosedTicketsCount = Ticket.query.with_entities(Ticket.ticket_id, Ticket.user_id, User.name, Ticket.
                                ticket_created, Ticket.description, Ticket.state, Ticket.team_id,
                                Team.team_name, User.email, Ticket.priority, Ticket.summary, Ticket.environment,
                                Ticket.ticket_sp_instruction).join(Team, Ticket.team_id == Team.team_id).join(User, Ticket.
                                user_id == User.user_id).filter(and_(or_(Ticket.state == 'Fulfilled', Ticket.state ==
                     'Closed Incomplete'), Ticket.user_id == user, Ticket.team_id != loggedteam)).count()

        total_closed = int(closedTicketsCount) + int(myClosedTicketsCount)
        return render_template('home.html', user=user, openTickets=openTickets, openTicketsCount=openTicketsCount,
                               progTickets=progTickets, progTicketsCount=progTicketsCount,
                               closedTicketsCount=closedTicketsCount, total_closed=total_closed, username=username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        loginemail = request.form['email']
        loginpassword = request.form['password']

        if db.session.query(User.user_id).filter_by(email=loginemail, password=loginpassword).first() is not None:
            user = User.query.with_entities(User.user_id).filter_by(email=loginemail, password=loginpassword).first()
            user = str(user)
            user = user.strip(", ( )")
            session['user'] = user

            return redirect('/')

        else:
            return 'Incorrect Login Details, Please Go Back'


@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect('/login')


@app.route('/adduser', methods=['GET', 'POST'])
def addUser():
    teams = Team.query.all()

    if request.method == 'GET':
        return render_template('addUser.html', teams=teams)

    if request.method == 'POST':
        username = "n/a"
        name = request.form['name']
        email = request.form['email']
        jobTitle = request.form['jobTitle']
        password = request.form['password']
        tasksComplete = 0
        team_id = request.form['team_id']
        if name == "" or email == "" or jobTitle == "" or password == "":
            return 'Please go back and enter values for all fields'

        elif db.session.query(User.email).filter_by(email=email).first() is not None:
            return 'The email you have entered already exists for another user.\n ' \
                   'please go back and choose a different email'

        else:
            newuser = User(username=username, name=name, email=email, jobTitle=jobTitle, password=password,
                           tasksComplete=tasksComplete, team_id=team_id)

            db.session.add(newuser)
            db.session.commit()
            return redirect('/login')

@app.route('/deluser/<int:user_id>', methods=['GET', 'POST'])
def DeleteSingleUser(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if request.method == 'POST':
        if user:
            db.session.delete(user)
            db.session.commit()
            return redirect('/admin_data')

    return render_template('deleteUser.html', user=user)


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

# NEED TO ACCOUNT FOR IF WE DELETE A TEAM WHAT HAPPENS TO THE USERS ASSIGNED TO THOSE TEAMS
# @app.route('/delteam/<int:user_id>', methods=['GET', 'POST'])
# def DeleteSingleTeam(team_id):
#     team = Team.query.filter_by(user_id=user_id).first()
#     if request.method == 'POST':
#         if user:
#             db.session.delete(user)
#             db.session.commit()
#             return redirect('/admin_data')
#
#     return render_template('deleteUser.html', user=user)

@app.route('/admin_data')
def retrieveUsers():
    teams = Team.query.all()
    users = User.query.all()

    return render_template('admin_data.html', users=users, teams=teams)

# USED ONLY FOR TESTING
@app.route('/team/javadev')
def retrieveJava():
    javadevs = Team.query.with_entities(Team.team_id, Team.team_name, Team.team_category, User.user_id, User.name, User.
                email, User.jobTitle).join(User, Team.team_id == User.team_id).filter(Team.team_id == '2').all()

    return render_template('javateam.html', javadevs=javadevs)


@app.route('/teams')
def AllTeams():
    teams = Team.query.all()
    return render_template('teamlist.html', teams=teams)


@app.route('/teamchat', methods=['GET', 'POST'])
def teamChat():

    user = session["user"]

    loggedteam = User.query.with_entities(User.team_id).filter(User.user_id == user).all()
    loggedteam = str(loggedteam)
    loggedteam = loggedteam.strip("[ ] , ( )")

    username = User.query.with_entities(User.name).filter(User.user_id == user).all()
    username = str(username)
    username = username.strip("[ ] , ( ) '")

    teamComments = TeamChat.query.with_entities(TeamChat.teamcomment_id, TeamChat.comment, TeamChat.user_id,
                                                TeamChat.timecreated, User.name, User.team_id).join(User, TeamChat.
                                                user_id == User.user_id).filter(TeamChat.team_id == loggedteam).\
                                                order_by(desc(TeamChat.timecreated)).all()


    if request.method == 'GET':
        return render_template('teamChat.html', teamComments=teamComments, username=username)

    if request.method == 'POST':
        user_id = user
        team_id = loggedteam
        comment = request.form['comment']

        if comment == "":
            return 'Please go back and enter comment'

        else:
            newTeamComment = TeamChat(user_id=user_id, team_id=team_id, comment=comment)

        db.session.add(newTeamComment)
        db.session.commit()
        return redirect('/teamchat')


@app.route('/teams/<int:chosen_id>', methods=['GET', 'POST'])
def Teaminfo(chosen_id):


    teaminfo = Team.query.filter_by(team_id=chosen_id).first()
    allMembers = User.query.with_entities(User.user_id, User.name, User.email, User.jobTitle).filter(User.team_id ==
                    chosen_id).all()

    all_emails = User.query.with_entities(User.email).filter(User.team_id ==
                    chosen_id).all()
    groupemail_list = []
    for email in all_emails:
        email = str(email)
        email = email.strip("[ ] , ', ( )")
        groupemail_list.append(email)


    # if teaminfo:
    #     return render_template('team.html', teaminfo=teaminfo, allMembers=allMembers)
    # return f"No Team with id {chosen_id} in system"

    if request.method == 'GET':
        return render_template('team.html', teaminfo=teaminfo, allMembers=allMembers)

    if request.method == 'POST':
        team_email_message = request.form['team_email_message']
        if team_email_message == "":
            return 'Please go back and enter your message'
        user = session["user"]

        username = User.query.with_entities(User.name).filter(User.user_id == user).all()
        username = str(username)
        username = username.strip("[ ] , ( ) '")
        email_source = 'ticketsysJM@gmail.com'
        password = 'nwggowjpxnhpgvcv'
        email_list = ['johnamurphy0185@gmail.com', 'john.a.murphy.1989@gmail.com]']

        email_subj = 'Team Message'
        email_body = 'To be sent to ' + str(groupemail_list) + '\nMessage from ' + username + '\nMessage:\n' + team_email_message +\
                     '\nThank you,\nTicket Sys Team'
        email = EmailMessage()
        email['From'] = email_source
        email['To'] = ", ".join(email_list)
        email['Subject'] = email_subj
        email.set_content(email_body)

        securitycont = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=securitycont) as smtp:
            smtp.login(email_source, password)
            smtp.sendmail(email_source, email_list, email.as_string())

        return redirect(request.url)

@app.route('/newticket', methods=['GET', 'POST'])
def addNewTicket():

    user = session['user']

    teamList = Team.query.all()

    if request.method == 'GET':
        return render_template('newTicket.html', teamList=teamList)

    if request.method == 'POST':
        user_id = user
        description = request.form['description']
        state = "Open"
        team_id = request.form['team_id']
        contact_num = request.form['contact_num']
        priority = request.form['priority']
        summary = request.form['summary']
        environment = request.form['environment']
        ticket_sp_instruction = request.form['ticket_sp_instruction']
        # assigned_to = "unassigned"

        if user_id == "" or description == "" or team_id == "":
            return 'Please go back and enter values for fields'

        else:
            newTickets = Ticket(user_id=user_id, description=description, state=state, team_id=team_id, contact_num=contact_num,
                           priority=priority, summary=summary, environment=environment, ticket_sp_instruction=ticket_sp_instruction)

            db.session.add(newTickets)
            db.session.commit()
            return redirect('/opentickets')


@app.route('/opentickets')
def allOpenTickets():
    tickets = Ticket.query.all()
    user = session["user"]

    loggedteam = User.query.with_entities(User.team_id).filter(User.user_id == user).all()
    loggedteam = str(loggedteam)
    loggedteam = loggedteam.strip("[ ] , ( )")
    team_name = Team.query.with_entities(Team.team_name).filter(Team.team_id == loggedteam).all()
    team_name = str(team_name)
    team_name = team_name.strip("[ ] , ( ), '")

    openTickets = Ticket.query.with_entities(Ticket.ticket_id, Ticket.user_id,  User.name, Ticket.
                    ticket_created, Ticket.description, Ticket.state, Ticket.team_id, Team.team_name, User.
                    email, Ticket.priority, Ticket.summary, Ticket.environment, Ticket.ticket_sp_instruction)\
                    .join(Team, Ticket.team_id == Team.team_id).join(User, Ticket.
                    user_id == User.user_id).filter(and_(Ticket.state == 'Open', Ticket.team_id == loggedteam)).all()

    progTickets = Ticket.query.with_entities(Ticket.ticket_id, Ticket.user_id,  User.name, Ticket
                    .ticket_created, Ticket.description, Ticket.state, Ticket.team_id, Team.team_name, User
                    .email, Ticket.priority, Ticket.summary, Ticket.environment, Ticket
                    .ticket_sp_instruction).join(Team, Ticket.team_id == Team.team_id).join(User, Ticket
                    .user_id == User.user_id).filter(and_(Ticket.state == 'In Progress'), (Ticket.team_id == loggedteam)).all()
    waitTickets = Ticket.query.with_entities(Ticket.ticket_id, Ticket.user_id,  User.name, Ticket
                    .ticket_created, Ticket.description, Ticket.state, Ticket.team_id, Team.team_name, User
                    .email, Ticket.priority, Ticket.summary, Ticket.environment, Ticket
                    .ticket_sp_instruction).join(Team, Ticket.team_id == Team.team_id).join(User, Ticket
                    .user_id == User.user_id).filter(and_(Ticket.state == 'Waiting'), (Ticket.team_id == loggedteam)).all()

    myTickets = Ticket.query.with_entities(Ticket.ticket_id, Ticket.user_id,  User.name, Ticket
                    .ticket_created, Ticket.description, Ticket.state, Ticket.team_id, Team.team_name, User
                    .email, Ticket.priority, Ticket.summary, Ticket.environment, Ticket
                    .ticket_sp_instruction).join(Team, Ticket.team_id == Team.team_id).join(User, Ticket
                    .user_id == User.user_id).filter(and_(Ticket.user_id == user), (Ticket.state != 'Fulfilled'),
                    (Ticket.state != 'Closed Incomplete')).all()


    return render_template('openTickets.html', openTickets=openTickets, progTickets=progTickets, waitTickets=waitTickets,
                           myTickets=myTickets, team_name=team_name)


@app.route('/ticket/<int:chosen_ticket_id>', methods=['GET', 'POST'])
def viewTicket(chosen_ticket_id):
    ticketinfo = Ticket.query.with_entities(Ticket.ticket_id, Ticket.user_id,  User.name, Ticket.ticket_created,
                  Ticket.description, Ticket.state, Ticket.team_id, Team.team_name, User.email,
                 Ticket.contact_num, Ticket.priority, Ticket.summary, Ticket.environment, Ticket.ticket_sp_instruction)\
                 .join(Team,Ticket.team_id == Team.team_id).join(User, Ticket.user_id == User.user_id).filter\
        (Ticket.ticket_id == chosen_ticket_id).all()

    teamList = Team.query.all()
    allComments = TComment.query.with_entities(TComment.comm_id, TComment.ticket_id, TComment.comment, TComment.user_id, TComment
                                               .timecreated, User.name).join(User, TComment.user_id == User.user_id).filter(TComment.ticket_id == chosen_ticket_id)\
        .order_by(desc(TComment.timecreated)).all()


    if request.method == 'GET':
        if ticketinfo:
            return render_template('ticket.html', ticketinfo=ticketinfo, teamList=teamList, allComments=allComments)

    if request.method == 'POST':
        comment = request.form['comment']
        user_id = session['user']
        ticket_id = chosen_ticket_id



        if comment == "":
            return 'Please go back and enter values for fields'

        else:
            newComment = TComment(comment=comment, user_id=user_id, ticket_id=ticket_id)

        db.session.add(newComment)
        db.session.commit()
        return redirect(request.url)




@app.route('/editticket/<int:chosen_ticket_id>', methods=['GET', 'POST'])
def editTicket(chosen_ticket_id):
    ticketinfo = Ticket.query.with_entities(Ticket.ticket_id, Ticket.user_id,  User.name, Ticket.ticket_created, Ticket.description,
                    Ticket.state, Ticket.team_id, Team.team_name, User.email, Ticket.contact_num, Ticket.priority, Ticket.summary,
                    Ticket.environment, Ticket.ticket_sp_instruction).join(Team,Ticket.team_id == Team.
                    team_id).join(User, Ticket.user_id == User.user_id).filter(Ticket.ticket_id == chosen_ticket_id).all()

    ticketDesc = Ticket.query.with_entities(Ticket.description).filter(Ticket.ticket_id == chosen_ticket_id).all()
    ticketDesc = str(ticketDesc)
    ticketDesc = ticketDesc.strip("[ ] , ( ) '")

    ticketrequester_email = User.query.with_entities(User.email).join(Ticket, User.user_id == Ticket.user_id).filter(Ticket
                        .ticket_id == chosen_ticket_id).all()
    ticketrequester_email = str(ticketrequester_email)
    ticketrequester_email = ticketrequester_email.strip("[ ] , ( ) '")

    teamList = Team.query.all()

    user = session["user"]
    username = User.query.with_entities(User.name).filter(User.user_id == user).all()
    username = str(username)
    username = username.strip("[ ] , ( ) '")

    loggedteam = User.query.with_entities(User.team_id).filter(User.user_id == user).all()
    loggedteam = str(loggedteam)
    loggedteam = loggedteam.strip("[ ] , ( )")

    allMembers = User.query.with_entities(User.name).filter(User.team_id == loggedteam).all()
    emails = [('john.a.murphy.1989@gmail.com',), ('johnamurphy0185@gmail.com',)]

    if request.method == 'GET':
        if ticketinfo:
            return render_template('editTicket.html', ticketinfo=ticketinfo, teamList=teamList, allMembers=allMembers)
    # return f"No Ticket with id {chosen_ticket_id} in system"

    if request.method == 'POST':
        state = request.form['state']
        if state == 'Fulfilled':
            email_source = 'ticketsysJM@gmail.com'
            password = 'nwggowjpxnhpgvcv'
            email_list = 'johnamurphy0185@gmail.com'

            email_subj = 'Your Job ticket ' + str(chosen_ticket_id) + ' request has been fulfilled'
            email_body = 'To be sent to ' + ticketrequester_email + '\n\nYour Job ticket number '\
                         + str(chosen_ticket_id) + ' has been fulfilled by ' + username + '.\n\nTicket Description:\n'\
                         + ticketDesc + '\nThank you,\nTicket Sys Team.'

            email = EmailMessage()
            email['From'] = email_source
            email['To'] = email_list
            email['Subject'] = email_subj
            email.set_content(email_body)

            securitycont = ssl.create_default_context()

            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=securitycont) as smtp:
                smtp.login(email_source, password)
                smtp.sendmail(email_source, email_list, email.as_string())

            # look to add the update to the closed ticket table here
        team_id = request.form['team_id']
        priority = request.form['priority']
        environment = request.form['environment']
        db.session.query(Ticket).filter(Ticket.ticket_id == chosen_ticket_id).update({Ticket.state: state})
        db.session.query(Ticket).filter(Ticket.ticket_id == chosen_ticket_id).update({Ticket.team_id: team_id})
        db.session.query(Ticket).filter(Ticket.ticket_id == chosen_ticket_id).update({Ticket.priority: priority})
        db.session.query(Ticket).filter(Ticket.ticket_id == chosen_ticket_id).update({Ticket.environment: environment})

        db.session.commit()
        return redirect('/opentickets')


@app.route('/closedtickets')
def closedTickets():
    tickets = Ticket.query.all()
    user = session["user"]

    loggedteam = User.query.with_entities(User.team_id).filter(User.user_id == user).all()
    loggedteam = str(loggedteam)
    loggedteam = loggedteam.strip("[ ] , ( )")

    team_name = Team.query.with_entities(Team.team_name).filter(Team.team_id == loggedteam).all()
    team_name = str(team_name)
    team_name = team_name.strip("[ ] , ( ), '")

    closedTickets = Ticket.query.with_entities(Ticket.ticket_id, Ticket.user_id,  User.name, Ticket.
                    ticket_created, Ticket.description, Ticket.state, Ticket.team_id, Team.team_name, User.
                    email, Ticket.priority, Ticket.summary, Ticket.environment, Ticket.ticket_sp_instruction)\
                    .join(Team, Ticket.team_id == Team.team_id).join(User, Ticket.
                    user_id == User.user_id).filter(and_(or_(Ticket.state == 'Fulfilled', Ticket.state ==
                    'Closed Incomplete'), Ticket.team_id == loggedteam)).all()
    myClosedTickets = Ticket.query.with_entities(Ticket.ticket_id, Ticket.user_id,  User.name, Ticket.
                    ticket_created, Ticket.description, Ticket.state, Ticket.team_id, Team.team_name, User.
                    email, Ticket.priority, Ticket.summary, Ticket.environment, Ticket.ticket_sp_instruction)\
                    .join(Team, Ticket.team_id == Team.team_id).join(User, Ticket.
                    user_id == User.user_id).filter(and_(or_(Ticket.state == 'Fulfilled', Ticket.state ==
                    'Closed Incomplete'), Ticket.user_id == user, Ticket.team_id != loggedteam)).all()

    return render_template('closedTicket.html', closedTickets=closedTickets, myClosedTickets=myClosedTickets, team_name=team_name)


if __name__ == '__main__':
    app.run(debug=True)
