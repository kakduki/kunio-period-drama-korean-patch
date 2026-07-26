#!/usr/bin/env python3
"""Generate compact, explicitly scoped 16x16 Korean dialogue helpers.

The game renderer normally treats one source byte as one vertical 8x16 cell.
The helpers produced here redirect only declared Bank-1 dialogue records or a
declared contiguous record-base range, and only declared source-code ranges.
Two adjacent source cells can then form one readable 16x16 Korean syllable.
Keeping both filters explicit prevents renderer controls such as ``0xBB`` and
``0xCA`` from being mistaken for font data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


ENTRY_CONTINUE_NONZERO_CPU = 0x9563
ENTRY_CONTINUE_TILE_CPU = 0x956B
MARKER_CONTINUE_CPU = 0x958D


class HelperAssemblyError(ValueError):
    """Raised when a generated helper cannot fit or cannot branch safely."""


class _Assembler:
    """Tiny assembler for the handful of relative branches used by the hook."""

    def __init__(self, origin: int) -> None:
        self.origin = origin
        self.code = bytearray()
        self.labels: dict[str, int] = {}
        self.fixups: list[tuple[int, str]] = []

    @property
    def address(self) -> int:
        return self.origin + len(self.code)

    def emit(self, *values: int) -> None:
        if any(not 0 <= value <= 0xFF for value in values):
            raise HelperAssemblyError("assembler byte is outside 0x00-0xFF")
        self.code.extend(values)

    def label(self, name: str) -> None:
        if name in self.labels:
            raise HelperAssemblyError(f"duplicate helper label: {name}")
        self.labels[name] = self.address

    def branch(self, opcode: int, label: str) -> None:
        if opcode not in {0x90, 0xB0, 0xD0, 0xF0}:
            raise HelperAssemblyError(f"unsupported branch opcode: 0x{opcode:02X}")
        self.emit(opcode, 0)
        self.fixups.append((len(self.code) - 1, label))

    def jmp(self, cpu_address: int) -> None:
        if not 0 <= cpu_address <= 0xFFFF:
            raise HelperAssemblyError(f"invalid JMP target: 0x{cpu_address:X}")
        self.emit(0x4C, cpu_address & 0xFF, cpu_address >> 8)

    def finish(self) -> bytes:
        for offset, label in self.fixups:
            try:
                target = self.labels[label]
            except KeyError as exc:
                raise HelperAssemblyError(f"missing helper label: {label}") from exc
            next_cpu = self.origin + offset + 1
            delta = target - next_cpu
            if not -128 <= delta <= 127:
                raise HelperAssemblyError(
                    f"branch to {label!r} is out of range ({delta:+d} bytes)"
                )
            self.code[offset] = delta & 0xFF
        return bytes(self.code)


def _normalize_ranges(source_ranges: Iterable[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    ranges = tuple(source_ranges)
    if not ranges:
        raise HelperAssemblyError("a paired dialogue helper needs at least one source range")
    previous_end = -1
    for start, end in ranges:
        if not 0x00 <= start < end <= 0x100:
            raise HelperAssemblyError("source range must fit inside one byte")
        if start <= previous_end:
            raise HelperAssemblyError("source ranges must be sorted and non-overlapping")
        previous_end = end - 1
    return ranges


def _emit_range_dispatch(
    asm: _Assembler,
    source_ranges: tuple[tuple[int, int], ...],
    *,
    match_label: str,
    fallback_label: str,
) -> None:
    """Branch to ``match_label`` only when A falls in one declared range."""

    for start, end in source_ranges:
        asm.emit(0xC9, start)  # CMP #start
        asm.branch(0x90, fallback_label)  # BCC fallback
        asm.emit(0xC9, end)  # CMP #end (exclusive)
        asm.branch(0x90, match_label)  # BCC match
    # The caller places fallback immediately after this dispatch.


@dataclass(frozen=True)
class PairedDialogueHelper:
    """Bytecode and metadata for a record-scoped paired-cell renderer hook."""

    code: bytes
    marker_cpu: int
    source_ranges: tuple[tuple[int, int], ...]
    record_cpu_addresses: tuple[int, ...]
    entry_cpu: int
    record_cpu_range: tuple[int, int] | None = None

    @property
    def entry_length(self) -> int:
        return self.marker_cpu - self.entry_cpu

    def accepts_source_code(self, value: int) -> bool:
        return any(start <= value < end for start, end in self.source_ranges)

    @property
    def marker_hook(self) -> bytes:
        return bytes((0x4C, self.marker_cpu & 0xFF, self.marker_cpu >> 8))


def build_record_scoped_paired_helper(
    *,
    record_cpu_addresses: Iterable[int],
    source_ranges: Iterable[tuple[int, int]],
    entry_cpu: int,
    max_size: int,
) -> PairedDialogueHelper:
    """Build a helper for one or more records in a common 16 KiB CPU window.

    The marker hook stores the source byte in zero-page ``$1B`` temporarily,
    so all guarded records must share the same CPU high byte.  The current
    Bank-1 opening records satisfy that constraint.
    """

    records = tuple(record_cpu_addresses)
    if not records:
        raise HelperAssemblyError("at least one guarded record is required")
    if len(set(records)) != len(records):
        raise HelperAssemblyError("guarded record CPU addresses must not repeat")
    if any(not 0x8000 <= address <= 0xBFFF for address in records):
        raise HelperAssemblyError("guarded record must be inside a switchable CPU window")
    high = records[0] >> 8
    if any(address >> 8 != high for address in records):
        raise HelperAssemblyError("guarded records must share one CPU high byte")
    ranges = _normalize_ranges(source_ranges)
    if max_size <= 0:
        raise HelperAssemblyError("helper code cave size must be positive")

    asm = _Assembler(entry_cpu)
    asm.label("entry")
    asm.emit(0x48)  # PHA: retain the source byte while testing the record base.
    asm.emit(0xA5, 0x1B, 0xC9, high)  # LDA $1B; CMP #record-high
    asm.branch(0xD0, "entry_restore")  # BNE
    asm.emit(0xA5, 0x1A)  # LDA $1A
    for low in (address & 0xFF for address in records):
        asm.emit(0xC9, low)  # CMP #record-low
        asm.branch(0xF0, "entry_source")  # BEQ

    asm.label("entry_restore")
    asm.emit(0x68)  # PLA
    asm.jmp(entry_cpu)  # patched below once fallback is placed
    restore_fallback_operand = len(asm.code) - 2

    asm.label("entry_source")
    asm.emit(0x68)  # PLA
    _emit_range_dispatch(
        asm,
        ranges,
        match_label="entry_handle",
        fallback_label="entry_fallback",
    )

    asm.label("entry_fallback")
    entry_fallback_cpu = asm.address
    asm.emit(0xC9, 0x00)  # CMP #$00
    asm.branch(0xF0, "entry_zero")  # BEQ: replay the original zero-byte path.
    asm.jmp(ENTRY_CONTINUE_NONZERO_CPU)
    asm.label("entry_zero")
    asm.jmp(ENTRY_CONTINUE_TILE_CPU)

    asm.label("entry_handle")
    asm.emit(0x85, 0x1B, 0x18, 0x69, 0x20)  # STA $1B; CLC; ADC #$20
    asm.jmp(ENTRY_CONTINUE_TILE_CPU)

    entry_end_cpu = asm.address
    asm.code[restore_fallback_operand] = entry_fallback_cpu & 0xFF
    asm.code[restore_fallback_operand + 1] = entry_fallback_cpu >> 8

    asm.label("marker")
    marker_cpu = asm.address
    asm.emit(0xA5, 0x1B)  # LDA $1B: saved top tile or ordinary renderer state.
    _emit_range_dispatch(
        asm,
        ranges,
        match_label="marker_handle",
        fallback_label="marker_fallback",
    )
    asm.label("marker_fallback")
    asm.emit(0xA9, 0x00)  # LDA #$00
    asm.jmp(MARKER_CONTINUE_CPU)
    asm.label("marker_handle")
    asm.emit(0x48, 0xA9, high, 0x85, 0x1B, 0x68)  # PHA; LDA #high; STA $1B; PLA
    asm.jmp(MARKER_CONTINUE_CPU)

    code = asm.finish()
    if marker_cpu != entry_cpu + (entry_end_cpu - entry_cpu):
        raise HelperAssemblyError("marker helper start does not follow the entry helper")
    if len(code) > max_size:
        raise HelperAssemblyError(
            f"record-scoped helper needs {len(code)} bytes but cave holds {max_size}"
        )
    return PairedDialogueHelper(
        code=code,
        marker_cpu=marker_cpu,
        source_ranges=ranges,
        record_cpu_addresses=records,
        entry_cpu=entry_cpu,
    )


def build_record_range_scoped_paired_helper(
    *,
    record_cpu_start: int,
    record_cpu_end: int,
    source_ranges: Iterable[tuple[int, int]],
    entry_cpu: int,
    max_size: int,
) -> PairedDialogueHelper:
    """Build a helper for one explicitly owned contiguous record-base range.

    The range applies to the parser's base pointer in zero-page ``$1A/$1B``;
    it is not a broad byte-address range.  Callers must separately prove that
    every pointer-table owner in the range belongs to the same Korean batch.
    The end byte may not be ``0xFF`` because the compact gate compares an
    end-exclusive low byte.
    """

    if not 0x8000 <= record_cpu_start <= record_cpu_end <= 0xBFFF:
        raise HelperAssemblyError("record range must be inside a switchable CPU window")
    high = record_cpu_start >> 8
    if record_cpu_end >> 8 != high:
        raise HelperAssemblyError("record range must stay within one CPU high byte")
    end_low = record_cpu_end & 0xFF
    if end_low == 0xFF:
        raise HelperAssemblyError("record range ending in 0xFF cannot use the compact gate")
    ranges = _normalize_ranges(source_ranges)
    if max_size <= 0:
        raise HelperAssemblyError("helper code cave size must be positive")

    asm = _Assembler(entry_cpu)
    asm.label("entry")
    asm.emit(0x48)  # PHA: retain the source byte while testing the record base.
    asm.emit(0xA5, 0x1B, 0xC9, high)  # LDA $1B; CMP #record-high
    asm.branch(0xD0, "entry_restore")  # BNE
    asm.emit(0xA5, 0x1A)  # LDA $1A
    asm.emit(0xC9, record_cpu_start & 0xFF)  # CMP #range-start-low
    asm.branch(0x90, "entry_restore")  # BCC
    asm.emit(0xC9, end_low + 1)  # CMP #range-end-low, exclusive
    asm.branch(0xB0, "entry_restore")  # BCS

    # A successful range check falls straight into the source-code dispatch.
    # Keep the restore block after the dispatcher so this costs no extra JMP.
    asm.label("entry_source")
    asm.emit(0x68)  # PLA
    _emit_range_dispatch(
        asm,
        ranges,
        match_label="entry_handle",
        fallback_label="entry_fallback",
    )

    asm.label("entry_fallback")
    entry_fallback_cpu = asm.address
    asm.emit(0xC9, 0x00)  # CMP #$00
    asm.branch(0xF0, "entry_zero")  # BEQ: replay the original zero-byte path.
    asm.jmp(ENTRY_CONTINUE_NONZERO_CPU)
    asm.label("entry_zero")
    asm.jmp(ENTRY_CONTINUE_TILE_CPU)

    asm.label("entry_handle")
    asm.emit(0x85, 0x1B, 0x18, 0x69, 0x20)  # STA $1B; CLC; ADC #$20
    asm.jmp(ENTRY_CONTINUE_TILE_CPU)

    asm.label("entry_restore")
    asm.emit(0x68)  # PLA
    asm.jmp(entry_fallback_cpu)

    entry_end_cpu = asm.address

    asm.label("marker")
    marker_cpu = asm.address
    asm.emit(0xA5, 0x1B)  # LDA $1B: saved top tile or ordinary renderer state.
    _emit_range_dispatch(
        asm,
        ranges,
        match_label="marker_handle",
        fallback_label="marker_fallback",
    )
    asm.label("marker_fallback")
    asm.emit(0xA9, 0x00)  # LDA #$00
    asm.jmp(MARKER_CONTINUE_CPU)
    asm.label("marker_handle")
    asm.emit(0x48, 0xA9, high, 0x85, 0x1B, 0x68)  # PHA; LDA #high; STA $1B; PLA
    asm.jmp(MARKER_CONTINUE_CPU)

    code = asm.finish()
    if marker_cpu != entry_cpu + (entry_end_cpu - entry_cpu):
        raise HelperAssemblyError("marker helper start does not follow the entry helper")
    if len(code) > max_size:
        raise HelperAssemblyError(
            f"record-range-scoped helper needs {len(code)} bytes but cave holds {max_size}"
        )
    return PairedDialogueHelper(
        code=code,
        marker_cpu=marker_cpu,
        source_ranges=ranges,
        record_cpu_addresses=(),
        entry_cpu=entry_cpu,
        record_cpu_range=(record_cpu_start, record_cpu_end),
    )
