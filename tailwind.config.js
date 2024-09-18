/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'blue-900': '#003366',  // Custom color based on the deck
        'pink-600': '#FF3366',
      },
    },
  },
  plugins: [],
};