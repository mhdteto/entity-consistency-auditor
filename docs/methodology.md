# Methodology

The auditor compares **supplied observations** with a **supplied approved record**. Neither input is independently verified.

For each observation, each specified canonical field produces one result:

1. An empty or whitespace-only observation is `missing`.
2. A nonempty description is `manual_review`, regardless of text equality or aliases.
3. Other fields are normalized with Unicode NFKC, whitespace splitting/joining and Unicode casefold, in that order.
4. Equality with the normalized canonical value is `match`.
5. Equality with an explicitly listed normalized alias is `approved_alias`.
6. Otherwise the result is `mismatch`.

The original strings remain in JSON/HTML. NFKC intentionally equates compatibility characters such as full-width Latin letters. Casefold can equate Unicode case variants beyond ASCII; this is an explicit normalization policy, not an assertion of identity. Accent marks remain significant. There is no accent removal, transliteration, translation, fuzzy similarity, employer inference or semantic model.

An omitted canonical field generates no result. Description review cannot be bypassed by an alias. A legal subsidiary, previous employer, personal brand or translated trading name must be reviewed by a human before any alternative is approved. Aliases are global to a run, with no automatic date, market or language scoping.

## Exports

`report.json` includes schema version, as-of date, identity record, observation count, counts by status and detailed results. Counts are field outcomes, not a probability, search ranking or authority measure. Unseen fields and pages cannot be inferred from these counts.

`report.csv` uses explicit LF row terminators and quotes every cell for reproducible exports across platforms while preserving embedded carriage returns and contains one row per field result: source URL, observation date, language, market, field, canonical value, observed value and status. Formula-like strings beginning with `=`, `+`, `-`, `@` after leading whitespace and/or Unicode BOM characters, or with tab/carriage-return/newline, receive a leading apostrophe. This changes the CSV representation for safer spreadsheet import; JSON remains the exact-value interchange format. Preserve apostrophes when importing CSV; removing them can reactivate formulas.

`report.html` escapes all supplied text and attributes. Only input-validated HTTP/HTTPS URLs become clickable links. It contains no script, embedded remote resource or network request. Clicking a source link opens that supplied site and is outside the audit. Raw JSON values are not HTML or spreadsheet sanitized: downstream consumers must encode them for their destination.

Output order follows input row order and canonical field order (`name`, `role`, `organization`, `description`). Fixed inputs and a fixed as-of date yield reproducible report content; output files contain no current timestamp or random identifier. All input validation occurs before writing. Successful repeated runs overwrite the three report files; I/O errors may leave partial reports.

Before any report file is written, all three output paths and both input paths are resolved, including symbolic link destinations. Existing output files are also compared with each input using file identity (`Path.samefile`) to catch hard links. If any output would overwrite either input, the run fails with exit code `2` without writing any report. Keep inputs and exports in separate locations.
