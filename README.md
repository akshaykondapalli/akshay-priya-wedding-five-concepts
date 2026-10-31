# Five invitation concepts — design review (Akshay & Priya)

Five independent, mobile-first interactive invitation concepts for review. **This is a design-review site, not the official wedding invitation.** No concept has been chosen.

| # | Concept | Folder |
|---|---------|--------|
| 01 | Letters Across Continents | `site/letters/` |
| 02 | The Courtyard of Blessings | `site/courtyard/` |
| 03 | Nine Fifty-Five Under the Stars | `site/stars/` |
| 04 | The Royal Botanical Letter | `site/botanical/` |
| 05 | The Temple of Two Souls | `site/temple/` |

Comparison page: `site/index.html`. Live: https://akshaykondapalli.github.io/akshay-priya-wedding-five-concepts/

## Source of truth (wedding only)
- Akshay & Priya
- Saturday, 21 November 2026
- Wedding dinner 8:00 PM IST · Muhurtham 9:55 PM IST
- Priyanka Convention, Nallajerla, Andhra Pradesh, India

No other functions appear anywhere in `site/`. A CI guard fails the deploy if excluded ceremony wording appears.

## Photo and music
- The only photograph is the couple's own reference image, cropped to remove video-player controls and burned-in text. Faces are never redrawn, generated or altered. The photo is not used in link-preview images.
- No music file was supplied. Concepts with music synthesise an original instrumental live in the browser with the Web Audio API (drone plus bell-like phrases on the Mohanam scale). It is off by default and starts only when the guest taps play. There are no third-party recordings.

## Layout
- `site/`: the only folder deployed to GitHub Pages. Static files, relative paths, self-hosted fonts, no tracking.
- `tools/`: scripts that generated each concept's original artwork, plus the QA capture script.
- `reference/`: the original concept previews, README, prompt and board from the hand-off package.

## Public by design
GitHub Pages is public. Pages carry `noindex`, but anyone with the link can open them.
