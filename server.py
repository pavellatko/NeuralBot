from flask import Flask, make_response, jsonify, abort, Response, request

from db import Connector
from neural_art import neural_worker

from sqlalchemy.ext.automap import automap_base

from json import dumps

connection = Connector()
Session = connection.Session
engine = connection.engine
db_session = Session()
Base = automap_base()
Base.prepare(engine, reflect=True)
Image = Base.classes.images
Queue = Base.classes.queue

worker_thread = neural_worker.ImageProcessor(engine, Session)
worker_thread.start()

app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/api/image/<image_id>/status', methods=['GET'])
def get_image_status(image_id):
    img_info = db_session.query(Image).filter(Image.ID==image_id).first()
    if img_info is None:
        abort(404)
    return Response(img_info.Status, mimetype='application/json')


@app.route('/api/image', methods=['POST'])
def create_task():
    if not request.json or not 'subject' or not 'style' in request.json:
        abort(400)
    data = request.json
    if 'args' not in data:
        data['args'] = {}
    new_img = Image(Status='{"status": "queued"}')
    db_session.add(new_img)
    db_session.commit()
    db_session.refresh(new_img)
    img_id = new_img.ID

    data['args']['output'] = 'images/output_{0}.jpg'.format(img_id)

    try:
        with open('images/subject_{0}.jpg'.format(img_id), 'wb') as subj_file, \
                open('images/style_{0}.jpg'.format(img_id), 'wb') as style_file:
            subj_file.write(data['subject'].decode('base64'))
            style_file.write(data['style'].decode('base64'))
    except:
        abort(400)

    new_img.Style = 'images/style_{0}.jpg'.format(img_id)
    new_img.Subject = 'images/subject_{0}.jpg'.format(img_id)

    db_session.Add(Queue(ID=img_id, Args=dumps(data['args'])))
    db_session.commit()

    return jsonify({'id': img_id}), 201


app.run(debug=True, port=5002)

try:
    while worker_thread.is_alive:
        worker_thread.join(0.1)
except KeyboardInterrupt:
    print "Ctrl-c received! Sending kill to threads..."
    worker_thread.stop()
