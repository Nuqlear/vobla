module.exports = {
  plugins: [
    require('postcss-cssnext')({
        features: {
          customProperties: {
              warnings: false
          }
      }
    }),
    /*require('css-declaration-sorter')({
      order: 'Concentric CSS'
    }),*/
    require('css-mqpacker')(),
  ]
};
