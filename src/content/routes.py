"""
Content routes - posts, comments, search, feed.
"""

from flask import render_template, request, redirect, url_for, session
from session_helpers import login_required

from . import services, content_bp

@content_bp.route("/feed")
def feed():
    """Display public feed."""
    page = request.args.get("page", 1, type=int)
    posts = services.get_public_feed(page=page)

    return render_template("content/feed.html", posts=posts, page=page)


@content_bp.route("/post/<int:post_id>")
def view_post(post_id):
    """View a single post."""
    user_id = session.get("user_id")
    post = services.get_post_view(post_id, requesting_user_id=user_id)

    if not post:
        return render_template("404.html"), 404

    comments = services.get_by_post(post_id)
    return render_template("content/post_detail.html", post=post, comments=comments)


@content_bp.route("/post/create", methods=["GET", "POST"])
@login_required
def create_post():
    """Create a new post."""
    user_id = session.get("user_id")

    if request.method == "GET":
        return render_template("content/post_create.html")

    # POST
    title = request.form.get("title", "")
    body = request.form.get("body", "")
    is_public = request.form.get("is_public", "on") == "on"

    result = services.create_post(user_id, title, body, is_public)

    if not result.ok:
        return render_template("content/post_create.html", errors=result.errors)

    return redirect(url_for("content.view_post", post_id=result.post_id))


@content_bp.route("/search")
def search():
    """Search posts."""
    query = request.args.get("q", "").strip()

    if len(query) < 2:
        return render_template("content/search.html", posts=[], query=query)

    posts = services.search_posts(query)
    return render_template("content/search.html", posts=posts, query=query)
