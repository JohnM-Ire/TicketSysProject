import ssl
from email.message import EmailMessage
import smtplib
email_source = 'ticketsysJM@gmail.com'
password = 'nwggowjpxnhpgvcv'
email_list = 'johnamurphy0185@gmail.com'

email_subj = 'Your Job ticket request has been fulfilled'
email_body = """
Your Job ticket number <Var> has been fulfilled by <Var>
<Ticket Description>
<Current Time/Date>

Thank you,
Ticket Sys Team.
"""
email = EmailMessage()
email['From'] = email_source
email['To'] = email_list
email['Subject'] = email_subj
email.set_content(email_body)

securitycont = ssl.create_default_context()


with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=securitycont) as smtp:
    smtp.login(email_source, password)
    smtp.sendmail(email_source, email_list, email.as_string())
