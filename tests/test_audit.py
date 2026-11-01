import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HEADERS = ['source_url', 'observed_at', 'language', 'market', 'name', 'role', 'organization', 'description']


class AuditTests(unittest.TestCase):
    def run_audit(self, identity=None, rows=None, headers=None, raw_identity=None):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        directory = Path(self.temp.name)
        identity = identity if identity is not None else {'entity_id': 'fictional-1', 'entity_type': 'person', 'name': 'Élodie Tan', 'role': 'Director', 'description': 'Fictional leader'}
        (directory / 'identity.json').write_text(raw_identity if raw_identity is not None else json.dumps(identity), encoding='utf-8')
        rows = rows if rows is not None else [['https://example.com/a', '2026-10-01', 'fr', 'FR', 'Élodie Tan', 'Director', '', 'Fictional leader']]
        with (directory / 'profiles.csv').open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(headers if headers is not None else HEADERS)
            writer.writerows(rows)
        process = subprocess.run([sys.executable, str(ROOT / 'audit.py'), '--identity', str(directory / 'identity.json'), '--profiles', str(directory / 'profiles.csv'), '--output-dir', str(directory / 'reports'), '--as-of', '2026-11-01'], capture_output=True, text=True)
        self.directory = directory
        return process

    def report(self):
        return json.loads((self.directory / 'reports/report.json').read_text())

    def test_output_symlinks_cannot_overwrite_either_input(self):
        for source in ('identity.json', 'profiles.csv'):
            for extension in ('json', 'csv', 'html'):
                with self.subTest(source=source, extension=extension):
                    self.assertEqual(self.run_audit().returncode, 0)
                    directory = self.directory
                    output = directory / 'collision'
                    output.mkdir()
                    (output / f'report.{extension}').symlink_to(directory / source)
                    before = {name: (directory / name).read_bytes() for name in ('identity.json', 'profiles.csv')}
                    process = subprocess.run([sys.executable, str(ROOT / 'audit.py'), '--identity', str(directory / 'identity.json'), '--profiles', str(directory / 'profiles.csv'), '--output-dir', str(output), '--as-of', '2026-11-01'], capture_output=True, text=True)
                    self.assertEqual(process.returncode, 2, process.stderr)
                    self.assertIn('overwrite input', process.stderr)
                    self.assertEqual({name: (directory / name).read_bytes() for name in before}, before)
                    self.assertEqual(len(list(output.iterdir())), 1, 'No report may be written before refusing the collision')

    def test_output_hardlinks_cannot_overwrite_either_input(self):
        for source in ('identity.json', 'profiles.csv'):
            for extension in ('json', 'csv', 'html'):
                with self.subTest(source=source, extension=extension):
                    self.assertEqual(self.run_audit().returncode, 0)
                    directory = self.directory
                    output = directory / 'collision'
                    output.mkdir()
                    os.link(directory / source, output / f'report.{extension}')
                    before = {name: (directory / name).read_bytes() for name in ('identity.json', 'profiles.csv')}
                    process = subprocess.run([sys.executable, str(ROOT / 'audit.py'), '--identity', str(directory / 'identity.json'), '--profiles', str(directory / 'profiles.csv'), '--output-dir', str(output), '--as-of', '2026-11-01'], capture_output=True, text=True)
                    self.assertEqual(process.returncode, 2, process.stderr)
                    self.assertIn('overwrite input', process.stderr)
                    self.assertEqual({name: (directory / name).read_bytes() for name in before}, before)
                    self.assertEqual(len(list(output.iterdir())), 1, 'No report may be written before refusing the collision')

    def test_direct_output_path_cannot_overwrite_either_input(self):
        for source, target in (('identity.json', 'report.json'), ('profiles.csv', 'report.csv')):
            with self.subTest(source=source):
                self.assertEqual(self.run_audit().returncode, 0)
                directory = self.directory
                source_path = directory / source
                moved = directory / target
                source_path.rename(moved)
                identity = moved if source == 'identity.json' else directory / 'identity.json'
                profiles = moved if source == 'profiles.csv' else directory / 'profiles.csv'
                before = {p: p.read_bytes() for p in (identity, profiles)}
                process = subprocess.run([sys.executable, str(ROOT / 'audit.py'), '--identity', str(identity), '--profiles', str(profiles), '--output-dir', str(directory), '--as-of', '2026-11-01'], capture_output=True, text=True)
                self.assertEqual(process.returncode, 2, process.stderr)
                self.assertIn('overwrite input', process.stderr)
                self.assertEqual({p: p.read_bytes() for p in before}, before)
                self.assertFalse((directory / 'report.html').exists())

    def test_exact_identity_and_description_requires_review(self):
        result = self.run_audit()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.report()['results'][0]['status'], 'match')
        description = [r for r in self.report()['results'] if r['field'] == 'description'][0]
        self.assertEqual(description['status'], 'manual_review')

    def test_unicode_normalization_case_and_whitespace(self):
        result = self.run_audit(rows=[['https://example.com', '2026-10-01', '', '', '  E\u0301LODIE  TAN ', 'Ｄｉｒｅｃｔｏｒ', '', '']])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([r['status'] for r in self.report()['results']][:2], ['match', 'match'])

    def test_accent_not_erased(self):
        self.assertEqual(self.run_audit(rows=[['https://example.com', '2026-10-01', '', '', 'Elodie Tan', 'Director', '', '']]).returncode, 0)
        self.assertEqual(self.report()['results'][0]['status'], 'mismatch')

    def test_explicit_alias(self):
        result = self.run_audit(identity={'entity_id': 'x', 'entity_type': 'organization', 'name': 'Example Lab', 'aliases': {'name': ['Example Laboratory']}}, rows=[['https://example.com', '2026-10-01', 'en', 'GB', 'Example Laboratory', '', '', '']])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.report()['results'][0]['status'], 'approved_alias')

    def test_missing_observation_never_agreement(self):
        self.assertEqual(self.run_audit(rows=[['https://example.com', '2026-10-01', '', '', '', '', '', '']]).returncode, 0)
        self.assertTrue(all(r['status'] == 'missing' for r in self.report()['results']))

    def test_unspecified_fields_not_evaluated(self):
        self.assertEqual(self.run_audit(identity={'entity_id': 'x', 'entity_type': 'person', 'name': 'A'}).returncode, 0)
        self.assertEqual([r['field'] for r in self.report()['results']], ['name'])

    def test_unsafe_formula_and_html_exports(self):
        payload = '=HYPERLINK("evil")<script>alert(1)</script>'
        result = self.run_audit(identity={'entity_id': 'x', 'entity_type': 'person', 'name': payload}, rows=[['https://example.com/?x=<b>', '2026-10-01', '@evil', ' +formula', payload, '', '', '']])
        self.assertEqual(result.returncode, 0, result.stderr)
        html = (self.directory / 'reports/report.html').read_text()
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)
        with (self.directory / 'reports/report.csv').open(newline='') as stream:
            exported = list(csv.DictReader(stream))[0]
        self.assertTrue(exported['observed'].startswith("'="))
        self.assertTrue(exported['language'].startswith("'@"))
        self.assertTrue(exported['market'].startswith("' +"))

    def test_bom_prefixed_formulas_are_neutralized_in_csv(self):
        for payload in ('\ufeff=1+1', '  \ufeff  @SUM(1)', '\ufeff\ufeff+1', '\t\ufeff-1'):
            with self.subTest(payload=payload):
                result = self.run_audit(identity={'entity_id': 'x', 'entity_type': 'person', 'name': payload}, rows=[['https://example.com', '2026-10-01', '', '', payload, '', '', '']])
                self.assertEqual(result.returncode, 0, result.stderr)
                with (self.directory / 'reports/report.csv').open(newline='') as stream:
                    exported = list(csv.DictReader(stream))[0]
                self.assertEqual(exported['observed'], "'" + payload)
                self.assertEqual(exported['canonical'], "'" + payload)
                self.assertEqual(self.report()['results'][0]['observed'], payload)

    def test_invalid_dates(self):
        for value in ['2026-02-30', '01/10/2026', '', '2026-10-01T12:00:00']:
            with self.subTest(value=value):
                result = self.run_audit(rows=[['https://example.com', value, '', '', 'A', '', '', '']])
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn('observed_at', result.stderr)

    def test_future_date(self):
        result = self.run_audit(rows=[['https://example.com', '2026-11-02', '', '', 'A', '', '', '']])
        self.assertEqual(result.returncode, 2)
        self.assertIn('future', result.stderr)

    def test_duplicate_sources(self):
        row = ['https://example.com', '2026-10-01', '', '', 'A', '', '', '']
        result = self.run_audit(rows=[row, row])
        self.assertEqual(result.returncode, 2)
        self.assertIn('duplicate', result.stderr)

    def test_unsafe_or_missing_url(self):
        for url in ['', 'javascript:alert(1)', 'file:///tmp/a', 'https://', 'https://user:secret@example.com', 'https://example.com\nattack']:
            with self.subTest(url=url):
                result = self.run_audit(rows=[[url, '2026-10-01', '', '', 'A', '', '', '']])
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn('source_url', result.stderr)

    def test_invalid_headers(self):
        result = self.run_audit(headers=['source_url', 'observed_at'])
        self.assertEqual(result.returncode, 2)
        self.assertIn('headers', result.stderr)

    def test_malformed_json(self):
        result = self.run_audit(raw_identity='{bad')
        self.assertEqual(result.returncode, 2)
        self.assertNotIn('Traceback', result.stderr)

    def test_duplicate_json_keys(self):
        result = self.run_audit(raw_identity='{"entity_id":"x","entity_type":"person","name":"A","name":"B"}')
        self.assertEqual(result.returncode, 2)

    def test_invalid_identity_types_and_aliases(self):
        for identity in [{}, [], {'entity_id': 'x', 'entity_type': 'product', 'name': 'A'}, {'entity_id': 'x', 'entity_type': 'person', 'name': 'A', 'aliases': {'name': 'B'}}, {'entity_id': 'x', 'entity_type': 'person', 'name': 'A', 'aliases': {'role': ['CEO']}}, {'entity_id': 'x', 'entity_type': 'person', 'name': 3}]:
            with self.subTest(identity=identity):
                self.assertEqual(self.run_audit(identity=identity).returncode, 2)

    def test_empty_profiles_rejected(self):
        self.assertEqual(self.run_audit(rows=[]).returncode, 2)

    def test_wrong_row_length_rejected(self):
        self.assertEqual(self.run_audit(rows=[['https://example.com', '2026-10-01']]).returncode, 2)


if __name__ == '__main__':
    unittest.main()
