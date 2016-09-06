import random
import httplib2
import json
import string
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask import session as login_session
from flask import make_response
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

# Initialize database connection
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

# Read CLIENT_ID from file
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']


# Context Processors

# Make categories avaiable for all templates automatically
@app.context_processor
def inject_categories():
    categories = session.query(Category).all()
    return dict(categories=categories)

# Make login_session available for all templates automatically
@app.context_processor
def inject_session():
    return dict(login_session=login_session)

@app.route('/')
def home_page():
    items = session.query(Item).order_by(desc(Item.created)).limit(5)
    return render_template('index.html', items=items)

@app.route('/category/<int:category_id>')
def category(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return render_template('category.html', category=category, items=items)

@app.route('/category/<int:category_id>/<int:item_id>/')
def category_item(category_id, item_id):
    item = session.query(Item).filter_by(category_id=category_id, id=item_id).one()
    return render_template('category_item.html', item=item)

@app.route('/category/new', methods=['GET', 'POST'])
def new_category():
    if request.method == 'POST':
        if login_session.get('user_id'):
            # use lower() function to convert user input to lowercase
            cat = session.query(Category).filter_by(name=request.form['name'].lower()).first()
            if cat != None:
                flash("Category %s already exists" % cat.name)
                return render_template('new_category.html')
            new_category = Category(name=request.form['name'].lower(),
                                    user_id=login_session.get('user_id'))
            session.add(new_category)
            session.commit()
            flash("New category %s was added sucessfully" % new_category.name)
            return redirect(url_for('home_page'))
        else:
            return redirect(url_for('login'))
    else:
        if login_session.get('user_id'):
            return render_template('new_category.html')
        else:
            flash("Please log in first.")
            return redirect(url_for('login'))

@app.route('/item/new', methods=['GET', 'POST'])
def new_item():
    if request.method == 'POST':
        if login_session.get('user_id'):
            # use lower() function to convert user input to lowercase
            item_to_check = session.query(Item).filter_by(name=request.form['name'].lower()).first()
            if item_to_check != None:
                flash("Item %s already exists" % item_to_check.name)
                return render_template('new_item.html')

            new_item = Item(name=request.form['name'].lower(),
                            category_id=request.form['category'],
                            description=request.form['description'],
                            user_id = login_session.get('user_id'))
            session.add(new_item)
            session.commit()
            flash("Item %s successfully added" % new_item.name)
            return redirect(url_for('home_page'))
        else:
            flash("Please log in first")
            return redirect(url_for('login'))
    else:
        if login_session.get('user_id'):
            return render_template('new_item.html')
        else:
            flash("Please log in first")
            return redirect(url_for('login'))

@app.route('/category/<int:category_id>/<int:item_id>/update', methods=['GET', 'POST'])
def update_item(category_id, item_id):
    item = session.query(Item).filter_by(category_id=category_id, id=item_id).one()
    if request.method == 'POST':
        if login_session.get('user_id') and login_session.get('user_id') == item.user_id:
            if request.form['name']:
                item.name = request.form['name']
            if request.form['description']:
                item.description = request.form['description']
            if request.form['category']:
                item.category_id = request.form['category']
            session.add(item)
            session.commit()
            flash("Item %s successfully updated" % item.name)
            return redirect(url_for("home_page"))
    else:
        if login_session.get('user_id') and login_session.get('user_id') == item.user_id:
            return render_template('update_item.html', category_id=category_id, item=item)
        else:
            return redirect(url_for('error.html'))


@app.route('/category/<int:category_id>/delete', methods=['GET', 'POST'])
def delete_category(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if login_session.get('user_id') and login_session.get('user_id') == category.user_id:
            items_in_category = session.query(Item).filter_by(category_id=category_id).all()
            for item in items_in_category:
                session.delete(item)
                session.commit()
            session.delete(category)
            session.commit()
            flash("Category %s deleted successfully" % category.name)
            return redirect(url_for('home_page'))
    else:
        if login_session.get('user_id') and login_session.get('user_id') == category.user_id:
            return render_template('delete_category.html', category=category)
        else:
            return redirect(url_for('error'))

@app.route('/category/<int:category_id>/<int:item_id>/delete', methods=['GET', 'POST'])
def delete_item(category_id, item_id):
    item = session.query(Item).filter_by(category_id=category_id, id=item_id).one()
    if request.method == 'POST':
        if login_session.get('user_id') and login_session.get('user_id') == item.user_id:
            session.delete(item)
            session.commit()
            flash("Item %s deleted successfully" % item.name)
            return redirect(url_for('home_page'))
    else:
        if login_session.get('user_id') and login_session.get('user_id') == item.user_id:
            category = session.query(Category).filter_by(id=category_id).one()
            return render_template('delete_item.html', category=category, item=item)
        else:
            return redirect(url_for('error.html'))

@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # validate the STATE
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='', redirect_uri='postmessage')
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid
    access_token = credentials.access_token
    url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # In case of error, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user
    google_id = credentials.id_token['sub']
    if result['user_id'] != google_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's.", 401))
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that user is not already logged in
    stored_access_token = login_session.get('access_token')
    stored_google_id = login_session.get('google_id')
    if stored_access_token is not None and google_id == stored_google_id:
        response = make_response(json.dumps("Current user is already connected", 200))
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token and google_id in the session
    login_session['access_token'] = credentials.access_token
    login_session['google_id'] = google_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # check that the user already exits in the database. If not, create a new user
    try:
        user = session.query(User).filter_by(email=data['email']).one()
    except:
        user = None

    if user is None:
        new_user = User(email=data['email'], username=data['username'])
        session.add(new_user)
        session.commit()

    user_id = User.get_id_by_email(session, data['email'])
    login_session['user_id'] = user_id
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['google_id']
        del login_session['user_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/error')
def error():
    return render_template('error.html')

# JSON API

@app.route('/categories/JSON')
def categories_json():
    categories = session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in categories])

@app.route('/items/JSON')
def items_json():
    items = session.query(Item).all()
    return jsonify(Items=[i.serialize for i in items])

@app.route('/category/<int:category_id>/JSON')
def category_json(category_id):
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(Items=[i.serialize for i in items])

@app.route('/category/<int:category_id>/item/<int:item_id>/JSON')
def item_json(category_id, item_id):
    item = session.query(Item).filter_by(category_id=category_id, id=item_id).first()
    return jsonify(Item=[item.serialize])

if __name__ == '__main__':
    app.secret_key = "fwC3zfow9Rj0J801u99d3b66gjZAI1nn"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)