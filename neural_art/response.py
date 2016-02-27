import json


def image_processing_started():
    return json.dumps({
        'status': 'initializing',
    })


def image_iterations_progress(current_it, count_it):
    return json.dumps({
        'status': 'processing',
        'done_iterations': current_it,
        'iterations_number': count_it
    })


def image_processing_ended():
    return json.dumps({
        'status': 'done'
    })