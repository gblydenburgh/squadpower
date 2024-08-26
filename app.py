from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf.csrf import CSRFProtect
from forms import UserForm
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'

csrf = CSRFProtect(app)
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm()
    
    print("Reached the /register route")
    
    try:
        if form.validate_on_submit():
            print("Form validated successfully")
            
            user = User.query.filter_by(name=form.name.data).first()
            if user:
                flash('User already exists, please choose another name.', 'danger')
                print(f"User '{form.name.data}' already exists.")
            else:
                new_user = User(name=form.name.data, resistance=form.resistance.data)
                db.session.add(new_user)
                db.session.commit()
                flash('User registered successfully!', 'success')
                print(f"User '{form.name.data}' with resistance {form.resistance.data} registered.")
            
            return redirect(url_for('register'))
        else:
            print("Form did not validate")
            for fieldName, errorMessages in form.errors.items():
                for err in errorMessages:
                    flash(f"Error in {getattr(form, fieldName).label.text}: {err}", 'danger')
                    print(f"Validation error in {fieldName}: {err}")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        flash(f"An unexpected error occurred: {e}", 'danger')
    
    return render_template('register.html', form=form)

@app.route('/summary')
def summary():
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')
    
    if sort_by == 'resistance':
        if sort_order == 'asc':
            users = User.query.order_by(User.resistance.asc()).all()
        else:
            users = User.query.order_by(User.resistance.desc()).all()
    else:
        if sort_order == 'asc':
            users = User.query.order_by(User.name.asc()).all()
        else:
            users = User.query.order_by(User.name.desc()).all()
    
    return render_template('summary.html', users=users, sort_by=sort_by, sort_order=sort_order)

if __name__ == '__main__':
    try:
        with app.app_context():
            db.create_all()  # Ensure the database and tables are created
            print("Database and tables created successfully.")
        app.run(debug=True,host='0.0.0.0')
    except Exception as e:
        print(f"Failed to start the application: {e}")
