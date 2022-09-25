let waitPage;
var routes = [
  {
    path: '/',
    url: './index.html',
    keepAlive: true,
    master: true,
    options: {
      transition: 'f7-dive',
    },
  },
  {
    path: '/camera/',
    async: ({ router, to, resolve }) => {
      // App instance
      var app = router.app;
      app.preloader.show();
      waitPage = setTimeout(() => {
        app.preloader.hide();
        app.dialog.alert('Timeout in opening page.', 'Error', () => {});
      }, 7200);
      resolve(
        {
          componentUrl: './pages/camera.html',
        },
        {
          props: {
            waitPage,
          }
        }
      );

      /*
      // Show Preloader
      app.preloader.show();
      setTimeout(() => {
        // Hide Preloader
        app.preloader.hide();

        // Resolve route to load page
        resolve({
            componentUrl: './pages/camera.html',
          },
        );
      }, 500);
      */
    },
    options: {
      transition: 'f7-dive',
    },
  },
  {
    path: '/logs/',
    async: ({ router, to, resolve }) => {
      // App instance
      var app = router.app;
      app.preloader.show();
      waitPage = setTimeout(() => {
        app.preloader.hide();
        app.dialog.alert('Timeout in opening page.', 'Error', () => {});
      }, 7200);
      resolve(
        {
          componentUrl: './pages/logs.html',
        },
        {
          props: {
            waitPage,
          }
        }
      );

      /*
      // Show Preloader
      app.preloader.show();
      setTimeout(() => {
        // Hide Preloader
        app.preloader.hide();

        // Resolve route to load page
        resolve({
            componentUrl: './pages/logs.html',
          },
        );
      }, 1000);
      */
    },
    options: {
      transition: 'f7-dive',
    },
  },
  {
    path: '/settings/',
    componentUrl: './pages/settings.html',
    options: {
      transition: 'f7-dive',
    },
  },
  {
    path: '/about/',
    url: './pages/about.html',
    options: {
      transition: 'f7-dive',
    },
  },

  // Default route (404 page). MUST BE THE LAST
  {
    path: '(.*)',
    url: './pages/404.html',
    options: {
      transition: 'f7-dive',
    },
  },
];
