#!/usr/bin/env python
#
# webserver.py -- a python server to localhost restaurants
#
# info for using python to build a basic HTTP server: 
# https://docs.python.org/2/library/basehttpserver.html
import os
import sys
import jinja2
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import func
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def post_argument(dict, target):
    """ get arguments from post field/button name
     Argument format:
     "delete=1234567890987654321"
        ^             ^      
      button press | id
    """
    for key in dict:
        argument = key.split("=")
        if argument[0] == target:
            if len(argument) > 1:
                return argument[1]
            elif len(argument) == 1:
                return target



class WebServerHandler(BaseHTTPRequestHandler):

    def redirect(self, url_path):
        """ redirect to specified page """
        self.send_header('Content-type', 'text/html')
        # redirect to main page
        self.send_header("Location", url_path)
        self.end_headers()

    def render_restaurant_page(self):
        """ pull restaurants from db and render them to page """
        restaurants = session.query(Restaurant).order_by(Restaurant.name.asc()).all()
        output = render_str("restaurant-index.html", restaurants=restaurants)
        self.wfile.write(output)

    def render_new_restaurant_page(self):
        """ add new restaurant to your app """
        output = render_str("new-restaurant.html", 
                            subheader_text="add a new restaurant!",
                            field_name="new-restaurant",
                            button_name="add-restaurant",
                            submit_btn_name="Add",
                            placeholder_text="add here",
                            value="")
        self.wfile.write(output)

    def render_edit_restaurant_page(self, id):
        restaurant = session.query(Restaurant).filter_by(id=id).one()
        output = render_str("new-restaurant.html", 
                            subheader_text="rename restaurant name!",
                            field_name="edit-restaurant",
                            button_name="submit-edit-restaurant=%s" % id,
                            submit_btn_name="Rename",
                            placeholder_text="rename restaurant",
                            value=restaurant.name)
        self.wfile.write(output)

    def do_GET(self):
        if self.path.endswith("/restaurants"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.render_restaurant_page()
            return
        elif self.path.endswith("/new"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.render_new_restaurant_page()
            return
        elif self.path.endswith("/edit"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            # get the restaurant id from the 2nd to last path component
            id = self.path.split("/")[-2]
            self.render_edit_restaurant_page(id)
            return
        else:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            self.send_response(301)
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                items = cgi.parse_multipart(self.rfile, pdict)
                print items
                restaurant_id = post_argument(items, "edit")
                if restaurant_id:
                    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
                    if restaurant:
                        self.wfile.write("success!\n%s would get edited" % (restaurant.name))
                        self.redirect("/restaurants/%s/edit" % restaurant_id)
                        return
                print "not edit"
                restaurant_id = post_argument(items, "delete")
                if restaurant_id:
                    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
                    if restaurant:
                        session.delete(restaurant)
                        session.commit()
                        self.redirect("/restaurants")
                        return
                restaurant_id = post_argument(items, "submit-edit-restaurant")
                if restaurant_id:
                    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
                    if restaurant:
                        new_name = items.get("edit-restaurant")
                        if new_name:
                            restaurant.name = new_name[0]
                            session.add(restaurant)
                            session.commit()
                        self.redirect("/restaurants")
                        return
                arg = post_argument(items, "add-restaurant")
                if arg:
                    new_restaurant_name = items.get("new-restaurant")
                    if new_restaurant_name:
                        new_restaurant = Restaurant(name=new_restaurant_name[0])
                        session.add(new_restaurant)
                        session.commit()
                    self.redirect("/restaurants")
                    return
            self.end_headers()
            return

        except:
            print "POST failed"
            pass



def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print " entered, stopping web server ..."
        server.socket.close()

if __name__ == '__main__':
    main()