from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogger@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '#whatever#'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='owner', lazy='dynamic')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(70))
    body = db.Column(db.String(140))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


@app.before_request
def require_login():
    print(session)
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/')
def index():
    owners = User.query.all()
    return render_template('index.html', owners=owners, blog=blog)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    owner = User.query.filter_by(username = session['username']).first()
    #if user is not logged in redirect to login page
    if owner:
        if request.method == 'POST':
            title = request.form['title']
            body = request.form['body']
            blog_entry= Blog(title, body, owner)
            db.session.add(blog_entry)
            db.session.commit()
        return render_template('new_post.html') 
    else:
        return redirect('/login')
    

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.method == 'POST':
        owner = User.query.filter_by(username=session['username']).first()
        title = request.form['title']
        body = request.form['body']
        title_error = ""
        body_error = ""  
            
        if body == "":
            body_error = "Please enter something"            
        if title == "":
            title_error = "Please enter something"
        if title_error or body_error:
            return render_template('new_post.html', body_error=body_error,
                                                    title_error = title_error, title=title,
                                                    body = body)
        else:
            blog_entry= Blog(title, body, owner)
            db.session.add(blog_entry)
            db.session.commit()
            return render_template('blog_entry.html', blog = blog_entry, owner=owner)

    else:
        something_blog_id = request.args.get('id')
        user_id= request.args.get('user')
        print(user_id)
        owner_id = request.args.get('blog_owner_id')
        print(owner_id)
        
        if something_blog_id:
            single_blog = Blog.query.filter_by(id = something_blog_id).first()
            return render_template('blog_entry.html', blog = single_blog)
        
        if user_id:
            user_id= request.args.get('user')
            user = User.query.get(user_id)
            blogs = Blog.query.filter_by(owner=user).all()
            return render_template('singleUser.html', blogs=blogs)

        blogs = Blog.query.all()
        owner = User.query.all()
        
        return render_template('main_blog.html', blogs = blogs, owner=owner)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        #VALIDATE DATA, username and password must be >3 characters

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            if not verify == password:
                flash('passwords do not match', 'error')
            elif len(username) >= 3 and len(password) >= 3:
                new_user = User(username,password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                flash('Username and password must have at least 3 characters', 'error')     
        else:
            flash('This username already exists', 'error')
                
        return redirect('/signup')
    else:
        return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])  
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if username and not password == "":
            if user and user.password == password:
                session['username'] = username
                flash("logged in")
                return redirect('/newpost') 
            elif user and not user.password == password:
                flash('invalid password', 'error')
            else:
                flash('username does not exist', 'error')
        else:
            flash('Please enter a valid username and password', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


if __name__=='__main__':
    app.run()