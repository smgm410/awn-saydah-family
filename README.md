# Awn and Saydah Family History

Static family-history website. `index.html` is the page; `img/` holds the document images (thumbnails end in `-t.jpg`).
The "Share something" form uses Netlify Forms (including file uploads), so deploy on Netlify.

## Photographs (standing rule)
Every family photograph must open in the viewer fitted to the screen. Give the full-size `<img>` inside the item's `.pics` the class `photo` (`<img class="photo" loading="lazy" data-src="img/XXXX.jpg" ...>`); the CSS rule `#lb .pics img.photo:not(.zoom)` caps its height to the window (clicking still zooms). Save photo files without phone metadata. Newspaper pages and documents are not photos and do not get the class.
