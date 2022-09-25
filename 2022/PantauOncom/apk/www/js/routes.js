/* eslint-disable no-undef */
/* eslint-disable no-unused-vars */

const routes = [
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
    keepAlive: true,
    async: ({ router, to, resolve }) => {
      // App instance
      const { app } = router;
      app.preloader.show();
      waitPage = setTimeout(() => {
        app.preloader.hide();
        app.dialog.alert('Timeout in opening page.', 'Error', () => { });
      }, 3700);
      resolve(
        {
          componentUrl: './pages/camera.html',
        },
        {
          props: {
            waitPage,
          },
        },
      );
    },
    options: {
      transition: 'f7-dive',
    },
  },
  {
    path: '/settings/',
    keepAlive: true,
    componentUrl: './pages/settings.html',
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
