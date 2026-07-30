# PTR-181 Pointer Loader Probe

Status: **PASS**

This bounded run used the existing 450-frame opening-to-field route. It did
not attempt free-form gameplay.

## Result

- Pointer table CPU base: `$9DC4`.
- PTR-181 table bytes: `$9F2E=88`, `$9F2F=B1`.
- Low-byte read PC: `$914E`.
- High-byte read PC: `$9153`.
- Loader entry: `$9138`.
- Dialogue ID source: `LDA $708B,Y`.
- PTR-181 runtime dialogue ID: `$B6`.
- `$B6 - 1 = 181`, matching the catalog pointer index.
- The loader doubles the ID and uses carry to select the two halves beginning
  at `$9DC2` and `$9EC2`.

The stable implementation point is therefore the loader before its `ASL`.
A common hook can convert `dialogue_id - 1` to a page-table index and store
`page_id + 1` in `$07FF`. The fixed-bank mapper wrapper can then convert that
value to the extended MMC3 R1 page. No screen OCR or full gameplay route is
required for runtime page selection.

## Evidence

- `ptr181_pointer_loader_probe/summary.tsv`
- `ptr181_pointer_loader_probe/pointer_table_reads.tsv`

The read callbacks fired 60 times from frames 328 through 384 and consistently
reported the same PCs, values, and doubled index `$6C`.
