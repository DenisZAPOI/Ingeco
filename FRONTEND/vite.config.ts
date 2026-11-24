/// <reference types="vitest/config" />
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
      // The font too (docs/adr/023): kept after the first visit, so the next
      // ones show it at once.
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,woff2}'],
      },
      manifest: {
        name: "En route pour l'emploi",
        short_name: 'En route',
        description: 'VTC solidaire en Guyane',
        lang: 'fr',
        start_url: '/',
        display: 'standalone',
        theme_color: '#f7f7f2',
        background_color: '#f7f7f2',
        icons: [{ src: '/favicon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any' }],
      },
    }),
  ],
  server: {
    // Fixed port: it must match CORS_ORIGINS in the back-end .env.
    port: 5173,
    strictPort: true,
  },
  // Same port: the built app (the one to test on a slow network) talks to the API too.
  preview: {
    port: 5173,
    strictPort: true,
  },
  // Pure logic only (src/lib, src/i18n): no browser needed (docs/adr/016).
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts'],
  },
});
