#!/usr/bin/env python3

# local imports
import os
from os.path import abspath, dirname, join

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

# create the flask application object.
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = "skdjfgklsdflgkjsdflkgjabfglkjdsbflgkjsbdfgkl"

# get the ADMIN url from the environment variables from the .env file stored locally.
adminURL = "/1379b0159b5bccea882c040dee6b59b6970cc5d9e/"


# create/connect to the db.
_cwd = dirname(abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + join(_cwd, 'flask-database.db')
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# database models
class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __repr__(self):
        return '<Category {:d} {}>'.format(self.id, self.name)

    def __str__(self):
        return self.name


class Delegate(db.Model):
    __tablename__ = 'delegate'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    location = db.Column(db.String)
    description = db.Column(db.String)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    internalurl = db.Column(db.String)
    externalurl = db.Column(db.String)
    categoryRelationship = relationship("Category",backref="Category",uselist=True)
    category=relationship("Category",lazy="joined")

    def __repr__(self):
        return '<Delegate {:d} {}>'.format(self.id, self.name)

    def __str__(self):
        return self.name

# Local function used below.
def returnOrderByField(querystringParameter):
  #Let's see if they have asked for a specific sort 
  if querystringParameter=="location":
    return Delegate.location
  else:
    return Delegate.name

# Every page that is on the website will need an app.route defined here.
# Most of them are pretty simple - they just render a template from the templates directory with very little effort.
@app.route('/')
def get_home():
  return render_template('home.html', title='Home', description='This is the meta-description.')

@app.route('/about')
def get_about():
  return render_template('about.html', title='More about our Convention', description='')

@app.route('/acknowledgements')
def get_acknowledgements():
  return render_template('acknowledgements.html', title='Acknowledgements of the Convention', description='')

@app.route("/delegates/", defaults={"internalURL": None})
@app.route('/delegates/<string:internalURL>')
def get_delegates_filtered(internalURL):

  if internalURL is None:
    #Simply return all the delegate records - sorted if necessary
    query = Delegate.query.filter(Delegate.id >= 0).order_by(returnOrderByField(request.args.get('sort', default = 'name', type = str)))
    builtDescription=""
    filteredView=0
  else:
    #Filter the delegate records to only those whose category name matches the filter.
    #We have to replace the dashes (-) back to spaces, that were removed in the template files, for this to work.
    query = Delegate.query.filter(Delegate.category.has(name=internalURL.replace("-"," "))).order_by(returnOrderByField(request.args.get('sort', default = 'name', type = str)))
    filteredView=1
    builtDescription=internalURL.replace("-"," ")
    
  return render_template('delegates.html', title='Delegates attending the Convention', description=builtDescription, filteredView=filteredView,rows=query.all())

@app.route('/delegate/<string:internalURL>')
def get_delegate(internalURL):
  query = Delegate.query.filter_by(internalurl=internalURL).first_or_404()

  # In this instance, the meta title and description values must come from the database.
  return render_template('delegate.html', title='', description='', row=query)

@app.route('/feedback')
def get_feedback():
  #TO DO - Create the form itself.
  #TO DO - Create a new route to send the form contents to the database.

  return render_template('feedback.html', title='Feedback Form', description='')

@app.route('/map')
def get_map():
  return render_template('map.html', title='Location Map of the Convention', description='')

@app.route('/news')
def get_news():
  return render_template('news.html', title='Latest news from the Careers Convention', description='')

#*******************************************************************************
# These are the ADMIN URLS that are not public
#*******************************************************************************
@app.route(adminURL)
def get_adminHome():
  return render_template('admin.html', title='Admin: Home', description='')

@app.route(adminURL + '/categories/<int:pkid>', methods = ['GET', 'POST'])
def get_adminCategoriesInsert(pkid):
  if request.method == 'GET':
    if pkid > 0:
      query = Category.query.filter_by(id=pkid).first()
      return render_template('adminCategoriesEdit.html', title='Admin: Categories: Edit', description='', rows=query)
    else:
      return render_template('adminCategoriesEdit.html', title='Admin: Categories: Add', description='')

  if request.method == 'POST':
    if pkid > 0:
      flash('Category was successfully updated.')
    else:
      cat = Category(request.form['name'])
      db.session.add(cat)
      db.session.commit()
      flash('Category was successfully added.')
    return redirect(url_for('get_adminCategories'))


@app.route(adminURL + '/categories')
def get_adminCategories():
  query = Category.query.filter(Category.id >= 0).order_by(Category.name)
  return render_template('adminCategories.html', title='Admin: Categories', description='', rows=query.all())

@app.route(adminURL + '/delegates')
def get_adminDelegates():
  query = Delegate.query.filter(Delegate.id >= 0).order_by(Delegate.name)
  return render_template('adminDelegates.html', title='Admin: Delegates', description='', rows=query.all())
#*******************************************************************************

@app.errorhandler(404)
def page_not_found(error):
   return render_template('error404.html', title = 'Page not found'), 404

# start the server with the 'run()' method - debug=True for testing - NOT LIVE
if __name__ == '__main__':
    app.debug = True
    db.create_all(app=app)
    db.init_app(app=app)
    app.run()
