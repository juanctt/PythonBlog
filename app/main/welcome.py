# -*- coding: utf8 -*-

from flask import render_template, redirect, url_for, request
from app import app
from app.models import Feed
from app.utils.response import resp


@app.route('/', defaults={'page': 1})
@app.route('/page/<int:page>')
def index(page=1):
    limit = 20
    posts, total = Feed.posts(page=page, limit=limit)
    if not posts and page > 1:
        return redirect(url_for('index'))
    return resp("main/stamps/index.html",
                posts=posts,
                page=page,
                limit=limit,
                total=total)


@app.route('/ranking')
def ranking():
    page = 1
    limit = 5
    posts, total = Feed.ranking(page=page, limit=limit)
    if not posts and page > 1:
        return redirect(url_for('index'))
    return resp("main/stamps/ranking.html",
                posts=posts,
                page=page,
                limit=limit,
                total=total)
