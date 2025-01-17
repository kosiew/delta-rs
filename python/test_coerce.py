import polars as pl
from deltalake import DeltaTable
import deltalake

tmp_path = "test_table__"
df = pl.DataFrame({"foo": [1], "bar": [[{"foo": "!"}]]})
df.write_delta(tmp_path, mode="overwrite", overwrite_schema=True)

DeltaTable(tmp_path).merge(
    df.to_arrow(compat_level=1),
    predicate="s.foo = t.foo",
    source_alias="s",
    target_alias="t",
    large_dtypes=None,
).when_matched_update_all().execute()

print("\ndone\n")
print(f"DeltaLake Version: {deltalake.__version__}")
print(f"Polars Version: {pl.__version__}")