import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({ plugins: [react()], server: { proxy: { '/doc-rag/api': 'http://localhost:9090' } }, build: { rollupOptions: { output: { manualChunks: { react: ['react', 'react-dom', 'react-router-dom'], material: ['@mui/material', '@emotion/react', '@emotion/styled'] } } } } })
