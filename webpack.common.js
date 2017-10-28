const CleanWebpackPlugin = require('clean-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const path = require('path');

module.exports = {
    entry: {
        login: './src/static/app/module/login/index.ts'
    },
    module: {
		rules: [
			{test: /\.ts$/, exclude: /node_modules/, use: 'ts-loader'},
			{test: /\.html$/, exclude: /node_modules/, use: 'html-loader'},
			{test: /\.png$/, exclude: /node_modules/, use: 'file-loader'},
			{test: /\.scss$/, exclude: /node_modules/, use: ['css-loader', 'postcss-loader', 'sass-loader']}
		]
	},
    output: {
        filename: '[name]/[name].bundle.js',
        path: path.resolve(__dirname, 'src/static/dist')
    },
    plugins: [
        new CleanWebpackPlugin(['./src/static/dist/', './src/templates/kuzgun/']),
        new HtmlWebpackPlugin({
            filename: '../.././templates/kuzgun/login.html',
            template: './src/static/app/module/login/login.html',
            chunks: ['login']
        })
    ],
    resolve: {
        extensions: ['.ts', '.js', '.css', '.scss', '.html', '.webpack.js', '.web.js', '.tsx', '.jsx', '.json']
    }
};
