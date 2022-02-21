#!/usr/bin/env python3

# local imports
#import os
#from os.path import abspath, dirname

from tkinter.messagebox import QUESTION
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import json
from datetime import datetime
import requests 

# create the flask application object.
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = "skdjfgklsdflgkjsdflkgjabfglkjdsbflgkjsbdfgkl"

# get the ADMIN url from the environment variables from the .env file stored locally.
adminURL = "/1379b0159b5bccea882c040dee6b59b6970cc5d9e/"


# create/connect to the db.
#_cwd = dirname(abspath(__file__))
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + join(_cwd, 'flask-database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://doadmin:pxTKuPxJgluouWIZ@db-postgresql-lon1-79437-do-user-1903022-0.b.db.ondigitalocean.com:25060/defaultdb?sslmode=require'
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

class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime,default=datetime.now)
    ipaddr = db.Column(db.String)
    description = db.Column(db.String)
    q1 = db.Column(db.Integer)
    q2 = db.Column(db.Integer)
    q3 = db.Column(db.Integer)
    q4 = db.Column(db.Integer)
    q5 = db.Column(db.Integer)
    q6 = db.Column(db.Integer)
    q7 = db.Column(db.Integer)
    q8 = db.Column(db.Integer)

    def __repr__(self):
        return '<Feedback {:d} {}>'.format(self.id, self.ipaddr)

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
  queryDelCount = Delegate.query.filter(Delegate.id >= 0).count()
  queryCatCount = Category.query.filter(Category.id >= 0).count()

  return render_template('home.html', title='Home', description='This is the meta-description.', countCat=queryCatCount, countDel=queryDelCount)

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

@app.route('/feedback', methods = ['GET', 'POST'])
def get_feedback():
  if request.method == 'GET':
    return render_template('feedback.html', title='Feedback Form', description='', host=requests.get('http://ipinfo.io/json').json()['ip'])

  if request.method == 'POST':
      feedbackForm = Feedback(ipaddr=request.form['ipaddr'],description=request.form['description'],q1=request.form['q1'],q2=request.form['q2'],q3=request.form['q3'],q4=request.form['q4'],q5=request.form['q5'])
      db.session.add(feedbackForm)
      db.session.commit()

      flash('Your feedback has been successfuly recieved.')
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

@app.route(adminURL + '/categories/<int:pkid>/delete/', methods = ['POST'])
def get_adminCategoriesDelete(pkid):
  if pkid > 0:
    deleteCat = Category.query.filter_by(id=pkid).first()
    db.session.delete(deleteCat)
    db.session.commit()
    flash('Category (#' + str(pkid) + ') was successfully deleted.')
    return redirect(url_for('get_adminCategories'))


@app.route(adminURL + '/categories/<int:pkid>', methods = ['GET', 'POST'])
def get_adminCategoriesInsertUodate(pkid):
  if request.method == 'GET':
    if pkid > 0:
      query = Category.query.filter_by(id=pkid).first()

      #This is here to pass the number of FK records that reference this category_ID.
      #We don't won't to allow the user to delete a record if it's related.
      subQueryCount = Delegate.query.filter_by(category_id=pkid).count()

      return render_template('adminCategoriesEdit.html', title='Admin: Categories: Edit', description='', catPKID=pkid, passedRecord=query, FKCount=subQueryCount)
    else:
      return render_template('adminCategoriesEdit.html', title='Admin: Categories: Add', description='', catPKID=0, passedRecord=None)

  if request.method == 'POST':
    if pkid > 0:
      updateCat = Category.query.filter_by(id=pkid).first()
      updateCat.name = request.form['name']
      db.session.commit()

      flash('Category (#' + str(updateCat.id) + ') was successfully updated.')
    else:
      cat = Category(name=request.form['name'])
      db.session.add(cat)
      db.session.commit()
      flash('Category (#' + str(cat.id) + ') was successfully added.')
    return redirect(url_for('get_adminCategories'))


@app.route(adminURL + '/categories')
def get_adminCategories():
  query = Category.query.filter(Category.id >= 0).order_by(Category.name)
  return render_template('adminCategories.html', title='Admin: Categories', description='', rows=query.all())


@app.route(adminURL + '/feedback/<int:question>')
def get_adminFeedback(question):
  builtData = ""
  qryResponses = Feedback.query.filter(Feedback.id >= 0).order_by(Feedback.created)

  if (question > 0):
    builtResponses = {"5" : 0,"4" : 0,"3" : 0,"2" : 0,"1" : 0}

    for response in qryResponses.all():
      localObject = getattr(response, 'q' + str(question))

      if localObject==1:
        builtResponses["1"] = builtResponses["1"] + 1
      elif localObject==2:
        builtResponses["2"] = builtResponses["2"] + 1
      elif localObject==3:
        builtResponses["3"] = builtResponses["3"] + 1
      elif localObject==4:
        builtResponses["4"] = builtResponses["4"] + 1
      elif localObject==5:
        builtResponses["5"] = builtResponses["5"] + 1

      builtData = "[['Question','Responses'],"
      builtData = builtData + "['Strongly Agree'," +  str(builtResponses["5"]) + "],"
      builtData = builtData + "['Agree'," +  str(builtResponses["4"]) + "],"
      builtData = builtData + "['Neither agree or disagree'," +  str(builtResponses["3"]) + "],"
      builtData = builtData + "['Disagree'," +  str(builtResponses["2"]) + "],"
      builtData = builtData + "['Strongly Disagree'," +  str(builtResponses["1"]) + "]]"
    
  return render_template('adminFeedback.html', title='Admin: Feedback: Question ' + str(question), description='', rows=qryResponses.all(), question=question,builtData=builtData)



@app.route(adminURL + '/delegates/import', methods = ['GET', 'POST'])
def get_adminDelegatesImport():
  if request.method == 'GET':
      return render_template('adminDelegatesImport.html', title='Admin: Delegates: Import', description='')

  if request.method == 'POST':
      localJSON  = json.loads(request.form['importdata'])

      findCategory = Category.query.filter_by(name=localJSON["category"]).first()
      if findCategory.id > 0:
        localDataCategory = findCategory.id
        localDataName = localJSON["name"]
        localDataLocation = localJSON["location"]
        localDataDescription = localJSON["description"]
        localDataInternalURL = localDataName.lower().replace(" ", "-")
        localDataExternalURL = localJSON["externalurl"]

        insertDel = Delegate(name=localDataName,category_id=localDataCategory,location=localDataLocation,description=localDataDescription,internalurl=localDataInternalURL,externalurl=localDataExternalURL)
        db.session.add(insertDel)
        db.session.commit()

        flash('Delegate (#' + str(insertDel.id) + ') was successfully added.')
      return redirect(url_for('get_adminDelegates'))



@app.route(adminURL + '/delegates/<int:pkid>', methods = ['GET', 'POST'])
def get_adminDelegatesInsertUodate(pkid):
  if request.method == 'GET':
    #These rows are used to build the Category Drop Down List on the Delegate Page
    catListContent = Category.query.filter(Category.id >= 0).order_by(Category.name)

    if pkid > 0:
      query = Delegate.query.filter_by(id=pkid).first()
      return render_template('adminDelegatesEdit.html', title='Admin: Delegates: Edit', description='', catRows=catListContent.all(), delPKID=pkid, passedRecord=query)
    else:
      return render_template('adminDelegatesEdit.html', title='Admin: Delegates: Add', description='', catRows=catListContent.all(), delPKID=0, passedRecord=None)

  if request.method == 'POST':
    if pkid > 0:
      updateDel = Delegate.query.filter_by(id=pkid).first()
      updateDel.name = request.form['name']
      updateDel.location = request.form['location']
      updateDel.description = request.form['description']
      updateDel.internalurl = request.form['internalurl']
      updateDel.externalurl = request.form['externalurl']
      updateDel.category_id = request.form['category_id']
      db.session.commit()
      flash('Delegate (#' + str(updateDel.id) + ') was successfully updated.')
    else:
      insertDel = Delegate(name=request.form['name'],location = request.form['location'],description = request.form['description'],internalurl = request.form['internalurl'],externalurl = request.form['externalurl'],category_id=request.form['category_id'])
      db.session.add(insertDel)
      db.session.commit()
      flash('Delegate (#' + str(insertDel.id) + ') was successfully added.')
    return redirect(url_for('get_adminDelegates'))


@app.route(adminURL + '/delegates/<int:pkid>/delete/', methods = ['POST'])
def get_adminDelegatesDelete(pkid):
  if pkid > 0:
    deleteDel = Delegate.query.filter_by(id=pkid).first()
    db.session.delete(deleteDel)
    db.session.commit()
    flash('Delegate (#' + str(pkid) + ') was successfully deleted.')
    return redirect(url_for('get_adminDelegates'))


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
    app.debug = False
    db.create_all(app=app)
    db.init_app(app=app)
    app.run()
