# UDACITY FSND
## Item Catalog Project
### Objective
1. CRUD - Proof of Concept (or Ability if you prefer)
  1. Create
  2. Read
  3. Update
  4. Delete

2. Develop CRUD abilities by using SQLAlchemy module with the python 2.7
3. Deploy to localhost and allow users operate the website as registered users, and have permissions set due to ownership of postings within the web based catalog.

### File Structure Guide:
- readme.md:  This file that you are reading...
- static folder:
  * css folder
    - Bootstrap files <http://getbootstrap.com/>
    - main2.css (personalized css file)
  * js folder
    - Bootstrap files <http://getbootstrap.com/>
    - glogin.js - abandoned javascript.  Moving the google login javascript outside of the login.html causes complexity of registering authorized urls within google console, and I decided it was simpler to leave it inside html.
  * templates folder: most are self-explanatory
    - deleteitem.html
    - deletelist.html - List = Category (It's easier to type list than category)
    - edititem.html
    - headers.html
    - listings.html - it's odd.  The end of the project, this became the 'landing page' that extends welcome.html and headers.html
    - login-in.html - a old fashioned way of logging in.
    - newitem.html
    - newlisting.hmtl
    - register.html - you may notice that I did not include a 'link' in the website to register.  The design of this project was to use OAuth2 login only, but for testing, it was way easier to create random users this way.  Just go http:localhost:5000/register.html to sign up your imaginary friends.
    - welcome.html - The first landing page during early phase of testing, but became an extension html file instead for listing.html.
  * client_secret.json - a file you copy from google console for credentials purposes.
  * database_setup.py - A program to create tables for the database in this program.  See special instructions below.
  * Implementation.py - $14 dollar word for 'main.py'.  What can I say? Just type ```python Implementation.py``` and go to <http:localhost:5000> to see all this magic come to life!
  * item-makers.py - A program to populate the database with some basic items.  Used for testing.



### What do you need?

The database that I am using is Postgres 9.6.5.  [Install Postgres](https://wiki.postgresql.org/wiki/Detailed_installation_guides).
The programming language that I currently use is python
[Install Python](https://www.python.org/downloads/)

If you are using Linux or MacOS, you should already have Python installed.  

There is also standardized method of using virtualized machine using vagrant and Virtualbox with ready-made files at https://github.com/udacity/fullstack-nanodegree-vm
- [Install Virtualbox](https://www.virtualbox.org/)
- [Install Vagrant](https://www.vagrantup.com/)

For comprehensive guide on creating this virtual standardized server, check out the documentation provided by Udacity:  [Guide](https://docs.google.com/document/d/16IgOm4XprTaKxAa8w02y028oBECOoB1EI1ReddADEeY/pub?embedded=true)

### Now what?

I shall assume you successfully done the following...
1. cloned this repository to your local machine or virtual machine, or cloud machine, or your imaginary machine...
2. that machine have operational Linux/Mac up running with python and Postgres installed.
3. All the modules are available on the machine.  For example, if you see errors with import issues such as "sqlalchemy module is not found",  type ```pip install SQLAlchemy```, by the way, you do also need to ```pip install sqlalchemy-utils``` as well.


#### Special Instructions: Database setup

1. You need to setup a specific user. Go to the folder where Implementation.py is then do the following:

  1. ```sudo su - postgres```
  2. ```psql```
  3. ```create user cataloguser with password "password" createdb```
  4. ```\q```
  5. ```python database_setup.py```
  6. Pray fervently that it works.

2. ```python Implementation.py```

  1. Create at least three users.  If you use OAuth2 process, it will automatically add new users.  Otherwise, go to <http:localhost:5000/register> to add users.
  2. Once you have least three users, ```python item-makers.py``` if you want to populate the database with junk data, albeit few.

3. Play at your heart's content.
