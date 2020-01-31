import json
import os
from itertools import groupby

from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from flaskblog import db
from flaskblog.models import Post, Comments
from flaskblog.posts.forms import PostForm, CommentForm

posts = Blueprint('posts', __name__)


@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        if form.poll_data.data:
            poll_data = form.poll_data.data.split(',')
            post = Post(title=form.title.data, content=form.content.data, author=current_user, poll_data=poll_data, tag=form.tag.data)
        else:
            post = Post(title=form.title.data, content=form.content.data, author=current_user, tag=form.tag.data)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created', 'success')
        return redirect(url_for('main.home'))
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    comm_ents = Comments.query.order_by(Comments.date_posted.desc())
    post_s = Post.query.order_by(Post.date_posted.desc())
    return render_template('create_post.html', title='New Post', form=form, legend="New Post", image_file=image_file,
                           comm_ents=comm_ents, post_s=post_s)


@posts.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    pos_t = str(post.id)
    comm_ents = Comments.query.order_by(Comments.date_posted.desc())
    post_s = Post.query.order_by(Post.date_posted.desc())
    if current_user.is_authenticated:
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    else:
        image_file = ""
    cmt_form = CommentForm()
    # posts = Post.query.order_by(Post.date_posted.desc())
    comments = Comments.query.filter_by(post_id=post_id).order_by(Comments.date_posted.desc())
    number_cmt = comments.count()
    if cmt_form.validate_on_submit():
        comment = Comments(content=cmt_form.comment.data, post_id=int(pos_t), author=current_user)
        db.session.add(comment)
        db.session.commit()
        cmt_form.comment.data = ""
        flash('Commented successfully', 'success')
        return redirect(url_for('posts.post', post_id=post_id))
    post_poll = Post.query.filter_by(id=post_id).order_by(Post.date_posted.desc())
    dict_list = []
    new_dict_list = []
    dicted_data = {}
    for post in post_poll:
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

    return render_template('post.html', title=post.title, post=post, image_file=image_file, cmt_form=cmt_form,
                           comments=comments, number_cmt=number_cmt, comm_ents=comm_ents, post_s=post_s, final_list=final_list)


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        if form.poll_data.data is not None:
            splited = form.poll_data.data.split(',')
            post.poll_data = splited
        db.session.commit()
        flash('Your post has been updated', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        if post.poll_data is not None:
            listToStr = ','.join([str(elem) for elem in post.poll_data])
            # print(listToStr)
            form.poll_data.data = listToStr
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    comm_ents = Comments.query.order_by(Comments.date_posted.desc())
    post_s = Post.query.order_by(Post.date_posted.desc())
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post',
                           image_file=image_file, comm_ents=comm_ents, post_s=post_s)


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    comment = Comments.query.filter_by(post_id=post_id).delete()
    if os.path.exists(str(post_id) + "_.txt"):
        os.remove(str(post_id) + "_.txt")
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))


@posts.route("/post/<int:post_id>/<int:comment_id>/delete", methods=['POST'])
@login_required
def delete_comment(post_id, comment_id):
    post = Post.query.get_or_404(post_id)
    comment = Comments.query.filter_by(id=comment_id).delete()
    db.session.commit()
    flash('Your comment has been deleted!', 'success')
    return redirect(url_for('posts.post', post_id=post_id))


@posts.route("/post/<int:post_id>/<int:comment_id>", methods=['GET', 'POST'])
@login_required
def comment_notification(post_id, comment_id):
    comments = Comments.query.get(comment_id)
    # print(comments)
    # print(comments.action)
    comments.action = True
    db.session.commit()
    flash(f'Successfully read the comment: {comments.action}', 'success')
    return redirect(url_for('posts.post', post_id=post_id))


@posts.route("/comment/<int:comment_id>/update", methods=['GET', 'POST'])
@login_required
def update_comment(comment_id):
    comments = Comments.query.get_or_404(comment_id)
    if comments.author != current_user:
        abort(403)
    form = CommentForm()

    if form.validate_on_submit():
        comments.content = form.comment.data
        db.session.commit()
        flash('Your comment has been updated', 'success')
        return redirect(url_for('posts.post', post_id=comments.post_id))
    elif request.method == 'GET':
        form.comment.data = comments.content
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    comm_ents = Comments.query.order_by(Comments.date_posted.desc())
    post_s = Post.query.order_by(Post.date_posted.desc())
    return render_template('update_comment.html', title='Update Comment', form=form, legend='Update Comment',
                           image_file=image_file, comm_ents=comm_ents, post_s=post_s)


@posts.route("/search")
@login_required
def search_posts():
    page = request.args.get('page', 1, type=int)
    tag = request.args.get('tag', 0, type=str)
    # posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    posts = Post.query.filter_by(tag=tag).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
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

    return render_template('search_posts.html', posts=posts, title='Home',
                           image_file=image_file, comments=comments, comm_ents=comm_ents, post_s=post_s,
                           final_list=final_list, tag=tag)

