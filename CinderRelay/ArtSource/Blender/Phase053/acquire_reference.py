"""Fetch only pinned, hash-verified CC0 authoring inputs into an ignored evaluation directory.

No marketplace content, credentials, executable source, or asset library downloads.
The two license documents describe the upstream program/data distinction; no program is executed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument('--output-dir', required=True)
args = parser.parse_args()
destination = Path(args.output_dir).resolve()
destination.mkdir(parents=True, exist_ok=True)
manifest = json.loads(Path(__file__).with_name('upstream-manifest.json').read_text(encoding='utf-8-sig'))
for item in manifest['files']:
    path = destination / item['name']
    if path.exists():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'], f'Preserving mismatched existing file: {path}'
        continue
    with urllib.request.urlopen(item['url'], timeout=30) as response:
        content = response.read()
    assert len(content) == item['bytes'] and hashlib.sha256(content).hexdigest() == item['sha256'], item['name']
    with path.open('xb') as output:
        output.write(content)
print(f'CR053_REFERENCE_VERIFIED files={len(manifest["files"])} output={destination}')
