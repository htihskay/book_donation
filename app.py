from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SelectField,RadioField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from passlib.hash import sha256_crypt
from functools import wraps
from flask_uploads import UploadSet, configure_uploads, IMAGES
import timeit
import datetime
from flask_mail import Mail, Message
import os
from wtforms.fields.html5 import EmailField

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/image/product'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

# Config MySQL
mysql = MySQL()
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'book_donation'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize the app for use with this MySQL class
mysql.init_app(app)


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, *kwargs)
        else:
            return redirect(url_for('login'))

    return wrap


def not_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return redirect(url_for('index'))
        else:
            return f(*args, *kwargs)

    return wrap


def is_admin_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin_logged_in' in session:
            return f(*args, *kwargs)
        else:
            return redirect(url_for('admin_login'))

    return wrap


def not_admin_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin_logged_in' in session:
            return redirect(url_for('admin'))
        else:
            return f(*args, *kwargs)

    return wrap


def wrappers(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)

    return wrapped



#updated with the cs field pending withe rest
@app.route('/')
def index():
    form = OrderForm(request.form)
    # Create cursor
    cur = mysql.connection.cursor()
    # Get message
    values = 'cs'
    cur.execute("SELECT * FROM books WHERE category=%s ORDER BY RAND() LIMIT 4", (values,))
    cs = cur.fetchall()
    values = 'ec'
    cur.execute("SELECT * FROM books WHERE category=%s ORDER BY RAND() LIMIT 4", (values,))
    ec = cur.fetchall()
    values = 'me'
    cur.execute("SELECT * FROM books WHERE category=%s ORDER BY RAND() LIMIT 4", (values,))
    me = cur.fetchall()
    values = 'cv'
    cur.execute("SELECT * FROM books WHERE category=%s ORDER BY RAND() LIMIT 4", (values,))
    cv = cur.fetchall()
    # Close Connection
    cur.close()
    return render_template('home.html', cs=cs, ec=ec, me=me, cv=cv, form=form)


class LoginForm(Form):  # Create Login Form
    username = StringField('', [validators.length(min=1)],
                           render_kw={'autofocus': True, 'placeholder': 'Username'})
    password = PasswordField('', [validators.length(min=3)],
                             render_kw={'placeholder': 'Password'})


# User Login
@app.route('/login', methods=['GET', 'POST'])
@not_logged_in
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        # GEt user form
        username = form.username.data
        # password_candidate = request.form['password']
        password_candidate = form.password.data

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username=%s", [username])

        if result > 0:
            # Get stored value
            data = cur.fetchone()
            password = data['password']
            uid = data['id']
            name = data['name']

            # Compare password
            if sha256_crypt.verify(password_candidate, password):
                # passed
                session['logged_in'] = True
                session['uid'] = uid
                session['s_name'] = name


                return redirect(url_for('index'))

            else:
                flash('Incorrect password', 'danger')
                return render_template('login.html', form=form)

        else:
            flash('Username not found', 'danger')
            # Close connection
            cur.close()
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)


@app.route('/out')
def logout():
    if 'uid' in session:
        # Create cursor
        cur = mysql.connection.cursor()
        uid = session['uid']
        
        session.clear()
        flash('You are logged out', 'success')
        return redirect(url_for('index'))
    return redirect(url_for('login'))


class RegisterForm(Form):
    name = StringField('', [validators.length(min=3, max=50)],
                       render_kw={'autofocus': True, 'placeholder': 'Full Name'})
    username = StringField('', [validators.length(min=3, max=25)], render_kw={'placeholder': 'Username'})
    email = EmailField('', [validators.DataRequired(), validators.Email(), validators.length(min=4, max=25)],
                       render_kw={'placeholder': 'Email'})
    password = PasswordField('', [validators.length(min=3)],
                             render_kw={'placeholder': 'Password'})
    mobile = StringField('', [validators.length(min=11, max=15)], render_kw={'placeholder': 'Mobile'})


@app.route('/register', methods=['GET', 'POST'])
@not_logged_in
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        mobile = form.mobile.data

        # Create Cursor
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, username, password, mobile) VALUES(%s, %s, %s, %s, %s)",
                    (name, email, username, password, mobile))

        # Commit cursor
        mysql.connection.commit()

        # Close Connection
        cur.close()

        flash('You are now registered and can login', 'success')

        return redirect(url_for('index'))
    return render_template('register.html', form=form)



class DonorLoginForm(Form):  # Create Login Form
    username = StringField('', [validators.length(min=1)],
                           render_kw={'autofocus': True, 'placeholder': 'Username'})
    password = PasswordField('', [validators.length(min=3)],
                             render_kw={'placeholder': 'Password'})



#Donor Login 
@app.route('/donor_login', methods=['GET', 'POST'])
def donor_login():
    form = DonorLoginForm(request.form)
    if request.method == 'POST' and form.validate():
        # GEt user form
        username = form.username.data
        # password_candidate = request.form['password']
        password_candidate = form.password.data

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM donors WHERE username=%s", [username])

        if result > 0:
            # Get stored value
            data = cur.fetchone()
            password = data['password']
            uid = data['d_id']
            name = data['name']

            # Compare password
            if sha256_crypt.verify(password_candidate, password):
                # passed
                session['logged_in'] = True
                session['uid'] = uid
                session['s_name'] = name
                
                

                return redirect(url_for('book_register'))

            else:
                flash('Incorrect password', 'danger')
                return render_template('donor_login.html', form=form)

        else:
            flash('Username not found', 'danger')
            # Close connection
            cur.close()
            return render_template('donor_login.html', form=form)
    return render_template('donor_login.html', form=form)


#pending with the book registration do it by today itself , create class for book_reg and @route(/donor_login/book_reg) write function

@app.route('/book_register',methods=['GET','POST'])
def book_register():
    if 'uid' in session:
        d_id=session['uid']
    if request.method == 'POST':
        bname = request.form.get('bname')
        author = request.form['author']
        description = request.form['description']
        category = request.form['category']
        file = request.files['picture']
           
        if bname and author and description and  category and file:
            pic = file.filename
            photo = pic.replace("'", "")
            picture = photo.replace(" ", "_")
            if picture.lower().endswith(('.png', '.jpg', '.jpeg')):
                save_photo = photos.save(file, folder=category)
                if save_photo:
                    # Create Cursor
                    cur = mysql.connection.cursor()
                    cur.execute("INSERT INTO books(d_id,bname,author,category,description,picture) VALUES(%s,%s,%s,%s,%s,%s)",
                                (d_id,bname,author,category,description,picture))
                    mysql.connection.commit()
                
                    flash('Book added successful', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Picture not save', 'danger')
                    return redirect(url_for('book_register'))
            else:
                flash('File not supported', 'danger')
                return redirect(url_for('book_register'))
        else:
            flash('Please fill up all form', 'danger')
            return redirect(url_for('book_register'))
    else:
        return render_template('add_books.html')


#Donor registration form
class DonorRegister(Form):
    name = StringField('', [validators.length(min=3, max=50)],
                       render_kw={'autofocus': True, 'placeholder': 'Full Name'})
    username = StringField('', [validators.length(min=3, max=25)], render_kw={'placeholder': 'Username'})
    email = EmailField('', [validators.DataRequired(), validators.Email(), validators.length(min=4, max=25)],
                       render_kw={'placeholder': 'Email'})
    password = PasswordField('', [validators.length(min=3)],
                             render_kw={'placeholder': 'Password'})
    mobile = StringField('', [validators.length(min=11, max=15)], render_kw={'placeholder': 'Mobile'})
    address = StringField('',[validators.length(min=5,max=30)],render_kw={'placeholder':'Address'}) 
   

@app.route('/donate',methods=['GET','POST'])    
def donate():
    form=DonorRegister(request.form)
    if request.method == 'POST' and form.validate():
        name=form.name.data
        email=form.email.data
        username=form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        mobile = form.mobile.data
        address=form.address.data



        #create cusror
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO donors(name, email, username, password, mobile,address) VALUES(%s, %s, %s, %s, %s,%s)",
                    (name, email, username, password, mobile,address))
         # Commit cursor
        mysql.connection.commit()

        # Close Connection
        cur.close()

        flash('Donor registration is successfull') 
        return redirect(url_for('index'))
    return render_template('donor_register.html', form=form)           

class MessageForm(Form):  # Create Message Form
    body = StringField('', [validators.length(min=1)], render_kw={'autofocus': True})



class OrderForm(Form):  # Create Order Form
    name = StringField('', [validators.length(min=1), validators.DataRequired()],
                       render_kw={'autofocus': True, 'placeholder': 'Full Name'})
    mobile_num = StringField('', [validators.length(min=1), validators.DataRequired()],
                             render_kw={'autofocus': True, 'placeholder': 'Mobile'})
    order_place = StringField('', [validators.length(min=1), validators.DataRequired()],
                              render_kw={'placeholder': 'Order Place'})
    area_pin = StringField('', [validators.length(min=1), validators.DataRequired()],
                              render_kw={'placeholder': 'Area Pin'})                          


@app.route('/cs', methods=['GET', 'POST'])
def cs():
    form = OrderForm(request.form)
    # Create cursor
    cur = mysql.connection.cursor()
    # Get message
    values = 'cs'
    cur.execute("SELECT * FROM books WHERE category=%s ORDER BY b_id ASC", (values,))
    books = cur.fetchall()
    # Close Connection
    cur.close()
    if request.method == 'POST' and form.validate():
        name = form.name.data
        mobile = form.mobile_num.data
        order_place = form.order_place.data
        area_pin = form.area_pin.data
        print(area_pin)
        pid = request.args['order']
        
        # Create Cursor
        curs = mysql.connection.cursor()
        if 'uid' in session:
            uid = session['uid']
            curs.execute("INSERT INTO orders(uid, pid, ofname, mobile, oplace, area_pin) "
                         "VALUES(%s, %s, %s, %s, %s, %s)",
                         (uid, pid, name, mobile, order_place, area_pin))
        else:
            curs.execute("INSERT INTO orders(pid, ofname, mobile, oplace, area_pin) "
                         "VALUES(%s, %s, %s, %s, %s)",
                         (pid, name, mobile, order_place, area_pin))
        # Commit cursor
        mysql.connection.commit()

        # Close Connection
        cur.close()

        flash('Order successful', 'success')
        return render_template('cs.html', cs=books, form=form)
    if 'view' in request.args:
        product_id = request.args['view']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM books WHERE b_id=%s", (product_id,))
        books = curso.fetchall()
        
        
        return render_template('view_product.html',cs=books)
    elif 'order' in request.args:
        product_id = request.args['order']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM books WHERE b_id=%s", (product_id,))
        books = curso.fetchall()
        
        return render_template('order_product.html', cs=books, form=form)
    return render_template('cs.html', cs=books, form=form)


@app.route('/ec', methods=['GET', 'POST'])
def ec():
    form = OrderForm(request.form)
    # Create cursor
    cur = mysql.connection.cursor()
    # Get message
    values = 'ec'
    cur.execute("SELECT * FROM books WHERE category=%s ORDER BY b_id ASC", (values,))
    books = cur.fetchall()
    # Close Connection
    cur.close()

    if request.method == 'POST' and form.validate():
        name = form.name.data
        mobile = form.mobile_num.data
        order_place = form.order_place.data
        area_pin = form.area_pin.data
        print(area_pin)
        pid = request.args['order']
        # Create Cursor
        curs = mysql.connection.cursor()
        if 'uid' in session:
            uid = session['uid']
            curs.execute("INSERT INTO orders(uid, pid, ofname, mobile, oplace, area_pin) "
                         "VALUES(%s, %s, %s, %s, %s, %s)",
                         (uid, pid, name, mobile, order_place, area_pin))
        else:
            curs.execute("INSERT INTO orders(pid, ofname, mobile, oplace, area_pin) "
                         "VALUES(%s, %s, %s, %s, %s)",
                         (pid, name, mobile, order_place, area_pin))
        # Commit cursor
        mysql.connection.commit()
        # Close Connection
        cur.close()

        flash('Order successful', 'success')
        return render_template('ec.html', ec=books, form=form)
    if 'view' in request.args:
        product_id = request.args['view']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM books WHERE b_id=%s", (product_id,))
        books = curso.fetchall()
        return render_template('view_product.html', cs=books)
    elif 'order' in request.args:
        product_id = request.args['order']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM books WHERE b_id=%s", (product_id,))
        books = curso.fetchall()
       
        return render_template('order_product.html', cs=books, form=form)
    return render_template('ec.html', ec=books, form=form)


@app.route('/me', methods=['GET', 'POST'])
def me():
    form = OrderForm(request.form)
    # Create cursor
    cur = mysql.connection.cursor()
    # Get message
    values = 'me'
    cur.execute("SELECT * FROM books WHERE category=%s ORDER BY b_id ASC", (values,))
    books = cur.fetchall()
    # Close Connection
    cur.close()

    if request.method == 'POST' and form.validate():
        name = form.name.data
        mobile = form.mobile_num.data
        order_place = form.order_place.data
        area_pin = form.area_pin.data
        print(area_pin)
        pid = request.args['order']
        # Create Cursor
        curs = mysql.connection.cursor()
        if 'uid' in session:
            uid = session['uid']
            curs.execute("INSERT INTO orders(uid, pid, ofname, mobile, oplace, area_pin) "
                         "VALUES(%s, %s, %s, %s, %s, %s)",
                         (uid, pid, name, mobile, order_place, area_pin))
        else:
            curs.execute("INSERT INTO orders(pid, ofname, mobile, oplace, area_pin) "
                         "VALUES(%s, %s, %s, %s, %s)",
                         (pid, name, mobile, order_place, area_pin))
        # Commit cursor
        mysql.connection.commit()

        # Close Connection
        cur.close()

        flash('Order successful', 'success')
        return render_template('me.html', me=books, form=form)
    if 'view' in request.args:
        product_id = request.args['view']
        
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM books WHERE b_id=%s", (product_id,))
        books = curso.fetchall()
        return render_template('view_product.html', cs=books)
    elif 'order' in request.args:
        product_id = request.args['order']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM books WHERE b_id=%s", (product_id,))
        books = curso.fetchall()
       
        return render_template('order_product.html', cs=books, form=form)
    return render_template('me.html', me=books, form=form)


@app.route('/cv', methods=['GET', 'POST'])
def cv():
    form = OrderForm(request.form)
    # Create cursor
    cur = mysql.connection.cursor()
    # Get message
    values = 'cv'
    cur.execute("SELECT * FROM books WHERE category=%s ORDER BY b_id ASC", (values,))
    books = cur.fetchall()
    # Close Connection
    cur.close()

    if request.method == 'POST' and form.validate():
        name = form.name.data
        mobile = form.mobile_num.data
        order_place = form.order_place.data
        area_pin = form.area_pin.data
        print(area_pin)
        pid = request.args['order']
        # Create Cursor
        curs = mysql.connection.cursor()
        if 'uid' in session:
            uid = session['uid']
            curs.execute("INSERT INTO orders(uid, pid, ofname, mobile, oplace, area_pin) "
                         "VALUES(%s, %s, %s, %s, %s, %s)",
                         (uid, pid, name, mobile, order_place, area_pin))
        else:
            curs.execute("INSERT INTO orders(pid, ofname, mobile, oplace, area_pin) "
                         "VALUES(%s, %s, %s, %s, %s)",
                         (pid, name, mobile, order_place, area_pin))
        # Commit cursor
        mysql.connection.commit()
        # Close Connection
        cur.close()

        flash('Order successful', 'success')
        return render_template('cv.html', cv=books, form=form)
    if 'view' in request.args:
        product_id = request.args['view']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM books WHERE b_id=%s", (product_id,))
        books = curso.fetchall()
        return render_template('view_product.html',cs=books)
    elif 'order' in request.args:
        product_id = request.args['order']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM products WHERE id=%s", (product_id,))
        books = curso.fetchall()
        
        return render_template('order_product.html',cs=books, form=form)
    return render_template('cv.html', cv=books, form=form)


@app.route('/admin_login', methods=['GET', 'POST'])
@not_admin_logged_in
def admin_login():
    if request.method == 'POST':
        # GEt user form
        username = request.form['email']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM admin WHERE email=%s", [username])

        if result > 0:
            # Get stored value
            data = cur.fetchone()
            password = data['password']
            uid = data['id']
            name = data['firstName']

            # Compare password
            if password_candidate==password:
                # passed
                session['admin_logged_in'] = True
                session['admin_uid'] = uid
                session['admin_name'] = name

                return redirect(url_for('admin'))

            else:
                flash('Incorrect password', 'danger')
                return render_template('pages/login.html')

        else:
            flash('Username not found', 'danger')
            # Close connection
            cur.close()
            return render_template('pages/login.html')
    return render_template('pages/login.html')


@app.route('/admin_out')
def admin_logout():
    if 'admin_logged_in' in session:
        session.clear()
        return redirect(url_for('index'))
    return redirect(url_for('index'))


@app.route('/admin')
@is_admin_logged_in
def admin():
    curso = mysql.connection.cursor()
    num_books = curso.execute("SELECT A.b_id,B.name,A.bname,A.category,A.author,A.description,A.date,A.picture FROM books A,donors B  WHERE A.d_id=B.d_id")
    result = curso.fetchall()
    
    order_rows = curso.execute("SELECT * FROM orders")
    users_rows = curso.execute("SELECT * FROM users")
    donors_rows=curso.execute("SELECT * FROM donors")
    return render_template('pages/index.html', books=result, row=num_books, order_rows=order_rows,
                           users_rows=users_rows,donors_rows=donors_rows)

#Deleting the orders
@app.route('/delete_book',methods=['POST','GET'])
@is_admin_logged_in
def delete_order():
    if 'id' in request.args:
        delete_id=request.args['id']
        cur=mysql.connection.cursor()
        res=cur.execute("DELETE FROM books WHERE b_id=%s",(delete_id,))
        print(res,"Deleted from book table")
        mysql.connection.commit()
        curso = mysql.connection.cursor()
        num_books = curso.execute("SELECT * FROM books")
        result = curso.fetchall()
        order_rows = curso.execute("SELECT * FROM orders")
        users_rows = curso.execute("SELECT * FROM users")
        donors_rows=cur.execute("SELECT * FROM donors")
        return render_template('pages/index.html', books=result, row=num_books, order_rows=order_rows,
                           users_rows=users_rows,donors_rows=donors_rows)


@app.route('/orders')
@is_admin_logged_in
def orders():
    curso = mysql.connection.cursor()
    num_rows = curso.execute("SELECT * FROM books")
    order_rows = curso.execute("SELECT * FROM orders")
    result = curso.fetchall()
    users_rows = curso.execute("SELECT * FROM users")
    donors_rows=curso.execute("SELECT * FROM donors")
    return render_template('pages/all_orders.html', result=result, row=num_rows, order_rows=order_rows,
                           users_rows=users_rows,donors_rows=donors_rows)


#Donors list
@app.route('/donors_list')
@is_admin_logged_in
def donors_list():
    cur=mysql.connection.cursor()
    num_rows=cur.execute("SELECT * FROM books")
    order_rows=cur.execute("SELECT * FROM orders")
    users_rows=cur.execute("SELECT * FROM users")
    donors_rows=cur.execute("SELECT * FROM donors")
    result=cur.fetchall()
    return render_template('pages/all_donors.html',donors=result,row=num_rows,order_rows=order_rows,
                          users_rows=users_rows,donors_rows=donors_rows)


#Pending_Deleting donors;
#remvoed delete button from all_donors
@app.route('/delete_donor')
@is_admin_logged_in
def delete_donor():
    if 'id' in request.args:
        delete_id=request.args['id']
        cur=mysql.connection.cursor()
        print("Here is delete id",delete_id)
        res=cur.execute("SELECT * FROM donors WHERE d_id=%s",(delete_id,))
        print(res,"Deleted from donor table")
        curso = mysql.connection.cursor()
        num_rows = curso.execute("SELECT * FROM books")
        order_rows = curso.execute("SELECT * FROM orders")
        users_rows = curso.execute("SELECT * FROM users")
        donors_rows=cur.execute("SELECT * FROM donors")
        result = curso.fetchall()
        return redirect(url_for('admin'))


    

@app.route('/users')
@is_admin_logged_in
def users():
    curso = mysql.connection.cursor()
    num_rows = curso.execute("SELECT * FROM books")
    order_rows = curso.execute("SELECT * FROM orders")
    users_rows = curso.execute("SELECT * FROM users")
    result = curso.fetchall()
    donors_rows=curso.execute("SELECT * FROM donors")
    return render_template('pages/all_users.html', result=result, row=num_rows, order_rows=order_rows,
                           users_rows=users_rows,donors_rows=donors_rows)

#Editing the books details
@app.route('/edit_books',methods=['POST','GET'])
@is_admin_logged_in
def edit_books():
    if 'id' in request.args:
        book_id=request.args['id']
        cur=mysql.connection.cursor()
        res=cur.execute('SELECT * FROM books WHERE b_id=%s',(book_id,))
        books=cur.fetchall()
        for i in books:
            print(i)
        if res:
            if request.method == 'POST':
                bname = request.form.get('bname')
                author = request.form['author']
                category = request.form['category']
                description = request.form['description']
                
                
                
                if bname and author and description and  category:
                          # Create Cursor
                    cur = mysql.connection.cursor()
                    cur.execute("UPDATE books SET bname=%s,author=%s,category=%s,description=%s WHERE b_id=%s",
                                        (bname,author,category,description,book_id))
                    mysql.connection.commit()
                        
                    flash('Book Updated successful', 'success')
                    return redirect(url_for('admin'))
                        
                else:
                    flash('Please fill up all form', 'danger')
                    return redirect(url_for('edit_books'))
            else:
                return render_template('pages/edit_books.html',books=books)





@app.route('/profile')
@is_logged_in
def profile():
    if 'user' in request.args:
        q = request.args['user']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM users WHERE id=%s", (q,))
        result = curso.fetchone()
        if result:
            if result['id'] == session['uid']:
                curso.execute("SELECT * FROM orders WHERE uid=%s ORDER BY id ASC", (session['uid'],))
                res = curso.fetchall()
                return render_template('profile.html', result=res)
            else:
                flash('Unauthorised', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Unauthorised! Please login', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Unauthorised', 'danger')
        return redirect(url_for('login'))


class UpdateRegisterForm(Form):
    name = StringField('Full Name', [validators.length(min=3, max=50)],
                       render_kw={'autofocus': True, 'placeholder': 'Full Name'})
    email = EmailField('Email', [validators.DataRequired(), validators.Email(), validators.length(min=4, max=25)],
                       render_kw={'placeholder': 'Email'})
    password = PasswordField('Password', [validators.length(min=3)],
                             render_kw={'placeholder': 'Password'})
    mobile = StringField('Mobile', [validators.length(min=11, max=15)], render_kw={'placeholder': 'Mobile'})


@app.route('/settings', methods=['POST', 'GET'])
@is_logged_in
def settings():
    form = UpdateRegisterForm(request.form)
    if 'user' in request.args:
        q = request.args['user']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM users WHERE id=%s", (q,))
        result = curso.fetchone()
        if result:
            if result['id'] == session['uid']:
                if request.method == 'POST' and form.validate():
                    name = form.name.data
                    email = form.email.data
                    password = sha256_crypt.encrypt(str(form.password.data))
                    mobile = form.mobile.data

                    # Create Cursor
                    cur = mysql.connection.cursor()
                    exe = cur.execute("UPDATE users SET name=%s, email=%s, password=%s, mobile=%s WHERE id=%s",
                                      (name, email, password, mobile, q))
                    if exe:
                        flash('Profile updated', 'success')
                        return render_template('user_settings.html', result=result, form=form)
                    else:
                        flash('Profile not updated', 'danger')
                return render_template('user_settings.html', result=result, form=form)
            else:
                flash('Unauthorised', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Unauthorised! Please login', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Unauthorised', 'danger')
        return redirect(url_for('login'))




if __name__ == '__main__':
    app.run(debug=True)
