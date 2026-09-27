# Contributing

Issues and pull requests are welcome.

## Reporting a problem

Open an issue with your Obsidian version, operating system, light or dark mode, and a
screenshot. If a plugin or a CSS snippet is involved, name it.

## Working on the theme

1. Clone the repository and link it into a test vault:
   `ln -s "$PWD" "<vault>/.obsidian/themes/Borozdov Herbarium"`
2. Choose Borozdov Herbarium under Settings → Appearance → Themes. After editing
   `theme.css`, run **Reload app without saving** from the command palette.
3. Lint with the rules the community directory applies: `npm install`, then
   `npm run lint`.
4. After a visible change, rerender the screenshots: `npm run screenshots`. It needs
   macOS with Obsidian and Google Chrome installed, and Pillow for Python. The theme is
   laid over Obsidian's own stylesheet, extracted from the installed app at run time;
   `screenshots/` is rewritten.

House rules:

- Obsidian's CSS variables first, plain selectors after; no `!important`, no `:has()`.
- Colors come from the palette in section 1 of `theme.css`; nothing else holds a color
  literal.
- Forest ink for the text and the main button, sage for fills, eucalyptus for tags and the
  open file, crimson for links and the caret, an amber pin for the highlighter; labels are
  monospace capitals. The only embedded font is EB Garamond Regular (the title, the
  largest heading and quotes): `fonts/*.woff2` are written into `theme.css` by
  `npm run fonts`.
- The release ships `dist/theme.css` from `npm run build`: the same file without
  comments. The build fails on any lint problem.

## Releasing

1. Bump `version` in `manifest.json` and add the same version to `versions.json`, mapped
   to the minimum Obsidian version it needs.
2. Commit, then push an annotated tag named with the bare version:
   `git tag -a 1.0.1 -m "1.0.1: …"` and `git push origin 1.0.1`.
3. The release workflow lints and builds the theme, checks the tag against
   `manifest.json` and `versions.json`, attests `manifest.json` and `dist/theme.css`, and
   publishes the GitHub release with both files attached. The tag message becomes the
   release notes.
4. Never delete a published release: the community directory keeps its own record of
   every version it has reviewed.
