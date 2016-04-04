from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Usuario

class UsuarioForm(forms.ModelForm):
	departamento = forms.ChoiceField() #le mando 0 como señal de usuario ROOT
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
		user.depto = self.cleaned_data['departamento']
		user.tipoUser = self.cleaned_data['tipo']
		if commit:
			user.save()
		return user

	class Meta:
		model = Usuario
		fields = ('alias','nombres','apellidos','correo')