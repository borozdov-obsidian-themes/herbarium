# Borozdov Herbarium

A theme from the Borozdov collection. Two faces — light **Linen**, a botanist's specimen
journal on warm linen, and dark **Moss**, the same journal under the forest canopy. Sage
annotations, one literary serif headline, monospace labels and crimson ink for what you act on.

![Borozdov Herbarium in light mode](https://raw.githubusercontent.com/borozdov-obsidian-themes/herbarium/main/screenshots/light.png)

![Borozdov Herbarium in dark mode](https://raw.githubusercontent.com/borozdov-obsidian-themes/herbarium/main/screenshots/dark.png)

## Principles

- **One serif anchor.** EB Garamond for the title, the largest heading and pull quotes —
  the literary opening of every page. Every other heading is the platform's sans, tracked
  tight.
- **Field-note labels.** Tags, table headers, callout titles, property names and the
  status bar are set in a monospace, in capitals, tracked open, like the labels on a
  pressed specimen.
- **Colour used organically.** Forest ink carries the text and the main button; sage fills
  a checked task and a toggle; eucalyptus washes tags and the open file; crimson marks
  links and the caret; an amber pin is the highlighter.
- **Specimen cards.** Callouts are light washes of their type's colour over bone, with a
  hairline edge and 10px corners; nothing casts a shadow.

## Features

- Light and dark modes, following Settings → Appearance → Base color scheme
- Pull quotes in the serif, a size up, behind a sage rule
- Tables as linen cards with a bone header band and monospace column labels
- Code blocks as terminal traces on bone with a hairline edge
- Quiet editing: no focus ring around the note, its title or form fields while you type;
  property names read as labels, not boxed fields
- Text colours meet WCAG contrast on both faces
- The phone layout keeps the same colours and shapes
- No `!important`: every rule can be overridden with a CSS snippet

## Installation

**From the community directory, as a variant:** this theme ships inside **Borozdov
Trellis**. Install Borozdov Trellis under Settings → Appearance → Themes → Manage, then
the [Style Settings](https://github.com/mgmeyers/obsidian-style-settings) plugin, and
choose **Herbarium** under Style Settings → Borozdov Trellis → Variant. The variant brings
this theme's palette, type and corners; its own layout, and its embedded font if it has
one, come with the full theme below.

**The full theme, by hand:** download `manifest.json` and `theme.css` from the
[latest release](https://github.com/borozdov-obsidian-themes/herbarium/releases/latest) into
`<vault>/.obsidian/themes/Borozdov Herbarium/`, then choose Borozdov Herbarium under
Settings → Appearance → Themes.

## Font

EB Garamond Regular (© 2017 The EB Garamond Project Authors) is embedded in `theme.css` as
base64 WOFF2 under the SIL Open Font License 1.1 — see [`fonts/OFL.txt`](fonts/OFL.txt).
One weight, Latin and Cyrillic, for the title, the largest heading and pull quotes only.
The monospace is your platform's own.

## License

MIT — see [LICENSE](LICENSE).

---

**По-русски.** Тема из коллекции Borozdov. Два лика: светлый «Лён» — дневник ботаника на
тёплом льне, и тёмный «Мох» — тот же дневник под пологом леса. Шалфейные пометки, один
литературный заголовок с засечками (EB Garamond), моноширинные ярлыки и малиновые чернила
для того, что вы делаете. В каталоге тема живёт вариантом Borozdov Trellis: установите Borozdov Trellis и плагин Style Settings, затем выберите Herbarium в Style Settings → Borozdov Trellis → Variant. Целиком, со своей вёрсткой, тема ставится вручную из последнего релиза репозитория.
