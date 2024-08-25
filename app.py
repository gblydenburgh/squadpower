from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from models import db, User, Squad
from forms import UserForm, SearchForm
from rapidfuzz import process

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///squadpower.db'
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)

# Create the database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # Display the search form on the homepage
    search_form = SearchForm()
    return render_template('index.html', form=search_form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Handle user registration
    form = UserForm()
    if form.validate_on_submit():
        # Check if the user already exists
        user = User.query.filter_by(name=form.name.data).first()
        if user:
            flash('User already exists, please update instead.', 'danger')
        else:
            # Create a new user
            user = User(name=form.name.data, resistance=form.resistance.data)
            for squad_form in form.squads.entries:
                squad = Squad(power=squad_form.data['power'], user=user)
                db.session.add(squad)
            db.session.add(user)
            db.session.commit()
            flash('User registered successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/update/<int:user_id>', methods=['GET', 'POST'])
def update(user_id):
    # Handle user updates
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        # Update user details
        user.name = form.name.data
        user.resistance = form.resistance.data
        for i, squad_form in enumerate(form.squads.entries):
            if i < len(user.squads):
                user.squads[i].power = squad_form.data['power']
            else:
                squad = Squad(power=squad_form.data['power'], user=user)
                db.session.add(squad)
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('update.html', form=form, user=user)

@app.route('/summary')
def summary():
    # Display a summary of all users and their squads
    users = User.query.all()
    return render_template('summary.html', users=users)

@app.route('/search', methods=['POST'])
def search():
    # Handle the typeahead search
    query = request.json['query']
    users = [user.name for user in User.query.all()]
    results = process.extract(query, users, limit=5)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
