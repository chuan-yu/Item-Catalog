from flask import Flask, render_template, request

app = Flask(__name__)

categories = [{'id':1, 'name':'soccer'}, {'id':2, 'name':'basketball'}, {'id':3, 'name':'Football'}]
category_items = [{'id':1, 'name':'stick', 'cat_id':1, 'description':"This is description"},
        {'id':2, 'name':'goggles', 'cat_id':1, 'description':"This is description"},
        {'id':3, 'name':'shoes', 'cat_id':2, 'description':"This is description"}]

# Make categories avaiable for all templates automatically
@app.context_processor
def inject_categories():
    return dict(categories=categories)

@app.route('/')
def homePage():

    return render_template('index.html')

@app.route('/category/<int:category_id>')
def category(category_id):
    category = None
    for c in categories:
        if c['id'] == category_id:
            category = c
    items = []
    for i in category_items:
        if i['cat_id'] == category_id:
            items.append(i)
    return render_template('category.html', category=category, items=items)

@app.route('/category/<int:category_id>/<int:item_id>/')
def categoryItem(category_id, item_id):
    item = None
    for i in category_items:
        if i['id'] == item_id:
            item = i
    return render_template('category_item.html', item=item)

@app.route('/category/new')
def newCategory():
    return render_template('new_category.html')

@app.route('/category/<int:category_id>/item/new')
def newCategoryItem(category_id):
    category = None
    for c in categories:
        if c['id'] == category_id:
            category = c
    return render_template('new_category_item.html', category=category)

@app.route('/category/<int:category_id>/<int:item_id>/update')
def updateCategoryItem(category_id, item_id):
    category = None
    item = None
    for c in categories:
        if c['id'] == category_id:
            category = c

    for i in category_items:
        if i['id'] == item_id:
            item = i
    return render_template('update_category_item.html', category=category, item=item)

@app.route('/category/<int:category_id>/delete', methods=['GET', 'POST'])
def deleteCategory(category_id):
    category = None
    for c in categories:
        if c['id'] == category_id:
            category = c
    return render_template('delete_category.html', category=category)

@app.route('/category/<int:category_id>/<int:item_id>/delete')
def deleteCategoryItem(category_id, item_id):
    category = None
    item = None
    for c in categories:
        if c['id'] == category_id:
            category = c

    for i in category_items:
        if i['id'] == item_id:
            item = i
    return render_template('delete_item.html', category=category, item=item)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)