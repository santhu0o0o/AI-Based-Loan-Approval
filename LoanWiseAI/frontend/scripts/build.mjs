// Production build -> frontend/dist (served by Flask, base "/").
import * as esbuild from 'esbuild';
import fs from 'node:fs';
import path from 'node:path';
import { options, renderHtml, root } from './esbuild.config.mjs';

const dist = path.join(root, 'dist');
fs.rmSync(dist, { recursive: true, force: true });
fs.mkdirSync(dist, { recursive: true });

const result = await esbuild.build(options({ dev: false }));
const template = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
fs.writeFileSync(path.join(dist, 'index.html'), renderHtml(template, result.metafile, dist));

const pub = path.join(root, 'public');
if (fs.existsSync(pub)) fs.cpSync(pub, dist, { recursive: true });

const size = Object.entries(result.metafile.outputs)
  .map(([f, o]) => `  ${path.relative(root, f).padEnd(48)} ${(o.bytes / 1024).toFixed(1)} kB`)
  .join('\n');
console.log(`\nBuilt to dist/\n${size}`);
