from flask import Flask, render_template, url_for, redirect, request, flash
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import func
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

@app.route("/")
@app.route("/restaurants/<int:restaurant_id>/")
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    return render_template("menu.html", restaurant=restaurant, items=items)


@app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == "POST":
        newItem = MenuItem(name=request.form["name"], restaurant_id=restaurant_id)
        session.add(newItem)
        session.commit()
        flash("%s added!" % newItem.name)
        return redirect(url_for("restaurantMenu", restaurant_id=restaurant_id))
    else:
        return render_template("new-menu-item.html", restaurant_id=restaurant_id)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    menuItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == "POST":
        menuItem.name = request.form["name"]
        session.add(menuItem)
        session.commit()
        flash("%s updated!" % menuItem.name)
        return redirect(url_for("restaurantMenu", restaurant_id=restaurant_id))
    else:
        return render_template("edit-menu-item.html", restaurant_id=restaurant_id, menu_id=menu_id, menuItem=menuItem)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    menuItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == "POST":
        session.delete(menuItem)
        session.commit()
        flash("%s deleted" % menuItem.name)
        return redirect(url_for("restaurantMenu", restaurant_id=restaurant_id))
    else:
        return render_template("delete-menu-item.html", restaurant_id=restaurant_id, menu_id=menu_id, menuItem=menuItem)




if __name__ == "__main__":
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host="0.0.0.0", port=5000)