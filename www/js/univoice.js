function setMessage(msg,level,append){
	if( level == undefined )
		level="ok"
	if( append )
		msg = $('#message').html() + "<br>" + msg;
	$('#message').removeClass('ok error').addClass(level).html(msg);
}
function check(tab){
	$('#message').empty();
	if( tab && tab.message ){
		setMessage(tab.message,'ok')
	}
	if( tab && tab.trace ){
		setMessage('<pre>'+tab.trace.replace(/</g,'&lt;').replace(/>/g,'&gt;')+'</pre>','ok')
	}
	if( tab && tab.error ){
		setMessage(tab.error,'error',true)
	}
}

