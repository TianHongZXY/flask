from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from .import db
from .models import User, Post


def users(count=100):
    fake = Faker()  
    i = 0
    while i < count:
        u = User(email=fake.email(),
                 username=fake.user_name(),
                 password='password',
                 confirmed=True,
                 name=fake.name(),
                 location=fake.city(),
                 about_me=fake.text(),
                 member_since=fake.past_date())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def posts(count=100):
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        # offset查询过滤器会跳过参数指定的记录数量，而每次跳过的数量用randint随机生成
        # 这样每次随机获得一个用户，分配一篇文章给它。
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(body=fake.text(),
                 timestamp=fake.past_date(),
                 author=u)
        db.session.add(p)
    db.session.commit()
