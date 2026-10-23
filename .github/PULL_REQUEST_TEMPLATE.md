## Summary

What a visitor can do after this change.

## Why

The reason the change belongs in Potato Fan Club.

## Test plan

- [ ] `python3 scripts/check_site.py`
- [ ] Home: click the potato, reveal a fact, join with a plain name
- [ ] Home: join with a name that includes `<b>hi</b>` and confirm it shows as text
- [ ] Stats: rate a potato, change the background, type a short string and a longer one
- [ ] Screenshots updated if the pages look different

## Notes

No secrets in the diff. User-typed text still goes through `textContent`.
