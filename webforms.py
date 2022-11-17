from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField, DateField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField

# Create A Search Form
class SearchForm(FlaskForm):
	searched = StringField("Pesquisar", validators=[DataRequired()])
	submit = SubmitField("Ok")


# Create Login Form
class LoginForm(FlaskForm):
	username = StringField("Usuário", validators=[DataRequired()])
	password = PasswordField("Senha", validators=[DataRequired()])
	submit = SubmitField("Ok")


# Create a Posts Form
class PostForm(FlaskForm):
	title = StringField("Título", validators=[DataRequired()])
	#content = StringField("Content", validators=[DataRequired()], widget=TextArea())

	endereco = StringField("Endereço", validators=[DataRequired()])
	bairro = StringField("Bairro", validators=[DataRequired()])
	data_evento = DateField("Data do evento (dd/mm/aaaa)", format='%d/%m/%Y')
	hora_evento = StringField("Hora do evento (HH:MM)", validators=[DataRequired()] )
	content = CKEditorField("Conteúdo", validators=[DataRequired()])
	#author = StringField("Author")
	#slug = StringField("AutorURL", validators=[DataRequired()])
	submit = SubmitField("Ok")

# Create a Form Class
class UserForm(FlaskForm):
	name = StringField("Nome", validators=[DataRequired()])
	username = StringField("Usuário", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired()])
	#favorite_color = StringField("Cor Favorita")
	about_author = TextAreaField("Sobre Autor")
	password_hash = PasswordField('Senha', validators=[DataRequired(), EqualTo('password_hash2', message='As senhas têm que ser iguais!')])
	password_hash2 = PasswordField('Confirmar Senha', validators=[DataRequired()])
	profile_pic = FileField("Foto de Perfil")
	submit = SubmitField("Ok")

class PasswordForm(FlaskForm):
	email = StringField("Qual o seu email?", validators=[DataRequired()])
	password_hash = PasswordField("Qual a sua senha?", validators=[DataRequired()])
	submit = SubmitField("Ok")

# Create a Form Class
class NamerForm(FlaskForm):
	name = StringField("Qual o seu nome?", validators=[DataRequired()])
	submit = SubmitField("Ok")

	# BooleanField
	# DateField
	# DateTimeField
	# DecimalField
	# FileField
	# HiddenField
	# MultipleField
	# FieldList
	# FloatField
	# FormField
	# IntegerField
	# PasswordField
	# RadioField
	# SelectField
	# SelectMultipleField
	# SubmitField
	# StringField
	# TextAreaField

	## Validators
	# DataRequired
	# Email
	# EqualTo
	# InputRequired
	# IPAddress
	# Length
	# MacAddress
	# NumberRange
	# Optional
	# Regexp
	# URL
	# UUID
	# AnyOf
	# NoneOf
