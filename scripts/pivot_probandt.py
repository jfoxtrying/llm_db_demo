# scripts/pivot_probandt.py
import sys, pandas as pd
from pathlib import Path

src = Path(sys.argv[1])
dst = Path(sys.argv[2])

df_long = pd.read_csv(src, header=0)

df_wide = (
    df_long
    .set_index("Variable")
    .T
    .reset_index()
    .rename(columns={"index": "property_name"})
)

df_wide.insert(
    0,
    "project_id",
    df_wide.property_name.str.replace(r"\s+", "_", regex=True).str.lower()
)

pct_cols = [c for c in df_wide.columns if df_wide[c].astype(str).str.contains("%").any()]
num_cols = [c for c in df_wide.columns if df_wide[c].astype(str).str.contains(",").any()]

for c in pct_cols:
    df_wide[c] = (
        df_wide[c]
        .astype(str)
        .str.replace("%", "", regex=False)
        .replace("", pd.NA)
        .astype(float)
    )

for c in num_cols:
    df_wide[c] = (
        df_wide[c]
        .astype(str)
        .str.replace(",", "", regex=False)
        .replace("", pd.NA)
        .astype(float)
    )

df_wide.to_csv(dst, index=False)
print(f"✓ wrote {dst} with shape {df_wide.shape}")

# --- deduplicate column names ----------------------------------------------
# pandas' built-in helper adds .1, .2 suffixes to duplicates
df_wide.columns = (
    pd.io.parsers.ParserBase({'names': df_wide.columns})
      ._maybe_dedup_names(df_wide.columns)
)

df_wide = (
     df_long
     .set_index("Variable")
     .T
     .reset_index()
     .rename(columns={"index": "property_name"})
 )

# deduplicate duplicate column labels (adds .1, .2 … suffixes)
df_wide.columns = (
+    pd.io.parsers.ParserBase({'names': df_wide.columns})
    ._maybe_dedup_names(df_wide.columns)
)