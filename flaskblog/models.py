# **********Learn about circular imports or watch the 5th video of Corey Schafer**********
from datetime import datetime
from flaskblog import db, loginManager, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

'''The login manager allows for easy session management
	The login manager requires you to load the user to manage the session hence we need to implement
	the following method:'''


@loginManager.user_loader
def loadUser(userId):
    return User.query.get(int(userId))


'''The login manager requires our model to have the following 4 methods:
	isAuthenticated(): if they have provided valid credentials
	isActive(), isAnonymous() and user loader
	The first 3 are such common methods that there is an extension which provides it to us 'UserMixin'
'''


# Creating the tables in the Database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    # We will hash the image files into 20 character long strings hence using db.String()
    imageFile = db.Column(db.String(20), nullable=False, default='default.jpg')

    password = db.Column(db.String(60), nullable=False)

    # So if the username is correct but password is wrong for more than 5 attempts then lock the
    # account for 30 mins. But if there is a DOS then block that IP for 30 mins.
    noOfFailedAttempts = db.Column(db.Integer, default=0)
    lockedTill = db.Column(db.DateTime)
    # As the author of the posts will be the user thus there is a possibility that a user has many
    # posts. Thus this is a one-to-many relationship. Thus we create a 'relationship' with the Posts
    # table. This relationship is not a column and hence in the database structure it will not be
    # shown. But it when needed it will get all the data in one go(lazy)
    posts = db.relationship('Post', backref='author')  # lazy = 'True')

    '''
	Creating a secure token so only those who have access to the users email can reset their password
	'''

    def getResetToken(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        # Creates token
        return s.dumps({'userId': self.id}).decode('utf-8')

    # For static methods put:
    @staticmethod
    def verifyResetToken(token):
        s = Serializer(app.config['SECRET_KEY'])
        # Putting it in a try except block as token could be invalid or have expired
        # If we get the user ID return the user ID else return None
        try:
            userId = s.loads(token)['userId']
        except:
            return None

        return User.query.get(userId)

    # This method defines what the object is going to look like when we print it out
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.imageFile}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000), nullable=False)
    # Default date will be the date and time when the post is created
    # We do not pass the utcnow() function as we want to pass the date when it was created
    # and not when it was added to the Database
    datePosted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    # Foreign Key- user which authored the posts
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.datePosted}')"
