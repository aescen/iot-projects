/* eslint-disable prefer-const */
/* eslint-disable no-unused-vars */

let routes = [
  {
    path: '/',
    url: './index.html',
  },
  {
    path: '/about/',
    url: './pages/about.html',
  },
  {
    path: '/cart/',
    componentUrl: './pages/cart.html',
  },
  {
    path: '/product/:id/',
    componentUrl: './pages/product.html',
  },
  {
    path: '/qrscan/',
    componentUrl: './pages/qrscan.html',
  },
  {
    path: '/request-and-load/user/:userId/',
    async: ({ router, to, resolve }) => {
      // App instance
      let { app } = router;

      // Show Preloader
      app.preloader.show();

      // User ID from request
      let { userId } = to.params;

      // Simulate Ajax Request
      setTimeout(() => {
        // We got user data from request
        let user = {
          firstName: 'Vladimir',
          lastName: 'Kharlampidi',
          about: 'Hello, i am creator of Framework7! Hope you like it!',
          links: [
            {
              title: 'Framework7 Website',
              url: 'https://framework7.io',
            },
            {
              title: 'Framework7 Forum',
              url: 'https://forum.framework7.io',
            },
          ],
        };
        // Hide Preloader
        app.preloader.hide();

        // Resolve route to load page
        resolve(
          {
            componentUrl: './pages/request-and-load.html',
          },
          {
            props: {
              user,
            },
          },
        );
      }, 1000);
    },
  },
  // Default route (404 page). MUST BE THE LAST
  {
    path: '(.*)',
    url: './pages/404.html',
  },
];
