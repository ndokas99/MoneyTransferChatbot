from flask import Flask, current_app, render_template, redirect, request, session, flash, \
    make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, OperationalError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from prompts import *
from os import path


app = Flask(__name__)
settings = {
    "SECRET_KEY": 'SDD89HE0J7G83NHF779JNG00G',
    "SQLALCHEMY_DATABASE_URI": 'sqlite:///database.db',
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
}
app.config.update(settings)
db = SQLAlchemy(app)


class Accounts(db.Model):
    accId = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    surname = db.Column(db.Text, nullable=False)
    nationalId = db.Column(db.Text, unique=True, nullable=False)
    pin = db.Column(db.Text, nullable=False)


class Transactions(db.Model):
    reference = db.Column(db.Text, primary_key=True)
    agent = db.Column(db.Text, nullable=False)
    phoneNumber = db.Column(db.Text, nullable=False)
    nationalId = db.Column(db.Text, unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    name = db.Column(db.Text, nullable=False)
    surname = db.Column(db.Text, nullable=False)
    dateOfBirth = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text, nullable=False)


class Collection(db.Model):
    reference = db.Column(db.Text, primary_key=True)
    address = db.Column(db.Text, nullable=False)


class Interface:

    def __init__(self):
        self.agencies = ['Mukuru', 'InnBucks', 'World Remit', 'Access Forex']

    def menu(self, text):
        if text == "1":
            session["option"] = 1
            session['step'] = 'name'
            session['create'] = []
            return self.createAcc(text)
        elif text == "2":
            session["option"] = 2
            session['step'] = 'login_no'
            session['login'] = []
            return self.login(text)
        elif text == "3":
            session["code"], session['step'], session['option'] = "intro", '', 0
            return say_goodbye
        else:
            pass

    def createAcc(self, text):
        if session['step'] == 'name':
            session['step'] = 'surname'
            return ask_name
        elif session['step'] == 'surname':
            session['create'].append(text)
            session['step'] = 'phone'
            return ask_surname
        elif session['step'] == 'phone':
            session['create'].append(text)
            session['step'] = 'natId'
            return ask_phone_no
        elif session['step'] == 'natId':
            session['create'].append(text)
            session['step'] = 'pin'
            return ask_natId
        elif session['step'] == 'pin':
            session['create'].append(text)
            session['step'] = 'success'
            return ask_pin
        elif session['step'] == 'success':
            session['create'].append(text)
            acc = Accounts(
                accId=session['create'][2],
                name=session['create'][0],
                surname=session['create'][1],
                nationalId=session['create'][3],
                pin=generate_password_hash(session['create'][4], method="sha1")
            )
            db.session.add(acc)
            db.session.commit()
            session["code"], session['step'], session['option'] = "intro", '', 0
            return acc_creation_succ
        else:
            pass

    def login(self, text):
        if session['step'] == 'login_no':
            session['step'] = 'login_pin'
            return ask_login_no
        elif session['step'] == 'login_pin':
            session['login'].append(text)
            session['step'] = 'success'
            return ask_login_pin
        elif session['step'] == 'success':
            session['login'].append(text)
            acc = Accounts.query.filter_by(accId=session['login'][0]).first()
            if check_password_hash(acc.pin, session['login'][1]):
                session["code"], session['step'], session['option'] = "txn", 'agent', 0
                return ask_agent
            else:
                session['step'] = 'login_pin'
                session['login'] = []
                return login_failure
        else:
            pass

    def enterDetails(self, text):
        if session['step'] == 'agent':
            if text in ['1', '2', '3', '4']:
                session['details'] = []
                session['details'].append(self.agencies[int(text) - 1])
                session['step'] = 'reference'
                return ask_reference
            else:
                session['step'] = 'agent'
                return ask_agent
        elif session['step'] == 'reference':
            session['details'].append(text)
            session['step'] = 'name'
            return ask_name
        elif session['step'] == 'name':
            session['details'].append(text)
            session['step'] = 'surname'
            return ask_surname
        elif session['step'] == 'surname':
            session['details'].append(text)
            session['step'] = 'phone'
            return ask_phone_no
        elif session['step'] == 'phone':
            session['details'].append(text)
            session['step'] = 'natId'
            return ask_natId
        elif session['step'] == 'natId':
            session['details'].append(text)
            session['step'] = 'dob'
            return ask_dob
        elif session['step'] == 'dob':
            session['details'].append(text)
            session['step'] = 'amount'
            return ask_amount
        elif session['step'] == 'amount':
            session['details'].append(float(text))
            session['step'] = 'addr'
            return ask_address
        elif session['step'] == 'addr':
            txn = Transactions.query.filter_by(
                reference=session['details'][1], agent=session['details'][0], phoneNumber=session['details'][4],
                nationalId=session['details'][5], amount=session['details'][7], name=session['details'][2],
                surname=session['details'][3], dateOfBirth=session['details'][6]
            ).first()
            if txn:
                if txn.status == "COLLECTED":
                    session['step'] = 'agent'
                    return already_collected
                else:
                    txn.status = 'COLLECTED'
                    coll = Collection(
                        reference=session['details'][1],
                        address=text,
                    )
                    db.session.add(coll)
                    db.session.commit()
                    session["code"], session['step'], session['option'] = "intro", '', 0
                    return txn_success + text
            else:
                session['step'] = 'agent'
                return txn_failure
        else:
            pass


@app.route('/')
def index():
    session["code"] = "intro"
    session["step"] = ''
    session["option"] = 0
    return render_template("index.html")


@app.route('/query', methods=['POST'])
def query():
    text = request.get_json()["resp"]
    resp = ""
    if session["code"] == "intro":
        session['code'] = "menu"
        resp = say_welcome
    elif session["code"] == "menu":
        if session['option'] == 0:
            resp = current_app.interface.menu(text)
        elif session['option'] == 1:
            resp = current_app.interface.createAcc(text)
        elif session['option'] == 2:
            resp = current_app.interface.login(text)
    elif session["code"] == "txn":
        resp = current_app.interface.enterDetails(text)

    response = {'answer': resp}
    return make_response(jsonify(response))


def create_database():
    if not path.exists("/instance/database.db"):
        try:
            db.create_all()
        except IntegrityError:
            pass
        except OperationalError:
            pass


if __name__ == '__main__':
    with app.app_context():
        create_database()
        app.interface = Interface()
        app.run('0.0.0.0', debug=True)
