from itertools import groupby
from flask import render_template, request, Blueprint, url_for, jsonify
from flask_login import current_user, login_required
import os
from flaskblog.models import Post, Comments
from flaskblog.schemas import PostSchema
from flaskblog import db

main_api = Blueprint('main_api', __name__)


@main_api.route("/home/json", methods=['POST', 'GET'])
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    if current_user.is_authenticated:
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    else:
        image_file = ""
    comments = Comments.query.all()
    comm_ents = Comments.query.order_by(Comments.date_posted.desc())
    # post_s = Post.query.all()
    post_s = Post.query.order_by(Post.date_posted.desc())

    dict_list = []
    new_dict_list = []
    dicted_data = {}
    for post in post_s:
        if os.path.exists(str(post.id) + "_.txt"):
            with open(str(post.id) + "_.txt", 'r') as reader:
                json_text = reader.read()
                splited = json_text.splitlines()
                # print(splited)
                # print(len(splited))
                reader.close()
            # dict_list = [0] * len(splited)
            for x in range(0, len(splited)):
                data_sp = splited[x].split(',')
                it = iter(data_sp)
                dicted_data = dict(zip(it, it))
                # dict_list[x] = dicted_data
                dict_list.append(dicted_data)
            # new_dict_list.append(dict_list)
            dict_list.append('.')
    i = (list(g) for _, g in groupby(dict_list, key='.'.__ne__))
    final_list = [a + b for a, b in zip(i, i)]
    # print(final_list)
    posts_schema = PostSchema(many=True)
    post_t = db.session.query(Post).all()
    result = posts_schema.dump(post_t)
    return jsonify(result)


'''@main_api.route("/about")
def about():
    if current_user.is_authenticated:
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    else:
        image_file = ""
    comm_ents = Comments.query.order_by(Comments.date_posted.desc())
    post_s = Post.query.order_by(Post.date_posted.desc())
    return render_template('about.html', title='About', image_file=image_file, comm_ents=comm_ents, post_s=post_s)


@main_api.route('/background_process')
@login_required
def background_process():
    try:
        lang = request.args.get('proglang', 0, type=str)
        user = request.args.get('user', 0, type=str)
        post_id = request.args.get('post_id', 0, type=str)
        status = True
        data = f'user,{user},result,{lang.lower()},id,{post_id}'
        if os.path.exists(post_id + "_.txt"):
            with open(post_id + "_.txt", 'r') as reader:
                json_text = reader.read()
                splited = json_text.splitlines()
                # print(len(splited))
                reader.close()
            for x in range(0, len(splited)):
                data_sp = splited[x].split(',')
                it = iter(data_sp)
                dicted_data = dict(zip(it, it))
                if dicted_data['user'] != user:
                    pass
                else:
                    status = False
        if status:
            with open(post_id + "_.txt", 'a') as writer:
                writer.write(str(data) + '\n')
                writer.close()
            if lang:
                return jsonify(result=f'Data Received({lang}) from {user}.')
        else:
            return jsonify(result=f'Data Received ({lang}) from {user}, but invalid.')
    except Exception as e:
        return str(e)

'''