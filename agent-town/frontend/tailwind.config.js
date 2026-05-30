/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        parchment: "#f5e6c8",
        "parchment-dark": "#d4c4a0",
        "ink-black": "#2c2416",
        "chinese-red": "#c43a31",
        "jade-green": "#5b8c5a",
        "gold-accent": "#c9a84c",
      },
      fontFamily: {
        display: ["Georgia", "serif"],
        body: ["system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
