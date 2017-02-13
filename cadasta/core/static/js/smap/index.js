$(window).load(function () {
  var js_files = ['map.js', 'template_renderer.js', 'router.js'];
  var body = $('body');
  for (var i in js_files) {
    body.append($('<script src="/static/js/smap/' + js_files[i] + '"></script>'));
  }
  console.log('call router!');
  var sr = new SimpleRouter();
  sr.router();
});
