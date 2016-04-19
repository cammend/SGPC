from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Usuario, DeptoUser
from apps.Deptos.models import Departamento

class UsuarioForm(forms.ModelForm):
	departamento = forms.ChoiceField()
	tipo = forms.ChoiceField(label='Tipo de Usuario')
	password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Confirmar Contraseña', widget=forms.PasswordInput)

	def clean_password2(self):
		# Check that the two password entries match
		password1 = self.cleaned_data.get("password1")
		password2 = self.cleaned_data.get("password2")
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Contraseñas no coinciden!!!")
		return password2

	def save(self, commit=True):
		# Save the provided password in hashed format
		user = super(UsuarioForm, self).save(commit=False)
		user.set_password(self.cleaned_data["password1"])
		user.tipoUser = self.cleaned_data['tipo']
		if commit:
			user.save()
			deptouser = DeptoUser() #instancia del modelo 'DeptoUser'
			deptouser.usuario = user #le asigno el usuario recien creado
			idepto = self.cleaned_data['departamento']
			deptouser.depto = Departamento.objects.filter(id=idepto)[0] #le asigno el depto elegido
			deptouser.save() #guardamos
		return user

	class Meta:
		model = Usuario
		fields = ('alias','nombres','apellidos','correo')