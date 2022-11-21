from flask import Flask, render_template, flash, request, redirect, url_for
from datetime import datetime 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash 
from datetime import date
from webforms import LoginForm, PostForm, UserForm, PasswordForm, NamerForm, SearchForm
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PostForm, UserForm, PasswordForm, NamerForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen


# Cria a instância
app = Flask(__name__)
# Add CKEditor
ckeditor = CKEditor(app)
# Add Database
# SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# Secret Key!
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"
# Inicia db

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

# Navbar
@app.context_processor
def base():
	form = SearchForm()
	return dict(form=form)

# Cria admin
@app.route('/admin')
@login_required
def admin():
	id = current_user.id
	if id == 1:
		return render_template("admin.html")
	else:
		flash("Você deve ser administrador para acessar essa página")
		return redirect(url_for('dashboard'))



@app.route('/corridas')
def corridas():
	site = "https://www.esportividade.com.br/corrida-de-rua/"
	hdr = {'User-Agent': 'Mozilla/5.0'}
	req = Request(site, headers=hdr)
	page = urlopen(req)
	soup = BeautifulSoup(page)
	tag_list = soup.find("div", {"id": "lista_eventos"})

	'''site2 = "https://www.ativo.com/calendario"
	hdr2 = {'User-Agent': 'Mozilla/5.0'}
	req2 = Request(site2, headers=hdr2)
	page2 = urlopen(req2)
	soup2 = BeautifulSoup(page2)
	ativo_calendario = soup2.find("div", {"class": "col list-events"})'''
	return render_template('corridas.html', data=tag_list)

@app.route('/equipamentos_publicos')
def equipamentos_publicos():
	return render_template('equipamentos_publicos.html')

# Cria função busca
@app.route('/search', methods=["POST"])
def search():
	form = SearchForm()
	posts = Posts.query
	if form.validate_on_submit():
		# Pega os dados dos inputs
		post.searched = form.searched.data
		# Query o db
		posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
		posts = posts.order_by(Posts.title).all()

		return render_template("search.html",
		 form=form,
		 searched = post.searched,
		 posts = posts)
# Cria pagina login
@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(username=form.username.data).first()
		if user:
			# dupla verificacao da senha
			if check_password_hash(user.password_hash, form.password.data):
				login_user(user)
				flash("Login efetuado com sucesso")
				return redirect(url_for('dashboard'))
			else:
				flash("Senha incorreta!")
		else:
			flash("Usuário inválido")


	return render_template('login.html', form=form)

# Cria pagina logout
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
	logout_user()
	flash("Você saiu!")
	return redirect(url_for('login'))

# cria dashboard (painel do usuario)
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
	form = UserForm()
	id = current_user.id
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.username = request.form['username']
		name_to_update.about_author = request.form['about_author']
		

		# verifica se tem foto de perfil
		if request.files['profile_pic']:
			name_to_update.profile_pic = request.files['profile_pic']

			# pega o nome do arquivo
			pic_filename = secure_filename(name_to_update.profile_pic.filename)
			# Seta UUID
			pic_name = str(uuid.uuid1()) + "_" + pic_filename
			# Salva imagem
			saver = request.files['profile_pic']
			

			# muda para uma string para salvar no db
			name_to_update.profile_pic = pic_name
			try:
				db.session.commit()
				saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
				flash("Usuário atualizado com sucesso!")
				return render_template("dashboard.html", 
					form=form,
					name_to_update = name_to_update)
			except:
				flash("Erro! Tente novamente mais tarde")
				return render_template("dashboard.html", 
					form=form,
					name_to_update = name_to_update)
		else:
			db.session.commit()
			flash("Usuário atualizado com sucesso")
			return render_template("dashboard.html", 
				form=form, 
				name_to_update = name_to_update)
	else:
		return render_template("dashboard.html", 
				form=form,
				name_to_update = name_to_update,
				id = id)

	return render_template('dashboard.html')






@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
	post_to_delete = Posts.query.get_or_404(id)
	id = current_user.id
	if id == post_to_delete.poster.id or id == 14:
		try:
			db.session.delete(post_to_delete)
			db.session.commit()

			# Retorna msg
			flash("Evento foi apagado")

			# pega todos os anuncios/eventos/posts do db
			posts = Posts.query.order_by(Posts.data_evento)
			return render_template("posts.html", posts=posts)


		except:
			# retorna msg de erro
			flash("Opa! Tivemos um problema ao excluir esse evento!")

			# pega todos os anuncios/eventos/posts do db
			posts = Posts.query.order_by(Posts.data_evento)
			return render_template("posts.html", posts=posts)
	else:
		# Retorna msg
		flash("Você não está autorizado a excluir esse evento!")

		# pega todos os anuncios/eventos/posts do db
		posts = Posts.query.order_by(Posts.data_evento)
		return render_template("posts.html", posts=posts)

@app.route('/posts')
def posts():
	# pega todos os anuncios/eventos/posts do db
	posts = Posts.query.order_by(Posts.data_evento.desc())
	return render_template("posts.html", posts=posts)

@app.route('/posts/<int:id>')
def post(id):
	post = Posts.query.get_or_404(id)
	return render_template('post.html', post=post)

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
	post = Posts.query.get_or_404(id)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		post.endereco = form.endereco.data
		post.bairro = form.bairro.data
		post.data_evento = form.data_evento.data
		post.hora_evento = form.hora_evento.data

		# atualiza db
		db.session.add(post)
		db.session.commit()
		flash("Evento foi atualizado com sucesso!")
		return redirect(url_for('post', id=post.id))
	
	if current_user.id == post.poster_id or current_user.id == 14:
		form.title.data = post.title
		form.content.data = post.content
		form.endereco.data = post.endereco
		form.bairro.data = post.bairro
		form.data_evento.data = post.data_evento
		form.hora_evento.data = post.hora_evento
		return render_template('edit_post.html', form=form)
	else:
		flash("Você não está autorizado a editar esse evento!")
		posts = Posts.query.order_by(Posts.data_evento)
		return render_template("posts.html", posts=posts)



# adiciona post
@app.route('/add-post', methods=['GET', 'POST'])
#@login_required
def add_post():
	form = PostForm()

	if form.validate_on_submit():
		poster = current_user.id
		post = Posts(title=form.title.data, content=form.content.data, poster_id=poster, endereco=form.endereco.data,
					 bairro=form.bairro.data, data_evento=form.data_evento.data)
		# limpa formulario
		form.title.data = ''
		form.content.data = ''
		form.endereco.data = ''
		form.bairro.data = ''
		form.data_evento.data = ''
		# Adiciona evento pro db
		db.session.add(post)
		db.session.commit()

		# Retorna msg de sucesso
		flash("Evento anunciado com sucesso!")

	# Redireciona pra pagina de post
	return render_template("add_post.html", form=form)


'''
# Json Thing
@app.route('/date')
def get_current_date():
	favorite_pizza = {
		"John": "Pepperoni",
		"Mary": "Cheese",
		"Tim": "Mushroom"
	}
	return favorite_pizza
	#return {"Date": date.today()}
'''





@app.route('/delete/<int:id>')
@login_required
def delete(id):
	# verifica se ta logado no id que está solicitando a exclusão
	if id == current_user.id:
		user_to_delete = Users.query.get_or_404(id)
		name = None
		form = UserForm()

		try:
			db.session.delete(user_to_delete)
			db.session.commit()
			flash("Usuário apagado com sucesso!")

			our_users = Users.query.order_by(Users.date_added)
			return render_template("add_user.html", 
			form=form,
			name=name,
			our_users=our_users)

		except:
			flash("Opa! Tivemos um problema ao excluir esse usuário!")
			return render_template("add_user.html", 
			form=form, name=name,our_users=our_users)
	else:
		flash("Você não pode excluir esse usuário!")
		return redirect(url_for('dashboard'))

# atualiza db
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
	form = UserForm()
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.username = request.form['username']
		try:
			db.session.commit()
			flash("Usuário atualizado com sucesso!")
			return render_template("update.html", 
				form=form,
				name_to_update = name_to_update, id=id)
		except:
			flash("Erro! Tente novamente mais tarde")
			return render_template("update.html", 
				form=form,
				name_to_update = name_to_update,
				id=id)
	else:
		return render_template("update.html", 
				form=form,
				name_to_update = name_to_update,
				id = id)




# FILTERS!!!
#safe
#capitalize
#lower
#upper
#title
#trim
#striptags


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
	name = None
	form = UserForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None:
			# Codifica a senha
			hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
			user = Users(username=form.username.data, name=form.name.data, email=form.email.data,  password_hash=hashed_pw)
			db.session.add(user)
			db.session.commit()
		name = form.name.data
		form.name.data = ''
		form.username.data = ''
		form.email.data = ''
		form.password_hash.data = ''

		flash("Usuário adicionado com sucesso!")
	our_users = Users.query.order_by(Users.date_added)
	return render_template("add_user.html", 
		form=form,
		name=name,
		our_users=our_users)

# Cria pagina raiz
@app.route('/')
def index():
	first_name = "John"
	stuff = "This is bold text"

	favorite_pizza = ["Pepperoni", "Cheese", "Mushrooms", 41]
	return render_template("index.html", 
		first_name=first_name,
		stuff=stuff,
		favorite_pizza = favorite_pizza)

# localhost:5000/user/John
@app.route('/user/<name>')

def user(name):
	return render_template("user.html", user_name=name)

# Cria paginas de erro customizadas

# URL invalida
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

# erro interno
@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500

# Cria pagina de teste de senha
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
	email = None
	password = None
	pw_to_check = None
	passed = None
	form = PasswordForm()


	# Validate Form
	if form.validate_on_submit():
		email = form.email.data
		password = form.password_hash.data
		# Clear the form
		form.email.data = ''
		form.password_hash.data = ''

		# Lookup User By Email Address
		pw_to_check = Users.query.filter_by(email=email).first()
		
		# Check Hashed Password
		passed = check_password_hash(pw_to_check.password_hash, password)

	return render_template("test_pw.html", 
		email = email,
		password = password,
		pw_to_check = pw_to_check,
		passed = passed,
		form = form)


# Cria pagina nome
@app.route('/name', methods=['GET', 'POST'])
def name():
	name = None
	form = NamerForm()
	# Validate Form
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
		flash("Sucesso!")
		
	return render_template("name.html", 
		name = name,
		form = form)




# Create a Blog Post model
class Posts(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(255))
	content = db.Column(db.Text)
	#author = db.Column(db.String(255))
	date_posted = db.Column(db.DateTime, default=datetime.utcnow)
	#slug = db.Column(db.String(255))

	#add coisas relacionadas aos eventos
	endereco = db.Column(db.String(255))
	bairro = db.Column(db.String(255))
	data_evento = db.Column(db.DateTime)
	hora_evento = db.Column(db.String(8))

	# Foreign Key To Link Users (refer to primary key of the user)
	poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

# Create Model
class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), nullable=False, unique=True)
	name = db.Column(db.String(200), nullable=False)
	email = db.Column(db.String(120), nullable=False, unique=True)
	#favorite_color = db.Column(db.String(120))
	about_author = db.Column(db.Text(), nullable=True)
	date_added = db.Column(db.DateTime, default=datetime.utcnow)
	profile_pic = db.Column(db.String(), nullable=True)

	# Do some password stuff!
	password_hash = db.Column(db.String(128))
	# User Can Have Many Posts 
	posts = db.relationship('Posts', backref='poster')


	@property
	def password(self):
		raise AttributeError('Senha inválida')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	# Create A String
	def __repr__(self):
		return '<Name %r>' % self.name

