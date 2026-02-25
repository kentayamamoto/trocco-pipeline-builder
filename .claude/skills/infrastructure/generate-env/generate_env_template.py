#!/usr/bin/env python3
"""
.env.local テンプレート生成スクリプト

同ディレクトリの env-vars.json を読み取り、指定されたソース/デスティネーションの
組み合わせに必要な環境変数のみを含む .env.local テンプレートを生成する。

Usage:
    python3 .claude/skills/infrastructure/generate-env/generate_env_template.py --source kintone --destination snowflake
    python3 .claude/skills/infrastructure/generate-env/generate_env_template.py --source kintone --destination snowflake --dry-run
    python3 .claude/skills/infrastructure/generate-env/generate_env_template.py --source kintone --destination snowflake --force
    python3 .claude/skills/infrastructure/generate-env/generate_env_template.py --list-connectors
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path


def load_env_vars_json() -> dict:
    """同ディレクトリの env-vars.json をスクリプト位置からの相対パスで読み込む。"""
    script_dir = Path(__file__).resolve().parent
    json_path = script_dir / "env-vars.json"
    if not json_path.exists():
        print(f"Error: {json_path} が見つかりません。", file=sys.stderr)
        sys.exit(1)
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


def get_available_connectors(data: dict) -> tuple[list[str], list[str]]:
    """利用可能なソース/デスティネーション名のリストを返す。"""
    sources = list(data.get("sources", {}).keys())
    destinations = list(data.get("destinations", {}).keys())
    return sources, destinations


def format_variable_line(var: dict) -> str:
    """変数1つ分のテンプレート行を生成する。"""
    example = var.get("example", "")
    return f'{var["name"]}="{example}"'


def build_section_lines(connector: dict, role: str) -> list[str]:
    """コネクタ1つ分のセクション行を生成する。

    Args:
        connector: env-vars.json のコネクタ定義
        role: "ソース" or "デスティネーション"
    """
    lines = []
    display_name = connector["display_name"]
    description = connector.get("description", "")

    lines.append(f"# --- {display_name} {role} ---")
    if description:
        lines.append(f"# {description}")

    modes = connector.get("modes")
    if modes:
        for mode_key in sorted(modes.keys()):
            mode = modes[mode_key]
            label = mode["label"]
            mode_desc = mode.get("description", "")
            lines.append(f"# [{mode_key.upper()}] {label}:")
            if mode_desc:
                lines.append(f"#   {mode_desc}")
            for var in mode["variables"]:
                lines.append(format_variable_line(var))
    else:
        pass

    always = connector.get("always", [])
    if always:
        if modes:
            lines.append("# 共通:")
        for var in always:
            desc = var.get("description", "")
            if desc:
                lines.append(f"# {desc}")
            lines.append(format_variable_line(var))

    return lines


def generate_template(data: dict, source: str, destination: str) -> str:
    """テンプレート文字列を生成する。"""
    source_display = data["sources"][source]["display_name"]
    dest_display = data["destinations"][destination]["display_name"]

    lines = []
    lines.append("# TROCCO Pipeline Builder 環境変数テンプレート")
    lines.append(f"# Generated for: {source_display} -> {dest_display}")
    lines.append("#")
    lines.append("# このファイルは自動生成されました。各変数に適切な値を設定してください。")
    lines.append("")

    # Common section
    common = data["common"]
    lines.append(f"# === {common['description']} ===")
    for var in common["variables"]:
        desc = var.get("description", "")
        if desc:
            lines.append(f"# {desc}")
        lines.append(format_variable_line(var))
    lines.append("")

    # Source section
    source_connector = data["sources"][source]
    lines.extend(build_section_lines(source_connector, "ソース"))
    lines.append("")

    # Destination section
    dest_connector = data["destinations"][destination]
    lines.extend(build_section_lines(dest_connector, "デスティネーション"))
    lines.append("")

    return "\n".join(lines)


def list_connectors(data: dict) -> None:
    """利用可能なコネクタ一覧を表示する。"""
    sources, destinations = get_available_connectors(data)

    print("利用可能なコネクタ一覧:")
    print()
    print("ソース (--source):")
    for s in sources:
        display = data["sources"][s]["display_name"]
        print(f"  {s:30s} ({display})")

    print()
    print("デスティネーション (--destination):")
    for d in destinations:
        display = data["destinations"][d]["display_name"]
        print(f"  {d:30s} ({display})")


def main():
    parser = argparse.ArgumentParser(
        description=".env.local テンプレートを生成する"
    )
    parser.add_argument("--source", "-s", help="ソースコネクタ名")
    parser.add_argument("--destination", "-d", help="デスティネーションコネクタ名")
    parser.add_argument(
        "--output", "-o", default=".env.local", help="出力先パス (default: .env.local)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="stdoutに出力のみ（ファイル書き込みなし）"
    )
    parser.add_argument(
        "--force", action="store_true", help="確認なしで上書き"
    )
    parser.add_argument(
        "--list-connectors", action="store_true", help="利用可能なコネクタ一覧を表示"
    )
    args = parser.parse_args()

    data = load_env_vars_json()

    if args.list_connectors:
        list_connectors(data)
        sys.exit(0)

    if not args.source or not args.destination:
        parser.error("--source と --destination は必須です（--list-connectors 以外）")

    source = args.source.lower().replace(" ", "_")
    destination = args.destination.lower().replace(" ", "_")

    sources, destinations = get_available_connectors(data)

    if source not in sources:
        print(
            f"Error: ソース '{args.source}' は未対応です。",
            file=sys.stderr,
        )
        print(f"対応ソース: {', '.join(sources)}", file=sys.stderr)
        sys.exit(1)

    if destination not in destinations:
        print(
            f"Error: デスティネーション '{args.destination}' は未対応です。",
            file=sys.stderr,
        )
        print(f"対応デスティネーション: {', '.join(destinations)}", file=sys.stderr)
        sys.exit(1)

    template = generate_template(data, source, destination)

    if args.dry_run:
        print(template)
        sys.exit(0)

    output_path = Path(args.output)

    if output_path.exists() and not args.force:
        print(f"'{output_path}' は既に存在します。上書きしますか？ [y/N]: ", end="")
        answer = input().strip().lower()
        if answer not in ("y", "yes"):
            print("中止しました。")
            sys.exit(0)

    if output_path.exists():
        backup_path = Path(str(output_path) + ".backup")
        shutil.copy2(output_path, backup_path)
        print(f"バックアップを作成しました: {backup_path}")

    output_path.write_text(template, encoding="utf-8")
    print(f"テンプレートを生成しました: {output_path}")


if __name__ == "__main__":
    main()
