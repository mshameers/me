from flask import Blueprint, jsonify, request


from app import db
from app.api import InvalidUsage, LinkHeaderBuilder, parse_json, parse_arg, \
    parse_pagination_args, sql_ordering, handle_invalid_usage
from app.api.auth import require_authorization
from app.api.comment_validators import validate_name
from app.models import Post, Comment


bp = Blueprint('comments', __name__, url_prefix='/api')

# @bp.route('/comment/<int:id>', methods=['GET', 'POST', 'PATCH', 'DELETE'])
# # @require_authorization
# def comments(id):
#     post = Post.query.get(id)

#     if request.method == 'POST':
    #     if post:
    #         return replace_post(post)
    #     else:
    #         return create_post()

    # if not post:
    #     message = 'No post with id %s.' % id
    #     raise InvalidUsage(message, 404)

    # if request.method == 'GET':
    #     return retrieve_post(post)
    # if request.method == 'PATCH':
    #     return update_post(post)
    # if request.method == 'DELETE':
    #     return delete_post(post)

@bp.route('/comments', methods=['GET', 'POST'])
# @require_authorization
def comments():
    
    if request.method == 'POST':
        return create_comment()
    # else:
    #     return list_posts()


def create_comment():
    name = parse_json(request.json, str, 'name')
    content = parse_json(request.json, str, 'content')
    post_id = parse_json(request.json, str, 'post_id')

    validate_name(name)

    comment = Comment(name, content, '192.167.1.1', post_id)
    db.session.add(comment)
    db.session.commit()

    response = jsonify(comment.to_json(), message='Created Comment.')
    response.status_code = 201
    response.headers['Location'] = request.base_url + '/' + str(comment.id)
    print dir(response), response.mimetype
    return response