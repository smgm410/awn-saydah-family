# Awn and Saydah Family History

Static family-history website, deployed on Netlify from `main` (no build step on Netlify). `img/` holds the document images (thumbnails end in `-t.jpg`). The "Share something" form uses Netlify Forms (including file uploads).

## How to edit (multi-page build)
1. Edit the content in `src/site.html` (the single-page source). Never edit the generated pages by hand.
2. Run `python3 -I tools/build.py`. It writes `index.html`, `part-one.html`, `part-two.html`, `part-three.html`, `descendants.html`, `documents.html`, `people.html`, `journey.html`, `researchers.html`, `search.html`, `site.css`, `site.js`, `search.js` and `search-index.json`.
3. Commit the source **and** the generated files, then push. Styles live in `tools/extra.css`, scripts in `tools/site.js` and `tools/search.js`.

## Photographs (standing rule)
Every family photograph must open in the viewer fitted to the screen. Give the full-size `<img>` inside the item's `.pics` the class `photo` (`<img class="photo" loading="lazy" data-src="img/XXXX.jpg" ...>`); the CSS rule `#lb .pics img.photo:not(.zoom)` caps its height to the window (clicking still zooms). Save photo files without phone metadata. Newspaper pages and documents are not photos and do not get the class.
