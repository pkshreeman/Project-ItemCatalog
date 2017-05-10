from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Users, Base, Items, Category

engine = create_engine('postgresql://cataloguser:password@localhost/itemcat')# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


#Items

cat1 = Category(name = "Phone", users_id=1)

item1 = Items(name='iPhone7', description="awesomeness in a handsized package",
            price="$700.00", picture='https://upload.wikimedia.org/wikipedia/commons/e/e2/IPhone_7_%283%29.jpg',
            users_id=1, category=cat1)
item2 = Items(name="Samsung9", description="awesomeness in a unboxed package",
            price="$900.00", picture='https://c1.staticflickr.com/2/1585/24387900439_f3a89d9efb_b.jpg',
            users_id=1, category=cat1)
# session.add(cat1)
# session.add(item1)
# session.add(item2)
cat2 = Category(name="Computers", users_id=2)
item3 = Items(name = 'Macbook Pro', description='awesomeness in a bigger box',
             price='$4,000', picture='https://static.pexels.com/photos/18104/pexels-photo.jpg',
             users_id=3, category=cat2)

session.add(cat2)
session.add(item3)

session.commit()
