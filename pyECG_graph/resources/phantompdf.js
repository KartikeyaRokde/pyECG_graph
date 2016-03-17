var page = require('webpage').create();

page.paperSize = {
  format: 'A4',
  orientation: 'portrait'
}

page.open('file://$$file_path$$', function () {
    page.render('$$output_dir$$');
    phantom.exit();
});
