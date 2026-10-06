# Farmàcia Agramonte — website

### 👉 **<https://maragramonte.github.io/Farmacia-Agramonte/>**

> **The full documentation is [`README.md`](README.md), in Spanish, and it is
> the authoritative one.** This page is a short orientation for anyone who runs
> into the repository: what it is, how to run it and where to edit what. It
> deliberately repeats no counts, no legal reasoning and no history of past
> fixes — those live in the Spanish document and would go stale here.

Landing site for a neighbourhood pharmacy in Plaça de la Llana (El Born,
Barcelona). In **Spanish, Catalan and English**.

## What this is

A **static site**: HTML and CSS, no dependencies, no build step, no application
server. The only thing that runs in a visitor's browser is `cesta.js`, the
basket — just over five hundred lines, no libraries. There is no `npm`, no
`node_modules` and nothing to compile. A text editor and Python are enough.

It is published on GitHub Pages and every `git push` to `main` republishes it.

**It is not a shop.** The basket writes a WhatsApp message with the order; the
pharmacy prepares it and the customer pays at the counter. No payment gateway,
no accounts, no personal data collected, no external requests at all — the
fonts are served from this repository, not from Google Fonts.

## Running it

```
python servir.py            # port 8000, opens the browser
python servir.py 3000       # another port
python servir.py --no-abrir # without opening the browser
```

On Windows, double-clicking `servir.bat` does the same. On start it prints two
addresses: `localhost` and this machine's IP on the local network — the second
one is for opening the site on a phone over the same wifi.

Opening `index.html` directly works too, but the path will be `file://` and a
few things behave differently from production.

## How it is built

Most of the site is **generated**. One command rewrites it:

```
python herramientas/catalogo.py
```

It reads two JSON files and writes the category pages, the product pages, the
about page, the basket, the translated home pages and `sitemap.xml`, in all
three languages. Almost nothing under version control is meant to be edited by
hand — generated files say so in a comment at the top.

The generator **stops and explains itself** rather than writing something
wrong: if a Spanish fragment of the home page no longer matches its translation
pair, if a product name collides with another URL, if a photo named in the JSON
is missing. That is deliberate and it is the main reason the site is generated
instead of copied.

## Where to edit what

| To change… | Edit… |
|---|---|
| Products: names, summaries, pack sizes | `herramientas/catalogo-datos.json` |
| Any interface text: menu, buttons, footer, basket, the about page | `herramientas/textos.json` |
| The Spanish home page | `index.html` (the Catalan and English ones are generated from it) |
| Legal pages | `aviso-legal.html`, `privacidad.html`, `cookies.html` — and their copies under `ca/` and `en/`, all written by hand |
| Product photos | drop the file into `fotos/` — see `fotos/LEEME.txt` |
| Colours, type, layout | `portada.css` (home), `marca.css` + `catalogo.css` (catalogue), `legal.css` (text pages) |

Then run the generator again.

## Three languages

Spanish lives at the root, Catalan under `ca/` and English under `en/`. The
Spanish URLs were published first and are indexed, so they stay where they are
and other languages are added on top — adding English did not change a single
existing URL.

Translations are not a separate copy of the site. Interface strings carry
their languages together in `herramientas/textos.json`; product fields accept
either a plain string (meaning "same in every language", which is what a brand
name needs) or an object with one key per language. Anything untranslated
falls back to Spanish and the generator reports how many are missing, so a
language can be filled in gradually without ever leaving a blank on the page.

`herramientas/acentos.py` checks the spelling mistakes Spanish and Catalan
invite in each other. They are warnings, not corrections.

## Styling

A single intentional theme, not light/dark: it is a brand identity, so it looks
the same for everyone. Ink `#2a1d12`, cream `#f5f0e6`, gold `#c9a055`, with
Playfair Display for headings and Karla for body text, both self-hosted under
`tipografias/` with their OFL licences.

Note that the site has **three headers and three footers**, one per family of
pages, which do not share a stylesheet. Anything meant to appear "everywhere"
has to be written in all three. The Spanish README maps them.

## Licence

The code, the texts and the design belong to the pharmacy. `LICENSE` says what
may be done with them — it is **not** an open-source licence. The repository
being public grants nothing: any static site downloads in full into the
visitor's browser anyway.
