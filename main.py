from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogger@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'whatever#'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(70))
    body = db.Column(db.String(140))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
        

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25))
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/')
def index():
    return redirect('/blog')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    #if user is not logged in redirect to login page

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        blog_entry= Blog(title, body, owner)
        db.session.add(blog_entry)
        db.session.commit()
        

    return render_template('new_post.html') 
    

    
@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.method == 'POST':
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
            return render_template('blog_entry.html', blog = blog_entry)

    else:
        something_blog_id = request.args.get('id')
        if something_blog_id:
            single_blog = Blog.query.filter_by(id = something_blog_id).first()
            return render_template('blog_entry.html', blog = single_blog)
        else:
            blogs = Blog.query.all()
            return render_template('main_blog.html', blogs = blogs)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    #if request.method == 'POST':

    render_template('signup.html')

"""
@app.route('/login', methods=['GET', 'POST'])
def login():


@app.route('/logout', methods=['POST'])
def logout():
    #delete user from session
    redirect return ('/blog')
"""
    



if __name__=='__main__':
    app.run()