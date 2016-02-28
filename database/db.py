from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

DB_URI = 'sqlite:///image_queue'


class Connector(object):

    def __init__(self):
        self.engine = create_engine(DB_URI, echo=False,
                                    connect_args={'check_same_thread': False})
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
