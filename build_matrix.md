# Build Matrix

This matrix records the current development pipeline, not a release list.

| build | ROM offset / PRG bank | English-reference check | runtime | visual | result |
| --- | --- | --- | --- | --- | --- |
| opening_ptr_182_16x16_readability_proof | @0x071B6 / Bank 1 | IPS SHA-256 cb6ea2fdbf82e974c474f4ea0d489f7c65647c94de899caf2a6b8c089f202dad | PASS, PASS | PASS | PASS |
| opening_ptr_182_183_16x16_readability | @0x071B6 and @0x071D7 / Bank 1 | source slots `0x81-0x9A` structurally checked; pointer relocation checked | pointer 182 PASS (33/33); pointer 183 PASS (25/25) | PASS on both native screens | PASS_FOR_TWO_OPENING_CONTEXTS |

The verified candidate is limited to two pointer-driven opening records. Other
text renderer families remain outside this matrix until they have their own
context.
