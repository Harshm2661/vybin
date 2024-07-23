from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import datetime

app = Flask(name)
app.secret_key = 'your_secret_key'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Appu@123'
app.config['MYSQL_DB'] = 'CommunityIssueReporting'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Ensure the 'uploads' folder exists
os.makedirs(os.path.join('static', 'uploads'), exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM Users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()
        if user and check_password_hash(user['password'], password):
            session['user'] = user
            flash('Login successful!', 'success')
            return redirect(url_for('index'))  # Redirect to another page after successful login
        else:
            flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO Users (name, email, password, role) VALUES (%s, %s, %s, %s)',
                       (name, email, password, role))
        mysql.connection.commit()
        cursor.close()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/report_issue', methods=['GET', 'POST'])
def report_issue():
    if request.method == 'POST':
        category_id = request.form.get('category_id')
        description = request.form.get('description')
        location = request.form.get('location')

        if 'images' in request.files:
            images = request.files.getlist('images')
            image_filenames = []
            for image in images:
                filename = secure_filename(image.filename)
                image.save(os.path.join('static', 'uploads', filename))
                image_filenames.append(filename)

            images_str = ','.join(image_filenames)
        else:
            images_str = ''

        # Validate category_id exists
        if not category_id:
            # Handle error or redirect to form with error message
            return redirect(url_for('report_issue_form', error='Category is required'))

        # Insert into Problems table
        cursor = mysql.connection.cursor()
        cursor.execute(
            'INSERT INTO Problems (user_id, category_id, description, location, status, reported_date, images) VALUES (%s, %s, %s, %s, %s, NOW(), %s)',
            (session['user']['user_id'], category_id, description, location, 'Reported', images_str)
        )
        mysql.connection.commit()
        cursor.close()

        # Redirect to view issues or success page
        return redirect(url_for('view_issues'))

    # If GET request, fetch categories and render the report issue form
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM Categories')
    categories = cursor.fetchall()
    cursor.close()

    return render_template('report_issue.html', categories=categories)


@app.route('/update_status/<int:issue_id>', methods=['GET', 'POST'])
def update_status(issue_id):
    if 'user' not in session or session['user']['role'] != 'authority':
        flash('You are not authorized to perform this action.', 'error')
        return redirect(url_for('view_issues'))

    if request.method == 'POST':
        status = request.form['status']
        update_date = datetime.datetime.now()

        try:
            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE Problems SET status = %s, resolved_date = %s WHERE problem_id = %s',
                           (status, update_date, issue_id))
            mysql.connection.commit()
            cursor.close()

            flash('Status updated successfully.', 'success')
            return redirect(url_for('view_issues'))

        except Exception as e:
            flash(f'Failed to update status: {str(e)}', 'error')
            return redirect(url_for('view_issues'))

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT Problems.*, Categories.category_name FROM Problems JOIN Categories ON Problems.category_id = Categories.category_id WHERE Problems.problem_id = %s',
            (issue_id,))
        issue = cursor.fetchone()
        cursor.close()
        return render_template('update_status.html', issue=issue)

    except Exception as e:
        flash(f'Error fetching issue details: {str(e)}', 'error')
        return redirect(url_for('view_issues'))


@app.route('/view_issues')
def view_issues():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('''
            SELECT Problems.problem_id, Problems.description, Problems.location, Problems.status, 
                   Problems.reported_date, Categories.category_name
            FROM Problems
            JOIN Categories ON Problems.category_id = Categories.category_id
            ORDER BY Problems.problem_id DESC
        ''')
        issues = cursor.fetchall()
        cursor.close()

        return render_template('view_issues.html', issues=issues)

    except Exception as e:
        flash(f'Error fetching issues: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/issue/<int:issue_id>')
def issue_details(issue_id):
    cursor = mysql.connection.cursor()

    # Fetch issue details
    cursor.execute('''
        SELECT Problems.*, Categories.category_name, Users.name AS reported_by_name
        FROM Problems
        JOIN Categories ON Problems.category_id = Categories.category_id
        JOIN Users ON Problems.user_id = Users.user_id
        WHERE problem_id = %s
    ''', (issue_id,))
    issue = cursor.fetchone()

    # Fetch comments
    cursor.execute('''
        SELECT Comments.*, Users.name AS commenter_name
        FROM Comments
        JOIN Users ON Comments.user_id = Users.user_id
        WHERE problem_id = %s
    ''', (issue_id,))
    comments = cursor.fetchall()

    cursor.close()

    # Print session data for debugging
    print(session)

    return render_template('issue_details.html', issue=issue, comments=comments)


@app.route('/issue/<int:issue_id>/add_comment', methods=['POST'])
def add_comment(issue_id):
    if 'user' not in session or 'user_id' not in session['user']:
        flash('You must be logged in to add a comment.', 'error')
        return redirect(url_for('login'))  # Redirect to login if user is not logged in

    user_id = session['user']['user_id']
    comment_text = request.form.get('comment_text')
    if not comment_text:
        flash('Comment text is required.', 'error')
        return redirect(url_for('issue_details', issue_id=issue_id))

    comment_date = datetime.datetime.now()

    try:
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO Comments (problem_id, user_id, comment_text, comment_date) VALUES (%s, %s, %s, %s)',
                       (issue_id, user_id, comment_text, comment_date))
        mysql.connection.commit()
        cursor.close()
        flash('Comment added successfully!', 'success')
    except Exception as e:
        flash(f'Error occurred while adding comment: {str(e)}', 'error')
    finally:
        return redirect(url_for('issue_details', issue_id=issue_id))





@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    if 'user' not in session:
        flash('You must be logged in to delete a comment.', 'error')
        return redirect(url_for('login'))

    try:
        cursor = mysql.connection.cursor()

        # Fetch the comment to check ownership
        cursor.execute('SELECT user_id, problem_id FROM Comments WHERE comment_id = %s', (comment_id,))
        comment = cursor.fetchone()

        if not comment:
            flash('Comment not found.', 'error')
            return redirect(url_for('view_issues'))  # Or any appropriate redirect

        if comment['user_id'] != session['user']['user_id']:
            flash('You are not authorized to delete this comment.', 'error')
            return redirect(url_for('issue_details', issue_id=comment['problem_id']))

        # Delete the comment
        cursor.execute('DELETE FROM Comments WHERE comment_id = %s', (comment_id,))
        mysql.connection.commit()
        cursor.close()

        flash('Comment deleted successfully.', 'success')
        return redirect(url_for('issue_details', issue_id=comment['problem_id']))

    except Exception as e:
        flash(f'Failed to delete comment: {str(e)}', 'error')
        return redirect(url_for('issue_details', issue_id=comment['problem_id']))

if name == 'main':
    app.run(debug=True)