$(document).ready(main);
 
var contador = 1;
var estado_msg = 1;
var estado_pedido = 0;
var estado_cot = 0;
var id_cot = -1;
 
function main(){
	//añadir calendario
	//addCelendar();


	$(window).resize(function(){
		if ($(window).width() > 700){
			$('.nav header nav').show();
		}else{
			$('.nav header nav').hide();
		}
	})
	
	$('.menu_bar').click(function(){
		// $('nav').toggle(); 
 
		if(contador == 1){
			$('.nav header nav').show(500);
			$('nav').animate({
				left: '0'
			});
			contador = 0;
		} else {
			contador = 1;
			$('nav').animate({
				left: '-100%'
			});
			$('.nav header nav').hide(500);
		}
 
	});

	$('#com_pedido').hide(); //oculta los comentarios del pedido al inicio
	$('#com_pedido form').hide();
	$('#com_cotizacion').hide(); //oculta los comentarios de cotizacion al inicio
	$('#com_cotizacion form').hide();

	//muestra los comentarios al hacer click en el pedido
	$('#titulo_pedido').click(function(){
		if (estado_msg == 1){
			$('#msg').hide(200);
			estado_msg = 0;
		}else if( estado_cot == 0){
			$('#msg').show(200);
			estado_msg = 1;
		}
		if (estado_pedido == 0){
			$('#com_pedido').show(200);
			estado_pedido = 1;
		}else{
			$('#com_pedido').hide(200);
			estado_pedido = 0;
		}
	});

	//mestra los comentarios al hacer click en la cotizacion

	$('#com_pedido h3').click(function(){
		$('#com_pedido form').toggle(500);
	});

	$('#com_cotizacion h3').click(function(){
		$('#com_cotizacion form').toggle(500);
	});
 
};

function show_cot(id){
	$('#comment_'+id_cot).hide();
	id_cot = id;
	if (estado_cot == 0){
		$('#com_cotizacion').show(200);
		estado_cot = 1;
	}else if(id == id_cot){
		$('#com_cotizacion').hide(200);
		estado_cot = 0;
	}else{
		
	}
	if (estado_msg == 1 ){
		$('#msg').hide(200);
		estado_msg = 0;
	}else if( estado_pedido == 0 ){
		$('#msg').show(200);
		estado_msg = 1;
	}
	$('#id_c').attr('value',id);
	$('#comment_'+id).appendTo('#com_cotizacion');
	$('#comment_'+id).show();
}

//añadir calendario
function addCelendar(){
	$('#id_fecha').parent().append("<img src='/static/img/calendar.gif' id='selector' />")
}