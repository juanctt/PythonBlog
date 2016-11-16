'use strict';

module.exports = {
	dist: {
		options: {
			baseUrl:                 '<%= pkg.app.assets %>/headsup/scripts/base',
			mainConfigFile:          '<%= pkg.app.assets %>/headsup/scripts/base/main.js',
			optimize:                'uglify2',
			preserveLicenseComments: false,
			useStrict:               true,
			wrap:                    true,
			name:                    '../../../../lib/bower_components/almond/almond',
			include:				 'main',
			out:                     '<%= pkg.app.assets %>/headsup/scripts/main.js'
		}
	}
}
