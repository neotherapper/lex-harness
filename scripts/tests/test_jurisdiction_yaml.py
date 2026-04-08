# scripts/tests/test_jurisdiction_yaml.py
import pytest
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).parent.parent.parent

REQUIRED_FIELDS = [
    "jurisdiction_id", "display_name", "primary_authoritative_sources",
    "fallback_sources", "source_priority", "trusted_source_whitelist",
    "mandatory_citation_formats", "pack_dir",
]

def find_jurisdiction_yamls():
    law_packs = REPO_ROOT / "law-packs"
    return list(law_packs.glob("*/jurisdiction.yaml"))

def load_yaml(path):
    try:
        return yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        pytest.fail(f"YAML parse error in {path}: {exc}")

@pytest.mark.parametrize("yaml_path", find_jurisdiction_yamls() or ["__no_yamls__"], ids=str)
def test_jurisdiction_yaml_has_required_fields(yaml_path):
    if str(yaml_path) == "__no_yamls__":
        pytest.skip("No jurisdiction.yaml files found yet")
    data = load_yaml(yaml_path)
    for field in REQUIRED_FIELDS:
        assert field in data, f"Missing '{field}' in {yaml_path}"

@pytest.mark.parametrize("yaml_path", find_jurisdiction_yamls() or ["__no_yamls__"], ids=str)
def test_source_priority_entries_all_defined(yaml_path):
    if str(yaml_path) == "__no_yamls__":
        pytest.skip("No jurisdiction.yaml files found yet")
    data = load_yaml(yaml_path)
    all_ids = {
        s["source_id"]
        for s in data.get("primary_authoritative_sources", []) + data.get("fallback_sources", [])
    }
    for sid in data.get("source_priority", []):
        assert sid in all_ids, f"source_priority entry {sid!r} not defined in sources in {yaml_path}"

@pytest.mark.parametrize("yaml_path", find_jurisdiction_yamls() or ["__no_yamls__"], ids=str)
def test_all_source_hostnames_in_whitelist(yaml_path):
    if str(yaml_path) == "__no_yamls__":
        pytest.skip("No jurisdiction.yaml files found yet")
    from urllib.parse import urlparse
    data = load_yaml(yaml_path)
    whitelist = data.get("trusted_source_whitelist", [])
    all_sources = data.get("primary_authoritative_sources", []) + data.get("fallback_sources", [])
    for s in all_sources:
        host = urlparse(s["url"]).hostname or ""
        bare = host.removeprefix("www.")
        assert host in whitelist or bare in whitelist, (
            f"Source {s['source_id']!r} URL {s['url']!r} hostname not in "
            f"trusted_source_whitelist in {yaml_path}"
        )
