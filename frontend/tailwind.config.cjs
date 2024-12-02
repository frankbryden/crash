/** @type {import('tailwindcss').Config} */
const plugin = require('tailwindcss/plugin');

module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      boxShadow: {
        'custom-blue': '0 4px 6px -1px rgba(59, 130, 246, 0.5), 0 2px 4px -1px rgba(59, 130, 246, 0.25)',
        'custom-purple': '0 4px 6px -1px rgba(139, 92, 246, 0.5), 0 2px 4px -1px rgba(139, 92, 246, 0.25)',
      },
    },
  },
  plugins: [
    plugin(function({ addUtilities }) {
      const newUtilities = {
        '.flip-card': {
          perspective: '1000px',
        },
        '.flip-card-inner': {
          position: 'absolute',
          width: '100%',
          height: '100%',
          transition: 'transform 0.6s',
          'transform-style': 'preserve-3d',
        },
        '.flip-card:hover .flip-card-inner': {
          transform: 'rotateY(180deg)',
        },
        '.flip-card-front, .flip-card-back': {
          position: 'absolute',
          width: '100%',
          height: '100%',
          'backface-visibility': 'hidden',
        },
        '.flip-card-back': {
          transform: 'rotateY(180deg)',
        },
      };

      addUtilities(newUtilities, ['responsive', 'hover']);
    }),
  ],
};
