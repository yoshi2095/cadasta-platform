var SimpleRouter = function(){
  var routes = {};

  function route (path, templateID, controller) {
    routes[path] = {templateID: templateID, controller: controller};
  }

  function hideDetailPannel () {
    if (!$('.content-single').hasClass('detail-hidden')) {
      $('.content-single').addClass('detail-hidden');
      window.setTimeout(function() {
        map.invalidateSize();
      }, 400);
    }
  }

  function displayDetailPannel () {
    if ($('.content-single').hasClass('detail-hidden')) {
      $('.content-single').removeClass('detail-hidden');
      window.setTimeout(function() {
        map.invalidateSize();
      }, 400);
    }
  }

  route('/map', 'map-tab', function() {
    hideDetailPannel();
  });

  route('/overview', 'overview-tab', function() {
    displayDetailPannel();
  });

  route('/', 'overview-tab', function() {
    displayDetailPannel();
  });

  route('/location', 'location-tab', function() {
    displayDetailPannel();
  });


  var el = null;
  function router () {
    el = el || document.getElementById('project-detail');
    var url = location.hash.slice(1) || '/';
    var route = routes[url];
    if (el && route.controller) {
      el.innerHTML = TemplateEngine(route.templateID, new route.controller());
    }
  }

  return {
    router: router,
  };
};

var sr = new SimpleRouter();

window.addEventListener('hashchange', sr.router);
window.addEventListener('load', sr.router);
