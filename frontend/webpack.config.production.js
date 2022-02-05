var path = require('path');
var webpack = require('webpack');
var HtmlWebpackPlugin = require('html-webpack-plugin');
var MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = {
  entry: {
    vendor: ['react', 'react-dom', 'react-router'],
    app: ['@babel/polyfill', 'whatwg-fetch', './src/index.jsx']
  },
  output: {
    path: path.join(__dirname, 'dist'),
    publicPath: '/',
    filename: 'assets/[name].[hash].js',
    chunkFilename: 'assets/[name].[chunkhash].js'
  },
  devtool: 'cheap-module-source-map',
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        include: path.join(__dirname, 'src'),
        loader: 'babel-loader',
        options: {
          presets: [
            [
              '@babel/preset-env',
              {
                modules: false
              }
            ],
            '@babel/preset-react'
          ],
          plugins: [
            '@babel/plugin-transform-async-to-generator',
            ['@babel/plugin-proposal-decorators',
            {
              "legacy": true
            }],
            '@babel/plugin-syntax-dynamic-import',
            '@babel/plugin-proposal-function-bind',
          ]
        },
        resolve: {
          extensions: ['.js', '.jsx']
        }
      },
      {
        test: /\.scss|css$/,
        use: [
          MiniCssExtractPlugin.loader,
          { loader: 'css-loader', options: { sourceMap: true, url: true} },
          { loader: 'postcss-loader', options: {
            sourceMap: true, postcssOptions: {config: 'postcss.config.js'}}},
          { loader: 'resolve-url-loader', options: {sourceMap: true, debug: true} },
          { loader: 'sass-loader', options: { sourceMap: true } }
        ]
      },
      // {
      //   test: /\.css$/i,
      //   use: [MiniCssExtractPlugin.loader, "css-loader"],
      // },
      {
        test: /\.(jpe?g|png|gif|svg)$/i,
        use: [
          'file-loader?hash=sha512&digest=hex&name=[hash].[ext]',
          {
            loader: 'image-webpack-loader',
            options: {
              mozjpeg: {
                progressive: true
              },
              gifsicle: {
                interlaced: false
              },
              optipng: {
                optimizationLevel: 4
              },
              pngquant: {
                quality: [0.75, 0.90],
                speed: 3
              }
            }
          }
        ]
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/i,
        type: 'asset/resource',
      },
    ]
  },
  plugins: [
    new webpack.DefinePlugin({
      'process.env': {
        NODE_ENV: JSON.stringify('production')
      }
    }),
    new MiniCssExtractPlugin(),
    new HtmlWebpackPlugin({
      hash: false,
      template: './index.hbs',
      favicon: './src/assets/favicon.ico'
    })
  ]
};
