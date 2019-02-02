var nude = require('../nude'),
  images = [
    { id: 1, expected: false },
    { id: 2, expected: false },
    { id: 3, expected: false },
    { id: 4, expected: true },
    { id: 5, expected: true },
    { id: 6, expected: true },
  ];

/*images.forEach(function(image) {
  nude.scan(__dirname + '/images/' + image.id + '.jpg', function(res) {
    console.log('Image ' + image.id + ': ' + res);
    console.log('Expected: ' + image.expected);
  });
});
*/
image=process.argv[2];
//console.log(__dirname);
nude.scan(__dirname + '/images/' + image, function(res) {
    console.log('Image: ' + image + '   Result: ' + res);
    });
