#!/usr/bin/env python3
"""Build the Bank-1 dialogue-ID to Korean CHR-page loader hook."""

from __future__ import annotations

from collections.abc import Sequence

from paired_dialogue_helper import (
    ENTRY_CONTINUE_NONZERO_CPU,
    ENTRY_CONTINUE_TILE_CPU,
    MARKER_CONTINUE_CPU,
    _Assembler,
)


POINTER_COUNT = 248
LOADER_HOOK_CPU = 0x9137
LOADER_HOOK_ROM_OFFSET = 0x05147
LOADER_HOOK_ORIGINAL = bytes.fromhex("B9 8B 70 0A A8")
# The control-preserving full Korean stream ends before ROM 0x07000. The final
# compiler reserves the following bytes for this helper and its page table.
LOADER_CAVE_CPU = 0xAFF0
LOADER_CAVE_ROM_OFFSET = 0x07000
LOADER_CAVE_SIZE = 27
PAGE_TABLE_CPU = 0xB00B
PAGE_TABLE_ROM_OFFSET = 0x0701B
PAGE_STATE_ADDRESS = 0x07FF
TEMP_DIALOGUE_ID_ADDRESS = 0x07FE
TEMP_POINTER_HIGH_ADDRESS = 0x07FD
LOW_TABLE_CONTINUE_CPU = 0x913E
HIGH_TABLE_CONTINUE_CPU = 0x914B
RENDER_SOURCE_RANGES = ((0x81, 0x9B), (0xC0, 0xC8))
MAPPER_SELECT_CAVE_CPU = 0xF2B1
MAPPER_STORE_CAVE_CPU = 0xF2EE


class _TinyAssembler:
    """Small absolute/relative assembler for the loader's bounded cave."""

    def __init__(self, origin: int) -> None:
        self.origin = origin
        self.data = bytearray()
        self.labels: dict[str, int] = {}
        self.fixups: list[tuple[int, str, str]] = []

    @property
    def address(self) -> int:
        return self.origin + len(self.data)

    def emit(self, *values: int) -> None:
        self.data.extend(values)

    def label(self, name: str) -> None:
        if name in self.labels:
            raise ValueError(f"duplicate loader label: {name}")
        self.labels[name] = self.address

    def branch(self, opcode: int, label: str) -> None:
        self.emit(opcode, 0)
        self.fixups.append((len(self.data) - 1, label, "relative"))

    def jump(self, label: str) -> None:
        self.emit(0x4C, 0, 0)
        self.fixups.append((len(self.data) - 2, label, "absolute"))

    def finish(self) -> bytes:
        output = bytearray(self.data)
        for offset, label, kind in self.fixups:
            try:
                target = self.labels[label]
            except KeyError as exc:
                raise ValueError(f"unknown loader label: {label}") from exc
            if kind == "absolute":
                output[offset : offset + 2] = target.to_bytes(2, "little")
                continue
            relative = target - (self.origin + offset + 1)
            if not -128 <= relative <= 127:
                raise ValueError(f"loader branch is out of range: {label}")
            output[offset] = relative & 0xFF
        return bytes(output)

def encode_page_table(assignments: Sequence[int | None]) -> bytes:
    """Encode page indices as nonzero state bytes; zero means no Korean page."""

    if len(assignments) != POINTER_COUNT:
        raise ValueError(f"expected {POINTER_COUNT} page assignments")
    encoded = bytearray()
    for page in assignments:
        if page is None:
            encoded.append(0)
        elif not 0 <= page < 64:
            raise ValueError(f"page index outside MMC3 64-page budget: {page}")
        else:
            encoded.append(page + 1)
    return bytes(encoded)


def build_loader_helper(page_table_cpu: int = PAGE_TABLE_CPU) -> bytes:
    """Return a hook helper preserving the original ASL/carry table dispatch."""

    if not 0x8000 <= page_table_cpu <= 0xBFFF:
        raise ValueError("page table must be visible in the Bank-1 CPU window")
    helper = bytes(
        (
            0xB9, 0x8B, 0x70,  # LDA $708B,Y: one-based dialogue ID
            0x8D, TEMP_DIALOGUE_ID_ADDRESS & 0xFF, TEMP_DIALOGUE_ID_ADDRESS >> 8,
            0xAA,              # TAX
            0xCA,              # DEX: catalog index = dialogue ID - 1
            0xBD, page_table_cpu & 0xFF, page_table_cpu >> 8,
            0x8D, PAGE_STATE_ADDRESS & 0xFF, PAGE_STATE_ADDRESS >> 8,
            0xAD, TEMP_DIALOGUE_ID_ADDRESS & 0xFF, TEMP_DIALOGUE_ID_ADDRESS >> 8,
            0x0A,              # original ASL
            0xA8,              # original TAY
            0xB0, 0x03,        # BCS high_table
            0x4C, LOW_TABLE_CONTINUE_CPU & 0xFF, LOW_TABLE_CONTINUE_CPU >> 8,
            0x4C, HIGH_TABLE_CONTINUE_CPU & 0xFF, HIGH_TABLE_CONTINUE_CPU >> 8,
        )
    )
    if len(helper) > LOADER_CAVE_SIZE:
        raise AssertionError("pointer-page loader exceeds the approved Bank-1 cave")
    return helper


def build_loader_helper_with_direct_mapper(
    page_table_cpu: int,
    *,
    normal_r0: int = 0x3C,
    normal_r1: int = 0x3E,
) -> bytes:
    """Load a pointer page and select its CHR R1 without the fixed-bank cave.

    The original full-pointer candidate used the fixed-bank menu-template
    area for its mapper wrapper. This variant keeps that area available for
    the real menu template and performs the short-lived CHR selection from
    the Bank-1 loader cave instead. A zero page state restores the normal
    R0/R1 pair; a nonzero state maps the one-based page index to R1.
    """

    if not 0x8000 <= page_table_cpu <= 0xBFFF:
        raise ValueError("page table must be visible in the Bank-1 CPU window")
    if not 0 <= normal_r0 <= 0xFF or not 0 <= normal_r1 <= 0xFF:
        raise ValueError("normal mapper values must fit one byte")

    asm = _TinyAssembler(LOADER_CAVE_CPU)
    asm.emit(0xB9, 0x8B, 0x70)
    asm.emit(0x8D, TEMP_DIALOGUE_ID_ADDRESS & 0xFF, TEMP_DIALOGUE_ID_ADDRESS >> 8)
    asm.emit(0xAA, 0xCA)
    asm.emit(0xBD, page_table_cpu & 0xFF, page_table_cpu >> 8)
    asm.emit(0x8D, PAGE_STATE_ADDRESS & 0xFF, PAGE_STATE_ADDRESS >> 8)

    # Restore R0, select MMC3 R1, and map either the Korean page or the
    # original font page before returning to the game's pointer dispatch.
    asm.emit(0xA9, 0x00, 0x8D, 0x00, 0x80)
    asm.emit(0xA9, normal_r0, 0x8D, 0x01, 0x80)
    asm.emit(0xA9, 0x01, 0x8D, 0x00, 0x80)
    asm.emit(0xAD, PAGE_STATE_ADDRESS & 0xFF, PAGE_STATE_ADDRESS >> 8)
    asm.branch(0xF0, "normal_r1")
    asm.emit(0x38, 0xE9, 0x01, 0x0A, 0x09, 0x80)
    asm.emit(0x8D, 0x01, 0x80)
    asm.jump("dispatch")
    asm.label("normal_r1")
    asm.emit(0xA9, normal_r1, 0x8D, 0x01, 0x80)

    # Preserve the original carry-sensitive low/high pointer-table dispatch.
    asm.label("dispatch")
    asm.emit(0xAD, TEMP_DIALOGUE_ID_ADDRESS & 0xFF, TEMP_DIALOGUE_ID_ADDRESS >> 8)
    asm.emit(0x0A, 0xA8)
    asm.branch(0xB0, "high_table")
    asm.emit(0x4C, LOW_TABLE_CONTINUE_CPU & 0xFF, LOW_TABLE_CONTINUE_CPU >> 8)
    asm.label("high_table")
    asm.emit(0x4C, HIGH_TABLE_CONTINUE_CPU & 0xFF, HIGH_TABLE_CONTINUE_CPU >> 8)
    helper = asm.finish()
    if len(helper) > 0x40:
        raise AssertionError(f"direct-mapper loader needs {len(helper)} bytes; cave budget is 64")
    return helper


def loader_hook() -> bytes:
    return bytes(
        (0x4C, LOADER_CAVE_CPU & 0xFF, LOADER_CAVE_CPU >> 8, 0xEA, 0xEA)
    )


def mapper_page_value(page_state: int) -> int:
    """Mirror the fixed-bank helper's state-byte to MMC3 R1 conversion."""

    if not 1 <= page_state <= 64:
        raise ValueError("page state must be encoded page index + 1")
    return 0x80 | ((page_state - 1) << 1)


def build_page_scoped_renderer(
    entry_cpu: int,
    max_size: int,
    *,
    map_r1_from_page_state: bool = False,
) -> tuple[bytes, int]:
    """Build an 8x16 renderer enabled by the nonzero page-state byte."""

    asm = _Assembler(entry_cpu)
    asm.emit(0x48)  # PHA source byte
    asm.emit(0xAD, PAGE_STATE_ADDRESS & 0xFF, PAGE_STATE_ADDRESS >> 8)
    asm.branch(0xF0, "entry_restore")
    if map_r1_from_page_state:
        # The normal mapper routine leaves MMC3 R1 selected. Convert the
        # one-based page state into the active 1 KiB CHR page value.
        asm.emit(0x0A, 0x18, 0x69, 0x7E, 0x8D, 0x01, 0x80)
    asm.emit(0x68)  # PLA source byte
    for start, end in RENDER_SOURCE_RANGES:
        asm.emit(0xC9, start)
        asm.branch(0x90, "entry_fallback")
        asm.emit(0xC9, end)
        asm.branch(0x90, "entry_handle")
    asm.label("entry_fallback")
    asm.emit(0xC9, 0x00)
    asm.branch(0xF0, "entry_zero")
    asm.jmp(ENTRY_CONTINUE_NONZERO_CPU)
    asm.label("entry_zero")
    asm.jmp(ENTRY_CONTINUE_TILE_CPU)
    asm.label("entry_restore")
    asm.emit(0x68)
    asm.emit(0xC9, 0x00)
    asm.branch(0xF0, "entry_zero")
    asm.jmp(ENTRY_CONTINUE_NONZERO_CPU)
    asm.label("entry_handle")
    asm.emit(0x48, 0xA5, 0x1B)
    asm.emit(0x8D, TEMP_POINTER_HIGH_ADDRESS & 0xFF, TEMP_POINTER_HIGH_ADDRESS >> 8)
    asm.emit(0x68, 0x85, 0x1B, 0x18, 0x69, 0x20)
    asm.jmp(ENTRY_CONTINUE_TILE_CPU)

    marker_cpu = asm.address
    asm.emit(0xAD, TEMP_POINTER_HIGH_ADDRESS & 0xFF, TEMP_POINTER_HIGH_ADDRESS >> 8)
    asm.branch(0xF0, "marker_fallback")
    asm.emit(0xA5, 0x1B)
    asm.emit(0x48)
    asm.emit(0xAD, TEMP_POINTER_HIGH_ADDRESS & 0xFF, TEMP_POINTER_HIGH_ADDRESS >> 8)
    asm.emit(0x85, 0x1B, 0xA9, 0x00)
    asm.emit(0x8D, TEMP_POINTER_HIGH_ADDRESS & 0xFF, TEMP_POINTER_HIGH_ADDRESS >> 8)
    asm.emit(0x68)
    asm.jmp(MARKER_CONTINUE_CPU)
    asm.label("marker_fallback")
    asm.emit(0xA9, 0x00)
    asm.jmp(MARKER_CONTINUE_CPU)

    code = asm.finish()
    if len(code) > max_size:
        raise ValueError(f"page-scoped renderer needs {len(code)} bytes; cave has {max_size}")
    return code, marker_cpu


def build_generic_mapper_helpers(
    original_wrapper: bytes,
) -> tuple[bytes, bytes, bytes]:
    """Build fixed-bank R1 selection from the encoded page-state byte."""

    store_normal_cpu = MAPPER_STORE_CAVE_CPU
    store_common_cpu = MAPPER_STORE_CAVE_CPU + 15
    select = bytes(
        (
            0xAD, 0xFF, 0x07,                    # LDA $07FF
            0xF0, (store_normal_cpu - (MAPPER_SELECT_CAVE_CPU + 5)) & 0xFF,
            0xA5, 0x51, 0xC9, 0x13,             # target field dialogue context
            0xD0, (store_normal_cpu - (MAPPER_SELECT_CAVE_CPU + 11)) & 0xFF,
            0xA9, 0x3C, 0x8D, 0x02, 0x05,       # original R0
            0xAD, 0xFF, 0x07, 0x38, 0xE9, 0x01,
            0x0A, 0x09, 0x80,                   # R1 = $80 + page*2
            0x4C, store_common_cpu & 0xFF, store_common_cpu >> 8,
        )
    )
    store = bytes.fromhex(
        "A9 00 8D FF 07 A9 3C 8D 02 05 A9 3E EA EA EA 8D 03 05 60"
    )
    wrapper = bytearray(original_wrapper)
    wrapper[8:18] = bytes(
        (0x20, MAPPER_SELECT_CAVE_CPU & 0xFF, MAPPER_SELECT_CAVE_CPU >> 8)
    ) + b"\xEA" * 7
    if len(select) > 28 or len(store) > 26:
        raise AssertionError("generic mapper helper exceeds the fixed-bank caves")
    return bytes(wrapper), select, store
