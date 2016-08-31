from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

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
    items = session.query(Item).order_by(Item.created).limit(5)
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

        new_Item = Item(name=request.form['name'].lower(), category_id=request.form['category'],
                        description=request.form['description'])
        session.add(new_Item)
        session.commit()
        flash("Item %s successfully added" % new_item.name)
        return redirect(url_for('home_page'))
    else:
        return render_template('new_item.html')

@app.route('/category/<int:category_id>/<int:item_id>/update', methods=['GET', 'POST'])
def update_category_item(category_id, item_id):
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
        return render_template('update_category_item.html', category_id=category_id, item=item)

@app.route('/category/<int:category_id>/delete', methods=['GET', 'POST'])
def delete_category(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
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


if __name__ == '__main__':
    app.secret_key = "fwC3zfow9Rj0J801u99d3b66gjZAI1nn"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)