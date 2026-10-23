# Contributing to Potato Fan Club

Thanks for taking a look. The site is two HTML pages, one stylesheet, and two small scripts. A useful change is usually a few lines.

## Ground rules

- Keep the potato voice. The jokes, the clicker, the facts, and the stats page are the product.
- User-typed text is assigned with `textContent`. Do not use `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, or `eval` for it.
- Do not add a secret, token, or API key. If a change ever needs configuration, document the variable in `.env.example` and keep the value in an untracked `.env` file.
- Leave the behavior of the six buttons and the name checker as it is unless the pull request says why it should change.
- The Unsplash photo URLs are a known dependency. Replacing them with files in this repo is welcome. Hotlinking a new third party is not.

## Set up

```bash
git clone https://github.com/ryaneditraj/waffles-site.git
cd waffles-site
python3 -m http.server 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) and [http://127.0.0.1:8000/stats.html](http://127.0.0.1:8000/stats.html).

## Check before you open a pull request

```bash
python3 scripts/check_site.py
```

Then click through both pages: counter, fact, join (try a name that includes `<b>hi</b>` and confirm it shows up as text), rating, background color, and the length checker.

GitHub Actions runs the same Python script on pull requests.

## Pull requests

- Fork the repo and branch from `main`.
- Describe what a visitor can do after the change.
- Include a screenshot when the pages look different.
- Keep the diff focused. A fact-list change and a rewrite of the community docs are easier to review apart.

## Reporting issues

Use the bug report or feature request template. Security problems go through the process in [SECURITY.md](SECURITY.md), not a public issue.

By participating, you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).
