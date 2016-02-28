from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import scoped_session
from database.db import Connector

connection = Connector()
Session = connection.Session
engine = connection.engine
Base = automap_base()
Base.prepare(engine, reflect=True)
Image = Base.classes.images
Queue = Base.classes.queue
