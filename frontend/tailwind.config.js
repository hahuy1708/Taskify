/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",  
    "./src/layouts/**/*.{vue,js}",      
    "./src/pages/**/*.{vue,js}",        
    "./src/components/**/*.{vue,js}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
