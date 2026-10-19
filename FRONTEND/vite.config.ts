import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    // PWA: installable on the phone, and the app shell stays available on a
    // weak network. API calls are never cached: a ride state must be fresh.
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: "En route pour l'emploi",
        short_name: 'En route',
        description: 'VTC solidaire en Guyane',
        lang: 'fr',
        start_url: '/',
        display: 'standalone',
        theme_color: '#0b5d3b',
        background_color: '#ffffff',
        icons: [{ src: '/favicon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any' }],
      },
    }),
  ],
  server: {
    // Fixed port: it must match CORS_ORIGINS in the back-end .env.
    port: 5173,
    strictPort: true,
  },
});
