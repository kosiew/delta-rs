import pytest
import polars as pl
from deltalake import DeltaTable
import tempfile
import shutil

@pytest.mark.parametrize("mode", ["overwrite"])
def test_merge_large_dtype(mode):
    # Create a temporary directory for the Delta Table
    tmp_path = tempfile.mkdtemp(prefix="test_table__")

    try:
        # Create a DataFrame with a nested list structure
        df = pl.DataFrame({"foo": [1], "bar": [[{"foo": "!"}]]})

        # Write DataFrame to Delta Table
        df.write_delta(tmp_path, mode=mode, overwrite_schema=True)

        # Convert DataFrame to Arrow for merging
        arrow_data = df.to_arrow(compat_level=1)

        # Attempting a merge operation that should fail due to type coercion
        with pytest.raises(Exception) as excinfo:
            DeltaTable(tmp_path).merge(
                arrow_data,
                predicate="s.foo = t.foo",
                source_alias="s",
                target_alias="t",
                large_dtypes=None,
            ).when_matched_update_all().execute()
        
        # Ensure the error message contains the expected type coercion issue
        assert "type_coercion" in str(excinfo.value) or "Failed to coerce" in str(excinfo.value)

    finally:
        # Cleanup temporary directory
        shutil.rmtree(tmp_path)

