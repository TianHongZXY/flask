from flask import render_template, session, redirect, url_for, current_app, flash, request
from .. import db
from ..models import User, Permission, Role, Post
from ..email import send_email
from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm, PostForm
from ..decorators import admin_required, permission_required
from flask_login import login_required, current_user


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    # 渲染的页数从请求的查询字符串(request.args)中获取，如果没有明确指定，默认渲染第一页，type确保参数为int
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, pagination=pagination)


'''
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data, age=form.age.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            session['old'] = form.age.data >= 40
            # 163老是把我发的邮件当垃圾邮件，mmp以后再来搞它
            # if current_app.config['FLASKY_ADMIN']:
            #     send_email(to=current_app.config['FLASKY_ADMIN'], subject='Fuck Flask, fuckkkk!!',
            #                template='mail/new_user', user=user)
        else:
            session['known'] = True
            session['old'] = user.age >= 40

        session['name'] = form.name.data
        return redirect(url_for('main.index'))
    return render_template('index.html',
                           form=form, name=session.get('name'),
                           known=session.get('known', False), old=session.get('old', False))
'''


@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return 'For administrators only!'


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def for_moderators_only():
    return 'For moderators only!'


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('main.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('main.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)

@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', posts=[post])