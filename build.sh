#!/bin/bash

# Build script para Vercel
# Este script instala dependências e compila o frontend

set -e

echo "🔨 Building DistroWiki Monorepo..."

# Instalar dependências Node.js
echo "📦 Installing Node dependencies..."
npm install || yarn install || bun install

# Build do frontend Vite
echo "⚙️  Building Vite frontend..."
npm run build || yarn build || bun run build

echo "✅ Build completed successfully!"
