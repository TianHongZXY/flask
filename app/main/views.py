from flask import render_template, session, redirect, url_for, current_app
from .. import db
from ..models import User
from ..email import send_email
from . import main
from .forms import NameForm


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
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
