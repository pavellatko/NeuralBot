from flask import Flask, jsonify
import neural_worker
from db import Connector

app = Flask(__name__)

connection = Connector()
Session = connection.Session
engine = connection.engine

worker_thread = neural_worker.ImageProcessor(Session, engine)
worker_thread.start()

