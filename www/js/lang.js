// lang.js

var oldLang='';

function setLang(lang){
	if( oldLang != '' )
		$('span:lang('+oldLang+')').css('display','none');
	$('span:lang('+lang+')').css('display','block');
	oldLang=lang;
}