from flask.ext.bcrypt import generate_password_hash, check_password_hash

from app import db
from datetime import datetime
from app.utils import slugify


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(60))

    def __init__(self, name, password):
        self.name = name
        self.change_password(password)

    def __repr__(self):
        return u'<User(%s, %s)>' % (self.id, self.name)

    def compare_password(self, password):
        """Compare password against stored password hash."""
        return check_password_hash(self.password_hash, password)

    def change_password(self, password):
        """Change current password to a new password."""
        self.password_hash = generate_password_hash(password, 6)

tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))

    def __init__(self, name):
        self.name = name

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<Tag %r>' % self.name

class Post(db.Model):
    PER_PAGE_POST = 5
    PER_PAGE_STATUS = 5

    id = db.Column(db.Integer, primary_key=True)
    published = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    title = db.Column(db.String, nullable=True)
    body = db.Column(db.String, nullable=False)
    slug = db.Column(db.String, nullable=True, unique=True)
    tags = db.relationship('Tag', secondary=tags,
        backref=db.backref('posts', lazy='dynamic'))

    comments = db.relationship(
        "Comment",
        order_by="Comment.posted",
        passive_updates=False,
        cascade="all,delete-orphan",
        backref="post",
    )
    isStatus = db.Column(db.Boolean)

    def __init__(self, body, tags, title='', isStatus=True, visible=False):
        self.published = datetime.utcnow()
        self.title = title
        self.body = body
        self.tags = tags
        if self.title:
            self.slug = slugify(self.published, title)
        else:
            self.slug = slugify(self.published, body[:15])
        self.isStatus = isStatus
        self.visible = visible

    def __repr__(self):
        return u'<Post(%s,%s,Tags %r)>' % (self.id, self.slug, self.tags)

    def to_json(self):
        return {
            'id': self.id,
            'published': self.published.isoformat(),
            'title': self.title,
            'markup': self.body,
            'slug': self.slug,
            'tags': self.tags,
            'comments_url': '/api/posts/%s/comments' % self.id,
            'visible': self.visible,
        }


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    posted = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(510), nullable=False)
    ip = db.Column(db.String(45), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    reply_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    replies = db.relationship(
        'Comment',
        passive_updates=False,
        cascade='all,delete-orphan',
    )

    def __init__(self, name, body, ip, post_id, reply_id=None):
        self.name = name
        self.body = body
        self.ip = ip
        self.post_id = post_id
        self.reply_id = reply_id

    def __repr__(self):
        return u'<Comment(%s,%s,%s)>' % (self.id, self.name, self.body)

    @property
    def is_root(self):
        """Validate if this is not a reply to another comment."""
        return self.reply_id is None

    @property
    def has_replies(self):
        """Validate if this comment has any comment replies."""
        return len(self.replies) > 0

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'body': self.body,
            'ip': self.ip,
            'post_id': self.post_id,
            'reply_id': self.reply_id,
        }