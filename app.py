from flask import Flask, render_template, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField
from wtforms.validators import InputRequired, Email, Length, EqualTo
import email_validator
from wtforms import SelectField

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'bitcollege'
app.config['MYSQL_DB'] = 'dbms4'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


mysql = MySQL(app)
bcrypt = Bcrypt(app)


class SignupForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=50)])
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[InputRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
                         validators=[InputRequired()])
    submit = SubmitField('Sign Up')


@app.route('/')
def index():
    return render_template('index.html')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=20)])
    submit = SubmitField('Login')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        date_of_birth = form.date_of_birth.data
        gender = form.gender.data
        cursor = mysql.connection.cursor()
        cursor.execute(
            'INSERT INTO Users (Username, Email, PasswordHash, DateOfBirth, Gender) VALUES (%s, %s, %s, %s, %s)',
            (username, email, password, date_of_birth, gender))
        mysql.connection.commit()
        cursor.close()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM Users WHERE Email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()
        if user and bcrypt.check_password_hash(user['PasswordHash'], password):
            session['user_id'] = user['UserID']
            flash('Login successful!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Invalid credentials', 'error')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


@app.route('/profile')
def profile():
    if 'user_id' in session:
        user_id = session['user_id']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM Users WHERE UserID = %s', (user_id,))
        user = cursor.fetchone()
        cursor.close()
        return render_template('profile.html', user=user)
    else:
        flash('Please login to view your profile', 'error')
        return redirect(url_for('login'))


@app.route('/artists')
def artists():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM Artists')
    artists = cursor.fetchall()
    cursor.close()
    return render_template('artists.html', artists=artists)


@app.route('/playlist')
def playlists():
    if 'user_id' in session:
        user_id = session['user_id']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM Playlists WHERE UserID = %s', (user_id,))
        playlists = cursor.fetchall()
        cursor.close()
        return render_template('playlist.html', playlists=playlists)
    else:
        flash('Please login to view your playlists', 'error')
        return redirect(url_for('login'))


@app.route('/albums')
def albums():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM Albums')
    albums = cursor.fetchall()
    cursor.close()
    return render_template('albums.html', albums=albums)


@app.route('/playlist_tracks/<int:playlist_id>')
def playlist_tracks(playlist_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT Tracks.* FROM Tracks '
                   'JOIN PlaylistTracks ON Tracks.TrackID = PlaylistTracks.TrackID '
                   'WHERE PlaylistTracks.PlaylistID = %s', (playlist_id,))
    tracks = cursor.fetchall()
    cursor.close()
    return render_template('playlist_tracks.html', tracks=tracks)


@app.route('/play/<int:track_id>')
def play(track_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM Tracks WHERE TrackID = %s', (track_id,))
    track = cursor.fetchone()
    cursor.close()
    if track:
        track['AudioFileURL'] = f"audio/{track['AudioFileURL'].split('/')[-1]}"
        return render_template('play.html', track=track)
    else:
        flash('Track not found', 'error')
        return redirect(url_for('index'))


@app.route('/like/<int:track_id>', methods=['POST'])
def like(track_id):
    if 'user_id' in session:
        user_id = session['user_id']
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO Likes (UserID, TrackID) VALUES (%s, %s)', (user_id, track_id))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'message': 'Track liked successfully!'})
    else:
        return jsonify({'message': 'Please login to like tracks.'}), 403


@app.route('/likes')
def likes():
    if 'user_id' in session:
        user_id = session['user_id']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT Tracks.* FROM Tracks '
                       'JOIN Likes ON Tracks.TrackID = Likes.TrackID '
                       'WHERE Likes.UserID = %s', (user_id,))
        liked_tracks = cursor.fetchall()
        cursor.close()
        return render_template('likes.html', liked_tracks=liked_tracks)
    else:
        flash('Please login to view your liked songs', 'error')
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
