"""
Content routes - posts, comments, search, feed.
"""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    send_from_directory,
    abort,
)
from session_helpers import login_required

from . import services

content_bp = Blueprint(
    "content", __name__, url_prefix="/content", template_folder="templates"
)


@content_bp.route("/feed")
def feed():
    """Display public feed."""
    page = request.args.get("page", 1, type=int)
    posts = services.get_public_feed(page=page)

    return render_template("feed.html", posts=posts, page=page)


@content_bp.route("/posts")
@login_required
def user_posts():
    """Display current user's posts (both public and private)."""
    user_id = session.get("user_id")
    page = request.args.get("page", 1, type=int)
    posts = services.get_user_posts(user_id, page=page)

    return render_template("user_posts.html", posts=posts, page=page)


@content_bp.route("/post/<int:post_id>")
def view_post(post_id):
    """View a single post."""
    user_id = session.get("user_id")
    post = services.get_post_view(post_id, requesting_user_id=user_id)

    if not post:
        return render_template("404.html"), 404

    comments = services.get_by_post(post_id)
    attachments = services.get_attachments_for_post(post_id)
    return render_template(
        "post_detail.html", post=post, comments=comments, attachments=attachments
    )


@content_bp.route("/post/create", methods=["GET", "POST"])
@login_required
def create_post():
    """
    Handle GET and POST requests for creating a new post.

    GET: Renders the post creation form.

    POST: Processes form submission to create a new post.
        - Extracts title and body from form data
        - Determines is_public status from checkbox (checked = "on", unchecked = absent)
        - Accepts file attachments
        - Returns rendered form with errors if creation fails
        - Redirects to the new post view on success

    Returns:
        GET: Rendered post_create.html template
        POST: Rendered post_create.html with errors dict, or redirect to view_post
    """
    user_id = session.get("user_id")

    if request.method == "GET":
        return render_template("post_create.html")

    # POST
    title = request.form.get("title", "")
    body = request.form.get("body", "")
    # Treat missing checkbox as False so unchecked submissions remain private
    is_public = request.form.get("is_public") == "on"

    files = request.files.getlist("attachments")
    result = services.create_post(user_id, title, body, is_public, files=files)

    if not result.ok:
        return render_template("post_create.html", errors=result.errors)

    return redirect(url_for("content.view_post", post_id=result.post_id))


@content_bp.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    """Edit a post."""
    user_id = session.get("user_id")
    post = services.get_post_view(post_id, requesting_user_id=user_id)

    result = services.permissions.can_edit_post(user_id, post_id)
    if not post or not result:
        return render_template("404.html"), 404

    if request.method == "GET":
        attachments = services.get_attachments_for_post(post_id)
        return render_template("post_edit.html", post=post, attachments=attachments)

    # POST
    title = request.form.get("title", "")
    body = request.form.get("body", "")
    # Treat missing checkbox as False so unchecked submissions remain private
    is_public = request.form.get("is_public") == "on"

    files = request.files.getlist("attachments")
    result = services.edit_post(post_id, user_id, title, body, is_public, files=files)

    if not result.ok:
        attachments = services.get_attachments_for_post(post_id)
        return render_template(
            "post_edit.html", post=post, attachments=attachments, errors=result.errors
        )

    return redirect(url_for("content.view_post", post_id=post_id))


@content_bp.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    """Delete a post."""
    user_id = session.get("user_id")
    post = services.get_post_view(post_id, requesting_user_id=user_id)

    result = services.permissions.can_edit_post(user_id, post_id)
    if not post or not result:
        return render_template("404.html"), 404

    result = services.delete_post(post_id, user_id)

    if not result.ok:
        return redirect(url_for("content.view_post", post_id=post_id))

    return redirect(url_for("content.feed"))


@content_bp.route("/post/<int:post_id>/comment", methods=["POST"])
@login_required
def add_comment(post_id):
    """Add a comment to a post."""
    user_id = session.get("user_id")
    text = request.form.get("text", "").strip()

    if not text:
        return redirect(url_for("content.view_post", post_id=post_id))

    result = services.add_comment(post_id, user_id, text)

    if not result.ok:
        return redirect(url_for("content.view_post", post_id=post_id))

    return redirect(url_for("content.view_post", post_id=post_id))


@content_bp.route("/search")
def search():
    """Search posts."""
    query = request.args.get("q", "").strip()

    if not query:
        return render_template("search.html", posts=[], query=query, errors=[])

    posts, errors = services.search_posts(query)
    return render_template("search.html", posts=posts, query=query, errors=errors)


@content_bp.route("/attachment/<int:attachment_id>")
def download_attachment(attachment_id: int):
    """Serve an attachment file if viewer has permissions."""
    user_id = session.get("user_id")
    meta = services.get_attachment_file(attachment_id, requesting_user_id=user_id)
    if not meta:
        return abort(404)
    directory, stored_name, original_name, mime_type = meta
    # Use send_from_directory for safe serving; attachment filenames sanitized
    response = send_from_directory(
        directory,
        stored_name,
        mimetype=mime_type,
        as_attachment=True,
        download_name=original_name,
    )
    return response
