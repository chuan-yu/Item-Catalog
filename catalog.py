import random
import httplib2
import json
import string
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask import session as login_session
from flask import make_response
from database_setup import Base, Category, Item, User
from oauth2client import client

app = Flask(__name__)

# Read CLIENT_ID from file
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']


# Context Processors

# Make categories avaiable for all templates automatically
@app.context_processor
def inject_categories():
    categories = Category.all()
    return dict(categories=categories)

# Make login_session available for all templates automatically
@app.context_processor
def inject_session():
    return dict(login_session=login_session)


@app.route('/')
def home_page():
    items = Item.order_by_created_with_limit(limit=7)
    return render_template('index.html', items=items)

@app.route('/category/<int:category_id>')
def category(category_id):
    category = Category.by_id(category_id)
    items = Item.by_category_id(category_id)
    return render_template('category.html', category=category, items=items)

@app.route('/category/<int:category_id>/<int:item_id>/')
def category_item(category_id, item_id):
    item = Item.by_cat_id_and_item_id(category_id, item_id)
    return render_template('category_item.html', item=item)

@app.route('/category/new', methods=['GET', 'POST'])
def new_category():
    if request.method == 'POST':
        if login_session.get('user_id'):

            # check the category name does not already exist
            cat = Category.by_name(name=request.form['name'].lower())
            if cat != None:
                flash("Category %s already exists" % cat.name)
                return render_template('new_category.html')

            new_category = Category.new(name=request.form['name'],
                                    user_id=login_session.get('user_id'))
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

            # check that the name does not already exist in the category
            item_to_check = Item.by_name_and_cat_id(name=request.form['name'],
                            category_id=request.form['category'])
            if item_to_check != None:
                flash("Item %s already exists" % item_to_check.name)
                return render_template('new_item.html')

            new_item = Item.new(name=request.form['name'],
                            category_id=request.form['category'],
                            description=request.form['description'],
                            user_id = login_session.get('user_id'))
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
    item = Item.by_cat_id_and_item_id(category_id=category_id, item_id=item_id)

    if request.method == 'POST':
        if login_session.get('user_id') and login_session.get('user_id') == item.user_id:
            if request.form['name']:
                item.name = request.form['name']
            if request.form['description']:
                item.description = request.form['description']
            if request.form['category']:
                item.category_id = request.form['category']

            Item.update(item)
            flash("Item %s successfully updated" % item.name)
            return redirect(url_for("home_page"))
    else:
        if login_session.get('user_id') and login_session.get('user_id') == item.user_id:
            return render_template('update_item.html', category_id=category_id, item=item)
        else:
            return redirect(url_for('error.html'))


@app.route('/category/<int:category_id>/delete', methods=['GET', 'POST'])
def delete_category(category_id):
    category = Category.by_id(id=category_id)
    # category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if login_session.get('user_id') and login_session.get('user_id') == category.user_id:
            # delete all items in the category
            items_in_category = Item.by_category_id(category_id=category_id)
            for item in items_in_category:
                Item.delete(item)
            # delete the category
            Category.delete(category)
            flash("Category %s deleted successfully" % category.name)
            return redirect(url_for('home_page'))
    else:
        if login_session.get('user_id') and login_session.get('user_id') == category.user_id:
            return render_template('delete_category.html', category=category)
        else:
            return redirect(url_for('error'))

@app.route('/category/<int:category_id>/<int:item_id>/delete', methods=['GET', 'POST'])
def delete_item(category_id, item_id):
    item = Item.by_cat_id_and_item_id(category_id=category_id, item_id=item_id)
    if request.method == 'POST':
        if login_session.get('user_id') and login_session.get('user_id') == item.user_id:
            Item.delete(item)
            flash("Item %s deleted successfully" % item.name)
            return redirect(url_for('home_page'))
    else:
        if login_session.get('user_id') and login_session.get('user_id') == item.user_id:
            category = Category.by_id(id=category_id)
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
        response = create_json_response('Invalid state parameter.', 401)
        return response

    # Get one-time code from the request
    auth_code = request.data

    # exchange access token with the one-time code
    credentials = client.credentials_from_clientsecrets_and_code('client_secrets.json',
                ['https://www.googleapis.com/auth/userinfo.profile', 'profile', 'email'],
                auth_code)

    # check that the access is valid
    token_status = valid_token(credentials)

    # if access token not valid, abort
    if token_status['valid'] == False:
        response = create_json_response(token_status['error_message'],
                    token_status['code'])
        return response

    # check whether the user is already logged in
    if is_user_logged_in_google(login_session, credentials.id_token['sub']):
        response = create_json_response('Current user is already connected', 200)
        return response

    # store credentials in the session for later use
    login_session['credentials'] = client.OAuth2Credentials.to_json(credentials)
    login_session['google_id'] = credentials.id_token['sub']

    # use access token to get user profile
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    user_info = answer.json()

    # check whether the user exists in the DB. If not, create new user.
    user = User.by_email(email=user_info['email'])
    if user:
        user_id = user.id
    else:
        new_user = User.new(username=user_info['name'],
                    email=user_info['email'], picture=user_info['picture'])
        user_id = User.get_id_by_email(session, new_user.email)


    # store user info in the session
    login_session['username'] = user_info['name']
    login_session['user_id'] = user_id
    login_session['picture'] = user_info['picture']
    login_session['email'] = user_info['email']

    output = ""
    output += "welcome"

    return output


@app.route('/gdisconnect')
def gdisconnect():
    credentials = client.OAuth2Credentials.from_json(login_session['credentials'])
    if credentials is None:
        print 'Credentials is None'
        response = create_json_response('Current user not connected.', 401)
        return response

    # revoke access token
    try:
        credentials.revoke(httplib2.Http())
    except client.TokenRevokeError:
        print 'Token invalid. Pocceed anyway'

    # delete token and user info from the session
    del login_session['credentials']
    del login_session['google_id']
    del login_session['user_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    response = create_json_response('Successfully disconnected', 200)
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


# Helper Functions


def create_json_response(message, code):
    response = make_response(json.dumps(message), code)
    response.headers['Content-Type'] = 'application/json'
    return response

# validate Google OAuth access token
def valid_token(credentials):
    id_token = credentials.id_token
    access_token = credentials.access_token
    token_status = {}

    # validate token by sending a GET request to the validation url
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the result, abort
    if result.get('error') is not None:
        token_status['valid'] = False
        token_status['error_message'] = result.get('error')
        token_status['response_code'] = 500
        return token_status

    # verify that the access token is used for the intented user
    if result['user_id'] != id_token['sub']:
        token_status['valid'] = False
        token_status['error_message'] = "Token's user ID doesn't match given user ID."
        token_status['response_code'] = 401
        return token_status

    # verify that the access token is issued to this app
    if result['issued_to'] != CLIENT_ID:
        token_status['valid'] = False
        token_status['error_message'] = "Token's client ID does not match app's."
        token_status['response_code'] = 401
        return token_status

    # everything is okay, return valid
    token_status['valid'] = True
    token_status['error_message'] = ""
    token_status['response_code'] = 200
    return token_status

# check whether used is already logged using Goolge account
def is_user_logged_in_google(session, google_id):
    stored_credentials = session.get('credentials')
    stored_google_id = session.get('google_id')
    if stored_credentials is not None and stored_google_id == google_id:
        return True
    else:
        return False




if __name__ == '__main__':
    app.secret_key = "fwC3zfow9Rj0J801u99d3b66gjZAI1nn"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)