$(document).ready(function()
{
	$panneaux = $('div.panneau').hide();
	$('h2.titre').each(function(i)
	{
		$this = $(this);
		ancre = $this.next($panneaux)[0].id;
		lien = $('<a>',
		{
			'href':				'#' + ancre,
			'aria-expanded':	'false',
			'aria-controls':	ancre
		});
		$this.wrapInner(lien);
	});
	$('h2.titre > a').click(function() 
	{
		if ($(this).attr('aria-expanded') == 'false') 
		{
            $(this).attr('aria-expanded', true).parent().next($panneaux).show();
		} 
		else 
		{
            $(this).attr('aria-expanded', false).parent().next($panneaux).hide();
		}
		return false;
	}); 
	$('h3.titre').each(function(i)
	{
		$this = $(this);
		ancre = $this.next($panneaux)[0].id;
		lien = $('<a>',
		{
			'href':				'#' + ancre,
			'aria-expanded':	'false',
			'aria-controls':	ancre
		});
		$this.wrapInner(lien);
	});
	$('h3.titre > a').click(function() 
	{
		if ($(this).attr('aria-expanded') == 'false') 
		{
            $(this).attr('aria-expanded', true).parent().next($panneaux).show();
		} 
		else 
		{
            $(this).attr('aria-expanded', false).parent().next($panneaux).hide();
		}
		return false;
	}); 
});
