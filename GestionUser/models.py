from django.db import models
from django.contrib.auth.models import (
	BaseUserManager, AbstractBaseUser, PermissionsMixin
)

# Permisos:
# 0 = ROOT
# 1 = Admin
# 2 = Normal

# Variables
deptos = [(0,'Almacén'), 
		  (1,'Finanzas'),
		  (2,'Auditoría'),
		  (3,'Gerencia'),
		  (4,'Compras'),
		  (5,'Deptos. Técnicos'),
]

deptos_url = (
	'almacen/','finanzas/','auditoria/','gerencia/','compras/','deptos_tecnicos/',
)

tipos = [(0,'ROOT'),
		 (1,'ADMIN'),
		 (2,'NORMAL'),
]

def getStringTipo(num):
	return str(tipos[num][1])

def getStringDepto(num):
	return str(deptos[num][1])

def getDeptos():
	return deptos

def getTipos():
	return tipos

def getDeptosUrl():
	return deptos_url

# Create your models here.
class ManejadorUsuario(BaseUserManager):
	def create_user(self, alias, password=None):
		if not alias and not tipoUser:
			raise ValueError('Debe haber alias y tipo de usuario')

		user = self.model(
			alias = alias,
			tipoUser = 0
		)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, alias, password):
		user = self.create_user(alias, password)
		user.is_admin = True
		user.save(using=self._db)
		return user

class Usuario(AbstractBaseUser):
	alias = models.CharField(max_length=20,unique=True)
	nombres = models.CharField(max_length=30, blank=True, null=True)
	apellidos = models.CharField(max_length=30, blank=True, null=True)
	correo = models.EmailField(blank=True, null=True)
	tipoUser = models.IntegerField()

	is_admin = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)

	objects = ManejadorUsuario()

	USERNAME_FIELD = 'alias'
	REQUIRED_FIELDS = []

	def get_full_name(self):
		return '%s %s' % (self.nombres, self.apellidos)

	def get_short_name(self):
		return self.nombres

	def is_staff(self):
		return self.is_admin

	def has_perm(self, perm, obj=None):
		return True

	def has_module_perms(self, app_label):
		return True

	def __str__(self):
		return self.alias

	def get_tipo(self):
		if self.tipoUser is None:
			return self.alias
		return getStringTipo(self.tipoUser)

	def get_nombres(self):
		if self.nombres is '':
			return 'Sin nombres'
		return self.nombres

	def get_apellidos(self):
		if self.apellidos is '':
			return 'Sin apellidos'
		return self.apellidos

	def get_correo(self):
		if self.correo is '':
			return '-----'
		return self.correo

	def es_admin(self):
		if self.tipoUser == 1: return True
		return False

	def es_root(self):
		if self.tipoUser == 0: return True
		return False

	def es_normal(self):
		if self.tipoUser == 2: return True
		return False