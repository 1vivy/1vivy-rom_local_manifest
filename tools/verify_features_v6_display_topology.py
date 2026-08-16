"""Verify that features-v6 composes one native SM8850 display namespace."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FEATURE_MANIFEST = ROOT / "local_manifests/1vivy-features-v6.xml"
BASE_MANIFEST = ROOT / "local_manifests/1vivy-rom.xml"
COMMON_PROJECT = "OnePlus-SM8850-Development/android_hardware_qcom-caf_common"


class Refusal(ValueError):
    """A fail-closed manifest topology error."""


def parse_manifest(path: Path) -> ET.Element:
    try:
        return ET.parse(path).getroot()
    except (OSError, ET.ParseError) as exc:
        raise Refusal(f"cannot parse {path}: {exc}") from exc


def project_by_name(root: ET.Element, name: str) -> ET.Element:
    matches = [project for project in root.findall("project") if project.get("name") == name]
    if len(matches) != 1:
        raise Refusal(f"expected one project {name}, found {len(matches)}")
    return matches[0]


def require_project(root: ET.Element, name: str, path: str, revision: str) -> None:
    project = project_by_name(root, name)
    actual = (project.get("path"), project.get("revision"))
    expected = (path, revision)
    if actual != expected:
        raise Refusal(f"{name} expected path/revision {expected}, found {actual}")


def linkfiles(project: ET.Element) -> set[tuple[str, str]]:
    return {
        (linkfile.get("src") or "", linkfile.get("dest") or "")
        for linkfile in project.findall("linkfile")
    }


def validate() -> None:
    feature = parse_manifest(FEATURE_MANIFEST)
    base = parse_manifest(BASE_MANIFEST)

    require_project(
        feature,
        "1vivy/android_hardware_qcom_display",
        "hardware/qcom-caf/sm8850/display/hal",
        "staging/features-v6/all",
    )
    require_project(
        feature,
        "OnePlus-SM8850-Development/android_vendor_qcom_opensource_display-core",
        "hardware/qcom-caf/sm8850/display/core",
        "refs/heads/lineage-23.2-caf-sm8850",
    )
    require_project(
        feature,
        "OnePlus-SM8850-Development/android_vendor_qcom_opensource_display-intf",
        "hardware/qcom-caf/sm8850/display/intf",
        "refs/heads/lineage-23.2-caf-sm8850",
    )

    display = project_by_name(feature, "1vivy/android_hardware_qcom_display")
    if linkfiles(display):
        raise Refusal("SM8850 display HAL must not publish namespace alias linkfiles")

    feature_common = project_by_name(feature, COMMON_PROJECT)
    base_common = project_by_name(base, COMMON_PROJECT)
    if linkfiles(feature_common) != linkfiles(base_common):
        raise Refusal("features-v6 QCOM common linkfiles differ from the base manifest")


def main() -> int:
    try:
        validate()
    except Refusal as exc:
        print(f"REFUSED features-v6-sm8850-display-topology {exc}")
        return 1

    print("PASS features-v6-sm8850-display-topology hal=1 core=1 intf=1 aliases=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
