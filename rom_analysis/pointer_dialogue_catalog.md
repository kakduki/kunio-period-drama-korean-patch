# Complete Pointer Dialogue Catalog

This catalog is the structural starting point for the Korean patch.
The English patch supplies record order, pointer ownership, and a
reference rendering path only. Its wording is not Korean translation.

## Coverage

- Pointer table: `0x05DD4-0x05FC3`
- Records: `248` / `248`
- Development-verified opening rows: `PTR-182, PTR-183, PTR-184, PTR-185, PTR-186, PTR-187, PTR-188, PTR-189, PTR-190, PTR-191, PTR-192, PTR-193, PTR-194, PTR-195`
- Rows absent from the conservative catalog: `PTR-012, PTR-022, PTR-162, PTR-244, PTR-247`

| Korean work status | Count |
| --- | ---: |
| `development_verified_opening` | 14 |
| `structural_unknown` | 229 |
| `structural_unknown_missing_conservative_row` | 5 |

## Per-record contract

A row cannot enter a Korean candidate until it has a Japanese meaning,
renderer family, screen context, route, explicit controls, font slots,
and a bounded capture result. Unknown rows remain worklist entries.

| ID | JP offset | EN reference | JP bytes | Korean work status | Route |
| --- | ---: | --- | ---: | --- | --- |
| `PTR-000` | `0x05FE7` | <F0><BB><00>SO<00>FIGHT<00>ME<00>OR<00>I<00>AIN<B6>T<F8>LETTING<00>YOU<00>PASS<CA><FF> | 34 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-001` | `0x06009` | <F0><BB><00>HOLY<00>SHIT<CA><FF> | 11 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-002` | `0x06014` | <F0><BB><00>AH<71>SO<CA><00>WE<00>MEET<00>AGAIN<BA><FF> | 14 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-003` | `0x06022` | <F0><BB><00>REMEMBER<00>THOSE<00>DUDES<CC><F8>THEY<B6>RE<00>THE<00>ONES<CA><FF> | 50 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-004` | `0x06054` | <F0><BB><00>HOW<00>DID<00>YOU<00>BEAT<F8>MY<00>BOYS<CC><FF> | 42 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-005` | `0x0607E` | <F0><BB><00>YOU<00>FIGHT<00>LIKE<00>A<00>WUS<CA><FF> | 11 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-006` | `0x06089` | <F0><BB><00>PLEASE<00>LET<00>ME<00>JOIN<00>YOU<CA><FF> | 25 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-007` | `0x060A2` | <F0><BB><00>HE<00>AIN<B6>T<00>NOTHIN<B6><CB> | 11 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-008` | `0x060AD` | <FF><F0><BB><00>LET<00>ME<00>COME<00>TOO<CA><FF> | 22 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-009` | `0x060C3` | <F0><BB><00>OK<B9><00><FA><B9><00>LET<B6>S<00>FIGHT<CA><FF> | 16 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-010` | `0x060D3` | <F0><BB><00>I GIVE UP<CA><F8>YOU<B6>RE TOO GOOD<CA><FF> | 47 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-011` | `0x06102` | <F0><BB><00>YOU<00>AIN<B6>T<00>SEEN<00>NOTHIN<F8>YET<CA><FF> | 25 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-012` | `0x0611B` | <F0><BB><00>OK<CA><FF> | 8 | `structural_unknown_missing_conservative_row` | named route, save state, or cheat state required |
| `PTR-013` | `0x06123` | <F0><BB><00>LEMME<00>KICK<00>HIM<CA><FF> | 15 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-014` | `0x06132` | <F0><BB><00>THANKS<00>A<00>LOT<CA><FF> | 38 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-015` | `0x06158` | ICHI<BB><00>WHO<00>ARE<00>YOU<00>GUYS<B9><F8>ANYWAY<CC><FF> | 16 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-016` | `0x06168` | ROKU<BB><00>GET<00><B6>EM<CB><FF> | 19 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-017` | `0x0617B` | ROKU<BB><00>AARGH<CB><00>I<00>LOST<CA><FF> | 13 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-018` | `0x06188` | <F0><BB><00>WE<00>MAY<00>BE<00>BAD<B9><00>BUT<00>WE<F8>DON<B6>T<00>HURT<00>WOMEN<CA><FF> | 37 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-019` | `0x061AD` | <F0><BB><00>WHAT<CB><CB>I<00>BEAT<00>THEM<CA><FF> | 15 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-020` | `0x061BC` | <F0><BB><00>BEEG<00>BOSS<00>JINRO<00>SENT<F8>ME<00>TO<00>KICK<00>YOUR<00>BUTTS<CA><FF> | 43 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-021` | `0x061E7` | <F0><BB><00>I<B6>M<00>GONNA<00>KICK<00>YOUR<F8>ASSES<00>ALL<00>THE<00>WAY<00>TO<00>CHINA<CA><FF> | 45 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-022` | `0x06214` | <F0><BB><00>OK<CA><FF> | 13 | `structural_unknown_missing_conservative_row` | named route, save state, or cheat state required |
| `PTR-023` | `0x06221` | <F0><BB><00>JINRO<00>WILL<00>SEE<00>YA<00>NOW<CA><FF> | 23 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-024` | `0x06238` | <F0><BB><00>SO<B9><00>YOU<B6>RE<00>BEEG<00>BOSS<CB><FF> | 21 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-025` | `0x0624D` | <F0><BB><00>I<B6>LL<00>SHOW<00>THESE<00>LOSERS<F8>A<00>THING<00>OR<00>TWO<CA><FF> | 45 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-026` | `0x0627A` | <F0><BB><00>JEEZ<B9><00>YOU<B6>RE<00>TOUGH<B9><00>BUT<F8>HEISI<00>WILL<00>CRUSH<00>YOU<CA><CA><FF> | 44 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-027` | `0x062A6` | <F0><BB><00>NYAH<CA><00>LATER<CB><FF> | 23 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-028` | `0x062BD` | <F0><BB><00>HEY<CA><00>YOU<B6>RE<00>THOSE<F8>TWO<00>BAD<71>ASSES<CC><FF> | 20 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-029` | `0x062D1` | <F0><BB><00>I<B6>M<00>KINSU<CB><00>LET<B6>S<F8>BOOGIE<CA><FF> | 26 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-030` | `0x062EB` | <F0><BB><00>DAMN<CA><00>TOO<00>BAD<00>YOU<B6>RE<F8>ON<00>THE<00>WRONG<00>SIDE<BA><FF> | 46 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-031` | `0x06319` | <F0><BB><00>I<B6>M<00>GONNA<00>TELL<00>MY<F8>BROTHER<B9><00>HEISI<CA><FF> | 25 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-032` | `0x06332` | <F0><BB><00>CATCH<00>ME<00>IF<00>YOU<00>CAN<CA><FF> | 32 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-033` | `0x06352` | <F0><BB><00>HEY<CA><00>I<B6>M<00>HEISI<CB><FF> | 17 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-034` | `0x06363` | <F0><BB><00>GAWD<B9><00>YOU<B6>RE<00>TOUGH<CA><FF> | 32 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-035` | `0x06383` | <F0><BB><00>BEEG<00>BOSS<00>JINRO<F8>WILL<00>FIX<00>YOU<CA><FF> | 39 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-036` | `0x063AA` | <F0><BB><00>I<00>WON<B6>T<00>RUN<FF> | 22 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-037` | `0x063C0` | <F0><BB><00>FIGHT<00>ME<00>NOW<CA><FF> | 19 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-038` | `0x063D3` | <F0><BB><00>YOU<00>WORK<00>FOR<00><FB><00><CC><F8>I<00>THOUGHT<00>YOU<00>SERVED<00>TORA<CA><FF> | 46 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-039` | `0x06401` | <F0><BB><00>SORRY<B9><00>PAL<CB>HEY<B9><F8>GIMME<00>A<00>BREAK<CA><FF> | 43 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-040` | `0x0642C` | <F0><BB><00>TAKE<00><FB><01><00>WITH<00>YOU<CA><FF> | 22 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-041` | `0x06442` | <F0><BB><00>PHEW<CB><00>YOU<00>NEED<00>A<F8>BATH<CA><FF> | 21 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-042` | `0x06457` | <F0><BB><00>I<00>OWE<00>YA<00>ONE<CA><FF> | 10 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-043` | `0x06461` | <F0><BB><00>HERE<B9><00><FA><B9><00>TAKE<F8>THIS<00>KANPOU<BA><FF> | 45 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-044` | `0x0648E` | <F0><BB><00>USE<00>IT<00>TO<00>CURE<00><FB><00><CA><FF> | 19 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-045` | `0x064A1` | <F0><BB><00>I<B6>M<00>TORA<B6>S<00>HOLY<00>GUARD<BA><F8>PREPARE<00>FOR<00>HEAVEN<B6>S<00>WRATH<CA><FF> | 50 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-046` | `0x064D3` | <F0><BB><00>HEH<CB>WHAT<CC><FF> | 12 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-047` | `0x064DF` | <F0><BB><00>LOUSY<00>FOREIGNERS<CB><F8>YOUR<00>ENGLISH<00>SUCKS<CA><FF> | 35 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-048` | `0x06502` | <F0><BB><00>HEY<CA><00>GIMME<00>A<00>BREAK<BA><F8>LET<00>BYGONES<00>BE<00>BYGONES<CB><FF> | 38 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-049` | `0x06528` | <F0><BB><00>PLEASE<00>LET<00>ME<00>JOIN<00>YOU<CA><FF> | 21 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-050` | `0x0653D` | <F0><BB><00>LATER<B9><00>BUD<CB><FF> | 15 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-051` | `0x0654C` | <F0><BB><00>HEEHEE<CB><CB><FF> | 19 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-052` | `0x0655F` | <F0><BB><00>NOTHING<00>PERSONAL<CB><F8>SORRY<CA><FF> | 43 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-053` | `0x0658A` | <F0><BB><00>YOU<00>WORK<00>FOR<00><FB><00><CC><F8>WELL<B9><00>I<00>HAVE<00>SOME<00>NEWS<CB><FF> | 45 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-054` | `0x065B7` | <F0><BB><00>TORA<00>TOOK<00>THE<00>GIRL<CA><FF> | 24 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-055` | `0x065CF` | <F0><BB><00>I<00>CAN<B6>T<00>GO<00>WITH<00>YOU<B9><00>SO<B9><F8>INSTEAD<CB><00>LET<00>ME<00>TEACH<00>YOU<FF> | 42 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-056` | `0x065F9` | <F0><BB><00>MY<00>FAMOUS<00>DAGGER<00>ATTACK<CA><FF> | 26 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-057` | `0x06613` | <F0><BB><00>I<00>MUST<00>LEAVE<00>NOW<CB><FF> | 24 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-058` | `0x0662B` | <F0><BB><00>CATCH<00>YA<00>LATER<CB><FF> | 21 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-059` | `0x06640` | <F0><BB><00>LOOKING<00>FOR<00>TORA<CC><F8>BE<00>CAREFUL<CA><FF> | 46 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-060` | `0x0666E` | <F0><BB><00>TORA<00>WOULDN<B6>T<00>KIDNAP<F8>A<00>GIRL<B9><00>WOULD<00>HE<CC><FF> | 34 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-061` | `0x06690` | <F0><BB><00>I<B6>M<00>TELLING<00>YA<B9><00><FB><02><F8>AND<00><FB><03><00>GRABBED<00>HER<CA><FF> | 31 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-062` | `0x066AF` | <F0><BB><00>THEY<B6>RE<00>DANGEROUS<FF> | 18 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-063` | `0x066C1` | <F0><BB><00>YOU<B6>RE<00><FA><CC><00>I<00>HEARD<F8>YOU<B6>RE<00>PRETTY<00>TOUGH<CA><FF> | 41 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-064` | `0x066EA` | <F0><BB><00>PLEASE<00>LET<00>ME<00>JOIN<00>YOU<CA><FF> | 25 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-065` | `0x06703` | <F0><BB><00>PLEASE<CA><FF> | 12 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-066` | `0x0670F` | <F0><BB><00>I<B6>LL<00>BE<00>BACK<CA><FF> | 12 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-067` | `0x0671B` | <FB><02><BB><00>YEAH<B9><00>WE<00>GRABBED<00>THE<F8>GIRL<CB>FOR<00>THE<00>GREAT<00>ONE<FF> | 44 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-068` | `0x06747` | <F0><BB><00>GOTTA<00>BEAT<00>US<00>IF<F8>YA<00>WANT<00>HER<00>BACK<CA><FF> | 38 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-069` | `0x0676D` | <F0><BB><00>THAT<00>BOZO<00>RAN<00>AWAY<CA><F8>UNBELIEVABLE<CA><FF> | 33 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-070` | `0x0678E` | <F0><BB><00>FINISH<00>IT<B9><00>DAMN<00>YOU<CA><FF> | 23 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-071` | `0x067A5` | <F0><BB><00>YOU<B6>LL<00>REGRET<00>LETTING<F8>ME<00>GO<CB><FF> | 25 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-072` | `0x067BE` | <F0><BB><00>YOU<00>AND<00>WHO<B6>S<00>ARMY<F8>WILL<00>STOP<00>US<CC><FF> | 36 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-073` | `0x067E2` | <F0><BB><00>RUN<00>WHILE<00>YOU<00>CAN<CA><FF> | 24 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-074` | `0x067FA` | <F0><BB><00>YOU<00>AGAIN<CB>DAMN<CA><FF> | 14 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-075` | `0x06808` | <F0><BB><00>YOU<B6>RE<00>A<00>BIG<00>JOKE<CA><FF> | 19 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-076` | `0x0681B` | <F0><BB><00>PLEASE<00>LET<00>ME<00>JOIN<00>YOU<CA><FF> | 46 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-077` | `0x06849` | <F0><BB><00>MR<BA><00><FA><B9><00>THE<00>BEEG<F8>BOSS<00>IS<00>BEHIND<00>THIS<CA><FF> | 22 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-078` | `0x0685F` | <F0><BB><00>BE<00>CAREFUL<CA><00>TORA<00>HIRED<F8>SOME<00>GOON<00>CALLED<00>ASAJI<FF> | 48 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-079` | `0x0688F` | <F0><BB><00>BEEG<00>BOSS<00>SAYS<00>THANKS<CB><FF> | 42 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-080` | `0x068B9` | <F0><BB><00>WE<00>MUST<00>FIND<00>OUT<00>WHO<00><F8>ASAJI<00>REALLY<00>WORKS<00>FOR<BA><FF> | 50 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-081` | `0x068EB` | <F0><BB><00>I<B6>M<00>THE<00>BEEG<00>BOSS<CB><F8>I<B6>M<00>BAD<00>AND<00>I<B6>M<00>STRONG<CA><FF> | 32 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-082` | `0x0690B` | <F0><BB><00>FORGIVE<00>ME<B9><00>BRO<B9><00>I<00>WAS<CB><FF> | 25 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-083` | `0x06924` | <F0><BB><00>BROTHER<CB><CA><FF> | 8 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-084` | `0x0692C` | <F0><BB><00>HEH<CB>HOW<00>DO<00>YOU<00>LIKE<F8>MY<00>INGENIOUS<00>MASTER<00>PLAN<CC><FF> | 45 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-085` | `0x06959` | <F0><BB><00>ALL<00>WE<00>NEED<00>TO<00>DO<F8>IS<00>ELIMINATE<00><FB><00><BA><FF> | 47 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-086` | `0x06988` | <F0><BB><00>WATCH<00>YOUR<00>BACKS<CA><F8>HEEHEE<CB><FF> | 21 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-087` | `0x0699D` | TORA<BB><00>I<00>CAN<B6>T<00>BELIEVE<00>YOU<F8>IDIOTS<00>GOT<00>THIS<00>FAR<CA><FF> | 48 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-088` | `0x069CD` | ASAJI<BB><00>YOU<00>TWO<00>ARE<F8>BECOMING<00>A<00>NUISANCE<CA><FF> | 49 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-089` | `0x069FE` | ASAJI<BB><00>WHAT<00>DO<00>YOU<00>WANT<F8>DONE<00>WITH<00>THEM<CC><FF> | 23 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-090` | `0x06A15` | TORA<BB><00>I<B6>LL<00>TAKE<00>CARE<00>OF<F8>THEM<00>PERSONALLY<CB><FF> | 29 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-091` | `0x06A32` | <F0><BB><00>GAWD<B9><00>YOU<00>GUYS<00>ARE<F8>BAD<CA><FF> | 42 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-092` | `0x06A5C` | <F0><BB><00>YA<00>GOT<00>BALLS<CA><FF> | 18 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-093` | `0x06A6E` | <F0><BB><00>YOU<B6>RE<00>STILL<00>ALIVE<CC><FF> | 14 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-094` | `0x06A7C` | ASAJI<BB><00>YOU<00>SORRY<00>PIECE<F8>OF<00>SHIT<CA><FF> | 21 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-095` | `0x06A91` | <F0><BB><00>SO<B9><00>WE<00>MEET<00>AGAIN<BA><00>YOU<F8>BEAT<00>TORA<CC><00>WOW<CA><FF> | 44 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-096` | `0x06ABD` | <F0><BB><00>HERE<B9><00>TAKE<00>THIS<00>CHARM<BA><FF> | 21 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-097` | `0x06AD2` | <F0><BB><00>ARE<00>YOU<00>SHITTING<00>ME<CC><FF> | 24 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-098` | `0x06AEA` | <F0><BB><00>MAYBE<00>YOU<00>CAN<00>BEAT<F8>HIM<00>NOW<BA><FF> | 24 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-099` | `0x06B02` | <F0><BB><00>FIGHT<00>ME<00>IF<00>YOU<00>GOT<F8>THE<00>BALLS<CA><00><71>ASAJI<FF> | 57 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-100` | `0x06B3B` | <F0><BB><00>PLEASE<00>LET<00>ME<00>JOIN<00>YOU<CA><FF> | 21 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-101` | `0x06B50` | <F0><BB><00>BEEG<00>BOSS<00>GAVE<00>ME<F8>THIS<CB><FF> | 21 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-102` | `0x06B65` | <F0><BB><00>OH<00>NO<CA><00>BEEG<00>BOSS<CB><FF> | 20 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-103` | `0x06B79` | <F0><BB><00>WE<B6>LL<00>SETTLE<00>THIS<F8>LATER<BA><FF> | 24 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-104` | `0x06B91` | ASAJI<BB><00><FA><B9><00>WE<B6>RE<00>GONNA<F8>KICK<00>YOUR<00>ASS<CA><FF> | 46 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-105` | `0x06BBF` | <FB><04><BB><00>BUT<00>FIRST<B9><00>LET<F8>ME<00>CLUE<00>YOU<00>IN<CB><FF> | 46 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-106` | `0x06BED` | <FB><04><BB><00>YOU<00>WERE<00>JUST<00>A<00>PAWN<CB><FF> | 26 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-107` | `0x06C07` | ASAJI<BB><00>SO<B9><00>PRAY<00>WHILE<00>YOU<00>CAN<CA><FF> | 29 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-108` | `0x06C24` | <F0><BB><00>HEH<CB>STUPID<00>BASTARDS<CA><FF> | 17 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-109` | `0x06C35` | <F0><BB><00>ISN<B6>T<00>THE<00>MUSIC<00>IN<00>THIS<F8>VIDEO<00>GAME<00>GREAT<CA><CC><FF> | 26 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-110` | `0x06C4F` | <F0><BB><00>THEY<B6>RE<00>BACK<00>TO<00>HAVE<F8>THEIR<00>ASSES<00>KICKED<00>AGAIN<CA><FF> | 17 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-111` | `0x06C60` | <FF><F0><BB><00>HUH<CC><FF> | 5 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-112` | `0x06C65` | <F0><BB><00>TAKE<00>THAT<CB><00>WHA<CB><CC><FF> | 12 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-113` | `0x06C71` | <F0><BB><00>NOW<00>I<B6>M<00>REALLY<00>PISSED<CA><FF> | 23 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-114` | `0x06C88` | <F0><BB><00>AIYEE<CA><FF> | 7 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-115` | `0x06C8F` | <F0><BB><00>DUM<71>DEE<71>DUM<FF> | 14 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-116` | `0x06C9D` | <F0><BB><00>HEY<B9>TWERP<CA><FF> | 19 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-117` | `0x06CB0` | <F0><BB><00>ONE<00>MO<B6>TIME<CA><FF> | 16 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-118` | `0x06CC0` | <F0><BB><00>ROCK<00>N<B6><00>ROLL<CA><FF> | 18 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-119` | `0x06CD2` | <F0><BB><00>JEEZ<B9><00>THIS<00>SUCKS<CA><FF> | 17 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-120` | `0x06CE3` | <F0><BB><00>WHOOPS<CA><FF> | 13 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-121` | `0x06CF0` | <F0><BB><00>WHAT<00>THE<00><B1><AD><CA><B2><CC><FF> | 22 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-122` | `0x06D06` | <F0><BB><00>LEMME<00>HIT<00><B6>EM<CA><FF> | 19 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-123` | `0x06D19` | <F0><BB><00>I<B6>M<00>GONNA<00>KICK<F8>YOUR<00>ASS<CA><FF> | 18 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-124` | `0x06D2B` | <F0><BB><00>YA<00>WIMP<CA><FF> | 11 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-125` | `0x06D36` | <F0><BB><00>EAT<00>THIS<CA><FF> | 12 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-126` | `0x06D42` | <F0><BB><00>I<B6>LL<00>REMEMBER<00>YOU<CA><FF> | 15 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-127` | `0x06D51` | <F0><BB><00>EEE<CB><FF> | 13 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-128` | `0x06D5E` | <F0><BB><00>ARGH<CB><FF> | 8 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-129` | `0x06D66` | <F0><BB><00>DICKWEED<CA><FF> | 11 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-130` | `0x06D71` | <F0><BB><00>WAH<CA><FF> | 12 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-131` | `0x06D7D` | <F0><BB><00>GWA<CA><FF> | 8 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-132` | `0x06D85` | <F0><BB><00>AIYEE<CA><FF> | 7 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-133` | `0x06D8C` | <F0><BB><00>ARGH<CB><FF> | 8 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-134` | `0x06D94` | <F0><BB><00>AI<71>YAI<71>YAI<CA><FF> | 10 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-135` | `0x06D9E` | WELCOME<CA><FF> | 12 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-136` | `0x06DAA` | WHAT<00>WOULD<00>YOU<00>LIKE<CC><FF> | 24 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-137` | `0x06DC2` | YOUR<00>INVENTORY<00>IS<00>FULL<BA><FF> | 31 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-138` | `0x06DE1` | YOU<00>DON<B6>T<00>HAVE<00>ENOUGH<F8>MONEY<BA><FF> | 18 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-139` | `0x06DF3` | ARE<00>YOU<00>SURE<CC><FF> | 16 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-140` | `0x06E03` | THANKS<CA><FF> | 10 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-141` | `0x06E0D` | <F0><00>ATE<00><F1><FF> | 10 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-142` | `0x06E17` | <F0><00>DRANK<00><F1><FF> | 10 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-143` | `0x06E21` | <F0><00>GOT<00><F1><FF> | 12 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-144` | `0x06E2D` | <F0><00>EQUIPPED<00><F1><FF> | 12 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-145` | `0x06E39` | ANYTHING<00>ELSE<CC><FF> | 15 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-146` | `0x06E48` | THANKS<CA><00>COME<00>AGAIN<FF> | 30 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-147` | `0x06E66` | WILL<00>YOU<00>STAY<CC><FF> | 11 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-148` | `0x06E71` | PLEASE<00>RELAX<FF> | 15 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-149` | `0x06E80` | RESTED<CA><FF> | 8 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-150` | `0x06E88` | WANNA<00>GAMBLE<CC><FF> | 15 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-151` | `0x06E97` | READY<CC><FF> | 17 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-152` | `0x06EA8` | GO<00>NOW<CA><FF> | 15 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-153` | `0x06EB7` | WE<00>HAVE<00><FD><00>AND<00><FE><CB><CB><FC><CA><FF> | 16 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-154` | `0x06EC7` | YOU<00>WON<CA><FF> | 21 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-155` | `0x06EDC` | YOU<00>LOST<CB><FF> | 21 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-156` | `0x06EF1` | WELL<CC><FF> | 14 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-157` | `0x06EFF` | SANKI<BB><00>WELCOME<00>BACK<CA><FF> | 16 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-158` | `0x06F0F` | <F0><BB><00>NEED<00>SOMETHING<CC> | 15 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-159` | `0x06F1E` | <F0><BB><00>MY<00>PLEASURE<CA><FF> | 15 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-160` | `0x06F2D` | <F0><BB><00>NEED<00>SOMETHING<CC> | 15 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-161` | `0x06F3C` | <F0><BB><00>BE<00>CAREFUL<CA><FF> | 14 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-162` | `0x06F4A` | <FF> | 15 | `structural_unknown_missing_conservative_row` | named route, save state, or cheat state required |
| `PTR-163` | `0x06F59` | CHOOSE<00>ALLY<FF> | 23 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-164` | `0x06F70` | SANKI<BB><00><FA><CA><00>OKOTO<00>HAS<CB><CA><FF> | 35 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-165` | `0x06F93` | SANKI<BB><00>TWO<00>GUYS<CB>STRUCK<F8>LIKE<00>LIGHTNING<CB><FF> | 37 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-166` | `0x06FB8` | SANKI<BB><00>I<00>WAS<00>HELPLESS<CB>SORRY<FF> | 28 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-167` | `0x06FD4` | <FA><BB><00>IDIOTS<CA><00>WE<B6>LL<F8>FIND<00>THEM<BA><FF> | 18 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-168` | `0x06FE6` | <F0><BB><00>THE<00>KANPOU<00>WORKED<CA><F8>I<B6>M<00>CURED<CA><FF> | 33 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-169` | `0x07007` | <F0><BB><00>AT<00>LAST<CA><00>I<00>CAN<00>JOIN<F8>THE<00>WAR<00>AGAINST<00>TORA<CA><FF> | 38 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-170` | `0x0702D` | <F0><BB><00><FA><B9><00>THIS<00>CHARM<F8>WILL<00>PROTECT<00>YOU<BA><FF> | 48 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-171` | `0x0705D` | <F0><BB><00>I<B6>LL<00>WAIT<00>HERE<CB><F8>GO<00>SAVE<00>OKOTO<CA><FF> | 43 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-172` | `0x07088` | <F0><BB><00>YEAH<CB><FF> | 6 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-173` | `0x0708E` | ASAJI<BB><00>WHY<00>NOT<00>GO<00>TO<00><F4><CC><FF> | 33 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-174` | `0x070AF` | <F0><BB><00>I<B6>D<00>BETTER<00>GO<F8>CHECK<00>WITH<00>BEEG<00>BOSS<CB><FF> | 42 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-175` | `0x070D9` | <F0><BB><00>PLEASE<B9><00>LET<00>ME<F8>GO<B9><00><FA><FF> | 17 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-176` | `0x070EA` | <F0><BB><00><FA><B9><00>SOMEONE<F8>LEFT<00>THIS<00>AT<00>THE<00>DOOR<BA><FF> | 23 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-177` | `0x07101` | OKOTO<BB><00>WAH<CA><00>ASAJI<00>KIDNAPPED<F8>ME<CA><FF> | 50 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-178` | `0x07133` | <F0><BB><00>GO<00>HOME<CB><F8>EVERYONE<B6>S<00>WORRIED<FF> | 32 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-179` | `0x07153` | OKOTO<BB><00><CB>SOB<CB>THANK<00>YOU<BA><F8>PLEASE<CB>BE<00>CAREFUL<CB><FF> | 42 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-180` | `0x0717D` | <F0><BB><00><FA><B9><00>ASAJI<00>HAS<F8>DISAPPEARED<CB><FF> | 27 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-181` | `0x07198` | TSUU<BB><00>BROTHER<CA><00>WAIT<CA><FF> | 30 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-182` | `0x071B6` | KUNIO<BB><00>HURRY<B9><00>SLUG<CA><F8>MR<BA><00>BUNZO<B6>S<00>IN<00>TROUBLE<CA><FF> | 37 | `development_verified_opening` | bounded opening route; no combat required |
| `PTR-183` | `0x071DB` | OKOTO<BB><00>KUNIO<CA><FF> | 21 | `development_verified_opening` | bounded opening route; no combat required |
| `PTR-184` | `0x071F0` | KUNIO<BB><00>I<00>TRIED<00>TO<00>HURRY<00>BACK<CA><FF> | 24 | `development_verified_opening` | bounded opening route; no combat required |
| `PTR-185` | `0x07208` | OKOTO<BB><00>THIS<00>MAN<00>IS<CB><FF> | 15 | `development_verified_opening` | bounded opening route; no combat required |
| `PTR-186` | `0x07217` | ASAJI<BB><00>HEH<CB>I<B6>M<00>OKOTO<B6>S<F8>FIANCE<BA><FF> | 43 | `development_verified_opening` | bounded opening route; no combat required |
| `PTR-187` | `0x07242` | KUNIO<BB><00>WE<B6>LL<00>SEE<00>ABOUT<00>THAT<CA><FF> | 7 | `development_verified_opening` | bounded opening route; no combat required |
| `PTR-188` | `0x07249` | ASAJI<BB><00>SHUT<00>UP<B9><00>LOSER<CA><00>THE<F8>BOSS<00>IS<00>WAITING<CB><FF> | 30 | `development_verified_opening` | bounded opening route; no combat required |
| `PTR-189` | `0x07267` | KUNIO<BB><00>OH<B9><00>MASTER<CA><F8>FORGIVE<00>MY<00>DELAY<CA><FF> | 25 | `development_verified_opening` | bounded opening route; no combat required |
| `PTR-190` | `0x07280` | BUNZO<BB><00>AH<B9><00>KUNIO<CA><F8>YOU<00>FINALLY<00>GOT<00>HERE<CA><FF> | 44 | `development_verified_opening` | bounded opening route; no combat required |
| `PTR-191` | `0x072AC` | BUNZO<BB><00>TORA<00>HAS<00>CURSED<00>ME<CA><FF> | 26 | `development_verified_opening` | bounded opening route; no combat required |
| `PTR-192` | `0x072C6` | BUNZO<BB><00>GO<00>FIND<00>A<00>HEALER<CB><FF> | 22 | `development_verified_opening` | bounded opening route; no combat required |
| `PTR-193` | `0x072DC` | BUNZO<BB><00><CB>WHO<00>HAS<00>KANPOU<CA><FF> | 27 | `development_verified_opening` | bounded opening route; no combat required |
| `PTR-194` | `0x072F7` | KUNIO<BB><00>YOU<00>CAN<00>COUNT<00>ON<00>ME<CA><FF> | 41 | `development_verified_opening` | bounded opening route; no combat required |
| `PTR-195` | `0x07320` | BUNZO<BB><00>PLEASE<00>HURRY<CA><FF> | 20 | `development_verified_opening` | bounded opening route; no combat required |
| `PTR-196` | `0x07334` | <F0><BB><00>GOOD<00>JOB<CA><FF> | 13 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-197` | `0x07341` | <F0><BB><00>YOU<00>SAVED<00>THE<00>DAY<CA><FF> | 40 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-198` | `0x07369` | <F0><BB><00>BY<00>THE<00>WAY<B9><00><FA><CB><FF> | 12 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-199` | `0x07375` | <F0><BB><00>OKOTO<00>AND<00>YOU<F8>WILL<00>MAKE<00>A<00>FINE<00>FAMILY<BA><FF> | 39 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-200` | `0x0739C` | <F0><BB><00>RIGHT<B9><00>OKOTO<CC><FF> | 11 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-201` | `0x073A7` | OKOTO<BB><00>OH<B9><00>YES<CA><FF> | 8 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-202` | `0x073AF` | <F0><BB><00><FA><B9><00>I<00>BEG<00>YOU<CA><00><FF> | 21 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-203` | `0x073C4` | <F0><BB><00>GREAT<CA><00>A<00>MOMENT<F8>OF<00>ULTIMATE<00>HAPPINESS<CA><FF> | 29 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-204` | `0x073E1` | <F0><BB><00>I<B6>LL<00>ORDER<00>SAKE<F8>TO<00>CELEBRATE<CA><FF> | 35 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-205` | `0x07404` | <FA><BB><00>I<B6>M<00>A<00>VAGABOND<CB><F8>DRIFTING<00>FROM<00>TOWN<00>TO<00>TOWN<CB><FF> | 42 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-206` | `0x0742E` | <FA><BB><00>OKOTO<00>DESERVES<F8>SOMETHING<00>MUCH<00>BETTER<BA><FF> | 41 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-207` | `0x07457` | <F0><BB><00>SORRY<00>YOU<00>FEEL<00>THAT<F8>WAY<CB><00>BUT<CB><FF> | 42 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-208` | `0x07481` | <F0><BB><00>COME<00>SEE<00>US<CB><FF> | 26 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-209` | `0x0749B` | <F0><BB><00>WHENEVER<00>YOU<B6>RE<00>IN<F8>TOWN<BA><FF> | 29 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-210` | `0x074B8` | <FA><BB><00>YOU<00>GOT<00>IT<CA><F8>NOW<B9><00>I<00>MUST<00>GO<BA><FF> | 27 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-211` | `0x074D3` | <F0><BB><00>FAREWELL<CB><FF> | 10 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-212` | `0x074DD` | OKOTO<BB><00><FA><CB><FF> | 10 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-213` | `0x074E7` | OKOTO<BB><00><FA><CB><FA><CB>SOB<CB><FF> | 14 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-214` | `0x074F5` | DUM<71>DE<71>DUM<CB>DOESN<B6>T<F8>THIS<00>STORY<00>GRAB<00>YOU<CC><FF> | 32 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-215` | `0x07515` | YOU<00>FINISHED<00>IT<CC><F8>DON<B6>T<00>YOU<00>HAVE<00>A<00>LIFE<CC><FF> | 44 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-216` | `0x07541` | MAYBE<00>WE<B6>LL<00>MEET<00>AGAIN<CB><F8>AND<00>KICK<00>YOUR<00>ASS<CA><FF> | 42 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-217` | `0x0756B` | THE<00>END<CA><FF> | 8 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-218` | `0x07573` | <B6>S<00>ADVENTURE<00>BEGINS<00>NOW<CB><FF> | 17 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-219` | `0x07584` | WELCOME<00>TO<FF> | 14 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-220` | `0x07592` | DOWNTOWN<00>SPECIAL<CB><F8>HAIL<B9><00>FIGHTERS<CA><FF> | 26 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-221` | `0x075AC` | MEET<00>US<00>IN<CB><FF> | 8 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-222` | `0x075B4` | SURUGA<CB>LAND<00>OF<00>MYSTERY<CB><F8>HOME<00>OF<00>MT<BA><00>FUJI<BA><FF> | 38 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-223` | `0x075DA` | ACROSS<00>THE<00>RAGING<00>SEA<CB><FF> | 23 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-224` | `0x075F1` | DUTY<00>CALLS<CB><F8>AND<00>ROMANCE<CB><FF> | 31 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-225` | `0x07610` | KUNIO<B6>S<00>LOVE<00>AWAITS<CB><FF> | 16 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-226` | `0x07620` | OR<00>DOES<00>SHE<CC><FF> | 28 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-227` | `0x0763C` | USED<00><F1><BA><FF> | 11 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-228` | `0x07647` | ARE<00>YOU<00>READY<00>FOR<F8>THIS<00>NEW<00>AREA<CC><00>YEAH<CA><FF> | 31 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-229` | `0x07666` | <F0><00>GAVE<00><F1><FF> | 12 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-230` | `0x07672` | <F0><00>DROPPED<00><F1><FF> | 11 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-231` | `0x0767D` | <F0><B6>S<00>STATUS<00>IS<00>UP<CA><FF> | 17 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-232` | `0x0768E` | <F0><B6>S<00><F2><00>IS<00>UP<00><F5><CA><FF> | 14 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-233` | `0x0769C` | <F0><B6>S<00><F2><00>UP<00>BY<00><F5><CA><FF> | 16 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-234` | `0x076AC` | <F0><B6>S<00><F2><00>IS<00>MAXXED<CA><FF> | 15 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-235` | `0x076BB` | <F0><00>LEARNED<00>A<00>TECHNIQUE<CA><FF> | 13 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-236` | `0x076C8` | STATUS<00>LEVELS<71>UP<00>NOW<00>DOUBLE<CA><FF> | 25 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-237` | `0x076E1` | USE<00>MAP<00>CURSOR<00>TO<00>TRAVEL<FF> | 23 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-238` | `0x076F8` | <F0><00>REMOVED<00><F1><FF> | 12 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-239` | `0x07704` | <F0><00>SMILES<CA><FF> | 14 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-240` | `0x07712` | <F0><00>FELT<00>LIGHTER<FF> | 20 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-241` | `0x07726` | A<00>GREAT<00>MOMENT<CA><FF> | 17 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-242` | `0x07737` | EQUIPMENT<00>STATS<00>NOW<00>DOUBLE<CA><FF> | 26 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-243` | `0x07751` | <F0><00>FELL<FF> | 11 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-244` | `0x0775C` | <F1><CA><FF> | 5 | `structural_unknown_missing_conservative_row` | named route, save state, or cheat state required |
| `PTR-245` | `0x07761` | <F0><00>FAMILY<CA><FF> | 8 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-246` | `0x07C00` | <03><C8><B1><2A><29><0F><9D><35><03><29><08><F0><08><BD><35><03><09><F0><9D><35><03><B1><2A><29><F0><9D><2D><03><C8><4C><B1><BB><A9><00>MF<06><60><30><BC><30><BC><39><BC><4A><BC><5B><BC><6F><BC><78><BC>A<BC>J<BC>S<BC>X<BC><9D><BC><30><BC><00>B<4F><00><01>C<4F><00><FF> | 73 | `structural_unknown` | named route, save state, or cheat state required |
| `PTR-247` | `0x0429B` |  | 0 | `structural_unknown_missing_conservative_row` | named route, save state, or cheat state required |

The TSV and JSON files preserve all original and reference bytes so a
future compiler can build a declared record without rediscovering it by
blind autoplay.
