from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///business_site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Login Stuff

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '_________'  # Enter your MySql password 
app.config['MYSQL_DB'] = 'geeklogin'

# Define the Contact model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)   
    def __repr__(self):
        return f'<Contact {self.name}>'

# creates account storage
class Password(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    def __repr__(self):
        return f'<Contact {self.name}>'



@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # Create a new Contact instance
        new_contact = Contact(name=name, email=email, message=message)
        
        try:
            # Add to database and commit
            db.session.add(new_contact)
            db.session.commit()
            flash('Thank you for your message! We will get back to you soon.', 'success')
        except Exception as e:
            # In case of error, roll back
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
        
        return redirect(url_for('contact'))
        
    return render_template('contact.html')

@app.route('/admin/contacts/delete/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    try:
        db.session.delete(contact)
        db.session.commit()
        flash('Contact deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting contact: {str(e)}', 'danger')
    
    return redirect(url_for('view_contacts'))

# Edit a contact (GET shows form, POST processes form)
@app.route('/admin/contacts/edit/<int:contact_id>', methods=['GET', 'POST'])
def edit_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    
    if request.method == 'POST':
        contact.name = request.form.get('name')
        contact.email = request.form.get('email')
        contact.message = request.form.get('message')
        
        try:
            db.session.commit()
            flash('Contact updated successfully', 'success')
            return redirect(url_for('view_contacts'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating contact: {str(e)}', 'danger')
    
    return render_template('edit_contact.html', contact=contact)

@app.route('/admin/search')
def search_contacts():
    query = request.args.get('q', '')
    if query:
        # Search in name, email, and message
        contacts = Contact.query.filter(
            db.or_(
                Contact.name.contains(query),
                Contact.email.contains(query),
                Contact.message.contains(query)
            )
        ).order_by(Contact.date_submitted.desc()).all()
    else:
        contacts = []
    
    return render_template('search_contacts.html', contacts=contacts, query=query)

# Add a route to view all contact submissions (admin page)
@app.route('/admin/contacts')
def view_contacts():
    # In a real app, this should be protected with authentication
    contacts = Contact.query.order_by(Contact.date_submitted.desc()).all()
    return render_template('admin_contacts.html', contacts=contacts)

# Create database tables before running the app
# The following code works with all Flask versions
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)