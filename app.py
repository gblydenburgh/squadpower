from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_wtf.csrf import CSRFProtect
from forms import UserForm, SquadInputForm, DeleteForm
from models import db, User, Squad

app = Flask(__name__)

# Configuration for the database and security settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'

# Initialize CSRF protection
csrf = CSRFProtect(app)
# Initialize the database
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'squad_count' not in session:
        form = UserForm()

        if form.validate_on_submit():
            session['name'] = form.name.data
            session['resistance'] = form.resistance.data
            session['squad_count'] = form.squad_count.data

            print(f"User details stored: Name={session['name']}, Resistance={session['resistance']}, Squads={session['squad_count']}")
            return redirect(url_for('register'))
        return render_template('register.html', form=form)

    else:
        squad_count = session['squad_count']
        form = SquadInputForm()

        while len(form.squads) < squad_count:
            form.squads.append_entry()

        if form.validate_on_submit():
            new_user = User(name=session['name'], resistance=session['resistance'])
            db.session.add(new_user)
            db.session.commit()

            for index, squad_form in enumerate(form.squads.entries):
                squad = Squad(power=squad_form.data['power'], user=new_user)
                db.session.add(squad)
                print(f"Squad {index + 1} with power {squad.power} added for user '{new_user.name}'.")

            for index in range(squad_count, 4):
                squad = Squad(power=0, user=new_user)
                db.session.add(squad)
                print(f"Auto-filled Squad {index + 1} with power 0 for user '{new_user.name}'.")

            db.session.commit()
            flash('User and squads registered successfully!', 'success')
            print(f"User '{session['name']}' with resistance {session['resistance']} and squads registered successfully.")

            session.clear()
            return redirect(url_for('register'))

        return render_template('register_squads.html', form=form)

@app.route('/summary')
def summary():
    delete_form = DeleteForm()
    try:
        sort_by = request.args.get('sort_by', 'name')
        sort_order = request.args.get('sort_order', 'asc')

        if sort_by == 'resistance':
            users = User.query.order_by(User.resistance.asc() if sort_order == 'asc' else User.resistance.desc()).all()
        elif 'squad' in sort_by:
            # Extract the squad number and ensure it's an integer
            squad_number = int(sort_by.replace('squad', '').strip())
            users = (
                User.query
                .join(Squad)
                .filter(Squad.id == squad_number)
                .order_by(Squad.power.asc() if sort_order == 'asc' else Squad.power.desc())
                .all()
            )
        else:
            users = User.query.order_by(User.name.asc() if sort_order == 'asc' else User.name.desc()).all()

        print(f"Loaded summary page with sort_by={sort_by} and sort_order={sort_order}.")
        return render_template('summary.html', users=users, sort_by=sort_by, sort_order=sort_order, delete_form=delete_form)

    except Exception as e:
        print(f"An error occurred while generating the summary: {e}")
        flash(f"An error occurred while generating the summary: {e}", 'danger')
        return render_template('summary.html', users=[], sort_by=sort_by, sort_order=sort_order, delete_form=delete_form)

@app.route('/delete_users', methods=['POST'])
def delete_users():
    try:
        user_ids = request.form.getlist('user_ids')

        if not user_ids:
            flash('No users were selected for deletion.', 'danger')
            return redirect(url_for('summary'))

        users_to_delete = User.query.filter(User.id.in_(user_ids)).all()

        for user in users_to_delete:
            db.session.delete(user)
            print(f"User '{user.name}' with ID {user.id} deleted.")

        db.session.commit()
        flash('Selected users deleted successfully.', 'success')

    except Exception as e:
        print(f"An error occurred while deleting users: {e}")
        flash(f"An error occurred while deleting users: {e}", 'danger')

    return redirect(url_for('summary'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    try:
        if request.method == 'POST' and form.validate_on_submit():
            username = form.username.data
            user = User.query.filter_by(name=username).first()
            if user:
                flash(f"User '{username}' found, redirecting to update page.", 'success')
                return redirect(url_for('update_user', user_id=user.id))
            else:
                flash(f"User '{username}' not found.", 'danger')
        return render_template('search.html', form=form)
    except Exception as e:
        flash(f"An error occurred during the search: {str(e)}", 'danger')
        return render_template('search.html', form=form)

@app.route('/update/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        form = UserForm(obj=user)  # Populate the form with the user's existing data

        if form.validate_on_submit():
            user.name = form.name.data
            user.resistance = form.resistance.data

            # Update squad power levels
            for i, squad_form in enumerate(form.squads.entries):
                if i < len(user.squads):
                    user.squads[i].power = squad_form.data['power']
                else:
                    # Add a new squad if more squads are added than previously existed
                    new_squad = Squad(power=squad_form.data['power'], user=user)
                    db.session.add(new_squad)

            # Handle any reduction in the number of squads
            for i in range(len(form.squads.entries), len(user.squads)):
                db.session.delete(user.squads[i])

            db.session.commit()
            flash(f"User '{user.name}' updated successfully.", 'success')
            return redirect(url_for('search'))

        return render_template('update.html', form=form, user=user)
    except Exception as e:
        flash(f"An error occurred while updating the user: {str(e)}", 'danger')
        return redirect(url_for('search'))

@app.route('/add_squad/<int:user_id>', methods=['POST'])
def add_squad(user_id):
    try:
        user = User.query.get_or_404(user_id)
        if len(user.squads) < 4:  # Maximum of 4 squads
            new_squad = Squad(power=0, user=user)
            db.session.add(new_squad)
            db.session.commit()
            flash('Squad added successfully.', 'success')
        else:
            flash('User already has 4 squads, cannot add more.', 'danger')
        return redirect(url_for('update_user', user_id=user.id))
    except Exception as e:
        flash(f"An error occurred while adding a squad: {str(e)}", 'danger')
        return redirect(url_for('update_user', user_id=user.id))

@app.route('/remove_squad/<int:user_id>', methods=['POST'])
def remove_squad(user_id):
    try:
        user = User.query.get_or_404(user_id)
        if len(user.squads) > 1:  # Minimum of 1 squad must remain
            squad_to_remove = user.squads[-1]
            db.session.delete(squad_to_remove)
            db.session.commit()
            flash('Squad removed successfully.', 'success')
        else:
            flash('User must have at least 1 squad.', 'danger')
        return redirect(url_for('update_user', user_id=user.id))
    except Exception as e:
        flash(f"An error occurred while removing a squad: {str(e)}", 'danger')
        return redirect(url_for('update_user', user_id=user.id))

if __name__ == '__main__':
    try:
        with app.app_context():
            db.create_all()
            print("Database and tables created successfully.")

        app.run(debug=True, host='0.0.0.0')
        print("Application started and listening on all available IPs.")
    except Exception as e:
        print(f"Failed to start the application: {e}")
