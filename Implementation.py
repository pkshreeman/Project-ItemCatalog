import flask as f
import oauth2client.client as oa2
import json
import random
import string
import requests
import os
import hashlib
import re
import sys


from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Users, Items, Base, Category

engine = create_engine('postgresql://cataloguser:password@localhost/itemcat')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


app = f.Flask(__name__)


def checkstate():
    """
    The ongoing issue with where to create 'state' for a header
    that is available on every page is a major headache, so I decided to
    create a function that deals with this automatically to be called
    on every route.
    """
    try:
        state = f.session['state']
        print(state)
        print('the state is obtained.')
        return state
    except:
        state = ''.join(random.choice(string.ascii_uppercase + string.digits) # noqa
                        for x in xrange(32))
        f.session['state'] = state
        print 'State created'
        return state


@app.route('/listing/JSON')
def listJSON():
    """
    This function lists all the Category(ies)
    in the database in JSON format.  'Listing' is term
    used to describe the Category(ies)
    """
    lists = session.query(Category).order_by(asc(Category.name))
    return f.jsonify(lists=[i.serialize for i in lists])


@app.route('/listing/<int:list_id>/items/JSON')
def itemJSON(list_id):
    """
    This function lists all the items
    under specific category_id in JSON format.
    """
    items = session.query(Items).filter_by(category_id=list_id).all()
    return f.jsonify(items=[k.serialize for k in items])


@app.route('/listing/<int:list_id>/items/<int:item_id>/delete/', methods=['POST', 'GET']) # noqa
def deleteitem(item_id, list_id):
    """
    This function will delete a given item
    only if you are the owner of the orginial post.
    """
    deleteitem = session.query(Items).filter_by(id=item_id).one()
    print deleteitem.id
    try:
        checkId = session.query(Users).filter_by(email=f.session['email']).one() # noqa
        print 'The checkId name is ' + checkId.name
        print 'The checkIds id is ' + str(checkId.id)
        if checkId.id != deleteitem.users_id:
            print('The id does not match')
            f.flash('Only the orginial authors have ability to edit or delete their creations') # noqa
            return f.redirect('/')
        else:
            print('The id do match')
            if f.request.method == 'POST':
                session.delete(deleteitem)
                session.commit()
                f.flash('The item has been deleted')
                return f.redirect(f.url_for('listing'))
            else:
                print ('Get method triggered in deletelist')
                print deleteitem.name
                return f.render_template('deleteitem.html',
                                         item_name=deleteitem.name,
                                         name=f.session['name'],
                                         picture=f.session['picture'])
    except:
        e = sys.exc_info()[0]
        print("<p>Error: %s</p>" % e)
        return "Only Registered Users allowed"


@app.route('/listing/<int:list_id>/items/<int:item_id>/edit/', methods=['POST', 'GET']) # noqa
def edititem(item_id, list_id):
    """This function will allow the owner of the post to edit their items."""
    edititem = session.query(Items).filter_by(id=item_id).one()
    print str(edititem.users_id)+' This number should be appearing '
    try:
        checkId = session.query(Users).filter_by(email=f.session['email']).one() # noqa
        print 'The checkId name is ' + checkId.name
        print 'The checkIds id is ' + str(checkId.id)
        if checkId.id != edititem.users_id:
            f.flash('Only the orginial authors have ability to edit or delete their creations') # noqa
            return f.redirect('/')
        else:
            if f.request.method == 'POST':
                if f.request.form['name']:
                    edititem.name = f.request.form['name']
                    edititem.description = f.request.form['description']
                    edititem.price = f.request.form['price']
                    edititem.picture = f.request.form['picture']
                    session.add(edititem)
                    session.commit()
                    f.flash('Item Successfully Edited')
                    return f.redirect(f.url_for('listing'))
            else:
                return f.render_template('edititem.html',
                                         item=edititem,
                                         name=f.session['name'],
                                         picture=f.session['picture'])
    except:
        e = sys.exc_info()[0]
        print("<p>Error: %s</p>" % e)
        return "Only Registered Users allowed"


@app.route('/listing/<int:list_id>/items/new/', methods=['POST', 'GET'])
def newitems(list_id):
    """
    Only Registered users will be allowed to create new item postings,
    and they will have their id branded on it for editing rights.
    """
    currentcategory = session.query(Category).filter_by(id=list_id).one()
    lists = session.query(Category).order_by(asc(Category.name))
    items = session.query(Items).filter_by(category_id=list_id).all()
    try:
        checkId = session.query(Users).filter_by(email=f.session['email']).one() # noqa
        print 'The checkId name is ' + checkId.name
        print 'The checkIds id is ' + str(checkId.id)
        if f.request.method == 'POST':
            newitem = Items(name=f.request.form['name'],
                            description=f.request.form['description'],
                            price=f.request.form['price'],
                            picture=f.request.form['picture'],
                            users_id=f.session['id'],
                            category_id=list_id)
            session.add(newitem)
            session.commit()
            f.flash('The new item has been added.')
            return f.redirect(f.url_for('listing'))

        else:
            print('Get Method for new items is generated')
            return f.render_template('newitem.html', lists=lists,
                                     items=items, currentlist=currentcategory,
                                     picture=f.session['picture'],
                                     name=f.session['name'])
    except:
        e = sys.exc_info()[0]
        print("<p>Error: %s</p>" % e)
        return "Only Registered Users allowed"


@app.route('/listing/<int:list_id>/items')
def showitems(list_id):
    """
    Just lists items under the currently selected category
    """
    state = checkstate()
    currentcategory = session.query(Category).filter_by(id=list_id).one()
    lists = session.query(Category).order_by(asc(Category.name))
    items = session.query(Items).filter_by(category_id=list_id).all()
    try:
        return f.render_template('listing.html', lists=lists,
                                 items=items, currentlist=currentcategory,
                                 picture=f.session['picture'],
                                 name=f.session['name'])
    except:
        return f.render_template('listing.html', lists=lists,
                                 items=items, currentlist=currentcategory,
                                 state=state)


@app.route('/listing')
def listing():
    """ This function lists all the categories for viewing"""
    state = checkstate()
    currentcategory = session.query(Category).first()
    lists = session.query(Category).order_by(asc(Category.name))
    print lists
    try:
        return f.render_template('listing.html', lists=lists, picture=f.session['picture'], # noqa
                                 name=f.session['name'], currentlist=currentcategory) # noqa
    except:
        print ('Exception occured in /listing - This is Paul error tracker')
        return f.render_template('listing.html', lists=lists,
                                 currentlist=currentcategory, state=state)


@app.route('/listing/<int:list_id>/delete/', methods=['POST', 'GET'])
def deletelist(list_id):
    """This function will allow only the owner to delete their category"""
    deletelist = session.query(Category).filter_by(id=list_id).one()
    print deletelist.id
    try:
        checkId = session.query(Users).filter_by(email=f.session['email']).one() # noqa
        print 'The checkId name is ' + checkId.name
        print 'The checkIds id is ' + str(checkId.id)
        if checkId.id != deletelist.users_id:
            print('The id does not match')
            f.flash('Only the orginial authors have ability to edit or delete their creations') # noqa
            return f.redirect('/')
        else:
            print('The id do match')
            if f.request.method == 'POST':
                session.delete(deletelist)
                session.commit()
                f.flash('The Cateogry has been deleted')
                return f.redirect(f.url_for('listing'))
            else:
                print ('Get method triggered in deletelist')
                print deletelist.name
                return f.render_template('deletelist.html',
                                         name=deletelist.name)
    except:
        e = sys.exc_info()[0]
        print("<p>Error: %s</p>" % e)
        return "Only Registered Users allowed"


@app.route('/listing/<int:list_id>/edit/', methods=['POST', 'GET'])
def editlist(list_id):
    """
    This function will only allow the owner to review and edit
    their Category names
    """
    print list_id
    editlist = session.query(Category).filter_by(id=list_id).one()
    print str(editlist.users_id) + ' This number should be appearing '
    try:
        checkId = session.query(Users).filter_by(email=f.session['email']).one() # noqa
        print 'The checkId name is ' + checkId.name
        print 'The checkIds id is ' + str(checkId.id)
        if checkId.id != editlist.users_id:
            f.flash('Only the orginial authors have ability to edit or delete their creations') # noqa
            return f.redirect('/')
        else:
            if f.request.method == 'POST':
                if f.request.form['name']:
                    editlist.name = f.request.form['name']
                    session.add(editlist)
                    session.commit()
                    f.flash('Category Renamed')
                    return f.redirect(f.url_for('listing'))
            else:
                return f.render_template('newlisting.html',
                                         list=editlist.name,
                                         name=f.session['name'],
                                         picture=f.session['picture'])
    except:
        return "Only Registered Users allowed"


@app.route('/listing/new', methods=['GET', 'POST'])
def addlisting():
    """This function will allow the registered user to create
    a new category and have their name branded on it for editing rights
    """
    try:
        checkId = session.query(Users).filter_by(email=f.session['email']).one() # noqa
        print 'The checkId name is ' + checkId.name
        print 'The checkIds id is ' + str(checkId.id)

        if f.request.method == 'POST':
            newlisting = Category(
                                  name=f.request.form['name'],
                                  users_id=f.session['id']
            )
            session.add(newlisting)
            session.commit()
            f.flash('The new category has been added.')
            return f.redirect(f.url_for('listing'))
        else:
            return f.render_template('newlisting.html',
                                     picture=f.session['picture'],
                                     name=f.session['name'])
    except:
        return "Only Registered Users Allowed."


@app.route('/')
@app.route('/welcome')
def welcome():
    try:
        user_email = f.session['email']
        userdatabase = session.query(Users).filter_by(email=user_email).first()
        f.session['id'] = userdatabase.id
        f.flash('Welcome back %s !' % f.session['name'])
        print 'Welcome Back to be generated'
        # return f.render_template('listing.html', name=userdatabase.name,
        #                         picture=userdatabase.picture)
        return f.redirect(f.url_for('listing'))
    except:
        try:
            newprofile = Users(name=f.session['name'], email=f.session['email'], # noqa
                               picture=f.session['picture'],
                               google_id=f.session['g_id'])
            session.add(newprofile)
            session.commit()
            userdatabase = session.query(Users).filter_by(email=user_email).first() # noqa
            f.session['id'] = userdatabase.id
            f.flash('Welcome %s !' % f.session['name'])
            print 'New account has been registered, redirecting to welcome'
            # return f.render_template('welcome.html', name=userdatabase.name,
            #                         picture=userdatabase.picture)
            return f.redirect(f.url_for('listing'))
        except:
            state = ''.join(random.choice(string.ascii_uppercase + string.digits) # noqa
                            for x in xrange(32))
            f.session['state'] = state
            print 'State created'
            # return f.render_template('login.html', state=state)
            return f.redirect(f.url_for('listing'))


@app.route('/googlelogin', methods=['POST'])
def googlelogin():
    if f.request.args.get('state') != f.session['state']:
        response = f.make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('the states matched.')
    auth_code = f.request.data
    CLIENT_SECRET_FILE = 'client_secret.json'
    credentials = oa2.credentials_from_clientsecrets_and_code(
        CLIENT_SECRET_FILE,
        ['https://www.googleapis.com/auth/userinfo.profile', 'profile', 'email'], # noqa
        auth_code)

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    userdata = answer.json()

    f.session['name'] = userdata['name']
    f.session['email'] = userdata['email']
    f.session["picture"] = userdata['picture']
    f.session['g_id'] = userdata['id']

    return json.dumps(userdata)


@app.route('/logout')
def logout():
    f.session.clear()
    return f.redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
        f.session.clear()

        def valid_username(username):
            USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
            return USER_RE.match(username)

        def valid_email(email):
            EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
            return EMAIL_RE.match(email)

        def valid_password(password):
            PASS_RE = re.compile(r"^.{3,20}$")
            return PASS_RE.match(password)

        if f.request.method == 'POST':

            username = f.request.form["username"]
            password = f.request.form["password"]
            verify = f.request.form["verify"]
            email = f.request.form["email"]
            errorQ = False
            params = dict(username=username,
                          email=email)

            if not valid_username(username):
                params['error_name'] = "Invalid Entry"
                errorQ = True
            if not valid_password(password):
                params['error_password'] = "Invalid Password"
                errorQ = True
            elif password != verify:
                params['error_verify'] = "Your password does not match"
                errorQ = True
            if not valid_email(email):
                params['error_email'] = "Invalid email"
                errorQ = True

            if errorQ:
                return f.render_template("register.html", **params)
            elif session.query(Users).filter_by(email=email).first():
                    return f.render_template("register.html",
                                             error_name="This email already exists") # noqa
            else:
                # Putting new user data into database

                def salty_password(name, password, salt=None):
                    if not salt:
                        salt = ''.join(random.choice(string.letters)for z in xrange(5)) # noqa
                    salting = hashlib.sha256(name+password+salt).hexdigest()
                    return '%s|%s' % (salt, salting)
                hashedpassword = salty_password(username, password)
                newregister = Users(name=username, email=email,
                                    password=hashedpassword)
                session.add(newregister)
                session.commit()
                f.session['name'] = username
                f.session['email'] = email
                f.session['id'] = newregister.id
                # return f.render_template('welcome.html', name=username)
                return f.redirect(f.url_for('listing'))

        else:
            return f.render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

        def valid_email(email):
            EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
            return EMAIL_RE.match(email)

        def valid_password(password):
            PASS_RE = re.compile(r"^.{3,20}$")
            return PASS_RE.match(password)

        if f.request.method == 'POST':
            password = f.request.form["password"]
            email = f.request.form["email"]
            errorQ = False
            parmas = dict(password=password,
                          email=email)

            if not valid_password(password):
                parmas['error_password'] = "Invalid Password"
                errorQ = True
            if not valid_email(email):
                parmas['error_email'] = "Invalid email"
                errorQ = True

            if errorQ:
                return f.render_template("login-in.html", **parmas)
            elif session.query(Users).filter_by(email=email).first():
                checkDB = session.query(Users).filter_by(email=email).first()
                if checkDB.password is None:
                    return f.render_template("login-in.html",
                                             error_password="Your Password is None, please login using Google or contact pkshreeman@gmail.com") # noqa
                else:
                    username = checkDB.name
                    stored_password = checkDB.password

                    def salty_password(name, password, salt=None):
                        if not salt:
                            salt = ''.join(random.choice(string.letters)for z in xrange(5)) # noqa
                        salting = hashlib.sha256(name+password+salt).hexdigest() # noqa
                        return '%s|%s' % (salt, salting)

                    def tasting_salt(name, password, hashedpassword):
                        taste = hashedpassword.split('|')[0]
                        return salty_password(name, password,
                                              taste) == hashedpassword

                    if tasting_salt(username, password, stored_password):
                        f.session['name'] = username
                        f.session['email'] = email
                        f.session['id'] = checkDB.id
                        f.session['picture'] = checkDB.picture
                        #return f.render_template('welcome.html', name=username) # noqa
                        print('using  f.url_for to listing')
                        return f.redirect(f.url_for('listing'))

                    else:
                        return f.render_template('login-in.html',
                                                 error='Invalid Username or Password') # noqa
            else:
                f.flash('You are not registered.  Please Register or login using Google Login') # noqa
                return f.render_template('register.html', **parmas)
        else:
            return f.render_template('login-in.html')


@app.url_defaults
def hashed_url_for_static_file(endpoint, values):
    """
    Copied from https://gist.github.com/Ostrovski/f16779933ceee3a9d181
    designed to consistently update css/html for facelifting real-time
    """
    if 'static' == endpoint or endpoint.endswith('.static'):
        filename = values.get('filename')
        if filename:
            if '.' in endpoint:  # has higher priority
                blueprint = endpoint.rsplit('.', 1)[0]
            else:
                blueprint = f.request.blueprint  # can be None too

            if blueprint:
                static_folder = app.blueprints[blueprint].static_folder
            else:
                static_folder = app.static_folder

            param_name = 'h'
            while param_name in values:
                param_name = '_' + param_name
            values[param_name] = static_file_hash(os.path.join(static_folder, filename)) # noqa


def static_file_hash(filename):
    return int(os.stat(filename).st_mtime)
    # or app.config['last_build_timestamp'] or md5(filename) or etc...


if __name__ == '__main__':
    app.secret_key = "GimmeBurger"
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
