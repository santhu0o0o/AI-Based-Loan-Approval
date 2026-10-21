// Shared esbuild options for dev and production builds.
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

export function options({ dev }) {
  return {
    absWorkingDir: root,
    entryPoints: ['src/main.jsx'],
    bundle: true,
    outdir: dev ? '.dev/assets' : 'dist/assets',
    publicPath: '/assets',
    entryNames: dev ? '[name]' : '[name]-[hash]',
    assetNames: '[name]-[hash]',
    format: 'esm',
    target: 'es2020',
    jsx: 'automatic',
    // framer-motion's TS source relies on TypeScript's legacy class-field semantics.
    tsconfigRaw: { compilerOptions: { useDefineForClassFields: false } },
    loader: { '.js': 'jsx', '.woff': 'file', '.woff2': 'file', '.svg': 'file', '.png': 'file' },
    minify: !dev,
    sourcemap: dev ? 'inline' : false,
    metafile: true,
    logLevel: 'info',
    define: {
      'process.env.NODE_ENV': JSON.stringify(dev ? 'development' : 'production'),
      __DEV__: dev ? 'true' : 'false',
    },
    // framer-motion optionally requires this; a stub keeps it out of the bundle.
    external: [],
  };
}

/** Inject hashed asset tags into index.html. */
export function renderHtml(template, metafile, outBase) {
  const outputs = Object.keys(metafile.outputs);
  const toUrl = (p) => '/' + path.relative(outBase, path.resolve(root, p)).split(path.sep).join('/');
  const js = outputs.filter((o) => o.endsWith('.js') && metafile.outputs[o].entryPoint);
  const css = outputs.filter((o) => o.endsWith('.css'));
  return template
    .replace('<!--STYLES-->', css.map((c) => `<link rel="stylesheet" href="${toUrl(c)}" />`).join('\n    '))
    .replace('<!--SCRIPTS-->', js.map((j) => `<script type="module" src="${toUrl(j)}"></script>`).join('\n    '));
}
