# Input format

Use UTF-8 JSON and CSV (UTF-8 BOM is accepted). One canonical entity per run. All strings preserve their original value in JSON output.

## Canonical JSON

```json
{
  "entity_id": "fictional-person-001",
  "entity_type": "person",
  "name": "Élodie Tan",
  "role": "Research Director",
  "organization": "Aster Meridian Lab",
  "description": "Fictional research leader used solely for this example.",
  "aliases": {"role": ["Directrice de recherche"]}
}
```

`entity_id`, `entity_type` and `name` are required nonempty strings. `entity_type` is exactly `person` or `organization`. `role`, `organization` and `description` are optional nonempty strings; omit unknown canonical fields rather than using empty strings or null. Unknown keys and duplicate JSON keys are rejected.

`aliases` is an optional object whose keys are canonical comparison fields (`name`, `role`, `organization`, `description`) and whose values are arrays of nonempty strings. The corresponding canonical field must exist. Description aliases are retained as supplied context but never produce automatic agreement: descriptions always require human review. Aliases do not alter canonical values and are approved by the input author, not the software. Do not put a different person or legal entity in an alias list merely because the names look similar.

## Observations CSV

Exactly these eight unique column headers are required, in any order:

```csv
source_url,observed_at,language,market,name,role,organization,description
```

Every row must contain eight cells. At least one row is required. Quote commas, double quotes and newlines using ordinary CSV rules. Empty observed fields are allowed; they are never agreement. `language` and `market` are free-text supplied context, not validated language/country codes, and may be empty.

`source_url` must be an absolute HTTP or HTTPS URL with a host, no credentials, no whitespace or control characters, and a syntactically valid port if present. No URL is requested or checked for existence. Store credentials separately; never place secrets in input files.

`observed_at` must be an actual calendar date in exactly `YYYY-MM-DD` format and cannot exceed `--as-of`. Date-times and ambiguous local date formats are rejected. The default as-of date is the machine's local date; examples explicitly pin it to `2026-11-01`.

A duplicate observation is the same literal URL, date, normalized language and normalized market. Duplicate rows are rejected even when field values disagree. Different dates or language/market contexts for the same source are allowed and counted as separate observations. URL spelling variants, redirects and tracking parameters are not deduplicated; keep source identifiers consistent yourself.

Malformed JSON/CSV, missing files, invalid UTF-8, unknown headers, duplicate headers and malformed rows produce an error with exit code `2`. Do not use a generated `report.json` or `report.csv` as an input file in the same output directory.

The auditor refuses output collisions with either input before writing any reports. This includes a report filename that is a symbolic link or hard link to an input, regardless of its extension. Existing files are compared by file identity as well as resolved path.
