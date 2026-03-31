from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)
app.secret_key = "secret123"

# DATABASE
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="_@Anushree09",
    database="narrateit"
)
cursor = db.cursor()

analyzer = SentimentIntensityAnalyzer()

# ---------------- LOGIN PAGE ----------------
@app.route('/')
def login_page():
    return render_template("login.html")

# ---------------- REGISTER PAGE ----------------
@app.route('/register')
def register_page():
    return render_template("register.html")

# ---------------- REGISTER ----------------
@app.route('/register_user', methods=['POST'])
def register_user():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        return "Passwords do not match"

    cursor.execute(
        "INSERT INTO signup (name,email,password) VALUES (%s,%s,%s)",
        (name, email, password)
    )
    db.commit()

    return redirect(url_for('login_page'))

# ---------------- LOGIN ----------------
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    cursor.execute(
        "SELECT * FROM signup WHERE email=%s AND password=%s",
        (email, password)
    )
    user = cursor.fetchone()

    if user:
        session['user_id'] = user[0]
        session['user_name'] = user[1]
        return redirect(url_for('images'))
    else:
        return "Invalid credentials"

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# ---------------- IMAGE PAGE ----------------
@app.route('/images')
def images():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    images = ['img1.jpg', 'img2.jpg', 'img3.jpg', 'img4.jpg', 'img5.jpg', 'img6.jpg', 'img7.jpg', 'img8.jpg', 'img9.jpg', 'img10.jpg',]

    return render_template(
        "image.html",
        images=images,
        username=session['user_name']
    )


# ---------------- SUBMIT STORY ----------------
@app.route('/submit_story', methods=['POST'])
def submit_story():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    story = request.form['story_text']
    image = request.form['image_filename']

    score = analyzer.polarity_scores(story)

    if score['compound'] > 0:
        sentiment = "Positive"
    elif score['compound'] < 0:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    cursor.execute(
        """INSERT INTO story (user_id, story_text, sentiment, image_filename)
           VALUES (%s,%s,%s,%s)""",
        (session['user_id'], story, sentiment, image)
    )
    db.commit()

    return render_template(
        "result.html",
        story=story,
        sentiment=sentiment,
        positive=score['pos'],
        negative=score['neg'],
        neutral=score['neu'],
        image_filename=image
    )

# ---------------- PROFILE PAGE ----------------
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    cursor.execute(
        "SELECT story_id, image_filename FROM story WHERE user_id=%s",
        (session['user_id'],)
    )
    data = cursor.fetchall()

    stories = [{"id": row[0], "image": row[1]} for row in data]

    return render_template(
        "profile.html",
        username=session['user_name'],
        stories=stories,
        total=len(stories)
    )

# ---------------- STORY PAGE ----------------
@app.route('/story/<int:story_id>')
def view_story(story_id):
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    cursor.execute(
        """SELECT story_text, sentiment, image_filename
           FROM story WHERE story_id=%s AND user_id=%s""",
        (story_id, session['user_id'])
    )
    story = cursor.fetchone()

    return render_template(
        "storyOpen.html",
        text=story[0],
        sentiment=story[1],
        image=story[2]
    )

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)