# Connected fictional example

**Entirely fictional teaching data:** Alex Rowan, Cedar Notes, publishers, HTTP responses, reviews, engines and answers are invented. Reserved example domains are placeholders. No client case or live AI measurement is presented.

Run from the repository root:

```sh
python3 audit.py --identity examples/connected-workflow/inputs/identity.json --profiles examples/connected-workflow/inputs/profiles.csv --as-of 2026-11-01 --output-dir examples/connected-workflow/report
```

Inputs: [identity.json](inputs/identity.json) · [profiles.csv](inputs/profiles.csv)

## Expected output

Four supplied profiles: 6 matches, 2 approved aliases, 2 mismatched fields, 3 missing fields and 3 descriptions requiring manual review. These are field counts, not people or an authority score.

Inspect [the generated HTML](report/report.html) and [JSON](report/report.json). The command replaces the report directory’s output files; keep your own inputs elsewhere.

## Where this fits

[Follow the complete five-tool workflow](https://github.com/mhdteto/authority-architecture-system/tree/main/examples/fictional-workflow) · [Operating method](https://github.com/mhdteto/authority-architecture-system) · [Next: authority-evidence-mapper](https://github.com/mhdteto/authority-evidence-mapper)

These original synthetic inputs and reports use CC BY 4.0; the tool retains its existing code license. Verify reproduction with:

```sh
python3 tools/verify_connected_example.py
```
