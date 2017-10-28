module.exports = {
	parser:'postcss-scss',
	plugins:{
		autoprefixer: {},
		cssnano: { preset: 'default' },
		'postcss-assets': {},
		'postcss-cssnext': {},
		oldie: {}
	}
};