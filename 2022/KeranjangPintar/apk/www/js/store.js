/* eslint-disable prefer-const */
/* eslint-disable no-unused-vars */
/* eslint-disable no-undef */
/* eslint-disable no-param-reassign */

let { createStore } = Framework7;
const store = createStore({
  state: {
    products: [
      {
        id: '1',
        title: 'Product 1',
        description: 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Nisi tempora similique reiciendis, error nesciunt vero, blanditiis pariatur dolor, minima sed sapiente rerum, dolorem corrupti hic modi praesentium unde saepe perspiciatis.',
        img: 'https://cdn.framework7.io/placeholder/fashion-88x88-5.jpg',
        count: '1',
      },
      {
        id: '2',
        title: 'Product 2',
        description: 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Nisi tempora similique reiciendis, error nesciunt vero, blanditiis pariatur dolor, minima sed sapiente rerum, dolorem corrupti hic modi praesentium unde saepe perspiciatis.',
        img: 'https://cdn.framework7.io/placeholder/fashion-88x88-5.jpg',
        count: '2',
      },
      {
        id: '3',
        title: 'Product 3',
        description: 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Nisi tempora similique reiciendis, error nesciunt vero, blanditiis pariatur dolor, minima sed sapiente rerum, dolorem corrupti hic modi praesentium unde saepe perspiciatis.',
        img: 'https://cdn.framework7.io/placeholder/fashion-88x88-6.jpg',
        count: '3',
      },
    ],
  },
  getters: {
    products({ state }) {
      return state.products;
    },
  },
  actions: {
    addProduct({ state }, product) {
      state.products = [...state.products, product];
    },
  },
});
