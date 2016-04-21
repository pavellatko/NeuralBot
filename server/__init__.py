from sqlalchemy.ext.automap import automap_base

from database.db import Connector
from neural_art import neural_worker
from database import engine, Session, Image, Queue
from flask import Flask

app = Flask(__name__)
worker_thread = neural_worker.ImageProcessor(engine, Session)
db_session = Session()

from server import rest
