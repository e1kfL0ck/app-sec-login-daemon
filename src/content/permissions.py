"""
Authorization checks for content operations, e.g., view, edit, delete posts.
"""

from .repository import PostRepository


def can_view_post(user_id, post_id):
    """Check if user can view a post."""
    post = PostRepository.get_by_id(post_id)
    if not post:
        return False

    # Public posts can be viewed by anyone
    if post[4]:  # is_public
        return True

    # Private posts can only be viewed by author
    if user_id == post[1]:  # author_id
        return True

    # TODO: Check if user is admin
    return False


def can_edit_post(user_id, post_id):
    """Check if user can edit a post."""
    post = PostRepository.get_by_id(post_id)
    if not post:
        return False

    # Only author can edit
    return user_id == post[1]  # author_id


def can_delete_post(user_id, post_id):
    """Check if user can delete a post."""
    post = PostRepository.get_by_id(post_id)
    if not post:
        return False

    # Author can delete own post
    if user_id == post[1]:
        return True

    # TODO: Check if user is admin
    return False
