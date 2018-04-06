var path = require("path");
var glob = require("glob");
var htmlWebpackPlugin = require("html-webpack-plugin");
var extractTextPlugin = require('extract-text-webpack-plugin');
var copyWebpackPlugin = require('copy-webpack-plugin');

var rand = function() {
	var r = (Math.random() + 1) * 100000000;
	return r.toString().substr(1, 8);
};

var env = {
    src: path.resolve(__dirname, "webclient", "webclient"),
    output: path.resolve(__dirname, "webclient", "dist"),
    config_id: rand(),
};

////////////////
// entries
////////////////
var entries = {};

// js entries
var js_entries = {
    muddery_main: path.join(env.src, "controllers", "muddery_main.js")
}
Object.assign(entries, js_entries);

////////////////
// plugins
////////////////
var plugins = [];

// html files
var get_html_plugins = new htmlWebpackPlugin({
    template: path.join(env.src, "views", "main.html"),
    filename: path.join("views", "main.html"),
    inject: true,
    contents: {
            // config文件id
            config_id: env.config_id,

            // 屏蔽html代码
            comment_begin: '"</script><!--',
            comment_end: '--><script>"',
        }
    }
);

plugins.push(get_html_plugins);

// css files
var extractCSS = new extractTextPlugin(path.join('css', '[name]-[chunkhash:8].css'));
plugins.push(extractCSS);

// copy files
var copyFiles = new copyWebpackPlugin([
    {
    	from: path.join(env.src, "settings.js"),
    	to: path.join(env.output, "settings.js",)
	},
    {
    	from: path.join(env.src, "libs"),
    	to: path.join(env.output, "libs",)
	},
]);
plugins.push(copyFiles);


////////////////
// cacheGroups
////////////////
/*
var get_public_files = function() {
    var r = {};
    var entries = [
    	/\/webclient\/client\/.*\.js$/,
    	/\/webclient\/controllers\/.*\.js$/,
    	/\/webclient\/utils\/.*\.js$/,
    	/\/webclient\/css\/.*\.css$/,
    ];

    for (var i = 0; i < entries.length; i++) {
        var conf = {
            test: entries[i],
          	chunks: 'initial',
    		name: 'public',
          	enforce: true,
        }

        r[i] = conf;
    }
    return r
}
var cacheGroups = get_public_files();
*/

////////////////
// webpack config
////////////////
module.exports = {
  	entry: entries,
  	output: {
    	filename: path.join("js", "[name]-[chunkhash:8].js"),
    	path: env.output,
    	publicPath: "/dist/",
  	},
	module: {
		rules: [
			{
				test: /.css$/,
				use: extractTextPlugin.extract(
					{
						fallback: 'style-loader',
						use: 'css-loader',
						})
				},
			{
				test: /.(jpg|jpeg|png|gif)$/,
				use: {
					loader: 'url-loader',
					options: {
					   	limit: 8192,
					   	name: './img/[name]-[hash:8].[ext]',
					},
				},
			}
		]
	},
    resolve: {
        extensions: ["*", ".js", ".jsx", ".htm", ".html", ".css", '.png', '.jpg', '.jpeg', '.gif'],
    },
    plugins: plugins,
    devServer: {
       contentBase: env.output,
       open: 'Google Chrome',
       openPage: 'views/main.html',
   }
}
