const path = require('path');
const webpack = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
  entry: [
    'react-hot-loader/patch',
    'webpack-dev-server/client?http://0.0.0.0:3000',
    'webpack/hot/only-dev-server',
    '@babel/polyfill',
    'whatwg-fetch',
    './src/index.jsx'
  ],
  devServer: {
    hot: true,
    port: process.env.PORT || 3000,
    host: '0.0.0.0',
    static: [
      {
        directory: path.resolve(__dirname, 'dist'),
        publicPath: '/',
      },
    ],
    historyApiFallback: true,
    proxy: {
      '/api': {
        target: 'http://backend:5000',
        secure: false,
        changeOrigin: true
      },
      '/f/': {
        target: 'http://backend:5000',
        secure: false,
        changeOrigin: true
      },
      '/d/*/preview': {
        target: 'http://backend:5000',
        secure: false,
        changeOrigin: true
      }
    }
  },
  output: {
    path: path.join(__dirname, 'dist'),
    publicPath: '/',
    filename: 'app.[hash].js'
  },
  devtool: 'eval',
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
        options: {
          presets: [
            [
              '@babel/preset-env',
              {
                'modules': false
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
    new webpack.HotModuleReplacementPlugin(),
    new MiniCssExtractPlugin(),
    new HtmlWebpackPlugin({
      hash: false,
      template: './index.hbs',
      favicon: './src/assets/favicon.ico'
    }),
    new webpack.ContextReplacementPlugin(/moment[\/\\]locale$/, /nb/),
  ],
  resolve: {
      alias: {
        'react-dom': '@hot-loader/react-dom'
      }
  }
};
