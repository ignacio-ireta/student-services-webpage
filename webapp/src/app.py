from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Don't use this in production
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql://user:password@mysql/student_registration')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    registrations = db.relationship('Registration', backref='student', lazy=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    registrations = db.relationship('Registration', backref='course', lazy=True)

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Add unique constraint to prevent duplicate registrations
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='_student_course_uc'),)

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    student_id = StringField('Student ID', validators=[DataRequired()])
    courses = SelectMultipleField('Select Courses (Multiple Selection Allowed)', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Register for Selected Courses')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ManageEnrollmentForm(FlaskForm):
    student_id = StringField('Student ID', validators=[DataRequired()])
    courses_to_drop = SelectMultipleField('Select Courses to Drop', coerce=int)
    submit = SubmitField('Drop Selected Courses')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('register'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('register'))
        flash('Invalid username or password', 'error')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    return redirect(url_for('login'))
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    form = RegistrationForm()
    form.courses.choices = [(c.id, f"{c.code} - {c.name}") for c in Course.query.all()]
    
    # Initialize registrations as None
    registrations = None
    
    # Get the current user's student record
    student = Student.query.filter_by(student_id=session.get('student_id')).first()
    
    if form.validate_on_submit():
        try:
            # Only allow students to register themselves
            if student and student.student_id != form.student_id.data:
                flash('You can only register courses for yourself', 'error')
                return redirect(url_for('register'))
            
            if student:
                # Update name if it changed
                if student.name != form.name.data:
                    student.name = form.name.data
            else:
                # Create new student
                student = Student(name=form.name.data, student_id=form.student_id.data)
                db.session.add(student)
                session['student_id'] = form.student_id.data
            
            # Ensure student is in the session
            db.session.flush()
            
            # Get current registrations
            existing_registrations = {r.course_id for r in student.registrations}
            
            # Process new registrations
            for course_id in form.courses.data:
                if course_id not in existing_registrations:
                    registration = Registration(student_id=student.id, course_id=course_id)
                    db.session.add(registration)
            
            db.session.commit()
            flash('Course registration successful!', 'success')
            
            # Redirect to student dashboard
            return redirect(url_for('view_enrollments', student_id=student.student_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error during registration: {str(e)}', 'error')
            print(f"Error: {str(e)}")
    
    elif request.method == 'POST':
        # If form validation failed
        flash('Please correct the errors in the form.', 'error')
    
    # Show existing registrations if student ID is provided
    if student:
        form.student_id.data = student.student_id
        form.name.data = student.name
        registrations = [
            {'course_code': reg.course.code, 'course_name': reg.course.name}
            for reg in student.registrations
        ]
    
    return render_template('register.html', form=form, registrations=registrations)

@app.route('/enrollments', methods=['GET'])
@login_required
def view_enrollments():
    student_id = request.args.get('student_id', '')
    
    if not student_id:
        flash('Please enter a student ID', 'error')
        return redirect(url_for('register'))
    
    # Only allow students to view their own enrollments
    if student_id != session.get('student_id'):
        flash('You can only view your own enrollments', 'error')
        return redirect(url_for('register'))
    
    student = Student.query.filter_by(student_id=student_id).first()
    
    if not student:
        flash(f'No student found with ID: {student_id}', 'error')
        return redirect(url_for('register'))
    
    enrollments = []
    for reg in student.registrations:
        enrollments.append({
            'id': reg.id,
            'course_id': reg.course_id,
            'course_code': reg.course.code,
            'course_name': reg.course.name,
            'registration_date': reg.registration_date
        })
    
    return render_template('enrollments.html', student=student, enrollments=enrollments)

@app.route('/manage-enrollments', methods=['GET', 'POST'])
@login_required
def manage_enrollments():
    form = ManageEnrollmentForm()
    student = None
    
    if request.method == 'GET':
        student_id = request.args.get('student_id', '')
        if student_id:
            # Only allow students to manage their own enrollments
            if student_id != session.get('student_id'):
                flash('You can only manage your own enrollments', 'error')
                return redirect(url_for('register'))
            form.student_id.data = student_id
    
    if form.student_id.data:
        # Only allow students to manage their own enrollments
        if form.student_id.data != session.get('student_id'):
            flash('You can only manage your own enrollments', 'error')
            return redirect(url_for('register'))
            
        student = Student.query.filter_by(student_id=form.student_id.data).first()
        if student:
            # Get current enrollments
            current_enrollments = student.registrations
            # Update form choices
            form.courses_to_drop.choices = [(reg.course_id, f"{reg.course.code} - {reg.course.name}") 
                                           for reg in current_enrollments]
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            student = Student.query.filter_by(student_id=form.student_id.data).first()
            
            if not student:
                flash(f'No student found with ID: {form.student_id.data}', 'error')
                return redirect(url_for('manage_enrollments'))
            
            # Process drops
            if form.courses_to_drop.data:
                for course_id in form.courses_to_drop.data:
                    registration = Registration.query.filter_by(
                        student_id=student.id, 
                        course_id=course_id
                    ).first()
                    
                    if registration:
                        db.session.delete(registration)
                
                db.session.commit()
                flash('Selected courses have been dropped successfully', 'success')
                return redirect(url_for('view_enrollments', student_id=student.student_id))
            else:
                flash('No courses selected to drop', 'warning')
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error dropping courses: {str(e)}', 'error')
            print(f"Error: {str(e)}")
    
    return render_template('manage_enrollments.html', form=form, student=student)

@app.route('/find-student', methods=['GET', 'POST'])
@login_required
def find_student():
    if request.method == 'POST':
        student_id = request.form.get('student_id', '')
        if student_id:
            # Only allow students to find their own information
            if student_id != session.get('student_id'):
                flash('You can only view your own information', 'error')
                return redirect(url_for('register'))
            return redirect(url_for('view_enrollments', student_id=student_id))
    
    return render_template('find_student.html')

@app.before_first_request
def create_admin_user():
    if User.query.count() == 0:
        admin = User(username='admin', is_admin=True)
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()

@app.before_first_request
def create_sample_courses():
    if Course.query.count() == 0:
        sample_courses = [
            Course(code='CS101', name='Introduction to Programming'),
            Course(code='CS201', name='Data Structures'),
            Course(code='CS301', name='Algorithms'),
            Course(code='CS401', name='Database Systems'),
            Course(code='CS501', name='Machine Learning')
        ]
        for course in sample_courses:
            db.session.add(course)
        db.session.commit()

class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    student_id = StringField('Student ID', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_student_id(self, field):
        student = Student.query.filter_by(student_id=field.data).first()
        if student:
            raise ValidationError('Student ID already exists. Please check your information.')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('register'))
    
    form = SignUpForm()
    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            flash('Passwords do not match', 'error')
            return render_template('signup.html', form=form)
        
        try:
            # Create new user
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            
            # Create new student
            student = Student(name=form.name.data, student_id=form.student_id.data)
            db.session.add(student)
            
            db.session.commit()
            
            # Log the user in
            session['user_id'] = user.id
            session['student_id'] = student.student_id
            flash('Registration successful! Welcome!', 'success')
            return redirect(url_for('register'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error during registration: {str(e)}', 'error')
            print(f"Error: {str(e)}")
    
    return render_template('signup.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)