
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
   name: 'about',
   path: '/about/',
   url: './pages/about.html',
   options: {
      transition: 'f7-dive',
    },
  },
  {
   path: '(.*)',
   url: './pages/404.html',
   options: {
      transition: 'f7-dive',
    },
  },
];
