from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Configuración de la app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'  # Ruta de la base de datos
app.config['SECRET_KEY'] = 'clave_secreta'  # Cambia esto por una clave secreta más segura

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelo de la base de datos para Contactos
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100))

# Modelo de Usuario para login
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    @staticmethod
    def check_password(hashed_password, password):
        return check_password_hash(hashed_password, password)

# Crear la base de datos y agregar un usuario administrador si no existe
with app.app_context():
    db.create_all()  # Crear todas las tablas
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", password="admin123")
        db.session.add(admin)
        db.session.commit()

# Cargar usuario para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    contacts = Contact.query.all()  # Obtener todos los contactos
    return render_template('index.html', contacts=contacts)

@app.route('/add', methods=['POST'])
@login_required
def add_contact():
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')

    if not name or not phone:
        flash("Todos los campos son obligatorios.", "danger")
        return redirect(url_for('index'))

    new_contact = Contact(name=name, phone=phone, email=email)
    db.session.add(new_contact)
    db.session.commit()
    flash("Contacto agregado con éxito.", "success")

    return redirect(url_for('index'))

@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_contact(id):
    contact = Contact.query.get_or_404(id)
    if request.method == 'POST':
        contact.name = request.form.get('name')
        contact.phone = request.form.get('phone')
        contact.email = request.form.get('email')
        db.session.commit()
        flash("Contacto actualizado con éxito.", "success")
        return redirect(url_for('index'))
    return render_template('update.html', contact=contact)

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_contact(id):
    contact = Contact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    flash("Contacto eliminado con éxito.", "success")
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and User.check_password(user.password, password):
            login_user(user)
            flash("Iniciaste sesión correctamente.", "success")
            return redirect(url_for('index'))
        flash("Usuario o contraseña incorrectos.", "danger")
    return render_template('login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("logout.html")


@app.route('/cv')
def cv():
    return render_template('cv.html')  # Redirige a la página de CV

@app.errorhandler(401)
def unauthorized_error(e):
    return redirect(url_for("login"))

@app.errorhandler(404)
def error_404(error):
    return render_template("error404.html"), 404

if __name__ == '__main__':
    app.run(debug=True)
