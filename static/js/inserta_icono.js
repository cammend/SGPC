$(document).ready(function(){
$('#form_inicio p:nth-child(3)').append('<i class="fa fa-user"></i>');

$('#form_inicio p:nth-child(4)').append('<i class="fa fa-key"></i>');

$('#id_username').attr({placeholder : "Usuario"});
$('#id_password').attr({placeholder : "Ingrese Contraseña"});

$('#id_alias').attr({placeholder : "Alias"});
$('#id_nombres').attr({placeholder : "Ingrese sus Nombres"});
$('#id_apellidos').attr({placeholder : "Ingrese sus apellidos"});
$('#id_correo').attr({placeholder : "Ingrese su correo Electronico"});
$('#id_password1').attr({placeholder : "Ingrese Contraseña"});
$('#id_password2').attr({placeholder : "Repita Contraseña"});


$('#id_fecha').datepicker({
				changeMonth:true,
				changeYear:true,
								
			});


});