from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer
import os
from datetime import datetime

app = Flask(__name__)

# ================= CONFIG =================

app.config['SECRET_KEY'] = 'mysecret123'
app.config['SECURITY_PASSWORD_SALT'] = 'mysalt'


if os.environ.get('TESTING'):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:123@localhost/restaurant_db'

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= MODEL =================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(200))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    guests = db.Column(db.Integer)
    date = db.Column(db.String(20))
    time = db.Column(db.String(10))
    table_number = db.Column(db.Integer)
    status = db.Column(db.String(20), default="Chờ")


class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Integer)
    description = db.Column(db.String(255))
    image = db.Column(db.String(255))

# ================= HOME =================

@app.route('/')
def index():
    return render_template('index.html')

# ================= LOGIN =================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()

        if user and user.check_password(request.form['password']):
            session['user'] = user.username
            flash("Đăng nhập thành công!")
            return redirect('/admin')
        else:
            flash("Sai tài khoản hoặc mật khẩu!")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Đã đăng xuất")
    return redirect('/')

# ================= FORGOT PASSWORD =================

@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user:
            user.set_password(new_password)
            db.session.commit()
            flash("Đổi mật khẩu thành công!")
            return redirect('/login')
        else:
            flash("Không tìm thấy tài khoản!")

    return render_template('forgot.html')
# ================= RESET PASSWORD =================

@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        username = s.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=300)
    except:
        flash("Link hết hạn hoặc sai!")
        return redirect('/login')

    if request.method == 'POST':
        user = User.query.filter_by(username=username).first()
        user.set_password(request.form['password'])
        db.session.commit()
        flash("Đổi mật khẩu thành công!")
        return redirect('/login')

    return render_template('reset.html')

# ================= RESERVATION =================
from datetime import datetime, date  

@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if request.method == 'POST':

        selected_date = datetime.strptime(request.form['date'], "%Y-%m-%d").date()
        today = date.today()

        if selected_date < today:
            flash("Không thể đặt bàn ngày trong quá khứ!")
            return redirect('/reserve')
        # ===============================
        time_str = request.form['time']
        time_obj = datetime.strptime(time_str, "%H:%M")

        if not (13 <= time_obj.hour <= 22):
            flash("Đặt bàn không thành công (13h-22h)")
            return redirect('/reserve')

        guests = int(request.form['guests'])
        if guests < 1 or guests > 10:
            flash("Chỉ nhận 1-10 người")
            return redirect('/reserve')

        table_number = int(request.form['table_number'])  

        exists = Reservation.query.filter_by(
            date=request.form['date'],
            time=time_str,
            table_number=table_number
        ).first()

        if exists:
            flash(f"Bàn {table_number} đã có người đặt!")
            return redirect('/reserve')

        count = Reservation.query.filter_by(
            date=request.form['date'],
            time=time_str
        ).count()

        if count >= 10:
            flash("Hết bàn!")
            return redirect('/reserve')

        r = Reservation(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            guests=guests,
            date=request.form['date'],
            time=time_str,
            table_number=table_number
        )

        db.session.add(r)
        db.session.commit()

        flash("Đặt bàn thành công!")
        return redirect('/')

    return render_template(
        'reservations.html',
        today=date.today().strftime("%Y-%m-%d")
    )

# ================= ADMIN =================
from datetime import date
@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect('/login')

    selected_date = request.args.get('date')

    if selected_date:
        reservations = Reservation.query.filter_by(date=selected_date).all()
    else:
        reservations = Reservation.query.all()

    return render_template(
        'admin.html',
        reservations=reservations,
        selected_date=selected_date
    )

@app.route('/admin/action/<int:id>')
def handle_action(id):
    if 'user' not in session:
        return redirect('/login')

    action = request.args.get('action')
    r = Reservation.query.get(id)

    if action == "confirm":
        r.status = "Đã xác nhận"

    elif action == "reject":
        r.status = "Từ chối"

    elif action == "delete":
        db.session.delete(r)
        db.session.commit()
        return redirect('/admin')

    db.session.commit()
    return redirect('/admin')

# ================= MENU =================

@app.route('/menu')
def menu():
    return render_template('menu.html', items=Menu.query.all())


@app.route('/admin/menu')
def admin_menu():
    if 'user' not in session:
        return redirect('/login')

    return render_template('admin_menu.html', items=Menu.query.all())


@app.route('/admin/menu/add', methods=['GET', 'POST'])
def add_menu():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        file = request.files['image']
        filename = None

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        m = Menu(
            name=request.form['name'],
            price=request.form['price'],
            description=request.form['description'],
            image=filename
        )

        db.session.add(m)
        db.session.commit()
        flash("Thêm món thành công")  
        return redirect('/admin/menu')

    return render_template('add_menu.html')


@app.route('/admin/menu/edit/<int:id>', methods=['GET', 'POST'])
def edit_menu(id):
    if 'user' not in session:
        return redirect('/login')

    item = Menu.query.get(id)

    if request.method == 'POST':
        item.name = request.form['name']
        item.price = request.form['price']
        item.description = request.form['description']
        file = request.files.get('image')

        if file and file.filename != "":
            import os, uuid
            filename = str(uuid.uuid4()) + "_" + file.filename
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            item.image = filename

        db.session.commit()
        flash("Cập nhật thành công")  
        return redirect('/admin/menu')

    return render_template('edit_menu.html', item=item)


@app.route('/admin/menu/delete/<int:id>')
def delete_menu(id):
    if 'user' not in session:
        return redirect('/login')

    db.session.delete(Menu.query.get(id))
    db.session.commit()
    flash("Xoá thành công")  
    return redirect('/admin/menu')

# ================= RUN =================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username='admin').first():
            u = User(username='admin')
            u.set_password('123')
            db.session.add(u)
            db.session.commit()

    app.run(debug=True)
