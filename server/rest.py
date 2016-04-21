from flask import Flask, make_response, jsonify, abort, Response, request, send_file
from json import dumps
from server import db_session, Image, Queue, app, worker_thread
from config import *
import uuid, os, json


def allowed_file(filename):
    return '.' in filename and \
           get_ext(filename) in ALLOWED_EXTENSIONS


def get_ext(filename):
    return filename.rsplit('.', 1)[1]


def add_img_to_queue(id, subject, style, args, result):
    new_img = Image(ID=id, Subject=subject, Style=style, Status='{"status": "queued"}', Result=result)
    db_session.add(new_img)
    db_session.add(Queue(ID=id, Args=args))
    db_session.commit()

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'success': False,
                                  'error': 'Not found'}), 404)


@app.route('/', methods=['GET'])
def upload_page():
    return '''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>upload</title>
</head>
<body>
  <form action="/api/image" method="post" enctype="multipart/form-data">
  <p>Image
  <p><input type="file" name="subject">
  <p>Style
  <p><input type="file" name="style">
  <p>Arguments in JSON
  <p><input type="text" name="args">
  <p><button type="submit">Submit</button>
</form>
</body>
</html>'''


@app.route('/api/image/<image_id>/status', methods=['GET'])
def get_image_status(image_id):
    img_info = db_session.query(Image).filter(Image.ID==image_id).first()
    if img_info is None:
        abort(404)
    return Response(img_info.Status, mimetype='application/json')


@app.route('/api/image/<image_id>', methods=['GET'])
def get_image(image_id):
    cur_img = db_session.query(Image).filter(Image.ID==image_id).first()
    cur_status = json.loads(cur_img.Status)
    if cur_status['status'] == 'done':
        return send_file(ROOT_PATH + cur_img.Result, 'output' + get_ext(cur_img.Result))
    else:
        abort(404)


@app.route('/api/image/<image_id>', methods=['DELETE'])
def delete_image(image_id):
    cur_img = db_session.query(Image).filter(Image.ID==image_id).first()
    if not cur_img:
        abort(404)
    else:
        if cur_img.Status not in ['queued', 'done']:
            worker_thread.skip()
        os.remove(ROOT_PATH + cur_img.Subject)
        os.remove(ROOT_PATH + cur_img.Style)
        try:
            os.remove(ROOT_PATH + cur_img.Result)
        except:
            pass
        db_session.delete(cur_img)
        db_session.commit()
        return jsonify({'success': True}), 200


@app.route('/api/image', methods=['POST'])
def create_task():
    if 'style' not in request.files or 'subject' not in request.files or \
            not request.files['style'] or not request.files['subject']:
        abort(400)

    style = request.files['style']
    subject = request.files['subject']
    if 'args' in request.form:
        args = request.form['args'] or '{}'
    else:
        args = '{}'

    id = str(uuid.uuid4())

    if allowed_file(style.filename) and allowed_file(subject.filename):
        style_name = os.path.join(UPLOAD_FOLDER, '{}_style.{}'.format(id, get_ext(style.filename)))
        subject_name = os.path.join(UPLOAD_FOLDER, '{}_subject.{}'.format(id, get_ext(subject.filename)))
        result_name = os.path.join(UPLOAD_FOLDER, '{}_result.{}'.format(id, get_ext(subject.filename)))

        style.save(style_name)
        subject.save(subject_name)
        add_img_to_queue(id, subject_name, style_name, args, result_name)
        return jsonify({'success': True, 'id': id}), 201
    else:
        abort(400)

