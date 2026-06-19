/**
 * Record per-scene screen video with Playwright (Chromium), driven by build/manifest.json.
 *
 * For each scene whose action.type === "browser":
 *   - opens the action.url (dashboard, or a local title/diagram HTML in video/assets/)
 *   - optionally runs a named interaction routine (action.script) to make the UI "do something"
 *   - records for the scene's narration duration (from the voiceover manifest), so picture
 *     and voice line up. Falls back to action.duration_hint if duration is 0.
 *
 * Output: build/video/<scene_id>.webm  (assembler transcodes/pads to final mp4)
 *
 * Usage:
 *   node record_scenes.js --manifest ../build/manifest.json --out ../build/video
 *
 * Env expanded in URLs: ${ASSETS}, ${CONTROLLER_IP}, etc. (set in video/.env)
 */
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

function arg(name, def) {
  const i = process.argv.indexOf(`--${name}`);
  return i > -1 ? process.argv[i + 1] : def;
}
const expand = (s) =>
  (s || "").replace(/\$\{(\w+)\}/g, (_, k) => process.env[k] || "");

// Named interaction routines. Add one per dashboard you want to "drive" on camera.
const ROUTINES = {
  async evebox_walkthrough(page) {
    // Example: land on EveBox, wait for alerts, scroll the alert list, open one.
    await page.waitForTimeout(2500);
    await page.mouse.wheel(0, 600);
    await page.waitForTimeout(2500);
    const firstAlert = page.locator("table tbody tr").first();
    if (await firstAlert.count()) {
      await firstAlert.click().catch(() => {});
      await page.waitForTimeout(3000);
    }
    await page.mouse.wheel(0, 800);
    await page.waitForTimeout(2500);
  },
  // default: just hold on the page (good for title cards / static diagrams)
  async hold(page) {
    /* no-op; recording duration handles timing */
  },
};

(async () => {
  const manifestPath = arg("manifest", "../build/manifest.json");
  const outDir = arg("out", "../build/video");
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  const [w, h] = (manifest.episode.resolution || "1920x1080").split("x").map(Number);
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch({ args: ["--no-sandbox", "--hide-scrollbars"] });

  for (const scene of manifest.scenes) {
    const action = scene.action || {};
    if (action.type !== "browser") {
      console.log(`[record] skip ${scene.id} (type=${action.type || "none"})`);
      continue;
    }
    const seconds = scene.duration && scene.duration > 0 ? scene.duration : (action.duration_hint || 10);
    const url = expand(action.url);
    console.log(`[record] ${scene.id}  ${seconds}s  ${url}`);

    const context = await browser.newContext({
      viewport: { width: w, height: h },
      recordVideo: { dir: outDir, size: { width: w, height: h } },
    });
    const page = await context.newPage();
    try {
      await page.goto(url, { waitUntil: "load", timeout: 30000 });
    } catch (e) {
      console.warn(`   nav warning: ${e.message}`);
    }

    const routine = ROUTINES[action.script] || ROUTINES.hold;
    const started = Date.now();
    await routine(page);
    const remaining = seconds * 1000 - (Date.now() - started);
    if (remaining > 0) await page.waitForTimeout(remaining);

    const video = page.video();
    await context.close(); // finalizes the webm
    if (video) {
      const finalPath = path.join(outDir, `${scene.id}.webm`);
      const tmp = await video.path();
      fs.renameSync(tmp, finalPath);
      console.log(`   -> ${finalPath}`);
    }
  }

  await browser.close();
  console.log("[record] done");
})();
