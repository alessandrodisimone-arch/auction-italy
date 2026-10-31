# auction-italy

Sito di [auction-italy.com](https://www.auction-italy.com): assistenza alle aste immobiliari del Tribunale di Fermo, in inglese e italiano.

## Struttura

- `src/en/`, `src/it/`: contenuto delle pagine (una per file, stesso nome nelle due lingue)
- `data/properties.json`: esempi di aste passate mostrati nelle schede
- `data/auctions.json`: aste aperte scelte a mano (vetrina). Campi: `id`, `category` (seaside, countryside, mountain, historic, modern, heritage, fixer), `town`, `title` {en, it}, `size`, `base_price`, `min_offer` (facoltativo), `date` (`AAAA-MM-GG` o `AAAA-MM-GGTHH:MM`), `features` {en, it}, `link` (annuncio ufficiale), `image` (facoltativo, solo foto con diritti d'uso). Le aste con data passata non vengono mostrate.
- `static/`: CSS, JavaScript, immagini, `_redirects`
- `build.py`: genera il sito in `public/` (solo Python 3, nessuna dipendenza)

## Anteprima in locale

```
python3 build.py
python3 -m http.server -d public 8000
```

## Pubblicazione

Netlify legge `netlify.toml`: esegue `python3 build.py` e pubblica `public/`. Il modulo contatti usa Netlify Forms.
