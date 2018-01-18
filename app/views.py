from app import app
from flask import render_template
from flask import request
from flask_responses import json_response
from app import controllers
import json


@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'Igor'}  # выдуманный пользователь
    return render_template('index.html', title='home', user=user)


@app.route('/api/user/<nickname>/create',  methods=['GET', 'POST'])
def user_create(nickname):
    if request.method == 'POST':
        json_request = request.get_json()
        user_data = json_request
        user_data['nickname'] = nickname
        response = controllers.create_user(user_data)
        if response['status_code'] == 409:
            json_resp = app.response_class(
                response=json.dumps(response['user']),
                status=response['status_code'],
                mimetype='application/json'
            )
            return json_resp
        return json_response(response['user'], status_code=response['status_code'])


@app.route('/api/user/<nickname>/profile',  methods=['GET', 'POST'])
def user_profile(nickname):
    if request.method == 'GET':
        response = controllers.get_user_data(nickname)
        if response['status_code'] == 200:
            return json_response(response['user'], status_code=response['status_code'])
        return json_response(response['message'], status_code=response['status_code'])
    else:
        json_request = request.get_json()
        user_data = json_request
        response = controllers.set_user_data(nickname, user_data)
        if response['status_code'] == 200:
            return json_response(response['user'], status_code=response['status_code'])
        return json_response(response['message'], status_code=response['status_code'])


@app.route('/api/forum/create', methods=['POST'])
def forum_create():
    print(request.url)

    json_request = request.get_json()
    forum_data = json_request
    response = controllers.forum_create(forum_data)
    if response['status_code'] == 201 or response['status_code'] == 409:
        return json_response(response['forum'], status_code=response['status_code'])
    return json_response(response['message'], status_code=response['status_code'])


@app.route('/api/forum/<slug>/details')
def forum_detail(slug):
    response = controllers.get_forum_detail(slug)
    if response['status_code'] == 200:
        return json_response(response['forum'], status_code=response['status_code'])
    return json_response(response['message'], status_code=response['status_code'])


@app.route('/api/forum/<slug>/create', methods=['POST'])
def thread_create(slug):
    json_request = request.get_json()
    thread_data = json_request
    response = controllers.thread_create(slug, thread_data)
    if response['status_code'] == 201 or response['status_code'] == 409:
        return json_response(response['thread'], status_code=response['status_code'])
    return json_response(response['message'], status_code=response['status_code'])


# поменять сравнение с нулем в дате
@app.route('/api/forum/<slug>/threads')
def get_forum_threads(slug):
    parameters = dict()
    parameters['limit'] = request.args.get('limit') or 'ALL'
    parameters['since'] = request.args.get('since')
    parameters['order'] = 'DESC' if request.args.get('desc') == 'true' else 'ASC'
    response = controllers.get_forum_threads(slug, parameters)
    if response['status_code'] == 200:
        json_resp = app.response_class(
            response=json.dumps(response['threads']),
            status=response['status_code'],
            mimetype='application/json'
        )
        return json_resp
    return json_response(response['message'], status_code=response['status_code'])


@app.route('/api/thread/<slug_or_id>/create', methods=['POST'])
def posts_create(slug_or_id):
    json_request = request.get_json()
    posts_data = json_request
    response = controllers.posts_create(slug_or_id, posts_data)
    if response['status_code'] == 201:
        json_resp = app.response_class(
            response=json.dumps(response['posts']),
            status=response['status_code'],
            mimetype='application/json'
        )
        return json_resp
    return json_response(response['message'], status_code=response['status_code'])


@app.route('/api/thread/<slug_or_id>/vote', methods=['POST'])
def vote_add(slug_or_id):
    json_request = request.get_json()
    vote_data = json_request
    response = controllers.vote_add(slug_or_id, vote_data)
    if response['status_code'] == 200:
        thread = response['thread']
        # thread['message'] = ''
        # print(json.dumps(thread))
        return json_response(response['thread'], status_code=response['status_code'])
    return json_response(response['message'], status_code=response['status_code'])


@app.route('/api/thread/<slug_or_id>/details', methods=['GET', 'POST'])
def thread_detail(slug_or_id):
    if request.method == 'GET':
        response = controllers.get_thread_detail(slug_or_id)
    else:
        json_request = request.get_json()
        thread_data = json_request
        response = controllers.update_thread_detail(slug_or_id, thread_data)
    if response['status_code'] == 200:
        return json_response(response['thread'], status_code=response['status_code'])
    return json_response(response['message'], status_code=response['status_code'])


@app.route('/api/thread/<slug_or_id>/posts')
def get_thread_posts(slug_or_id):
    parameters = dict()
    parameters['limit'] = request.args.get('limit') or 'ALL'
    parameters['sort'] = request.args.get('sort') or 'flat'
    parameters['order'] = 'DESC' if request.args.get('desc') == 'true' else 'ASC'
    parameters['since'] = request.args.get('since')
    response = controllers.get_thread_posts(slug_or_id, parameters)
    if response['status_code'] == 200:
        json_resp = app.response_class(
            response=json.dumps(response['posts']),
            status=response['status_code'],
            mimetype='application/json'
        )
        return json_resp
    return json_response(response['message'], status_code=response['status_code'])


@app.route('/api/forum/<slug>/users')
def get_forum_active_users(slug):
    parameters = dict()
    parameters['limit'] = request.args.get('limit') or 999999
    parameters['order'] = 'DESC' if request.args.get('desc') == 'true' else 'ASC'
    parameters['since'] = request.args.get('since')
    response = controllers.get_forum_active_users(slug, parameters)
    if response['status_code'] == 200:
        json_resp = app.response_class(
            response=json.dumps(response['users']),
            status=response['status_code'],
            mimetype='application/json'
        )
        return json_resp
    return json_response(response['message'], status_code=response['status_code'])


@app.route('/api/post/<id>/details', methods=['GET', 'POST'])
def post_detail(id):
    if request.method == 'GET':
        related = request.args.get('related')
        response = controllers.get_post_detail(id, related)
    else:
        json_request = request.get_json()
        post_data = json_request
        response = controllers.update_post_detail(id, post_data)
    if response['status_code'] == 200:
        return json_response(response['post'], status_code=response['status_code'])
    return json_response(response['message'], status_code=response['status_code'])


@app.route('/api/service/status')
def get_service_status():
    print(request.url)

    response = controllers.get_service_status()
    return json_response(response['service_status'], status_code=response['status_code'])


@app.route('/api/service/clear', methods=['POST'])
def service_clear():
    print(request.url)

    response = controllers.service_clear()
    return json_response({}, status_code=response['status_code'])



