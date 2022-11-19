import ibm_db
from flask import Flask, redirect, render_template, request, url_for, session
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('secrets.env')
load_dotenv(dotenv_path=dotenv_path)
try: 
    conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=0c77d6f2-5da9-48a9-81f8-86b520b87518.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31198;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID="+os.getenv("DBUSERNAME")+";PWD="+os.getenv("DBPASSWORD"),'','')
    print("Connected to IBM DB2, Server Details:")
    server = ibm_db.server_info(conn)

    print ("DBMS_NAME: ", server.DBMS_NAME)
    print ("DBMS_VER:  ", server.DBMS_VER)
    print ("DB_NAME:   ", server.DB_NAME)
except Exception as err:
    print("Error: Cannot connect with IBM DB2", err)

app = Flask(__name__)
app.secret_key = os.urandom(16)

@app.route('/')
def home():
    return render_template("landing.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        sql = "select * from user where username=? and password=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        res = ibm_db.fetch_assoc(stmt)
        if res:
            session['ROLE'] = res['ROLE']
            session['USERID'] = res['USERID']
            return render_template('dashboard.html', username=username, role=res['ROLE'])
        else:
            return render_template('login.html')
    else:
       return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone_no = request.form['phone_no']
        sex = request.form['sex']
        age = request.form['age']
        address = request.form['address']
        blood_group = request.form['blood_group']
        sql = "insert into user(username, email, password, phone, sex, age, role, address, bloodgroup) values(?,?,?,?,?,?,?,?,?)"
        prep_stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(prep_stmt, 1, username)
        ibm_db.bind_param(prep_stmt, 2, email)
        ibm_db.bind_param(prep_stmt, 3, password)
        ibm_db.bind_param(prep_stmt, 4, phone_no)
        ibm_db.bind_param(prep_stmt, 5, sex)
        ibm_db.bind_param(prep_stmt, 6, age)
        ibm_db.bind_param(prep_stmt, 7, "USER")
        ibm_db.bind_param(prep_stmt, 8, address)
        ibm_db.bind_param(prep_stmt, 9, blood_group)
        ibm_db.execute(prep_stmt)

        message = Mail(
        from_email='2019ec0181@svce.ac.in',
        to_emails=email,
        subject='Confirmation Email From Plasma Donor Application.',
        html_content='''

        <h1>You are a Lifesaver, ''' +username+ ''',</h1><br>
        <p> Thank you so much for registering with us </p><br>
        <p> You are now registered user. Now, you can visit our website and login to your profile using the credentials you have registered with.</p>
        <p> You have made a very important step towards making earth a better place! Thank you.</p>
        '''
        )
        try:
            sg = SendGridAPIClient(os.getenv("SENDGRIDAPIKEY"))
            response = sg.send(message=message)
    
        except Exception as e:
            print(e)
        # db post operation
        return redirect(url_for('login'))
    elif request.method == 'GET':
        return render_template('signup.html')

if __name__=='__main__':
    app.run(host="0.0.0.0",debug = True)

