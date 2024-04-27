import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
    base:
        mode == "development"
            ? "http://localhost:5173/"
            : "/static/globalVoice/spa/",
    build: {
        emptyOutDir: true,
        outDir: "../globalVoice/static/globalVoice/spa",
    },
    plugins: [vue()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
}));
