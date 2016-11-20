require.config({
	paths: {
		jquery: '../../../../lib/bower_components/jquery/dist/jquery',
		underscore: '../../../../lib/bower_components/underscore/underscore',
		bootstrap: '../../../../lib/bower_components/bootstrap-sass/assets/javascripts/bootstrap',
		jqueryVimeoEmbed: '../../../../lib/bower_components/jquery-smart-vimeo-embed/jquery-smartvimeoembed',
		alertifyjs: '../../../../lib/node_modules/alertifyjs/build/alertify',
		notification: '../../../../assets/plugins/scripts/notifications',
		jquery_ujs: '../../../../assets/plugins/scripts/jquery_ujs'
	},
	shim: {
		bootstrap: {
			deps: ['jquery']
		},
		jqueryVimeoEmbed: {
			deps: ['jquery']
		},
		notification: {
			deps: ['jquery', 'alertifyjs']
		},
		jquery_ujs: {
			deps: ['jquery']
		},
	}
});

require([
	'jquery',
	'underscore',
	'bootstrap',
	'jquery_ujs',
	'alertifyjs',
	'jqueryVimeoEmbed',
	'notification',
	'plugins/miscellaneous'
]);
