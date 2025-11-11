from flask import Flask, render_template, request, redirect, url_for, flash
from models import Contact, db

from sqlalchemy.exc import IntegrityError
from country_tel import telephone_codes
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'
app.config['SECRET_KEY'] = 'fsjdhfsjiodjoa#fdshjiajsqiuoiplkj'

db.init_app(app)

def check_phone(phone_number):
    if len(phone_number) > 9 and len(phone_number) < 14:
        if phone_number.startswith('+998'):
            return True, f'{phone_number} is Correct'

    if len(phone_number) < 9 or len(phone_number) > 9:
        return False, f'{phone_number} phone number Incorrect!'
    else:
        return True, f'{phone_number} is Correct!'


def set_format(phone_number, region):
    if phone_number.startswith('+998'):
        return phone_number

    for obj in telephone_codes:
        if obj['region'] == region:
            phone_number = obj['calling_code'] + phone_number
            return phone_number


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/contact')
def view_contacts():
    contacts = Contact.query.order_by(Contact.name.asc()).all()

    return render_template('contacts.html', contacts=contacts)


@app.route('/contact/<int:id>')
def view_contact(id):
    contact = Contact.query.get_or_404(id)

    return render_template('contact.html', contact=contact)


@app.route('/contact/add', methods=['POST', 'GET'])
def add_contact():
    if request.method == 'POST':
        name = request.form.get('name').strip()
        phone_number = request.form.get('phone_number').strip()
        email = request.form.get('email').strip()
        address = request.form.get('address').strip()

        temporary = {
            'name' : name, 
            'phone_number' : phone_number,
            'email' : email,
            'address' : address
        }

        if not name or not phone_number:
            flash('Please complete the form!', category='warning')
            return render_template('add_contact.html', temporary=temporary)

        if len(name) < 2:
            flash('Please enter the contact name longer than 2 characters!', category='warning')
            return render_template('add_contact.html', temporary=temporary)

        if not check_phone(phone_number)[0]:
            flash('Phone number is incorrect!', category='error')
            return render_template('add_contact.html', temporary=temporary)

        phone_number = set_format(phone_number, 'UZB')

        try:
            new_contact = Contact(
                name = name,
                phone_number = phone_number,
                email = email if email else None,
                address = address if address else None
            )

            db.session.add(new_contact)
            db.session.commit()

            flash('Contact successfully created!', category='success')
            return redirect(url_for('view_contact', id=new_contact.id))

        except IntegrityError:
            db.session.rollback()

            flash('Error on adding Contact!', category='error')
            return redirect(url_for('home'))

    return render_template('add_contact.html')


@app.route('/contact/update/<int:id>', methods=['POST', 'GET'])
def update_contact(id):
    contact = Contact.query.get_or_404(id)
    if request.method == 'POST':
        name = request.form.get('name').strip()
        phone_number = request.form.get('phone_number').strip()
        email = request.form.get('email').strip()
        address = request.form.get('address').strip()

        pattern = ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', ',', '-', '.', '/',
            ':', ';', '<', '=', '>', '?', '@',
            '[', '\\', ']', '^', '_', '`',
            '{', '|', '}', '~'
        ]

        pattern = '[' + ' '.join(re.escape(char) for char in pattern) + ']'

        if not name or not phone_number:
            flash('Please complete the form!')
            return render_template('update_contact.html', contact=contact)

        if len(name) < 2:
            flash('Please enter the contact name longer than 2 characters!', category='warning')
            return render_template('update_contact.html', contact=contact)

        if not check_phone(phone_number)[0]:
            flash('Phone number is incorrect!', category='error')
            return render_template('update_contact.html', contact=contact)

        if re.search(pattern, phone_number):
            flash('Phone number doesn\'t contains any of patterns like < ! >  < ~ >', category='warning')
            return render_template('update_contact.html', contact=contact)

        phone_number = set_format(phone_number, 'UZB')

        try:
            contact.name = name if name else contact.name
            contact.phone_number = phone_number if phone_number else contact.phone_number
            contact.email = email if email else contact.email
            contact.address = address if address else contact.address

            db.session.commit()

        except IntegrityError:
            db.session.rollback()

            flash('Like this informations already exists')
            return redirect(url_for('update_contact', id=id))

        return redirect(url_for('view_contacts'))

    return render_template('update_contact.html', contact=contact)


@app.route('/contact/delete/<int:id>')
def delete_contact(id):
    contact = Contact.query.get_or_404(id)

    if not contact:
        flash('Object not found Error on deleting!')
        return redirect(url_for('home'))
    
    db.session.delete(contact)
    db.session.commit()

    return redirect(url_for('view_contacts'))


@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        q = request.form.get('q')
        
        if not q:
            return redirect(url_for('view_contacts'))

        contacts = Contact.query.filter(Contact.name.ilike(f'%{q}%') | Contact.phone_number.ilike(f'%{q}%')).all()

        return render_template('contacts.html', contacts=contacts)


if __name__ == '__main__':
    app.run(debug=True)