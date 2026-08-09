/**
 * Generate one image-to-video clip from a local approved comic panel.
 *
 * Uses Higgsfield's official SDK V1 upload helper because the source panel is
 * local. The public API documents this upload -> /v1/image2video/dop flow.
 * Run only after a human approves the input panel and after credentials are
 * present in the environment.
 */

import { readFile, mkdir, writeFile } from "node:fs/promises";
import { dirname, extname } from "node:path";
import { HiggsfieldClient } from "@higgsfield/client";

function valueAfter(name) {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : undefined;
}

function requireEnv(name) {
  const value = process.env[name];
  if (!value) throw new Error(`${name} is required.`);
  return value;
}

const inputPath = valueAfter("--input");
const outputPath = valueAfter("--output");
const prompt = valueAfter("--prompt");
if (!inputPath || !outputPath || !prompt) {
  throw new Error(
    "Usage: node scripts/higgsfield_video.mjs --input <panel.png> --output <clip.mp4> --prompt <motion prompt>"
  );
}

const extension = extname(inputPath).toLowerCase();
const contentType = extension === ".png" ? "image/png" : extension === ".webp" ? "image/webp" : "image/jpeg";
const client = new HiggsfieldClient({
  apiKey: requireEnv("HIGGSFIELD_API_KEY"),
  apiSecret: requireEnv("HIGGSFIELD_API_KEY_SECRET"),
});

const inputUrl = await client.uploadImage(await readFile(inputPath), contentType.split("/")[1]);
const jobSet = await client.generate("/v1/image2video/dop", {
  model: "dop-turbo",
  prompt,
  input_images: [{ type: "image_url", image_url: inputUrl }],
});

if (!jobSet.isCompleted) {
  throw new Error(`Higgsfield request did not complete: ${JSON.stringify(jobSet)}`);
}
const videoUrl = jobSet.jobs[0]?.results?.raw?.url;
if (!videoUrl) throw new Error("Completed request contained no video URL.");

const response = await fetch(videoUrl);
if (!response.ok) throw new Error(`Video download failed: HTTP ${response.status}`);
await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, Buffer.from(await response.arrayBuffer()));
console.log(JSON.stringify({ inputPath, outputPath, videoUrl }, null, 2));
