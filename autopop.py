#!/usr/bin/env python3
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

# Config
# Resolve project root even when this script is inside the `docs/` folder
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent if SCRIPT_DIR.name == "docs" else SCRIPT_DIR
DOCS_JSON = ROOT / "docs/docs.json"
OPENAPI_JSON = ROOT / "docs/deribit_openapi.json"

# Ignore these OpenAPI tags when populating pages
IGNORED_TAGS = {"public", "chat", "websocket only"}

# Tags we care about -> slug mapping used in docs.json groups (lowercase-hyphenated)
def tag_to_group_slug(tag_name: str) -> str:
    return tag_name.strip().lower().replace(" ", "-")

def is_ignored_tag(tag_name: str) -> bool:
    return tag_name.strip().lower() in IGNORED_TAGS

def generate_page_slug(http_method: str, openapi_path: str) -> str:
    # Example: GET + /private/get_positions -> get-privateget_positions
    method_part = http_method.lower()
    path_part = openapi_path.lstrip("/").replace("/", "")
    return f"{method_part}-{path_part}"

def to_page_path(tag_name: str, page_slug: str) -> str:
    # Example: Session Management + get-publicset_heartbeat -> api-reference/session-management/get-publicset_heartbeat
    return f"api-reference/{tag_to_group_slug(tag_name)}/{page_slug}"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

def extract_tagged_pages_from_openapi(openapi: dict) -> dict:
    # Returns: { tag_name (original): [page_path, ...] }
    tag_to_pages = defaultdict(list)
    paths = openapi.get("paths", {})

    for openapi_path, methods in paths.items():
        if not isinstance(methods, dict):
            continue

        for http_method, op in methods.items():
            if http_method.lower() not in ("get", "post", "put", "patch", "delete", "options", "head"):
                continue
            if not isinstance(op, dict):
                continue

            tags = op.get("tags", [])
            if not tags:
                continue

            slug = generate_page_slug(http_method, openapi_path)
            for tag in tags:
                if is_ignored_tag(tag):
                    continue
                # Only attach to known top-level tags; keep original tag names (not slug) for display mapping
                page_path = to_page_path(tag, slug)
                tag_to_pages[tag].append(page_path)

    # Sort pages within each tag for consistent output
    for tag in tag_to_pages:
        tag_to_pages[tag] = sorted(set(tag_to_pages[tag]))

    return tag_to_pages

def find_methods_tab(docs: dict):
    tabs = docs.get("navigation", {}).get("tabs", [])
    for tab in tabs:
        if isinstance(tab, dict) and tab.get("tab") == "Methods":
            return tab
    return None

def find_api_v2_group(methods_tab: dict):
    groups = methods_tab.get("groups", [])
    for grp in groups:
        if grp.get("group") == "Methods overview":
            return grp
    return None

def update_docs_groups_with_pages(docs: dict, tag_to_pages: dict) -> bool:
    methods_tab = find_methods_tab(docs)
    if not methods_tab:
        print("Could not find 'Methods' tab in docs.json", file=sys.stderr)
        return False

    api_v2 = find_api_v2_group(methods_tab)
    if not api_v2:
        print("Could not find 'API v2' group under 'Methods' in docs.json", file=sys.stderr)
        return False

    pages_groups = api_v2.get("pages", [])
    if not isinstance(pages_groups, list):
        print("'API v2'.pages is not a list", file=sys.stderr)
        return False

    # Build a temporary mapping from group slug to group object
    slug_to_group_obj = {}
    for group_obj in pages_groups:
        if not isinstance(group_obj, dict):
            continue
        group_name = group_obj.get("group")
        if not group_name:
            continue
        slug_to_group_obj[tag_to_group_slug(group_name)] = group_obj

    # Apply pages by matching tag names to group slug
    any_updates = False
    for tag_name, pages in tag_to_pages.items():
        slug = tag_to_group_slug(tag_name)
        group_obj = slug_to_group_obj.get(slug)
        if not group_obj:
            # Group not present in docs.json; skip silently to avoid adding new structural groups unexpectedly
            continue
        # Set/replace pages
        group_obj["pages"] = pages
        any_updates = True

    return any_updates

def main():
    if not Path(OPENAPI_JSON).is_file():
        print(f"OpenAPI file not found: {OPENAPI_JSON}", file=sys.stderr)
        sys.exit(1)
    if not Path(DOCS_JSON).is_file():
        print(f"docs.json not found: {DOCS_JSON}", file=sys.stderr)
        sys.exit(1)

    openapi = load_json(OPENAPI_JSON)
    docs = load_json(DOCS_JSON)

    tag_to_pages = extract_tagged_pages_from_openapi(openapi)

    updated = update_docs_groups_with_pages(docs, tag_to_pages)
    if not updated:
        print("No matching groups were updated (ensure your 'API v2' subgroups match OpenAPI tag names).")
        sys.exit(0)

    save_json(DOCS_JSON, docs)
    print(f"Updated {DOCS_JSON} with pages generated from {OPENAPI_JSON}")

if __name__ == "__main__":
    main()