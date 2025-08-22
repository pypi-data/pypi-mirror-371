import pyarrow as pa

class TextIndex:
    id: str

class SearchScan:
    def to_record_batches(self) -> pa.RecordBatchReader: ...
