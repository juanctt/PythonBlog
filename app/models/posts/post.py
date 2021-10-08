# -*- coding: utf8 -*-

from flask import url_for
from flask_login import current_user
from app import sa
from app.models import Base
from app.helpers import ModelHelper, MutableObject
import datetime
import base64


class Post(Base, sa.Model, ModelHelper):

    __tablename__ = 'posts'

    __json_meta__ = ['id',
                     'title',
                     'body',
                     'extra_body',
                     'user',
                     'status',
                     'lang',
                     'url',
                     'cover_picture',
                     'cover_picture_id',
                     'created_at',
                     'modified_at',
                     'category',
                     'anonymous',
                     'likes',
                     'is_hidden',
                     'is_editable',
                     'is_owner']

    POST_PUBLIC = 0x001
    POST_DRAFT = 0x100
    POST_DRAFT_2 = 0x101
    POST_HIDDEN = 0x800

    KIND_STAMP = 1
    KIND_STORY = 2

    CATEGORY_NONE = 1

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(255))
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id',
                                                  ondelete='CASCADE',
                                                  onupdate='NO ACTION'))
    category_id = sa.Column(sa.Integer, sa.ForeignKey('categories.id',
                                                      ondelete='CASCADE',
                                                      onupdate='NO ACTION'))
    status = sa.Column(sa.Integer, default=1, index=True, nullable=False)
    lang = sa.Column(sa.String(4), default='en', index=True, nullable=False)
    anonymous = sa.Column(sa.SmallInteger)
    score = sa.Column(sa.Numeric(20, 7),
                      default=0,
                      index=True,
                      nullable=False,
                      server_default='0')
    attr = sa.Column(MutableObject.get_column())
    created_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    modified_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    comments = sa.relationship('Comment', backref='post', lazy='dynamic')

    def __repr__(self):  # pragma: no cover
        return '<Post %r>' % (self.id)

    @property
    def body(self):
        return self.get_attribute('body')

    @body.setter
    def body(self, value):
        return self.set_attribute('body', value)

    @property
    def extra_body(self):
        return self.get_attribute('extra_body')

    @extra_body.setter
    def extra_body(self, value):
        return self.set_attribute('extra_body', value)

    @property
    def cover_picture(self):
        from app.models import Picture
        return Picture.get_by_id(self.cover_picture_id)

    @property
    def cover_picture_id(self):
        return self.get_attribute('cover_picture_id', 0)

    @cover_picture_id.setter
    def cover_picture_id(self, value):
        return self.set_attribute('cover_picture_id', value)

    @property
    def page_views(self):
        return self.get_attribute('page_views', 1)

    @page_views.setter
    def page_views(self, value):
        return self.set_attribute('page_views', value)

    @property
    def save_count(self):
        return self.get_attribute('save_count', 0)

    @save_count.setter
    def save_count(self, value):
        return self.set_attribute('save_count', value)

    @property
    def votes(self):
        return self.get_attribute('votes', 0)

    @votes.setter
    def votes(self, value):
        return self.set_attribute('votes', value)

    @property
    def down_votes(self):
        return self.get_attribute('down_votes', 0)

    @down_votes.setter
    def down_votes(self, value):
        return self.set_attribute('down_votes', value)

    @property
    def likes(self):
        return self.get_attribute('likes', 0)

    @likes.setter
    def likes(self, value):
        return self.set_attribute('likes', value)

    @property
    def editor_version(self):
        return self.get_attribute('editor_version', 0)

    @editor_version.setter
    def editor_version(self, value):
        return self.set_attribute('editor_version', value)

    @property
    def kind(self):
        return self.get_attribute('kind', self.KIND_STAMP)

    @kind.setter
    def kind(self, value):
        return self.set_attribute('kind', value)

    @property
    def old_status(self):
        return self.get_attribute('old_status', self.POST_DRAFT)

    @old_status.setter
    def old_status(self, value):
        return self.set_attribute('old_status', value)

    @property
    def url(self):
        if not hasattr(self, '_url'):
            self._url = url_for('story.show', id=self.id)
        return self._url

    @property
    def is_hidden(self):
        return self.status == self.POST_HIDDEN

    @property
    def is_draft(self):
        return self.status == self.POST_DRAFT or self.status == self.POST_DRAFT_2

    @property
    def is_stamp(self):
        return self.kind == self.KIND_STAMP

    @property
    def is_story(self):
        return self.kind == self.KIND_STORY

    @property
    def has_category(self):
        return self.category_id and self.category_id != self.CATEGORY_NONE

    @property
    def comment_list(self):
        if not hasattr(self, '_comment_list'):
            data = dict([(item.id, item) for item in self.comments])

            for comment in self.comments:
                comment.children = []
                if comment.comment_id and comment.comment_id in data:
                    data[comment.comment_id].children.append(comment)

            self._comment_list = [c for c in self.comments if not c.comment_id]

        return self._comment_list

    def is_mine(self):
        return (current_user.is_authenticated and
                self.user.id == current_user.id)



    def can_edit(self):
        return (current_user.is_authenticated and
                (self.user.id == current_user.id or current_user.is_admin))

    @property
    def is_owner(self):
        return (current_user.is_authenticated and
                self.user.id == current_user.id)

    @property
    def is_editable(self):
        return (current_user.is_authenticated and
                (self.user.id == current_user.id or current_user.is_admin))

    @property
    def need_reply(self):
        return current_user.is_authenticated and self.user_id != current_user.id

    def update_score(self, page_view=0, vote=0, down_vote=0):
        from app.models import Feed

        scale = 10

        if page_view > 0:
            self.page_views = self.page_views + page_view

        if vote > 0:
            self.votes = self.votes + vote

        if down_vote > 0:
            self.down_votes = self.down_votes + down_vote

        self.score = Feed.score(page_views=self.page_views,
                                ups=self.votes,
                                downs=self.down_votes,
                                date=self.created_at)

    @property
    def encoded_id(self):
        return base64.b64encode(bytes('%s' % self.id)).encode('hex')

    @classmethod
    def decode_id(cls, encodedValue):
        return long(base64.b64decode(encodedValue.decode('hex')))

    @classmethod
    def minimun_date(cls):
        return datetime.datetime(1, 1, 1, 0, 0, 0, 0)

    @classmethod
    def current_date(cls):
        return datetime.datetime.utcnow()

    @classmethod
    def get_status_list(cls):
        return [(cls.POST_DRAFT, "Private"), (cls.POST_PUBLIC, "Public")]

    @classmethod
    def get_language_list(cls):
        import config
        return config.LANGUAGES

    @classmethod
    def posts_by_user(cls,
                      user_id,
                      limit=10,
                      page=1,
                      status=POST_PUBLIC,
                      orderby='created_at',
                      desc=True):
        query = cls.query.filter_by(user_id=user_id, status=status)

        count = query.count()
        records = []
        if count:
            sort_by = '%s %s' % (orderby, 'DESC' if desc else 'ASC')
            records = query.order_by(sa.text(sort_by)) \
                .offset((page - 1) * limit) \
                .limit(limit)
        return records, count

    @classmethod
    def last_draft(cls, user_id):
        sort_by = 'created_at DESC'

        return cls.query.filter_by(user_id=user_id, status=cls.POST_DRAFT_2) \
            .order_by(sa.text(sort_by)) \
            .offset(0) \
            .limit(1) \
            .first()

    @classmethod
    def posts_by_categories(cls,
                            category_ids,
                            limit=10,
                            page=1,
                            status=POST_PUBLIC,
                            orderby='created_at',
                            desc=True):
        if not category_ids:
            return [], 0

        query = cls.query.filter(cls.category_id.in_(
            category_ids), cls.status == status)
        count = query.count()
        records = []
        if count:
            sort_by = '%s %s' % (orderby, 'DESC' if desc else 'ASC')
            records = query.order_by(sa.text(sort_by)) \
                .offset((page - 1) * limit) \
                .limit(limit)
        return records, count

    @classmethod
    def init(cls, user, status=POST_DRAFT):
        p = cls.create()
        p.user = current_user
        p.status = status

        # init the score
        p.update_score(page_view=1)
        p.editor_version = 1
        return p
