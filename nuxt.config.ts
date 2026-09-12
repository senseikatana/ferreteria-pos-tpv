import tailwindcss from '@tailwindcss/vite'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-01-01',
  devtools: { enabled: false },

  css: ['~/assets/css/main.css'],

  vite: {
    plugins: [
      tailwindcss(),
    ],
  },

  // Estructura moderna de Nuxt 4
  future: {
    compatibilityVersion: 4,
  },

  typescript: {
    strict: true,
    typeCheck: false,
  },

  nitro: {
    experimental: {
      openAPI: false,
    },
  },

  runtimeConfig: {
    jwtSecret: process.env.JWT_SECRET || 'pos-universal-secret-key-change-in-prod-2026',
    databaseUrl: process.env.DATABASE_URL || 'file:./pos_ferreteria.db',
    public: {
      appName: 'Universal POS Core',
      currency: '$',
      katanakitCdnUrl: 'https://esm.sh/katanakit-js@2.14.1',
    },
  },
})
