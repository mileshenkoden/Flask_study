import math
import time
import os
from flask import Flask, g, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)
db = SQLAlchemy(app)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), nullable=False)
    intro = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    psw = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.name}>'

@app.route('/')
@app.route('/home')
def index():
    return render_template("index.html")

@app.route('/buyer')
def buyer():
    return render_template("buyer.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["psw"]
        password2 = request.form["psw2"]

        if len(name) > 4 and len(email) > 4 and len(password) > 4 and password == password2:
            new_user = Users(name=name, email=email, psw=generate_password_hash(password))
            try:
                db.session.add(new_user)
                db.session.commit()
                flash("Ви успішно зареєструвалися", "success")
                return redirect(url_for("login"))
            except Exception as e:
                db.session.rollback()  # Відкат у разі помилки
                flash("Помилка при додаванні в БД: " + str(e), "error")
        else:
            flash("Невірно заповнене поле", "error")
    return render_template("register.html", title="Реєстрація")



@app.route('/posts')
def posts():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template("posts.html", articles=articles)

@app.route('/posts/<int:id>')
def post_detail(id):
    article = Article.query.get(id)
    if article:
        return render_template("post_detail.html", article=article)
    return "Статтю не знайдено", 404

@app.route('/posts/<int:id>/del')
def post_delete(id):
    article = Article.query.get_or_404(id)

    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/posts')
    except Exception as e:
        return f"При видаленні статті виникла помилка: {e}"

@app.route("/posts/<int:id>/update", methods=['POST', 'GET'])
def post_update(id):
    article = Article.query.get_or_404(id)

    if request.method == "POST":
        article.title = request.form['title']
        article.intro = request.form['intro']
        article.text = request.form['text']

        try:
            db.session.commit()
            return redirect(f'/posts/{id}')
        except Exception as e:
            return f"При оновленні статті виникла помилка: {e}"
    else:
        return render_template("post_update.html", article=article)

@app.route("/create-article", methods=['POST', 'GET'])
def create_article():
    if request.method == "POST":
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        article = Article(title=title, intro=intro, text=text)

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f"При додаванні статті виникла помилка: {e}"
    else:
        return render_template("create-article.html")

if __name__ == "__main__":
    app.run(debug=True)
