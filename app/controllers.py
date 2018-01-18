import psycopg2
import datetime
import pytz
import time

conn_string = "host='localhost' port='5432' dbname='flask_db_1' user='igor' password='qwerty'"
conn = psycopg2.connect(conn_string)
# conn.set_isolation_level(2)


def create_user(user_data):
    cursor = conn.cursor()
    try:
        cursor.execute("""
          INSERT INTO db_users (about, email, fullname, nickname)
          VALUES (%s, %s, %s, %s);
                          """,
                       (user_data['about'], user_data['email'], user_data['fullname'], user_data['nickname']))
        conn.commit()
    except Exception:
        conn.rollback()
        cursor.execute("""
          SELECT * FROM db_users
          WHERE email = %s OR nickname = %s; 
        """, (user_data['email'], user_data['nickname']))
        conn.commit()
        tuples = cursor.fetchall()
        cursor.close()

        user_list = tuples_to_user(tuples)
        response = {'user': user_list, 'status_code': 409}
        return response
    else:
        cursor.close()
        user = user_data
        response = {'user': user, 'status_code': 201}
        return response


def tuples_to_user(tuples):
    users = []
    for node in tuples:
        user = tuple_to_user(node)
        users.append(user)
    return users


def tuple_to_user(node):
    user = {'about': node[1],
            'email': node[2],
            'fullname': node[3],
            'nickname': node[4],
            }
    return user


def get_user_data(nickname):
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM db_users
    WHERE nickname = %s;
    """, (nickname, ))
    conn.commit()
    user_tuple = cursor.fetchone()
    cursor.close()

    if user_tuple:
        user = tuple_to_user(user_tuple)
        response = {'user': user, 'status_code': 200}
        return response
    else:
        message = {'message': "Can' t find user"}
        response = {'message': message, 'status_code': 404}
        return response


def set_user_data(nickname, user_data):
    cursor = conn.cursor()
    try:
        cursor.execute("""
          SELECT * FROM db_users
          WHERE nickname = %s
        """, (nickname, ))
        user_tuple = cursor.fetchone()
        if user_tuple:
            user = tuple_to_user(user_tuple)
            for field in user_data:
                user[field] = user_data[field]
            cursor.execute("""
                  UPDATE db_users SET about = (%s), email = (%s), fullname = (%s)
                  WHERE nickname = %s;
                """, (user['about'], user['email'], user['fullname'], nickname))
            conn.commit()
            cursor.close()
            user['nickname'] = nickname
            response = {'user': user, 'status_code': 200}
            return response
        else:
            conn.rollback()
            cursor.close()
            message_obj = {'message': 'Can t find user'}
            response = {'message': message_obj, 'status_code': 404}
            return response
    except Exception:
        conn.rollback()
        cursor.close()
        message_obj = {'message': 'User already exist'}
        response = {'message': message_obj, 'status_code': 409}
        return response


def forum_create(forum_data):
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT nickname FROM db_users
        WHERE nickname = %s
        """, (forum_data['user'], ))
        nickname_tuple = cursor.fetchone()
        if nickname_tuple:
            nickname = nickname_tuple[0]
            cursor.execute("""
            INSERT INTO db_forums (slug, title, user_creator)
            VALUES (%s, %s, %s);
            """, (forum_data['slug'], forum_data['title'], nickname))
            conn.commit()
            cursor.close()
            forum = forum_data
            forum['posts'] = 0
            forum['threads'] = 0
            forum['user'] = nickname
            response = {'forum': forum, 'status_code': 201}
            return response
        else:
            conn.rollback()
            cursor.close()

            message_obj = {'message': 'Can t find user with nickname'}
            response = {'message': message_obj, 'status_code': 404}
            return response
    except Exception as err:
        conn.rollback()
        cursor.close()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM db_forums 
        WHERE slug = %s;
        """, (forum_data['slug'], ))

        forum_tuple = cursor.fetchone()
        cursor.close()

        forum = tuple_to_forum(forum_tuple)
        response = {'forum': forum, 'status_code': 409}
        return response


def tuple_to_forum(forum_tuple):
    forum = {'slug': forum_tuple[1],
             'title': forum_tuple[2],
             'user': forum_tuple[3],
             'posts': forum_tuple[4],
             'threads': forum_tuple[5]}
    return forum


def get_forum_detail(slug):
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM db_forums
    WHERE slug = %s
    """, (slug, ))
    forum_tuple = cursor.fetchone()
    if forum_tuple:
        conn.commit()
        cursor.close()
        forum = tuple_to_forum(forum_tuple)
        response = {'forum': forum, 'status_code': 200}
        return response
    conn.commit()
    cursor.close()

    message_obj = {'message': 'Cant find forum'}
    response = {'message': message_obj, 'status_code': 404}
    return response


def thread_create(slug, thread_data):
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM db_users
    WHERE nickname = %s
    ''', (thread_data['author'], ))
    author_tuple = cursor.fetchone()
    if author_tuple:
        author = author_tuple[4]
        cursor.execute('''
        SELECT slug FROM db_forums
        WHERE slug = %s
        ''', (slug, ))
        forum_slug_tuple = cursor.fetchone()
        if forum_slug_tuple:
            forum_slug = forum_slug_tuple[0]
            thread_id = 0
            try:
                cursor.execute('''
                INSERT INTO db_threads (author, created, forum, message, title, slug)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
                ''', (author, thread_data.get('created'), forum_slug,
                      thread_data['message'], thread_data['title'],
                      thread_data.get('slug')))
                thread_id = cursor.fetchone()[0]
                cursor.execute('''
                UPDATE db_forums SET threads = threads + 1
                WHERE slug = %s
                ''', (slug, ))
                conn.commit()
                cursor.close()

            except Exception:
                conn.rollback()
                cursor.close()
                cursor = conn.cursor()
                cursor.execute('''
                SELECT id, author, 
                    to_char (created::timestamp at time zone 'Etc/UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'), 
                    forum, message, title, votes, slug FROM db_threads
                WHERE slug = %s
                ''', (thread_data.get('slug'), ))

                thread_tuple = cursor.fetchone()
                cursor.close()

                thread = tuple_to_thread(thread_tuple)
                response = {'thread': thread, 'status_code': 409}
                return response
            cursor = conn.cursor()
            try:
                cursor.execute('''
                                INSERT INTO db_active_users (forum, nickname, user_id, about, email, fullname)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                ON CONFLICT (forum, nickname) DO NOTHING ;
                                ''', (forum_slug, author, author_tuple[0], author_tuple[1], author_tuple[2],
                                      author_tuple[3]))
                conn.commit()
                cursor.close()

            except Exception:
                conn.rollback()
                cursor.close()

            thread = thread_data
            thread['forum'] = forum_slug
            thread['author'] = author
            thread['id'] = thread_id
            response = {'thread': thread, 'status_code': 201}
            return response
    conn.rollback()
    cursor.close()

    message_obj = {'message': 'Cant find thread'}
    response = {'message': message_obj, 'status_code': 404}
    return response


# нужен ли select title? может сразу селект из треад?
def get_forum_threads(slug, parameters):
    cursor = conn.cursor()
    cursor.execute('''
    SELECT title FROM db_forums
    WHERE slug = %s;
    ''', (slug, ))
    forum_title_tuple = cursor.fetchone()
    if forum_title_tuple:
        sql = get_forum_threads_sql_by_params(parameters)
        if parameters['since']:
            cursor.execute(sql, (slug, parameters['since'], parameters['limit']))
        else:
            cursor.execute(sql, (slug, parameters['limit']))
        threads = []
        for thread_tuple in cursor:
            thread = tuple_to_thread(thread_tuple)
            threads.append(thread)
        conn.commit()
        cursor.close()

        response = {'threads': threads, 'status_code': 200}
        return response
    conn.rollback()
    cursor.close()

    message_obj = {'message': 'Cant find forum'}
    response = {'message': message_obj, 'status_code': 404}
    return response


# проверить индексы
def get_forum_threads_sql_by_params(parameters):
    if parameters['order'] == 'ASC':
        if parameters['since']:
            sql = '''
                   SELECT id, author, 
                   to_char (created::timestamp at time zone 'Etc/UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'), 
                   forum, message, title, votes, slug
                   FROM db_threads
                   WHERE forum = %s and created >= (%s)::TIMESTAMP WITH TIME ZONE
                   ORDER BY created 
                   LIMIT (%s);
                   '''
        else:
            sql = '''
                    SELECT id, author, 
                    to_char (created::timestamp at time zone 'Etc/UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'), 
                    forum, message, title, votes, slug
                    FROM db_threads
                    WHERE forum = %s
                    ORDER BY created 
                    LIMIT (%s);
                    '''
    else:
        if parameters['since']:
            sql = '''
                   SELECT id, author, 
                   to_char (created::timestamp at time zone 'Etc/UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'), 
                   forum, message, title, votes, slug
                   FROM db_threads
                   WHERE forum = %s and created <= (%s)::TIMESTAMP WITH TIME ZONE
                   ORDER BY created DESC
                   LIMIT (%s);
                   '''
        else:
            sql = '''
                    SELECT id, author, 
                    to_char (created::timestamp at time zone 'Etc/UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'), 
                    forum, message, title, votes, slug
                    FROM db_threads
                    WHERE forum = %s
                    ORDER BY created DESC
                    LIMIT (%s);
                    '''
    return sql


def tuple_to_thread(thread_tuple):
    thread = dict()
    thread['id'] = thread_tuple[0]
    thread['author'] = thread_tuple[1]
    thread['created'] = thread_tuple[2]
    thread['forum'] = thread_tuple[3]
    thread['message'] = thread_tuple[4]
    thread['title'] = thread_tuple[5]
    thread['votes'] = thread_tuple[6]
    thread['slug'] = thread_tuple[7]
    return thread


def posts_create(slug_or_id, posts_data):
    cursor = conn.cursor()
    current_slug_or_id = slug_or_id
    sql = get_slug_or_id(current_slug_or_id)
    cursor.execute(sql, (current_slug_or_id, ))
    thread_tuple = cursor.fetchone()
    if not thread_tuple:
        message_obj = {'message': 'Cant find thread'}
        response = {'message': message_obj, 'status_code': 404}
        return response
    thread_id = thread_tuple[0]
    forum_slug = thread_tuple[1]
    tz = pytz.timezone('Europe/Moscow')
    timestamp_now = time.time()
    created_date = datetime.datetime.fromtimestamp(timestamp_now, tz).isoformat()
    posts_full_data = list()
    parent_id = 0

    tz = pytz.timezone('UTC')
    date_to_response = datetime.datetime.fromtimestamp(timestamp_now, tz).strftime('%Y-%m-%dT%H:%M:%S.%f')[
                       0:23] + 'Z'

    for post in posts_data:
        # post_id += 1
        mpath = list()
        cursor.execute('''
            SELECT nickname FROM db_users
            WHERE nickname = %s;''', (post['author'], ))
        user_tuple = cursor.fetchone()
        if not user_tuple:
            message_obj = {'message': 'Cant find user'}
            response = {'message': message_obj, 'status_code': 404}
            return response
        if post.get('parent'):
            mpath_in_posts = find_parent_in_request_posts(
                post, posts_full_data)
            if mpath_in_posts:
                pass
            else:
                cursor.execute('''
            SELECT thread, mpath FROM db_posts
            WHERE id = %s;
            ''', (post.get('parent'), ))
                parent_thread_tuple = cursor.fetchone()
                if not parent_thread_tuple:
                    message_obj = {'message': 'Parent thread does not exist. Parent id: %d' % post.get('parent')}
                    response = {'message': message_obj, 'status_code': 409}
                    return response
                parent_thread = parent_thread_tuple[0]
                if parent_thread != thread_id:
                    message_obj = {'message': 'Parent post was created in another. Parent id: %d' % post.get('parent')}
                    response = {'message': message_obj, 'status_code': 409}
                    return response
                parent_mpath = parent_thread_tuple[1]
                mpath = parent_mpath

        cursor.execute('''
                    INSERT INTO db_posts (author, created, forum, 
                    message, parent, thread)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id;
                    ''', (post['author'], created_date, forum_slug,
                          post['message'], post.get('parent') or 0, thread_id))
        post_id = cursor.fetchone()[0]
        mpath.append(post_id)
        cursor.execute('''
        UPDATE db_posts SET mpath = %s 
        WHERE id = %s
        ''', (mpath, post_id))

        posts_full_data.append(
                posts_add_info(post, date_to_response, forum_slug,
                               parent_id, thread_id, post_id, mpath))
    active_users = set()
    cursor.execute('''
    UPDATE db_forums SET posts = posts + %s
    WHERE slug = %s
    ''', (len(posts_data), forum_slug))
    try:
        conn.commit()
        for post in posts_data:
            if post['author'].lower() not in active_users:
                cursor.execute('''
                            SELECT * FROM db_users
                            WHERE nickname = %s;''', (post['author'],))
                user_tuple = cursor.fetchone()
                active_users.add(post['author'].lower())
                cursor.execute('''
                    INSERT INTO db_active_users (forum, nickname, user_id, about, email, fullname)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (forum, nickname) DO NOTHING ;
                    ''', (forum_slug, post['author'], user_tuple[0], user_tuple[1], user_tuple[2],
                          user_tuple[3]))
                conn.commit()
    except Exception as err:
        conn.rollback()
        cursor.close()
        message_obj = {'message': 'Cant find thread'}
        response = {'message': message_obj, 'status_code': 404}
        return response
    cursor.close()
    response = {'posts': posts_full_data, 'status_code': 201}
    return response


def set_mpath(post_id, parent_mpath):
    parent_mpath.append(post_id)
    mpath = parent_mpath
    return mpath


def find_parent_in_request_posts(post, posts_full_data):
    parent_id = post['parent']
    for node in posts_full_data:
        if parent_id == node['id']:
            parent_mpath = node.get('mpath')
            # parent_mpath.append(post_id)
            mpath = parent_mpath
            return mpath
    return None


def get_slug_or_id(slug_or_id):
    if not slug_or_id.isdigit():
        sql = '''
        SELECT id, forum, posts FROM db_threads
        WHERE slug = %s
        '''
    else:
        sql = '''
        SELECT id, forum, posts FROM db_threads
        WHERE id = (%s)
        '''
    return sql


def posts_add_info(post, created_date, forum_slug, posts_number,
                   thread_id, post_id, mpath):
    post_full = post
    post_full['created'] = created_date
    post_full['forum'] = forum_slug
    post_full['posts_number'] = posts_number
    post_full['thread'] = thread_id
    post_full['id'] = post_id
    post_full['mpath'] = mpath
    return post_full


def vote_add(slug_or_id, vote_data):
    cursor_temp = conn.cursor()
    sql = get_full_thread_info_by_slug_or_id_for_update(slug_or_id)
    cursor_temp.execute(sql, (slug_or_id,))
    thread_tuple = cursor_temp.fetchone()
    if not thread_tuple:
        conn.rollback()
        cursor_temp.close()
        message_obj = {'message': 'Cant find thread'}
        response = {'message': message_obj, 'status_code': 404}
        return response
    thread = tuple_to_thread(thread_tuple)
    sql = get_vote_sql_by_slug_or_id(thread['id'])
    cursor_temp.execute(sql, (thread['id'], vote_data['nickname']))
    vote_tuple = cursor_temp.fetchone()

    if vote_tuple:
        voice = vote_tuple[1]
    else:
        voice = 0

    sql = get_update_sql_threads_by_id()
    cursor_temp.execute(sql, (vote_data['voice'] - voice, thread['id']))
    real_votes = cursor_temp.fetchone()
    sql = get_insert_sql_vote_by_slug_or_id()
    try:
        cursor_temp.execute(sql, (thread['slug'], thread['id'],
                                  vote_data['nickname'], vote_data['voice'],
                                  vote_data['voice']))
        old_thread_vote = thread['votes']
        thread['votes'] = thread['votes'] + vote_data['voice'] - voice
        cursor_temp.close()
        conn.commit()
        thread['votes'] = real_votes[0]
        thread['vote_author'] = vote_data['nickname']
        response = {'thread': thread, 'status_code': 200}
        return response
    except Exception as err:
        print('err: ', err)
        conn.rollback()
        cursor_temp.close()
        message_obj = {'message': 'Cant find user or something else'}
        response = {'message': message_obj, 'status_code': 404}
        return response


# проверить индексы!
def get_vote_sql_by_slug_or_id(slug_or_id):
    sql = '''
        SELECT nickname, voice FROM db_votes
        WHERE thread_id = %s AND nickname = %s
        '''
    return sql


# проверить индексы!
def get_full_thread_info_by_slug_or_id(slug_or_id):
    if not slug_or_id.isdigit():
        sql = '''
        SELECT id, author, 
                    to_char (created::timestamp at time zone 'Etc/UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'), 
                    forum, message, title, votes, slug FROM db_threads
        WHERE slug = %s
        '''
    else:
        sql = '''
        SELECT id, author, 
                    to_char (created::timestamp at time zone 'Etc/UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'), 
                    forum, message, title, votes, slug FROM db_threads
        WHERE id = %s
        '''
    return sql


# slug нужен? может просто id
def get_full_thread_info_by_slug_or_id_for_update(slug_or_id):
    if not slug_or_id.isdigit():
        sql = '''
        SELECT id, author, 
                    to_char (created::timestamp at time zone 'Etc/UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'), 
                    forum, message, title, votes, slug FROM db_threads
        WHERE slug = %s
        '''
    else:
        sql = '''
        SELECT id, author, 
                    to_char (created::timestamp at time zone 'Etc/UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'), 
                    forum, message, title, votes, slug FROM db_threads
        WHERE id = %s
        '''
    return sql


def get_update_sql_threads_by_id():
    sql = '''
            UPDATE db_threads SET votes = votes+%s
            WHERE id = %s
            RETURNING votes;
            '''
    return sql


def get_insert_sql_vote_by_slug_or_id():
    sql = '''
        INSERT INTO db_votes (thread_slug, thread_id, nickname, voice)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (nickname, thread_id) DO UPDATE SET voice = %s;
        '''
    return sql


#проверить индексы
def get_thread_detail(slug_or_id):
    cursor = conn.cursor()
    sql = get_full_thread_info_by_slug_or_id(slug_or_id)
    cursor.execute(sql, (slug_or_id, ))
    thread_tuple = cursor.fetchone()
    conn.commit()
    cursor.close()

    if thread_tuple:
        thread = tuple_to_thread(thread_tuple)
        response = {'thread': thread, 'status_code': 200}
        return response
    message_obj = {'message': 'Cant find thread'}
    response = {'message': message_obj, 'status_code': 404}
    return response


def update_thread_detail(slug_or_id, thread_data):
    cursor = conn.cursor()
    sql = get_full_thread_info_by_slug_or_id(slug_or_id)
    cursor.execute(sql, (slug_or_id,))
    thread_tuple = cursor.fetchone()
    if thread_tuple:
        thread = tuple_to_thread(thread_tuple)
        for key in thread_data:
            thread[key] = thread_data[key]
        sql = update_thread_info_by_id()
        cursor.execute(sql, (thread['title'], thread['message']))
        conn.commit()
        cursor.close()

        response = {'thread': thread, 'status_code': 200}
        return response
    conn.rollback()
    cursor.close()

    message_obj = {'message': 'Cant find thread'}
    response = {'message': message_obj, 'status_code': 404}
    return response


def update_thread_info_by_id():
    sql = '''
        UPDATE db_threads SET (title, message) = (%s, %s)
        '''
    return sql


#проверить индексы
def get_thread_posts(slug_or_id, params):
    cursor = conn.cursor()
    sql = find_thread_sql_by_slug_or_id(slug_or_id)
    cursor.execute(sql, (slug_or_id, ))
    thread_id_tuple = cursor.fetchone()
    if thread_id_tuple:
        thread_id = thread_id_tuple[0]
        if params['sort'] == 'flat':
            sql = get_posts_sql_by_id_flat_sort(params)
        elif params['sort'] == 'tree':
            sql = get_posts_sql_by_id_tree_sort(params)
        elif params['sort'] == 'parent_tree':
            sql = get_posts_sql_by_id_parent_tree_sort(params)
        if not params['since']:
            if params['sort'] == 'parent_tree':
                cursor.execute(sql, (thread_id, params['limit'], thread_id))
            else:
                cursor.execute(sql, (thread_id, params['limit']))
        else:
            since = None
            if params['sort'] == 'tree':
                cursor.execute('''
                SELECT mpath FROM db_posts
                WHERE id = %s
                ''', (params['since'], ))
                since = cursor.fetchone()[0]
            else:
                since = params['since']
            if params['sort'] == 'parent_tree':
                cursor.execute('''
                SELECT mpath[1] FROM db_posts
                WHERE id = %s''', (since, ))
                mpath_1 = cursor.fetchone()[0]
                cursor.execute(sql, (thread_id, mpath_1,
                                     params['limit'], thread_id))
            else:
                cursor.execute(sql, (thread_id, since,
                                     params['limit']))
        conn.rollback()

        posts = list()
        for post_tuple in cursor:
            post = tuple_to_post(post_tuple)
            posts.append(post)
        cursor.close()

        response = {'posts': posts, 'status_code': 200}
        return response
    conn.rollback()
    cursor.close()

    message_obj = {'message': 'Cant find thread'}
    response = {'message': message_obj, 'status_code': 404}
    return response


def find_thread_sql_by_slug_or_id(slug_or_id):
    if not slug_or_id.isdigit():
        sql = '''
        SELECT id FROM db_threads
        WHERE slug = %s
        '''
    else:
        sql = '''
        SELECT id FROM db_threads
        WHERE id = %s
        '''
    return sql


# проверить индесы
def get_posts_sql_by_id_flat_sort(params):
    if params['order'] == 'ASC':
        if not params['since']:
            sql = '''
            SELECT sub_select.id, sub_select.author,
            to_char (sub_select.created::timestamp at time zone 'Etc/UTC',
            'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
            sub_select.forum, sub_select.isedited, sub_select.message,
                  sub_select.parent, sub_select.thread
            FROM db_posts AS sub_select
            WHERE thread = (%s)
            ORDER BY sub_select.created, sub_select.id
            LIMIT %s;
'''
        else:
            sql = '''
            SELECT sub_select.id, sub_select.author,
            to_char (sub_select.created::timestamp at time zone 'Etc/UTC',
            'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
            sub_select.forum, sub_select.isedited, sub_select.message,
                  sub_select.parent, sub_select.thread
            FROM db_posts AS sub_select
            WHERE thread = %s AND id > %s
            ORDER BY sub_select.created, sub_select.id
            LIMIT %s
;'''
    else:
        if not params['since']:
            sql = '''
            SELECT sub_select.id, sub_select.author,
            to_char (sub_select.created::timestamp at time zone 'Etc/UTC',
            'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
            sub_select.forum, sub_select.isedited, sub_select.message,
                  sub_select.parent, sub_select.thread
            FROM db_posts AS sub_select
            WHERE thread = %s
            ORDER BY sub_select.created DESC, sub_select.id DESC
            LIMIT %s
;'''
        else:
            sql = '''
           SELECT sub_select.id, sub_select.author,
            to_char (sub_select.created::timestamp at time zone 'Etc/UTC',
            'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
            sub_select.forum, sub_select.isedited, sub_select.message,
                  sub_select.parent, sub_select.thread
            FROM db_posts AS sub_select
            WHERE thread = %s AND id < %s
            ORDER BY sub_select.created DESC, sub_select.id DESC
            LIMIT %s;
;'''
    return sql


def get_posts_sql_by_id_tree_sort(params):
    if params['order'] == 'ASC':
        if not params['since']:
            sql = '''
                SELECT sub_select.id, sub_select.author,
            to_char (sub_select.created::timestamp at time zone 'Etc/UTC',
            'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
            sub_select.forum, sub_select.isedited, sub_select.message,
                  sub_select.parent, sub_select.thread
                  FROM db_posts AS sub_select
                  WHERE thread = %s
            ORDER BY sub_select.mpath, sub_select.id
            LIMIT %s;
'''
        else:
            sql = '''
                SELECT sub_select.id, sub_select.author,
            to_char (sub_select.created::timestamp at time zone 'Etc/UTC',
            'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
            sub_select.forum, sub_select.isedited, sub_select.message,
                  sub_select.parent, sub_select.thread
                  FROM db_posts AS sub_select
                  WHERE thread = %s AND mpath > %s
            ORDER BY sub_select.mpath, sub_select.id
            LIMIT %s;;
'''
    else:
        if not params['since']:
            sql = '''    
            SELECT sub_select.id, sub_select.author,
            to_char (sub_select.created::timestamp at time zone 'Etc/UTC',
            'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
            sub_select.forum, sub_select.isedited, sub_select.message,
                  sub_select.parent, sub_select.thread
                  FROM db_posts AS sub_select
                  WHERE thread = %s
            ORDER BY sub_select.mpath DESC, sub_select.id DESC
            LIMIT %s;'''
        else:
            sql = '''
                SELECT sub_select.id, sub_select.author,
            to_char (sub_select.created::timestamp at time zone 'Etc/UTC',
            'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
            sub_select.forum, sub_select.isedited, sub_select.message,
                  sub_select.parent, sub_select.thread
                  FROM db_posts AS sub_select
                  WHERE thread = %s AND mpath < %s
            ORDER BY sub_select.mpath DESC,  sub_select.id DESC
            LIMIT %s;
'''
    return sql


# проверить индексы (parent thread id mpath?)?
def get_posts_sql_by_id_parent_tree_sort(params):
    if params['order'] == 'ASC':
        if not params['since']:
            sql = '''
            SELECT sub_select.id, sub_select.author,
            to_char (sub_select.created::timestamp at time zone 'Etc/UTC',
            'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
            sub_select.forum, sub_select.isedited,
            sub_select.message, sub_select.parent,
            sub_select.thread, sub_select.mpath FROM(
            SELECT DB2.id, DB2.mpath FROM db_posts AS DB2
            WHERE DB2.parent = 0
            AND DB2.thread = %s
            ORDER BY DB2.mpath
            LIMIT %s) AS sub_select_2
            JOIN db_posts AS sub_select
            ON sub_select_2.id = sub_select.mpath[1]
            WHERE sub_select.thread = %s
            ORDER BY sub_select.mpath'''
        else:
            sql = '''
            SELECT sub_select.id, sub_select.author,
            to_char (sub_select.created::timestamp at time zone 'Etc/UTC',
            'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
            sub_select.forum, sub_select.isedited,
            sub_select.message, sub_select.parent,
            sub_select.thread, sub_select.mpath  FROM(
            SELECT DB2.id, DB2.mpath FROM db_posts AS DB2
            WHERE DB2.parent = 0
                AND DB2.thread = %s
                AND DB2.mpath[1] > (SELECT mpath[1]
                                    FROM db_posts AS DB3
                        WHERE id = %s)
            ORDER BY DB2.mpath
            LIMIT %s) AS sub_select_2
            JOIN db_posts AS sub_select
            ON sub_select_2.id = sub_select.mpath[1]
            WHERE sub_select.thread = %s
            ORDER BY sub_select.mpath;'''
    else:
        if not params['since']:
            sql = '''
             SELECT sub_select.id, sub_select.author,
            to_char (sub_select.created::timestamp at time zone 'Etc/UTC',
            'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
            sub_select.forum, sub_select.isedited,
            sub_select.message, sub_select.parent,
            sub_select.thread, sub_select.mpath  FROM(
            SELECT DB2.id, DB2.mpath FROM db_posts AS DB2
            WHERE DB2.parent = 0
            AND DB2.thread = %s
            ORDER BY DB2.mpath DESC 
            LIMIT %s) AS sub_select_2
            JOIN db_posts AS sub_select
            ON sub_select_2.id = sub_select.mpath[1]
            WHERE sub_select.thread = %s
            ORDER BY sub_select.mpath DESC;'''
        else:
            sql = '''
            SELECT sub_select.id, sub_select.author,
            to_char (sub_select.created::timestamp at time zone 'Etc/UTC',
            'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
            sub_select.forum, sub_select.isedited,
            sub_select.message, sub_select.parent,
            sub_select.thread, sub_select.mpath FROM(
            SELECT DB2.id, DB2.mpath FROM db_posts AS DB2
            WHERE DB2.parent = 0
                AND DB2.thread = %s
                AND DB2.mpath[1] < %s
            ORDER BY DB2.mpath DESC 
            LIMIT %s) AS sub_select_2
            JOIN db_posts AS sub_select
            ON sub_select_2.id = sub_select.mpath[1]
            WHERE sub_select.thread = %s
            ORDER BY sub_select.mpath DESC;'''
    return sql


def tuple_to_post(post_tuple):
    post = dict()
    post['id'] = post_tuple[0]
    post['author'] = post_tuple[1]
    post['created'] = post_tuple[2]
    post['forum'] = post_tuple[3]
    post['isEdited'] = post_tuple[4]
    post['message'] = post_tuple[5]
    post['parent'] = post_tuple[6]
    post['thread'] = post_tuple[7]
    return post


def get_forum_active_users(slug, params):
    cursor = conn.cursor()
    cursor.execute('''
    SELECT slug FROM db_forums
    WHERE slug = %s
    ''', (slug, ))
    forum_slug_tuple = cursor.fetchone()
    if forum_slug_tuple:
        sql = get_active_users_sql_by_slug(params)
        if not params['since']:
            cursor.execute(sql, (slug, params['limit']))
        else:
            cursor.execute(sql, (slug, params['since'], params['limit']))
        users = list()
        for user_tuple in cursor:
            post = tuple_to_user(user_tuple)
            users.append(post)
        conn.rollback()
        cursor.close()

        response = {'users': users, 'status_code': 200}
        return response
    conn.rollback()
    cursor.close()

    message_obj = {'message': 'Cant find forum'}
    response = {'message': message_obj, 'status_code': 404}
    return response


# проверить индесы
def get_active_users_sql_by_slug(params):
    if params['order'] == 'ASC':
        if not params['since']:
            sql = '''
            SELECT U.user_id, U.about, U.email, U.fullname, U.nickname
            FROM db_active_users AS U
            WHERE U.forum = %s
            ORDER BY U.nickname
            LIMIT %s;'''
        else:
            sql = '''
      
            SELECT U.user_id, U.about, U.email, U.fullname, U.nickname
            FROM db_active_users AS U
            WHERE U.forum = %s AND U.nickname > %s
            ORDER BY U.nickname
            LIMIT %s;'''
    else:
        if not params['since']:
            sql = '''
            SELECT U.user_id, U.about, U.email, U.fullname, U.nickname
                  FROM db_active_users AS U
                  WHERE U.forum = %s
            ORDER BY U.nickname DESC
            LIMIT %s;'''
        else:
            sql = '''
            SELECT U.user_id, U.about, U.email, U.fullname, U.nickname
                  FROM db_active_users AS U
                  WHERE U.forum = %s and U.nickname  < %s
            ORDER BY U.nickname DESC
            LIMIT %s;'''
    return sql


# проверить индексы
def get_post_detail(id, related):
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, author, 
                to_char (created::TIMESTAMP AT TIME ZONE 'Etc/UTC',
                'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
                forum, isedited, message, parent, thread FROM db_posts
    WHERE id = (%s)
    ''', (id, ))
    post_tuple = cursor.fetchone()
    if post_tuple:
        post = tuple_to_post(post_tuple)
        post_json = {'post': post}
        if related:
            if 'user' in related:
                sql = get_related_user_sql()
                cursor.execute(sql, (post['author'], ))
                user_tuple = cursor.fetchone()
                user = tuple_to_user(user_tuple)
                post_json['author'] = user
            if 'thread' in related:
                sql = get_related_thread_sql()
                cursor.execute(sql, (post['thread'],))
                thread_tuple = cursor.fetchone()
                thread = tuple_to_thread(thread_tuple)
                post_json['thread'] = thread
            if 'forum' in related:
                sql = get_related_forum_sql()
                cursor.execute(sql, (post['forum'],))
                forum_tuple = cursor.fetchone()
                forum = tuple_to_forum(forum_tuple)
                post_json['forum'] = forum
        conn.rollback()
        cursor.close()

        response = {'post': post_json, 'status_code': 200}
        return response
    conn.rollback()
    cursor.close()

    message_obj = {'message': 'Cant find post'}
    response = {'message': message_obj, 'status_code': 404}
    return response


def get_related_user_sql():
    sql = '''
        SELECT * FROM db_users
        WHERE nickname = %s'''
    return sql


def get_related_thread_sql():
    sql = '''
        SELECT id, author, 
                    to_char (created::timestamp at time zone 'Etc/UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'), 
                    forum, message, title, votes, slug FROM db_threads
        WHERE id = %s
        '''
    return sql


def get_related_forum_sql():
    sql = '''
        SELECT * FROM db_forums
        WHERE slug = %s
        '''
    return sql


def update_post_detail(id, post_data):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, author, 
                to_char (created::timestamp at time zone 'Etc/UTC',
                'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'), 
                forum, isedited, message, parent, thread FROM db_posts
        WHERE id = (%s)
        ''', (id, ))
    post_tuple = cursor.fetchone()
    if post_tuple:
        post = tuple_to_post(post_tuple)
        if post_data.get('message') and post_data.get('message') != post['message']:
            post['message'] = post_data['message']
            sql = update_post_info_by_id()
            cursor.execute(sql, (post['message'], id))
            conn.commit()
            cursor.close()

            post['isEdited'] = True
        else:
            pass
        conn.rollback()
        cursor.close()

        response = {'post': post, 'status_code': 200}
        return response
    conn.rollback()
    message_obj = {'message': 'Cant find post'}
    response = {'message': message_obj, 'status_code': 404}
    return response


def update_post_info_by_id():
    sql = '''
          UPDATE db_posts SET (message, isedited) = (%s, TRUE)
          WHERE id = %s
            '''
    return sql


def get_service_status():
    cursor = conn.cursor()
    cursor.execute('''
        SELECT count(*) FROM db_forums
        ''')
    forums_number = cursor.fetchone()[0]
    cursor.execute('''
        SELECT count(*) FROM db_posts
        ''')
    posts_number = cursor.fetchone()[0]
    cursor.execute('''
        SELECT count(*) FROM db_threads
        ''')
    threads_number = cursor.fetchone()[0]
    cursor.execute('''
        SELECT count(*) FROM db_users
        ''')

    users_number = cursor.fetchone()[0]
    conn.rollback()
    cursor.close()

    service_status = {'forum': forums_number,
                      'post': posts_number,
                      'thread': threads_number,
                      'user': users_number
                      }
    response = {'service_status': service_status,
                'status_code': 200}
    return response


def service_clear():
    cursor = conn.cursor()
    cursor.execute('''
            DELETE FROM db_forums
            ''')
    cursor.execute('''
            DELETE FROM db_posts
            ''')
    cursor.execute('''
            DELETE FROM db_threads
            ''')
    cursor.execute('''
            DELETE FROM db_users
            ''')
    cursor.execute('''
            DELETE FROM db_votes
            ''')
    cursor.execute('''
            DELETE FROM db_active_users
            ''')
    conn.commit()
    cursor.close()

    response = {'status_code': 200}
    return response

