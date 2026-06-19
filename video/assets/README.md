# Scene asset cards (HTML)

Title/diagram cards recorded by Playwright. A scene points here via
`action.url: file://${ASSETS}/<name>.html`. All are 1920x1080, dark theme (#0b0f14 / accent
#5ad1a8), no external deps except Chart.js (CDN) on the data cards.

| Card | Scene | Data source |
|---|---|---|
| `title_cold_open.html` | s1 | static |
| `topology.html` | s2 | static (SVG diagram) |
| `contenders.html` | s3 | static |
| `metrics.html` | s7 | **edit `DATA`** → artifacts/<run>/metrics.csv + normalized alert CSV |
| `scorecard.html` | s8 | **edit `DATA`** → filled scorecard in the eval README |
| `outro.html` | s9 | edit repo URL + commit hash |

`metrics.html` and `scorecard.html` ship with clearly-labelled SAMPLE data and a ⚠ banner.
Replace the `DATA = {…}` block at the bottom of each with your real numbers before publishing,
then remove the banner line.
