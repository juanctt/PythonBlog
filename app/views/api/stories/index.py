# -*- coding: utf8 -*-

from flask import url_for, request, abort
from flask_login import current_user, login_required
from flask_classy import FlaskView, route
from app.helpers import render_json
from app.models import Post, Feed, Vote
from models import StoryView
from app import cache
from flask_socketio import emit


class StoriesApiView(FlaskView):
    route_base = '/api/stories'
    formatter = None

    @cache.cached(
        query_string=True,
        timeout=Feed.CACHE_FEED_EXPIRED_AT,
        forced_update=Feed.forced_update_posts
    )
    def index(self):
        data = request.values
        page = data.get('page', 1, int)
        limit = data.get('limit', 5, int)
        category_id = data.get('category', 0, int)

        posts, total = Feed.posts(category_id=category_id,
                                  page=page,
                                  limit=limit)

        stories = map(self.clean_story, posts)

        return render_json(stories=stories,
                           total=total,
                           page=page,
                           limit=limit)

    @route('/drafts', methods=['GET'])
    @login_required
    def drafts(self):
        data = request.values
        page = data.get('page', 1, int)
        limit = data.get('limit', 20, int)

        posts, total = Post.posts_by_user(current_user.id,
                                          limit=limit,
                                          page=page,
                                          status=Post.POST_DRAFT_2)

        return render_json(stories=posts,
                           total=total,
                           page=page,
                           limit=limit)

    def get(self, id):
        story = Post.get_by_id(int(id))

        if story is None or story.is_hidden:
            abort(404, 'API_ERROR_POST_NOT_FOUND')

        return render_json(story=story)

    @login_required
    def delete(self, id):
        story = Post.get_by_id(int(id))

        if story is None or story.is_hidden:
            abort(404, 'API_ERROR_POST_NOT_FOUND')

        if not story.can_edit():
            abort(404, 'API_ERROR_POST_NOT_FOUND')

        Post.delete(id)

        # clear related cache objects
        Feed.clear_cached_posts()

        return render_json(status=204)

    @route('/last-draft', methods=['GET'])
    @login_required
    def last_draft(self):
        draft = Post.last_draft(user_id=current_user.id)

        if draft is None:
            draft = Post.init(current_user, status=Post.POST_DRAFT_2)
            draft.save()

        return render_json(draft=draft)

    @route('/save-draft', methods=['POST'])
    @login_required
    def new_draft(self):
        # data = request.json
        # draft = Post.init(current_user, status=Post.POST_DRAFT_2)
        # self.update_story(draft, data, Post.POST_DRAFT_2)
        # draft.save()

        # return render_json(draft=draft)
        abort(404)

    @route('/save-draft/<int:id>', methods=['POST'])
    @login_required
    def save_draft(self, id):
        data = request.json
        story = Post.get_by_id(id)

        if story is None or story.is_hidden:
            abort(404, 'API_ERROR_POST_NOT_FOUND')

        if not story.can_edit:
            abort(403, 'API_ERROR_INVALID_ACCESS')

        self.update_story(story, data, Post.POST_DRAFT_2)

        story.save()

        # clear related cache objects
        Feed.clear_cached_posts()

        return render_json(story=story)

    @route('/<int:id>/hide', methods=['POST'])
    @login_required
    def hide_story(self, id):
        story = Post.get_by_id(id)

        if not current_user.is_admin:
            abort(404, 'API_ERROR_POST_NOT_FOUND')

        if story is None:
            abort(404, 'API_ERROR_POST_NOT_FOUND')

        if story.is_hidden:
            story.status = story.old_status
        else:
            # save current status and block the post
            story.old_status = story.status
            story.status = Post.POST_HIDDEN

        story.save()

        # clear related cache objects
        Feed.clear_cached_posts()

        return render_json(story=story)

    @route('/publish/<int:id>', methods=['POST'])
    @login_required
    def publish(self, id):
        data = request.json
        story = Post.get_by_id(id)

        if story is None or story.is_hidden:
            abort(404, 'API_ERROR_POST_NOT_FOUND')

        if not story.can_edit:
            abort(403, 'API_ERROR_INVALID_ACCESS')

        self.update_story(story, data, Post.POST_PUBLIC)

        if story.save_count <= 0:
            story.created_at = Post.current_date()
        story.save_count += 1
        story.save()

        # clear related cache objects
        Feed.clear_cached_posts()

        return render_json(story=story,
                           redirect_to=url_for('story.show', id=story.id))

    def update_story(self, story, data, status):
        story.title = data.get('title', u'')
        story.body = data.get('body', u'')
        story.extra_body = data.get('extra_body', u'')
        story.category_id = data.get('category_id', Post.CATEGORY_NONE)
        story.status = status
        story.kind = Post.KIND_STORY
        story.anonymous = data.get('anonymous', 0)

    def clean_story(self, story):
        return StoryView(story)
