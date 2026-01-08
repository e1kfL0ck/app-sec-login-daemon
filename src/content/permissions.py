"""
Authorization checks for content operations, e.g., view, edit, delete posts.
"""

from .repository import PostRepository


def can_view_post(user_id, post_id):
    """
    Check if a user has permission to view a specific post.

    Args:
        user_id: The ID of the user attempting to view the post.
        post_id: The ID of the post to be viewed.

    Returns:
        bool: True if the user can view the post, False otherwise.

    Behavior:
        - Returns False if the post does not exist.
        - Public posts (post[4] == True) can be viewed by any user.
        - Private posts can only be viewed by their author (user_id == post[1]).
        - Admin users should be able to view any post (see TODO).

    Note:
        - Post data structure: post[1] is author_id, post[4] is is_public flag.
        - Admin permission check is not yet implemented.
    """
    post = PostRepository.get_by_id(post_id)
    if not post:
        return False

    # Public posts can be viewed by anyone
    if post["is_public"]:  # is_public
        return True

    # Private posts can only be viewed by author
    if user_id == post["author_id"]:  # author_id
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
