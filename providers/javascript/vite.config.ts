import {defineConfig} from 'vite';
import {resolve} from 'path';
import react from '@vitejs/plugin-react';
import vue from '@vitejs/plugin-vue';
import dts from 'vite-plugin-dts';
import {visualizer} from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    react(),
    vue(),
    dts({
      insertTypesEntry: true,
      exclude: ['**/*.test.ts', '**/*.test.tsx', '**/*.stories.ts', '**/*.stories.tsx'],
    }),
    visualizer({
      filename: 'dist/bundle-analysis.html',
      open: false,
      gzipSize: true,
    }),
  ],

  build: {
    lib: {
      entry: {
        index: resolve(__dirname, 'src/index.ts'),
        react: resolve(__dirname, 'src/react/index.ts'),
        vue: resolve(__dirname, 'src/vue/index.ts'),
        'web-components': resolve(__dirname, 'src/web-components/index.ts'),
      },
      name: 'V402Provider',
      formats: ['es', 'cjs', 'umd'],
    },
    rollupOptions: {
      external: ['react', 'react-dom', 'vue', 'ethers', 'web3'],
      output: {
        globals: {
          react: 'React',
          'react-dom': 'ReactDOM',
          vue: 'Vue',
          ethers: 'ethers',
          web3: 'Web3',
        },
      },
    },
    sourcemap: true,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
  },

  test: {
    environment: 'happy-dom',
    setupFiles: ['src/test/setup.ts'],
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.stories.ts',
        '**/*.stories.tsx',
      ],
    },
  },

  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },

  define: {
    __VERSION__: JSON.stringify(process.env.npm_package_version),
  },
});
