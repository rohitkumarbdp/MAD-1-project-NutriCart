import os
from flask import Flask
from flask import render_template
from flask import request, redirect
from flask_login import UserMixin
from flask_sqlalchemy import  SQLAlchemy
current_dir = os.path.abspath(os.path.dirname(__file__))
app  = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= "sqlite:///"+os.path.join(current_dir, "grocery.db")

db = SQLAlchemy()
db.init_app(app)
app.app_context().push()


class User(db.Model,UserMixin ):
    __tablename__= "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30),nullable=False)
    email = db.Column(db.String, unique= True, nullable=False)
    address = db.Column(db.String(), nullable=False)
    pincode = db.Column(db.String(6), nullable=False)
    phone = db.Column(db.String(10))
    password = db.Column(db.String(16), nullable=False)

class Category(db.Model, UserMixin):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), unique= True, nullable= False )
    
class Product(db.Model, UserMixin):
    __tablename__="product"
    id= db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(50), unique=True, nullable= False)
    rate = db.Column(db.Float,nullable = False)
    unit = db.Column(db.String(20), nullable = False)
    manufacture= db.Column(db.String(100))
    expiry =db.Column(db.String(100))
    stock_quantity = db.Column(db.Integer,nullable = False)
    category_id = db.Column(db.Integer ,db.ForeignKey('category.id'), nullable=False)
class Cart(db.Model, UserMixin):
    __tablename__="cart"
    id= db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer , db.ForeignKey('product.id'), nullable =False)
    category_id= db.Column(db.Integer, db.ForeignKey('category.id'), nullable = False)
    product_quantity = db.Column(db.Integer, nullable = False)



def check_if_user_already_exist(column_name, value):
    user = User.query.filter(getattr(User, column_name) == value).first()
    return user is not None
    

@app.route('/',methods =["GET", "POST"])
def home():
    return render_template('home.html')

@app.route('/submit_form', methods=['GET','POST'])
def submit_form():
    form_type = request.form['form_type']
    if form_type=='user':
        user = User.query.filter_by(email=request.form['user_email']).first()
        if user is None:
            return '<center><h3>Account does not exist. Please register first!</h3></center>'
        elif user.password == request.form['user_password']:
            user_id =user.id
            
            return redirect('/user_dashboard/'+str(user_id))
        else:
            return '<h3><center> Incorrect Password. Please check!</center></h3>'
    elif form_type=='admin':
        if request.form['admin_email']=='rk@gmail.com' and request.form['admin_password']=='11':
            return redirect('/admin_dashboard')
        else: return '<h3><center>Either email or password is incorrect. Please check and try again!</center> <h3>'


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method =='POST':
        first_name= request.form['first_name']
        temp_email= request.form['user_email']
        address= request.form['address']
        pincode= request.form['pincode']
        temp_phone= request.form['phone'] 
        password= request.form['password']
        user = User(first_name= first_name, email= temp_email, address= address, pincode= pincode, phone= temp_phone, password= password )
        if check_if_user_already_exist('email', temp_email):
            return '<h1>Email address already exists, choose a different one.<h1>'
        elif check_if_user_already_exist('phone', temp_phone):
            return '<h1>Phone number already registered, choose a different one.<h1>'
            
        else:
            db.session.add(user)
            db.session.commit()
            return redirect('/')
    return render_template('register.html')


@app.route('/admin_dashboard', methods=['GET','POST'])
def admin_dashboard():
    allCategory = Category.query.all()
    allProducts = Product.query.all()

    return render_template('admin_dashboard.html', allCategory=allCategory, allProducts= allProducts)

def check_if_cat_already_exist(column_name, value):
    cat = Category.query.filter(getattr(Category, column_name) == value).first()
    return cat is not None

@app.route('/add_category', methods=['GET','POST'])
def add_category():
    if request.method=='POST':
        temp_cat = request.form['new_category']
        category =Category(category_name=temp_cat)
        if check_if_cat_already_exist('category_name', temp_cat):
            return '<h3><center>Category already exist</center><h3>'
        db.session.add(category)
        db.session.commit()
        return redirect('/admin_dashboard')
    return render_template('add_category.html')

def check_if_product_already_exist(column_name, value):
    prod = Product.query.filter(getattr(Product, column_name) == value).first()
    return prod is not None
@app.route('/add_product/<int:cat_id>',methods=['GET','POST'])
def add_product(cat_id):
    category = Category.query.filter_by(id=cat_id).first()
    if request.method=='POST':
        temp_prod = request.form['product_name']
        rate= request.form['rate']
        unit = request.form['unit']
        manufacture = request.form['manufacture']
        expiry =request.form['expiry']
        stock_quantity =request.form['stock_quantity']
        product = Product(product_name=temp_prod,rate=rate, unit=unit,  manufacture=manufacture,expiry=expiry,
                          stock_quantity=stock_quantity,category_id=cat_id)
        if check_if_product_already_exist('product_name',temp_prod ):
            return '<h3><center>This product already exist. Either add a different product or update the existing.</center><h3>'
        else:
            db.session.add(product)
            db.session.commit()
            return redirect('/see_product/admin/-1/'+str(cat_id))

    return render_template('/add_product.html',category=category)


@app.route('/delete_category/<int:cat_id>')
def delete_cat(cat_id):
    products =  Product.query.filter_by(category_id=cat_id).all()
    for prod in products:
        delete_product(prod.id)
    category =  Category.query.filter_by(id=cat_id).first()
    db.session.delete(category)
    db.session.commit()
    return redirect('/admin_dashboard')


@app.route('/see_product/<user_type>/<user_id>/<int:cat_id>')
def see_product(user_type, user_id, cat_id):
    view_type = request.args.get('user_type')
    

    allProduct = Product.query.filter_by(category_id=cat_id).all()
    category = Category.query.filter_by(id=cat_id).first()
    if view_type =='admin_view':
        return render_template('see_product.html',user_type=user_type, allProduct=allProduct, category=category)
    else:
        user = User.query.filter_by(id=int(user_id)).first()
        return render_template('see_product.html', user= user, user_type=user_type,allProduct=allProduct, category=category )

@app.route('/delete_product/<int:prod_id>')
def delete_product(prod_id):
    product = Product.query.filter_by(id=prod_id).first()
    cat_id = product.category_id
    db.session.delete(product)
    db.session.commit()
    return redirect('/see_product/admin/-1/'+str(cat_id))

@app.route('/edit_product/<int:prod_id>', methods=['GET','POST'])
def edit_product(prod_id):
    if request.method =='POST':
        temp_prod = request.form['product_name']
        rate= request.form['rate']
        unit = request.form['unit']
        manufacture = request.form['manufacture']
        expiry =request.form['expiry']
        stock_quantity =request.form['stock_quantity']
        product = Product.query.filter_by(id=prod_id).first()
        
        product.name= temp_prod
        product.rate= rate
        product.unit = unit
        product.manufacture = manufacture
        product.expiry =  expiry
        product.stock_quantity = stock_quantity

        db.session.add(product)
        db.session.commit()
        return redirect('/see_product/admin/-1/'+str(product.category_id))
    product = Product.query.filter_by(id= prod_id).first()
    return render_template('edit_product.html', product=product)



@app.route('/user_dashboard/<int:user_id>', methods=['GET','POST'])
def user_dashboard(user_id):
    user = User.query.filter_by(id=user_id).first()
    allProducts = Product.query.all()
    allCategory = Category.query.all()
    return render_template('user_dashboard.html',user = user,  allProducts=allProducts, allCategory=allCategory)




def check_if_product_already_exist_in_cart( user_id, product_id):
    prod = Cart.query.filter(Cart.user_id==user_id, Cart.product_id==product_id).first()
    return prod is not None

@app.route('/add_to_cart/<int:user_id>/<int:cat_id>/<int:product_id>')
def add_to_cart(user_id, cat_id, product_id):
    if check_if_product_already_exist_in_cart(user_id, product_id):
        return redirect(f'/see_product/user/{user_id}/{cat_id}')
    prod = Cart(user_id=user_id, product_id=product_id, category_id=cat_id, product_quantity=1)
    db.session.add(prod)
    db.session.commit()

    return redirect(f'/see_product/user/{user_id}/{cat_id}')

##################################################################
@app.route('/cart/<int:user_id>')
def cart(user_id):
    cart_items = Cart.query.filter_by(user_id= user_id).all()
    user = User.query.filter_by(id =user_id).first()
    
    allProducts = Product.query.all()
    return render_template('cart.html', cart_items = cart_items, user= user, allProducts =allProducts)

def get_price(product_id):
    product  = Product.query.filter_by(id = int(product_id)).first()
    return product.rate
app.jinja_env.globals.update(get_price=get_price)

def get_product_name(product_id):
    product =Product.query.filter_by(id = int(product_id)).first()

    return product.product_name

app.jinja_env.globals.update(get_product_name=get_product_name)

def get_product_unit(product_id):
    product =Product.query.filter_by(id = int(product_id)).first()
    return product.unit
app.jinja_env.globals.update(get_product_unit=get_product_unit)

def get_total_amount(user_id):
    cart_items= Cart.query.filter_by(user_id= user_id).all()
    total_amount = 0
    for item in cart_items:
        subtotal = get_price(item.product_id) * item.product_quantity
        total_amount+= subtotal
    return total_amount
app.jinja_env.globals.update(get_total_amount=get_total_amount)



@app.route('/update_cart/<int:user_id>', methods=['POST'])
def update_cart(user_id):
    
    items = Cart.query.filter_by(user_id = user_id).all()
    for item in items:
        quantity_key = f'quantity_{item.id}'
        new_quantity = int(request.form.get(quantity_key, 0))
        cart_item = Cart.query.filter_by(id = item.id).first()
        cart_item.product_quantity = new_quantity
        db.session.commit()
    return redirect('/cart/'+str(user_id))

@app.route('/delete_from_cart/<int:user_id>/<int:cart_id>')
def delete_from_cart(user_id,cart_id):
    item = Cart.query.filter_by(id=cart_id).first()
    db.session.delete(item)
    db.session.commit()
    return redirect('/cart/'+str(user_id))

@app.route('/cart/<int:user_id>/payment')
def payment(user_id):
    cart = Cart.query.filter_by(user_id=user_id).all()
    flag = True
    for item in cart:
        prod = Product.query.filter_by(id=item.product_id).first()
        if prod.stock_quantity - item.product_quantity >= 0:
            prod.stock_quantity -= item.product_quantity
            db.session.delete(item)
        else: 
            flag = False
            return f'<h2><center>{prod.product_name} Quantity is more than available stock</center></h2>'
    if flag:
        db.session.commit()
    return render_template('payment.html', user_id =user_id)

@app.route('/profile/<int:user_id>')
def profile(user_id):
    user= User.query.filter_by(id=user_id).first()
    return render_template('profile.html', user=user)

@app.route('/edit_profile/<int:user_id>', methods=['GET','POST'])
def edit_profile(user_id):
        if request.method=='POST':
            first_name = request.form['first_name']
            temp_email = request.form['email']
            temp_phone = request.form['phone']
            address = request.form['address']
            pincode= request.form['pincode']
            password = request.form['password']
            user= User.query.filter_by(id=user_id).first()

            user.first_name = first_name
            user.email= temp_email 
            user.phone= temp_phone 
            user.address= address 
            user.pincode= pincode 
            user.password= password
            db.session.add(user)
            db.session.commit()
            return redirect('/profile/'+str(user.id))
        user= User.query.filter_by(id=user_id).first()
        return render_template('edit_profile.html', user=user)


@app.route('/searched_product/<int:user_id>', methods=['GET','POST'])
def searched_products(user_id):
    query = request.form['query']
    user= User.query.filter_by(id=user_id).first()
    AllCat = Category.query.all()
    AllProd = Product.query.all()

    for cat in AllCat:
        if cat.category_name.startswith(str(query)):
            prods =  Product.query.filter_by(category_id = cat.id).all()
            return render_template('searched_products.html', prods = prods, user= user)
    prods = []
    for prod in AllProd :
        if prod.product_name.startswith(query):
            prods.append(prod)
    return render_template('searched_products.html', prods=prods, user= user)



            




if __name__ == "__main__":
    app.run(debug=True)
