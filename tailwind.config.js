/** @type {import('tailwindcss').Config} */
const colors = require("tailwindcss/colors");

module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",

    // Or if using `src` directory:
    "./src/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {},
    colors: {
      transparent: "transparent",
      current: "currentColor",
      white: colors.white,
      gray: colors.gray,
      qoherentblue: "#03A9F4",
      qoherentred: "#E63462",
      qoherentpurple: "#884DA0",
      qoherentblack: "#1c1c1c",
      qoherentgray: "#222",
      qoherentlightgray: "#625F63"
    }
  },
  plugins: []
};
