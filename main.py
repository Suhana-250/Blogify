import os
from datetime import date
from email.message import Message
from functools import wraps

from flask import Flask, abort, render_template, redirect, url_for, flash, request, session
from dotenv import load_dotenv
from flask_mail import Mail, Message
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash

from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm, ContactForm

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
ckeditor = CKEditor(app)
Bootstrap5(app)

gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ["EMAIL"]
app.config['MAIL_PASSWORD'] = os.environ["PASSWORD"]
app.config['MAIL_DEFAULT_SENDER'] = os.environ["EMAIL"]

mail = Mail(app)

class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///posts.db')
db = SQLAlchemy(model_class=Base)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, int(user_id))

def admin_only(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            flash("You are not authorized to access this page.", "error")
            return abort(403)
        return func(*args, **kwargs)
    return decorated_function

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))

    posts = relationship("BlogPost", back_populates="author")
    comment = relationship("Comment", back_populates="author")

class BlogPost(db.Model):
    __tablename__ = "blog_post"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    author = relationship("User", back_populates="posts")
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("user.id"))

    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

    comments = relationship("Comment", back_populates="parent_post")

class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("user.id"))
    author = relationship("User", back_populates="comment")

    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("blog_post.id"))
    parent_post = relationship("BlogPost", back_populates="comments")

    comment: Mapped[str] = mapped_column(Text)

with app.app_context():
    db.create_all()

@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost).order_by(BlogPost.date.desc()))
    posts = result.scalars().all()

    return render_template("index.html", all_posts=posts)

@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST":
        email = form.email.data
        password = generate_password_hash(password=form.password.data, method='pbkdf2:sha256', salt_length=8)
        name = form.name.data

        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please log in.")
            return redirect(url_for('login'))

        new_user = User(
            email = email,
            password = password,
            name = name
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('get_all_posts'))
    return render_template("register.html", form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if request.method == "POST":
        email = login_form.email.data
        password = login_form.password.data

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                flash("Logged in successfully")
                return redirect(url_for("get_all_posts"))
            else:
                flash("Incorrect Password. Try Again!", "error")
        else:
            flash("Email does not Exist. Try again.")
    return render_template("login.html", form = login_form)

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash("Hope To See You Soon! Adios amigo")
    return redirect(url_for('get_all_posts'))

@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    user = current_user
    comment_form = CommentForm()
    requested_post = db.get_or_404(BlogPost, post_id)
    if request.method == "POST" and comment_form.validate_on_submit():
        if current_user.is_authenticated:
            new_comment = Comment(
                comment=comment_form.comment.data,
                post_id=post_id,
                author=user
            )
            db.session.add(new_comment)
            db.session.commit()

            comment_form.comment.data = ""
        else:
            flash("Login to Comment on Posts!")
            return redirect(url_for('login'))
    return render_template("post.html", post=requested_post, form=comment_form)

@admin_only
@app.route("/new-post", methods=["GET", "POST"])
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)

@admin_only
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)

@admin_only
@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route("/about")
def about():
    if current_user.is_authenticated:
        return render_template("about.html")
    else:
        flash("You have to Login to view Content")
        return redirect(url_for('login'))

@app.route("/contact", methods=["GET", "POST"])
def contact():
    contact_form = ContactForm()
    if contact_form.validate_on_submit():
        name = contact_form.name.data
        c_email = contact_form.email.data
        phone = contact_form.phone.data
        message = contact_form.message.data

        msg = Message(
            subject=f"Blog Message! From {name}",
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=["cosmosjnr@icloud.com"],
            html=f"<strong>Name:</strong> {name}<br>"
                 f"<strong>Phone Number:</strong> {phone}<br>"
                 f"<strong>Email:</strong> {c_email}<br><br>"
                 f"<strong>Message:</strong><br>{message}"
        )

        try:
            mail.send(msg)
            return render_template("contact.html", form=contact_form, msg_sent=True)
        except Exception as e:
            flash(f'An error occurred while sending the email: {e}', 'danger')

    return render_template("contact.html", form=contact_form)

if __name__ == "__main__":
    app.run(debug=False)