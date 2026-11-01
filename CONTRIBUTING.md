# Contributing

Run `python3 -m unittest discover -s tests -v` and the README examples with Python 3.10+. Use only standard-library dependencies. Add a failing regression test before changing comparison or validation behavior, then confirm the complete suite passes. Keep examples fictional and free of credentials and personal information.

Document normalization changes explicitly: they can change previously reported outcomes. Preserve the distinction between supplied consistency and truth. Do not introduce ranking claims or automatic semantic description agreement. Regenerate `examples/output` with the fixed documented as-of date when output behavior changes. Explain the problem, resulting behavior and validation in your pull request.

Code contributions use MIT; documentation and fictional examples use CC BY 4.0 as described in the license files.
