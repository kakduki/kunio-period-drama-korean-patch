# SRAM Route Probe Report

## Scope

The English reference ROM was applied locally to the owned Japanese base ROM and run with a bounded route. The new `lua/kunio_sram_route_probe.lua` captures CPU RAM and `$6000-$7FFF` SRAM whenever the visible nametable fingerprint changes.

## Evidence

- Route cap: 7,200 frames.
- Captures: 65 snapshots from frames 120 through 7,167.
- The run reached repeated town/shop states and did not remain on the title screen.
- The English route produced visible shop text including `THANKS`, `YOUR INVENTORY IS`, `YOUR INVENTORY IS FULL`, and `KUNIO GOT SALVE` in the separate route trace.
- The item-list route reached the inventory context at frame 2,385, but the list was empty.

## Result

`UNKNOWN: inventory slot not identified.`

The broad SRAM changes include map/runtime data and screen buffers. The previously proposed slots `$7700`, `$7701`, `$7705`, `$7720-$7722` are not sufficient proof of item ownership. `$7705` and `$7720-$7722` changed during the route, but no change was correlated with a visibly owned item.

## Next bounded experiment

Use the documented Koganemushi name-entry secret to obtain the map cursor and money in a new probe. The route should then verify map-cursor behavior and natural event/boss dialogue before any Korean event text is promoted.

