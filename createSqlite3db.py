import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

 
engine = create_engine('sqlite:///keniyajie.db', echo=True)
 
# create a Session
Session = sessionmaker(bind=engine)
session = Session()
 
# commit the record the database
session.commit()