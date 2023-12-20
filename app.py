from flask import Flask, make_response, render_template, session, redirect, url_for, request
from functools import wraps
from datetime import date, timedelta
from config import *
from dataOperations import *
import hashlib

app = Flask(__name__)
app.secret_key = appSecret
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax'
)


def auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # redirect user to login page if they are not logged in
        if not 'user' in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# prevent user from going back to pages that require auth after they logout
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0, s-maxage=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


def getObjectByValue(objects, value, attribute):
    for obj in objects:
        if obj.get(attribute) == value:
            return obj
    return None


def getObjectsByValue(objects, value, attribute):
    objectList = []
    for obj in objects:
        if obj.get(attribute) == value:
            objectList.append(obj)
    return objectList


# app's home page
@app.route('/', methods=['GET', 'POST'])
@auth
def home():
    # fetch saunas from db
    saunas = fetchSaunas()

    # set the dates for calendar
    today = date.today()
    dates = []
    for i in range(7):
        newDate = today + timedelta(days=i)
        dates.append(newDate.strftime("%Y-%m-%d"))

    resDict = {}

    # handle changing the sauna selection
    if request.method == 'POST':
        id = int(request.form.get('sauna'))
        currentSauna = getObjectByValue(saunas, id, 'id')

        # save the sauna selection to the session
        session['sauna'] = currentSauna
        reservations = fetchReservations(id)
        reservs = getObjectsByValue(reservations, id, 'saunaid')

        tokens = fetchUserTokensCount(session['user']['id'])

        for obj in reservs:
            time = obj.get('time')
            user = obj.get('userid')
            resDict[time] = {'userid': user, 'id': obj.get('id')}

        return make_response(render_template('home.html', tokens=tokens, saunas=saunas, currentSauna=currentSauna, dates=dates, reservations=resDict))

    # get request
    if not 'sauna' in session:
        currentSauna = saunas[0]
    else:
        currentSauna = session['sauna']
    
    reservations = fetchReservations(int(currentSauna.get('id')))
    reservs = getObjectsByValue(reservations, currentSauna.get('id'), 'saunaid')

    tokens = fetchUserTokensCount(session['user']['id'])

    for obj in reservs:
        time = obj.get('time')
        user = obj.get('userid')
        resDict[time] = {'userid': user, 'id': obj.get('id')}

    return make_response(render_template('home.html', tokens=tokens, saunas=saunas, currentSauna=currentSauna, dates=dates, reservations=resDict))


@app.route('/booksauna', methods=['GET', 'POST'])
@auth
def booksauna():
    tokens = fetchUserTokensCount(session['user']['id'])

    if request.method == 'POST':
        saunaId = request.form.get('saunaid')
        userId = request.form.get('userid')
        timeString = request.form.get('time')

        user = fetchUserById(int(userId))

        # if user exists, and has tokens, create reservation
        if user and tokens > 0:
            createReservation(saunaId, userId, timeString)

        return redirect(url_for('home'))
    
    if not request.args:
        return redirect(url_for('home'))

    # fetch saunas from db
    saunas = fetchSaunas()
    saunaId = request.args.get('sauna')
    time = request.args.get('time')
        

    sauna = getObjectByValue(saunas, int(saunaId), 'id')
       
    return make_response(render_template('booksauna.html', tokens=tokens, sauna=sauna, time=time))


@app.route('/cancelsauna', methods=['GET', 'POST'])
@auth
def cancelsauna():
    tokens = fetchUserTokensCount(session['user']['id'])

    if request.method == 'POST':
        resId = request.form.get('resid')
        saunaId = request.form.get('saunaid')

        if cancelReservation(saunaId, resId):
            return redirect(url_for('home'))


    if not request.args:
        return redirect(url_for('home'))
    
    resid = request.args.get('resid')
    saunaid = request.args.get('saunaid')

    # fetch saunas from db
    saunas = fetchSaunas()
    reservations = fetchReservations(int(saunaid))
    sauna = getObjectByValue(saunas, int(saunaid), 'id')
    currentRes = getObjectByValue(reservations, resid, 'id')

    return make_response(render_template('cancelsauna.html', tokens=tokens, sauna=sauna, reservation=currentRes))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = False

    # handling POST request
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        user = fetchUser(username)

        # if user with given username exists, check password
        if user:
            hash = hashlib.sha512()
            hash.update(password.encode('UTF-8'))
            hash.update(str(user['id']).encode("UTF-8"))

            # if password correct, redirect to homepage
            if hash.hexdigest() == user['password']:
                session['user'] = user
                session['user']['id'] = int(session['user']['id'])

                # delete old reservations from system if found
                deleteOldReservations()
                return redirect(url_for('home'))
            else:
                error = True
            
        else:
            error = True
       
    return make_response(render_template('login.html', error=error))


@app.route('/logout')
def logout():
   session.clear()
   return redirect(url_for('login'))


if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5000)