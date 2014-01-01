from flask import redirect, url_for, session, flash, render_template, request

from app import app, db
from app.models import Post, Tag, User, Comment
from app.forms import PostForm, LoginForm
from app.utils import cached, login_required, getPostnStatus


@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/')
#@cached(120)  # from 200 req/s to 800 req/s
def index():
    allposts = Post.query.all()#order_by('created DESC')
    posts, status = getPostnStatus(allposts)
    # status = Post.query.filter_by(isStatus=True).order_by('created DESC').limit(app.config['STATUS_COUNT'])
    # Ordering by created time DESC isstead of reversing
    return render_template('index.html', posts=posts, status=status)


@app.route('/p/page/<int:page>')
def allPosts(page=1):
    """Show all blog posts in a paginated list.

    Number of posts visible per page has been hardcoded.
    Note that its the pagination object
    that is being sent in to the template and not the actual posts.

    """
    pagination = Post.query.filter_by(isStatus=False) \
                           .order_by(Post.published.desc()) \
                           .paginate(page, Post.PER_PAGE_POST, False)
    return render_template('allposts.html', pagination=pagination)

@app.route('/s/page/<int:page>')
def allStatus(page=1):
    """Show all status posts in a paginated list.

    Number of posts visible per page has been hardcoded. 
    Note that its the pagination object
    that is being sent in to the template and not the actual posts.

    """
    pagination = Post.query.filter_by(isStatus=True) \
                           .order_by(Post.published.desc()) \
                           .paginate(page, Post.PER_PAGE_POST, False)
    return render_template('allstatus.html', pagination=pagination)



@app.route('/<path:slug>', methods=['GET'])
def detail(slug):
    """Show post details with specified slug.

    If the specified slug could not be found a HTTP 404 response will be
    generated. Note that this will only show details of the post if its
    marked to be visible.

    """
    from app.forms import CommentForm

    post = Post.query.filter_by(isStatus=False, slug=slug) \
                     .first_or_404()
    return render_template('detail.html', post=post, commentForm=CommentForm)

@app.route('/t/<name>/')
#@cached(120)
def showTag(name):
    tag = Tag.query.filter_by(name=name).first()
    taggedposts = getattr(tag, 'posts', [])
    posts, status = getPostnStatus(taggedposts)
    return render_template('index.html', posts=posts, status=status)

@app.route('/post/', methods=['GET', 'POST'])
@login_required
def newPost():
    form = PostForm(formdata=request.form or None)
    taglist = []
    if request.method == 'POST':
        print form.validate()
        print form.errors
        if request.form and form.validate():
            tags = form.tags
            print tags, '$'*29
            for tag in tags.data.split('-'):
                tagPresent = Tag.query.filter_by(name=tag).first()
                if tagPresent:
                    taglist.append(tagPresent)
                else:
                    taglist.append(Tag(name=tag))
        else:
            flash('There was an error with your input: %s' % form.errors)
            return redirect(url_for('newPost'))
        if form.title.data:
            p = Post(title=form.title.data, body=form.body.data, tags=taglist, isStatus=False)
            redirectUrl = url_for('detail', slug=p.slug)
        else:
            p = Post(body=form.body.data, tags=taglist, isStatus=True)
            redirectUrl = url_for('allStatus', page=1)
        db.session.add(p)
        db.session.commit()
        return redirect(redirectUrl)
    else:
        tags = Tag.query.all()
        return render_template('newPost.html', form=form, tag=tags)

@app.route('/del/p/<id>/')
@login_required
def deletePost(id):
    post = Post.query.filter_by(id=id).first()
    if post:
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted.")
    else:
        flash("Couldn't delete the post.")
    return redirect(url_for('index'))

@app.route('/del/c/<id>/')
@login_required
def deleteComment(id):
    comment = Comment.query.filter_by(id=id).first()
    post = Post.query.filter_by(id=comment.post_id).first()
    if comment:
        db.session.delete(comment)
        db.session.commit()
        flash("Comment deleted.")
    else:
        flash("Couldn't delete the comment.")
    return redirect(url_for('detail', slug=post.slug))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logged = session.get('logged_in', None)
        if not logged:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login/', methods=['GET', 'POST'])
def login():
    error = None
    users = User.query.all()
    form = LoginForm(formdata=request.form or None)
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(name=username).first()
        if user:
            password = request.form['password']
            if user.compare_password(password):
                session['logged_in'] = True
                flash('You are logged in.')
                return redirect(url_for('index'))
        else:
            error = 'Invalid'
        flash(error)
    return render_template('login.html', form=form, error=error, users=users)


@app.route('/logout/')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('index'))



# @app.route('/archive')
# def archive():
#     """Show all blog posts in an foreseeable view.


#     """
#     posts = Post.query.filter_by() \
#                       .order_by(Post.published.desc())
#     return render_template('archive.html', posts=posts)



# @app.route('/admin')
# def admin():
#     """Show admin page.

#     The usage of the admin page requires valid authorization.
#     Javascript must be enabled but no cookies are required.

#     Warning!
#     The authorization is over HTTP Basic and should only be used with SSL.

#     """
#     return render_template('admin.html')



# @app.route('/users/', methods=['GET', 'POST'])
# @login_required
# def users():
#     form = LoginForm(formdata=request.form or None)
#     if request.method == 'POST':
#         print request
#     users = User.query.all()
#     return render_template('admin.html', form=form, users=users)