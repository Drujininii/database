conn_string = "host='localhost' port='5432' dbname='flask_db_1' user='igor' password='qwerty'"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

def posts_create(slug_or_id, posts_data):
    sql = get_slug_or_id(slug_or_id)
    cursor.execute(sql, (slug_or_id, ))
    thread_tuple = cursor.fetchone()
    if thread_tuple:
        thread_id = thread_tuple[0]
        forum_slug = thread_tuple[1]
        tz = pytz.timezone('Europe/Moscow')
        timestamp_now = time.time()
        created_date = datetime.datetime.fromtimestamp(timestamp_now, tz).isoformat()
        posts_full_data = list()
        cursor.execute('''
        SELECT min(id) FROM db_posts
        WHERE thread = %s;
        ''', (thread_id, ))
        parent_id_select = cursor.fetchone()[0]
        parent_id = 0
        post_id = 0
        if parent_id_select:
            parent_id = parent_id_select
        cursor.execute('''
        SELECT max(id) FROM db_posts''')
        max_id = cursor.fetchone()[0]
        if not max_id:
            cursor.execute('''
                SELECT nextval(pg_get_serial_sequence('db_posts', 'id'))
                ''')
            post_id = cursor.fetchone()[0]
        else:
            post_id = max_id
        print('max_id_tuple: ', max_id)
        for post in posts_data:
            post_id += 1
            print('post_id: ', post_id)
            print('post parent: ', post.get('parent'))
            mpath = list()
            parent_mpath = list()
            if post.get('parent'):
                parent_id = post.get('parent')
                cursor.execute('''
                SELECT mpath FROM db_posts
                WHERE parent = %s
                ''', (parent_id, ))
                parent_mpath_tuple = cursor.fetchone()
                if parent_mpath_tuple:
                    print('parent_mpath_tuple: ', parent_mpath_tuple)
                    parent_mpath = parent_mpath_tuple[0]
                    parent_mpath.append(parent_id)
                else:
                    for node in posts_full_data:
                        if parent_id == node.get('id'):
                            parent_mpath = node.get('mpath')
                            parent_mpath.append(parent_id)
                mpath = parent_mpath
            else:
                mpath.append(0)
            print(mpath)
            cursor.execute('''
                        INSERT INTO db_posts (author, created, forum, 
                        message, parent, thread, mpath)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ''', (post['author'], created_date, forum_slug,
                              post['message'], post.get('parent') or 0, thread_id, mpath))

            posts_full_data.append(
                posts_add_info(post, created_date, forum_slug,
                               parent_id, thread_id, post_id, mpath))
            if parent_id == 0:
                parent_id = post_id
        conn.commit()
        response = {'posts': posts_full_data, 'status_code': 201}
        return response
    message_obj = {'message': 'Cant find thread'}
    response = {'message': message_obj, 'status_code': 404}
    return response


def get_slug_or_id(slug_or_id):
    if not slug_or_id.isdigit():
        sql = '''
        SELECT id, forum, posts FROM db_threads
        WHERE LOWER(slug) = LOWER(%s)
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