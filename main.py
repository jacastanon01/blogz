from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'whatever#'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(70))
    body = db.Column(db.String(140))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog', methods=['POST', 'GET'])
def blog():

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        blog_entry= Blog(title, body)
        db.session.add(blog_entry)
        db.session.commit()
        

    return render_template('new_post.html') 
    

    
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
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
            blog_entry= Blog(title, body)
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
    



if __name__=='__main__':
    app.run()