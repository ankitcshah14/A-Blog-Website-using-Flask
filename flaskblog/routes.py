from flask import render_template, flash, redirect, url_for, request, abort
from flaskblog.models import User, Post
from flaskblog.forms import (RegistrationForm, LoginForm, UpdateAccountForm, PostForm,
                             RequestResponseForm, ResetPasswordForm)
from flaskblog import app, db, bcrypt, mail, limiter
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from datetime import datetime, timedelta


# Multiple routes
@app.route("/")
@app.route("/home")
@limiter.limit("10000 per day")
def home():
    # Only 5 posts per page
    # default page id is set to 1
    # All the posts are sorted in descending order i.e. latest post first
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.datePosted.desc()).paginate(page=page, per_page=5)

    # Whatever variable name we pass as an argument we will have access to that variable in the template
    # And it will be equal to the 'posts' data
    return render_template('home.html', posts=posts)


@app.route("/about")
@limiter.limit("10000 per day")
def about():
    return render_template('about.html', title='About')


# Adding a list a methods allowed - GET, POST else we get an Error: Method not allowed
@app.route("/register", methods=['GET', 'POST'])
@limiter.limit("10000 per day")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        # The hashing algo used is bcrypt which gives a hash which is 60 chars long.
        # Bcrypt also gives a hash which is different everytime we hash the same password.
        # So even if a hacker gets the hash and compares it with a hashtable he won't be
        # able to get the correct password.
        hashedPassword = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # To convert to string
        # creating User table row
        user = User(username=form.username.data, email=form.email.data, password=hashedPassword)
        # Adding to the db
        db.session.add(user)
        # You can add 'n' number of rows and commit only once. If we do not commit the changes will
        # not be saved.
        db.session.commit()

        # 'f' is for formatted string
        # Flash displays a message and also allows for a bootstrap class to be passed, here it is success
        flash(f"Account created for {form.username.data}!", 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
@limiter.limit("10000 per day")
def login():
    # Once we successfully login the user shouldnt go back to the login page on pressing back.
    # Hence we use this method:
    if (current_user.is_authenticated):
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        # Logic behind the following code is:
        # If the user enters invalid credentials more than 5 times than his account is locked
        # for 30 mins
        # If during the locked period the user tries to login he will be redirected to the same
        # page
        # If user has been previously locked but his timer has expired than number of failed
        # attempts is set back to zero

        noOfFailedAttempts = user.noOfFailedAttempts
        time = datetime.now()
        # If previously been locked and timer has expired set noOfFailedAttempts to 0
        if user.lockedTill != None and time > user.lockedTill:
            user.noOfFailedAttempts = 0
            db.session.commit()
            # Refreshing the database as the user object has already been queried from the database
            # But now as its value has changed realtime it requires this new value to be used in
            # the below code
            db.session.refresh(user)

        # If timer has not yet expired revert the user back to the same page
        if user.lockedTill is not None and time < user.lockedTill:
            flash(f"Account is locked", "danger")
            return redirect(url_for('login'))

        # If correct password is entered login the user
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            user.noOfFailedAttempts = 0
            db.session.commit()
            return redirect(url_for('home'))
        else:
            # No of failed attempts > 5 than lock account for 30 mins
            if noOfFailedAttempts > 5:
                flash(f"Account locked for 30 mins. Cannot log in", "danger")
                currentTime = datetime.now()
                lockedTill = currentTime + timedelta(seconds=1800)
                user.lockedTill = lockedTill
                db.session.commit()
            # Incrementing the noOfFailed by 1 and adding it to the database
            else:
                noOfFailedAttempts += 1
                flash(f"Incorrect credentials: Total {6 - noOfFailedAttempts} login attempts allowed", "danger")
                user.noOfFailedAttempts = noOfFailedAttempts
                db.session.commit()

    return render_template('login.html', title='Login', form=form)


# To logout the user from the session
@app.route("/logout")
@limiter.limit("10000 per day")
def logout():
    logout_user()
    return redirect(url_for('home'))


# Account page can be accessed only once the user has logged in
@app.route("/account", methods=['GET', 'POST'])
@limiter.limit("10000 per day")
# The following decorator enforces the user to login, but it needs to know where the login route is
# hence we define it in the __init__.py
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        # Read about current_user in flask_login
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        # This redirect will tell teh browser to run a GET method unlike if we let it fall down to
        # the render_template() which will run a POST request. This POST request will cause the
        # browser to pop-up the msg 'Do you want to resubmit the form values' which we do not want.
        return redirect(url_for('account'))

    elif request.method == 'GET':
        # Populating the form fields with current_user data
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template('account.html', title='Account', form=form)


@app.route("/createPost", methods=['GET', 'POST'])
@limiter.limit("10000 per day")
@login_required
def createPost():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('createPosts.html', title='Create Posts', form=form, legend='Create Posts')


@app.route("/post/<int:postId>")
@limiter.limit("10000 per day")
def post(postId):
    post = Post.query.get_or_404(postId)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:postId>/update", methods=['GET', 'POST'])
@limiter.limit("10000 per day")
def updatePost(postId):
    post = Post.query.get_or_404(postId)

    # Only if current user is author of post let the user update the post
    if post.author != current_user:
        abort(403)

    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', postId=post.id))

    elif request.method == 'GET':
        # Populating the fields with data
        form.title.data = post.title
        form.content.data = post.content

    # We can dynamically display stuff from the routes.py by passing it as a variable and putting
    # that variable in {{ <variable> }}
    return render_template('createPosts.html', title='Update Posts', form=form, legend='Update Posts')


@app.route("/post/<int:postId>/delete", methods=['POST'])
@limiter.limit("10000 per day")
def deletePost(postId):
    post = Post.query.get_or_404(postId)

    # Only if current user is author of post let the user delete the post
    if post.author != current_user:
        abort(403)

    db.session.delete(post)
    db.session.commit()

    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/user/<string:username>")
@limiter.limit("10000 per day")
def userPosts(username):
    # Only 5 posts per page
    # default page id is set to 1
    # All the posts are sorted in descending order i.e. latest post first
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user) \
        .order_by(Post.datePosted.desc()) \
        .paginate(page=page, per_page=5)

    # Whatever variable name we pass as an argument we will have access to that variable in the template
    # And it will be equal to the 'posts' data
    return render_template('userPosts.html', posts=posts, user=user)


# Send an email
def sendResetEmail(user):
    token = user.getResetToken()
    msg = Message('Password Reset Request', sender='noreply@blog.com', recipients=[user.email])

    # We use _external for an absolute url rather than a relative url
    msg.body = f'''To reset the password visit the following link:
{url_for('resetPassword', token=token, _external=True)}

If you did not make this request then simply ignore this email.
'''
    # Sending the mail
    mail.send(msg)


# Just a request to reset the password
@app.route("/resetRequest", methods=['GET', 'POST'])
@limiter.limit("10000 per day")
def resetRequest():
    # If already logged in redirect to homepage
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResponseForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        sendResetEmail(user)
        flash('An email has been sent with instructions to reset password!')
        return redirect(url_for('login'))
    return render_template('resetRequest.html', title='Reset Password', form=form)


# Request to reset the password with the token active
@app.route("/resetPassword/<token>", methods=['GET', 'POST'])
@limiter.limit("10000 per day")
def resetPassword(token):
    # If already logged in redirect to homepage
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    user = User.verifyResetToken(token)
    if user is None:
        flash('That is an invalid or an expired toekn', 'warning')
        return redirect(url_for('resetRequest'))
    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashedPassword = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # To convert to string
        user.password = hashedPassword
        db.session.commit()

        flash(f"Your Password has been updated!", 'success')
        return redirect(url_for('login'))
    return render_template('resetToken.html', title='Reset Password', form=form)
