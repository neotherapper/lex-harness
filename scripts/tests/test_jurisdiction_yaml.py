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

@pytest.mark.parametrize("yaml_path", find_jurisdiction_yamls() or ["__no_yamls__"])
def test_jurisdiction_yaml_has_required_fields(yaml_path):
    if str(yaml_path) == "__no_yamls__":
        pytest.skip("No jurisdiction.yaml files found yet")
    data = yaml.safe_load(Path(yaml_path).read_text(encoding="utf-8"))
    for field in REQUIRED_FIELDS:
        assert field in data, f"Missing '{field}' in {yaml_path}"

@pytest.mark.parametrize("yaml_path", find_jurisdiction_yamls() or ["__no_yamls__"])
def test_source_priority_entries_all_defined(yaml_path):
    if str(yaml_path) == "__no_yamls__":
        pytest.skip("No jurisdiction.yaml files found yet")
    data = yaml.safe_load(Path(yaml_path).read_text(encoding="utf-8"))
    all_ids = {
        s["source_id"]
        for s in data.get("primary_authoritative_sources", []) + data.get("fallback_sources", [])
    }
    for sid in data.get("source_priority", []):
        assert sid in all_ids, f"source_priority entry {sid!r} not defined in sources in {yaml_path}"
