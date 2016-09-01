import random
import httplib2
import json
import string
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
from flask import make_response
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

# categories = [{'id':1, 'name':'soccer'}, {'id':2, 'name':'basketball'}, {'id':3, 'name':'Football'}]
# category_items = [{'id':1, 'name':'stick', 'cat_id':1, 'description':"This is description"},
#         {'id':2, 'name':'goggles', 'cat_id':1, 'description':"This is description"},
#         {'id':3, 'name':'shoes', 'cat_id':2, 'description':"This is description"}]

# Make categories avaiable for all templates automatically
@app.context_processor
def inject_categories():
    categories = session.query(Category).all()
    return dict(categories=categories)

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
        # use lower() function to convert user input to lowercase
        cat = session.query(Category).filter_by(name=request.form['name'].lower()).first()
        if cat != None:
            flash("Category %s already exists" % cat.name)
            return render_template('new_category.html')

        new_category = Category(name=request.form['name'].lower())
        session.add(new_category)
        session.commit()
        flash("New category %s was added sucessfully" % new_category.name)
        return redirect(url_for('home_page'))
    else:
        return render_template('new_category.html')

@app.route('/item/new', methods=['GET', 'POST'])
def new_item():
    if request.method == 'POST':
        # use lower() function to convert user input to lowercase
        item_to_check = session.query(Item).filter_by(name=request.form['name'].lower()).first()
        if item_to_check != None:
            flash("Item %s already exists" % item_to_check.name)
            return render_template('new_item.html')

        new_item = Item(name=request.form['name'].lower(), category_id=request.form['category'],
                        description=request.form['description'])
        session.add(new_item)
        session.commit()
        flash("Item %s successfully added" % new_item.name)
        return redirect(url_for('home_page'))
    else:
        return render_template('new_item.html')

@app.route('/category/<int:category_id>/<int:item_id>/update', methods=['GET', 'POST'])
def update_item(category_id, item_id):
    item = session.query(Item).filter_by(category_id=category_id, id=item_id).one()
    if request.method == 'POST':
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
        return render_template('update_item.html', category_id=category_id, item=item)

@app.route('/category/<int:category_id>/delete', methods=['GET', 'POST'])
def delete_category(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        items_in_category = session.query(Item).filter_by(category_id=category_id).all()
        for item in items_in_category:
            session.delete(item)
            session.commit()
        session.delete(category)
        session.commit()
        flash("Category %s deleted successfully" % category.name)
        return redirect(url_for('home_page'))
    else:
        return render_template('delete_category.html', category=category)

@app.route('/category/<int:category_id>/<int:item_id>/delete', methods=['GET', 'POST'])
def delete_item(category_id, item_id):
    item = session.query(Item).filter_by(category_id=category_id, id=item_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("Item %s deleted successfully" % item.name)
        return redirect(url_for('home_page'))
    else:
        category = session.query(Category).filter_by(id=category_id).one()
        return render_template('delete_item.html', category=category, item=item)

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
    print code
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
        print 'access_token in connect'
        print stored_access_token
        response = make_response(json.dumps("Current user is already connected", 200))
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token and google_id in the session
    login_session['access_token'] = credentials.access_token
    login_session['google_id'] = google_id

    print 'access_token in connect'
    print credentials.access_token

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

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
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    print "access_token in disconnect"
    print access_token
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    print "url is "
    print url
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    print "result is also"
    print h.request(url, 'GET')[1]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['google_id']
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



if __name__ == '__main__':
    app.secret_key = "fwC3zfow9Rj0J801u99d3b66gjZAI1nn"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)