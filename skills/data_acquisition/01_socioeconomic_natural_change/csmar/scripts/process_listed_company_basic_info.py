#!/usr/bin/env python
"""Process CSMAR listed-company basic info zip into target-industry candidates.

Usage:
  python process_listed_company_basic_info.py \
    --zip <path/to/downloaded.zip> \
    --out-dir <path/to/output/dir>
"""

import argparse
import zipfile
from pathlib import Path
from typing import BinaryIO

import pandas as pd


TARGET_KEYWORDS = {
    "thermal_power": [
        "thermal power", "power generation", "coal power",
        "coal-fired", "electricity", "thermal"
    ],
    "district_heating": [
        "district heating", "heat supply", "steam",
        "heating", "thermal"
    ],
    "iron_steel": [
        "iron and steel", "steelmaking", "ironmaking",
        "coking", "blast furnace", "steel", "ferroalloy"
    ],
    "nonferrous_metals": [
        "nonferrous", "aluminum", "copper", "lead", "zinc",
        "nickel", "titanium", "magnesium", "tungsten",
        "rare earth", "smelting", "rolling"
    ],
    "cement": [
        "cement", "clinker", "building materials",
        "limestone", "slag powder"
    ],
    "lime": [
        "lime", "calcium oxide", "calcium carbonate", "limestone"
    ],
    "brick_tile": [
        "brick", "tile", "wall materials",
        "ceramic", "refractory materials"
    ],
    "glass": [
        "glass", "flat glass", "photovoltaic glass",
        "glass fiber", "fiberglass"
    ],
    "chemical": [
        "chemical", "chemistry", "petrochemical",
        "refining", "fertilizer", "pesticide",
        "chlor-alkali", "coal chemical", "synthetic ammonia",
        "methanol", "ethylene", "rubber", "plastic",
        "resin", "coating", "pharmaceutical intermediate"
    ],
}


def find_data_xlsx(archive: zipfile.ZipFile) -> str:
    # Read the chosen workbook through ZipFile.open. Archive member names never
    # become filesystem paths and the downloaded input directory stays read-only.
    matches = [name for name in archive.namelist() if name.endswith("STK_LISTEDCOINFOANL.xlsx")]
    if not matches:
        matches = [name for name in archive.namelist() if name.endswith(".xlsx") and "[DES]" not in name]
    if not matches:
        raise FileNotFoundError("No data workbook found in archive.")
    return matches[0]


def build_candidates(xlsx_path: Path | BinaryIO, out_dir: Path) -> None:
    df = pd.read_excel(xlsx_path, dtype=str)
    df = df[df["Symbol"].str.match(r"^\d{6}$", na=False)].copy()
    df["EndDate_dt"] = pd.to_datetime(df["EndDate"], errors="coerce")
    latest = (
        df.sort_values(["Symbol", "EndDate_dt"])
        .groupby("Symbol", as_index=False)
        .tail(1)
        .copy()
    )

    text_cols = [
        "IndustryName", "IndustryNameC", "IndustryNameD",
        "IndustryCode", "IndustryCodeC", "IndustryCodeD",
        "ShortName", "FullName", "MAINBUSSINESS",
    ]
    latest["_hay"] = latest[text_cols].fillna("").agg(" ".join, axis=1)

    rows = []
    for sector, keywords in TARGET_KEYWORDS.items():
        mask = latest["_hay"].apply(lambda s: any(k in s for k in keywords))
        tmp = latest[mask].copy()
        tmp["target_sector"] = sector
        tmp["match_keywords"] = ";".join(keywords)
        rows.append(tmp)

    all_matches = (
        pd.concat(rows, ignore_index=True)
        if rows
        else latest.iloc[0:0].copy()
    )
    all_matches = all_matches.drop_duplicates(["Symbol", "target_sector"])

    keep = [
        "target_sector", "Symbol", "ShortName", "FullName", "EndDate",
        "IndustryName", "IndustryCode", "IndustryNameC", "IndustryCodeC",
        "IndustryNameD", "IndustryCodeD", "SocialCreditCode", "PROVINCE",
        "CITY", "MAINBUSSINESS", "LISTINGSTATE", "match_keywords",
    ]
    out_dir.mkdir(parents=True, exist_ok=True)
    all_matches[keep].to_csv(
        out_dir / "csmar_target_industry_company_candidates.csv",
        index=False, encoding="utf-8-sig"
    )

    unique = (
        all_matches.groupby("Symbol")
        .agg({
            "target_sector": lambda x: ";".join(sorted(set(x))),
            "ShortName": "first", "FullName": "first",
            "EndDate": "first", "IndustryName": "first",
            "IndustryCode": "first", "IndustryNameC": "first",
            "IndustryCodeC": "first", "IndustryNameD": "first",
            "IndustryCodeD": "first", "SocialCreditCode": "first",
            "PROVINCE": "first", "CITY": "first",
            "MAINBUSSINESS": "first", "LISTINGSTATE": "first",
        })
        .reset_index()
    )
    unique.to_csv(
        out_dir / "csmar_target_industry_company_list_latest.csv",
        index=False, encoding="utf-8-sig"
    )
    with pd.ExcelWriter(
        out_dir / "csmar_target_industry_company_list_latest.xlsx",
        engine="openpyxl"
    ) as writer:
        unique.to_excel(writer, sheet_name="unique_company_latest", index=False)
        all_matches[keep].to_excel(writer, sheet_name="sector_matches", index=False)

    print(f"Latest companies: {len(latest)}")
    print(f"Sector matches: {len(all_matches)}")
    print(f"Unique matched companies: {len(unique)}")
    if not all_matches.empty:
        print(
            all_matches.groupby("target_sector")["Symbol"]
            .nunique()
            .sort_values(ascending=False)
            .to_string()
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", required=True, dest="zip_path")
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    zip_path = Path(args.zip_path)
    out_dir = Path(args.out_dir)
    with zipfile.ZipFile(zip_path) as archive:
        with archive.open(find_data_xlsx(archive)) as workbook:
            build_candidates(workbook, out_dir)


if __name__ == "__main__":
    main()
