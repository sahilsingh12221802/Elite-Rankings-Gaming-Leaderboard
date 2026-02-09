import type { Config } from 'tailwindcss'

export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        'dark-bg': '#0f0f1e',
        'dark-bg-secondary': '#1a1a2e',
        'dark-bg-tertiary': '#16213e',
        'neon-primary': '#00ff88',
        'neon-secondary': '#00d4ff',
        'neon-danger': '#ff0055',
        'neon-warning': '#ffaa00',
        'text-primary': '#e0e0ff',
        'text-secondary': '#a0a0c0',
      },
      fontFamily: {
        'gamer': ['Space Mono', 'monospace'],
        'sans': ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'neon': '0 0 20px rgba(0, 255, 136, 0.3), 0 0 40px rgba(0, 212, 255, 0.2)',
        'neon-lg': '0 0 40px rgba(0, 255, 136, 0.5), 0 0 80px rgba(0, 212, 255, 0.3)',
      },
      animation: {
        'pulse-neon': 'pulse-neon 2s ease-in-out infinite',
        'slide-up': 'slide-up 0.5s ease-out',
      },
    },
  },
  plugins: [],
} satisfies Config
