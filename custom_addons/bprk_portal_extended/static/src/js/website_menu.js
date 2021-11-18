odoo.define('bprk_portal_extended.websitemenu', function (require) {
    'use strict';
	var session = require('web.session');
    var ajax = require('web.ajax');
    var show_dashboard = false;
    

	$(this).scrollTop(0);
    window.onscroll = function(){
    	$('#top_menu li.nav-item').each(function(){
            var href = $(this).find('a').attr('href');
            var self = this;
            if(href == '/my/portal'){  
                if (show_dashboard == true){
                    $(self).removeClass('d-none');    
                }       
            }
        });
    } 


	$('#top_menu li.nav-item').each(function(){
        var href = $(this).find('a').attr('href');
        var self = this;
        if(href == '/my/portal'){
            $(self).addClass('d-none')
            var route = '/website/menu'
            var params = {user_id: session.user_id};
            ajax.jsonRpc(route, 'call', params
            ).then(function (result){
                if(result == true){
                    $(self).removeClass('d-none');
                    show_dashboard = true;
                }
            });
        }
       
    });

    $('.dropdown-menu.js_usermenu a').each(function(){
        var href = $(this).attr('href');
        var self = this;
        if (href == '/my/home'){
            $(self).addClass('d-none');
        }
        
    });


});