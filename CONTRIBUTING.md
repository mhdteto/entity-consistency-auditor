# Contributing

Run `python3 -m unittest discover -s tests -v` and the README examples with Python 3.10+. Use only standard-library dependencies. Add a failing regression test before changing comparison or validation behavior, then confirm the complete suite passes. Keep examples fictional and free of credentials and personal information.

Document normalization changes explicitly: they can change previously reported outcomes. Preserve the distinction between supplied consistency and truth. Do not introduce ranking claims or automatic semantic description agreement. Regenerate `examples/output` with the fixed documented as-of date when output behavior changes. Explain the problem, resulting behavior and validation in your pull request.

Code contributions use MIT; documentation and fictional examples use CC BY 4.0 as described in the license files.

## Choose a contribution route

- [Bug or documentation error](https://github.com/mhdteto/entity-consistency-auditor/issues/new?template=bug_report.yml): include a release tag or commit and a minimal public/fictional reproducer.
- [Feature request](https://github.com/mhdteto/entity-consistency-auditor/issues/new?template=feature_request.yml): state the task, example and proposed behavior.
- [Source or methodology proposal](https://github.com/mhdteto/entity-consistency-auditor/issues/new?template=source_proposal.yml): provide the specific claim, publisher, dates, market, relationship and limits.

Run the documented validation and preserve the distinction between observed, supplied, inferred and unknown. See the [connected fictional workflow](https://github.com/mhdteto/authority-architecture-system/tree/main/examples/fictional-workflow) for an example.
