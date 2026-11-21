# Data use

Venture Evidence Explorer records **where** a public fact about an early New Zealand venture was published, **when** it became public, and a short paraphrase of what the source says. It does not republish the sources themselves.

## What goes in

- **Public sources only.** Sources include news articles, press releases, fund portfolio pages, university and institute pages, published reports (for example PwC / NZGCP Young Company Finance tables) and the NZ Companies Office register. Every claim carries its URL, its publisher, its publication or capture date, and the date we retrieved it.
- **Short paraphrased passages.** Passages are written in our own words and point to a locator (a page, row or paragraph). Any direct quote is kept under about 25 words, and most claims contain none. Images in the repository are captures of this application only, with no third-party logos or photos.
- **Hand-checked entries.** Each entry and follow-up event is added by a person through the sourced-event path. Packet validation checks dates, labels and witness rules before anything is imported.

## What stays out

- **No bulk or automated extraction** from Dealroom, Crunchbase, PitchBook, LinkedIn or any other subscription or terms-restricted database. A LinkedIn post may be cited only if it was read by hand, with its URL and date recorded.
- **No scraping of sites that refuse automated access.** For example, PwC's PDFs are checked by hand in a browser.
- **No private or confidential data** in the public-source cohort. Partner or portfolio data, if added, goes in separate permissioned packets under the same witness rules.
- **No inferred facts presented as stated.** A label or value that goes beyond its source is recorded as inferred, or as unknown. Unknown is never turned into "No".

## Requesting a correction or removal

If you are a founder, investor, publisher or anyone else who thinks a record is wrong, out of date, or should not be here, contact the project owner through the channel you received this from. If you have repository access, you can open a GitHub issue instead. Please include:

1. the company name and the record or screen you are looking at;
2. what is wrong, and what you believe is correct;
3. a public, dated source for the correction, if you have one.

We aim to reply within five working days. A correction is applied through the normal sourced-event path, so the original claim, the correction and the reason stay in the audit trail. A removal request about third-party content is honoured by deleting the passage and keeping only the citation, or by deleting the record entirely where that is appropriate. Open data questions and decisions are tracked in [STATUS.md](STATUS.md).
