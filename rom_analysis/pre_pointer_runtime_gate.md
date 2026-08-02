# Pre-Pointer Runtime Gate

- Targets scanned: `168`.
- Runtime-approved records: `10`.
- Approved IDs: `EN-PRE-068, EN-PRE-069, EN-PRE-075, EN-PRE-076, EN-PRE-085, EN-PRE-087, EN-PRE-112, EN-PRE-133, EN-PRE-138, EN-PRE-169`.
- Classification counts: `{"RUNTIME_SOURCE_READ": 10, "RUNTIME_SOURCE_READ_EMPTY_OR_DATA": 2, "RUNTIME_SOURCE_READ_UNKNOWN_PC": 4, "STATIC_ONLY": 152}`.
- Release status: `NOT_READY`; this is a soft development gate, not visual release approval.

A record is approved here only when a non-empty target was read by the known Bank 1 render-source PCs `$8205` or `$8209` and its single-record structural probe does not regress the baseline route. Static memory presence alone is insufficient.

| record | offset | text | reads | PCs | first frame | PPU writes near first read | route probe | classification |
| --- | --- | --- | ---: | --- | ---: | --- | --- | --- |
| EN-PRE-000 | `0x056BC` | YUKI<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-001 | `0x056C1` | ITOKISAKI<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-002 | `0x056CB` | TAMO<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-003 | `0x056D0` | SAIZOHAGI<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-004 | `0x056DA` | HASHIKOSU<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-005 | `0x056E4` | HANSUKOUE<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-006 | `0x056EE` | HIRA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-007 | `0x056F3` | HIDE<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-008 | `0x056F8` | ASHI<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-009 | `0x056FD` | BEN<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-010 | `0x05701` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-011 | `0x05702` | SAITAMOEMOMURA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-012 | `0x05711` | SADA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-013 | `0x05716` | SEKI<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-014 | `0x0571B` | YOTSUTOMO<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-015 | `0x05725` | KUMA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-016 | `0x0572A` | WATA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-017 | `0x0572F` | URAE<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-018 | `0x05734` | TOME<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-019 | `0x05739` | ONOKIYATA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-020 | `0x05743` | ISORORIHEICHIE<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-021 | `0x05752` | SUMI<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-022 | `0x05757` | SHIN<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-023 | `0x0575C` | MUNE<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-024 | `0x05761` | GENSUOISA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-025 | `0x0576B` | HEMO<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-026 | `0x05770` | YOTA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-027 | `0x05775` | KAME<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-028 | `0x0577A` | TAKI<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-029 | `0x0577F` | HISA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-030 | `0x05784` | SAHEIKISU<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-031 | `0x0578E` | NORI<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-032 | `0x05793` | KOUKISUEMATAKE<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-033 | `0x057A2` | UMEMABOBU<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-034 | `0x057AC` | YUUE<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-035 | `0x057B1` | YOSHIRIHE<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-036 | `0x057BB` | HACHIDEZOUKUMI<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-037 | `0x057CA` | TARO<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-038 | `0x057CF` | URASAYONE<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-039 | `0x057D9` | SHIMATERU<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-040 | `0x057E3` | SUYA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-041 | `0x057E8` | MORI<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-042 | `0x057ED` | ISHI<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-043 | `0x057F2` | SAKU<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-044 | `0x057F7` | URAJISHIBAJMGQ<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-045 | `0x05806` | SHIROJUNZOINETAAKIZOYURI<FF> | 304 | $8250,$825E,$8282,$8469 | 1201 | 20 | - | RUNTIME_SOURCE_READ_UNKNOWN_PC |
| EN-PRE-046 | `0x0581F` | SUTE<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-047 | `0x05824` | SHUU<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-048 | `0x05829` | EBINOCHIJIATSU<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-049 | `0x05838` | KANA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-050 | `0x0583D` | SUKE<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-051 | `0x05842` | GOSU<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-052 | `0x05847` | TSUNOKIKU<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-053 | `0x05851` | TOSHITSUKIOBISAYASU<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-054 | `0x05865` | KENGOMANSIKATSUSONO<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-055 | `0x05879` | GOSA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-056 | `0x0587E` | TOUBEZENE<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-057 | `0x05888` | OMENOMOCHISHOU<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-058 | `0x05897` | INGO<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-059 | `0x0589C` | NEHA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-060 | `0x058A1` | TEMA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-061 | `0x058A6` | MOHE<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-062 | `0x058AB` | SOME<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-063 | `0x058B0` | KAMO<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-064 | `0x058B5` | MATA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-065 | `0x058BA` | UKI<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-066 | `0x058BE` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-067 | `0x058BF` | GORO<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-068 | `0x058C4` | KOTA<FF> | 117 | $8205 | 330 | 4 | 24 | RUNTIME_SOURCE_READ |
| EN-PRE-069 | `0x058C9` | TSUDAINOSUUMETAUSUKEMANGONENKIKURO<FF> | 579 | $8205 | 330 | 4 | 24 | RUNTIME_SOURCE_READ |
| EN-PRE-070 | `0x058EC` | TEHA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-071 | `0x058F1` | SENBESENPAHOME<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-072 | `0x05900` | TAHA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-073 | `0x05905` | KICHINETA<FF> | 145 | $8250,$825E,$8282,$8469 | 1201 | 20 | - | RUNTIME_SOURCE_READ_UNKNOWN_PC |
| EN-PRE-074 | `0x0590F` | TAGO<FF> | 285 | $8250,$825E,$8282 | 1201 | 20 | - | RUNTIME_SOURCE_READ_UNKNOWN_PC |
| EN-PRE-075 | `0x05914` | MANPEKETA<FF> | 700 | $8205,$8250,$8469 | 312 | 48 | 24 | RUNTIME_SOURCE_READ |
| EN-PRE-076 | `0x0591E` | KUNKIMOMO<FF> | 312 | $8205 | 334 | 4 | 24 | RUNTIME_SOURCE_READ |
| EN-PRE-077 | `0x05928` | TANE<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-078 | `0x0592D` | HEKO<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-079 | `0x05932` | MATAAMEHEIMASU<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-080 | `0x05941` | UNJI<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-081 | `0x05946` | MONO<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-082 | `0x0594B` | DENSUUMESIMAGO<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-083 | `0x0595A` | RAHA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-084 | `0x0595F` | MOHEISENROCHOU<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-085 | `0x0596E` | KAN<FF> | 192 | $8205 | 346 | 4 | 24 | RUNTIME_SOURCE_READ |
| EN-PRE-086 | `0x05972` | <FF> | 48 | $8205 | 346 | 4 | - | RUNTIME_SOURCE_READ_EMPTY_OR_DATA |
| EN-PRE-087 | `0x05973` | KANPAIMOHAMINO<FF> | 144 | $8205 | 346 | 4 | 24 | RUNTIME_SOURCE_READ |
| EN-PRE-088 | `0x05982` | KANTAFUNE<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-089 | `0x0598C` | KANSUSUJI<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-090 | `0x05996` | SICHIUSHI<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-091 | `0x059A0` | ROHEIKOME<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-092 | `0x059AA` | GOBEEZENJISUNE<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-093 | `0x059B9` | KINE<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-094 | `0x059BE` | SUZU<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-095 | `0x059C3` | INEMOHATA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-096 | `0x059CD` | UNOMAYAENONEKI<FF> | 110 | $8250,$825E,$8282,$8469 | 1640 | 0 | - | RUNTIME_SOURCE_READ_UNKNOWN_PC |
| EN-PRE-104 | `0x05AAD` | SCREW<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-105 | `0x05AB3` | TORNADO<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-107 | `0x05AC2` | HELICPTR<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-108 | `0x05ACB` | DRILL<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-111 | `0x05AE2` | HEADBUTT<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-112 | `0x05AEB` | BMPKNART<FF> | 468 | $8205 | 312 | 48 | - | RUNTIME_SOURCE_READ |
| EN-PRE-116 | `0x05B0B` | MASSAGE<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-117 | `0x05B13` | BIGBANG<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-118 | `0x05B1B` | WARPSHOT<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-119 | `0x05B24` | DEFLECT<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-122 | `0x05B3D` | PICKLE<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-123 | `0x05B44` | MEAL<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-124 | `0x05B49` | SOBA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-125 | `0x05B4E` | UDON<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-126 | `0x05B53` | SOUP<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-127 | `0x05B58` | IMO<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-128 | `0x05B5C` | FISH<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-129 | `0x05B61` | TENPURA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-130 | `0x05B69` | DANGO<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-131 | `0x05B6F` | RICEBALL<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-132 | `0x05B78` | MANJUU<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-133 | `0x05B7F` | SUSHI<FF> | 58 | $8205 | 1201 | 20 | 24 | RUNTIME_SOURCE_READ |
| EN-PRE-134 | `0x05B85` | SALVE<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-135 | `0x05B8B` | POULTICE<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-136 | `0x05B94` | TONIC<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-138 | `0x05BA2` | ELIXIR<FF> | 2 | $8205 | 1201 | 20 | 24 | RUNTIME_SOURCE_READ |
| EN-PRE-151 | `0x05BFD` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-160 | `0x05C36` | DOUBLEUP<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-169 | `0x05C7B` | GOODTIME<FF> | 940 | $8209 | 312 | 48 | 24 | RUNTIME_SOURCE_READ |
| EN-PRE-174 | `0x05CA3` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-175 | `0x05CA4` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-177 | `0x05CAC` | RAINCOAT<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-178 | `0x05CB5` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-179 | `0x05CB6` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-180 | `0x05CB7` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-181 | `0x05CB8` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-183 | `0x05CD6` | VIT<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-184 | `0x05CDA` | PUNCH<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-185 | `0x05CE0` | KICK<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-186 | `0x05CE5` | WPN<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-187 | `0x05CE9` | THROW<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-188 | `0x05CEF` | AGI<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-189 | `0x05CF3` | WILL<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-190 | `0x05CF8` | DEF<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-191 | `0x05CFC` | STR<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-194 | `0x05D11` | SURUGA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-195 | `0x05D18` | Z<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-196 | `0x05D1A` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-197 | `0x05D1B` | <FF> | 24 | $8405 | 222 | 100 | - | RUNTIME_SOURCE_READ_EMPTY_OR_DATA |
| EN-PRE-198 | `0x05D1C` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-199 | `0x05D1D` | KOUZ<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-200 | `0x05D22` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-201 | `0x05D23` | RIKUC<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-202 | `0x05D29` | ECCHU<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-203 | `0x05D2F` | INA<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-204 | `0x05D33` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-205 | `0x05D34` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-206 | `0x05D35` | KAW<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-207 | `0x05D39` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-208 | `0x05D3A` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-209 | `0x05D3B` | TO<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-210 | `0x05D3E` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-211 | `0x05D3F` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-212 | `0x05D40` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-213 | `0x05D41` | NAG<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-214 | `0x05D45` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-215 | `0x05D46` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-216 | `0x05D47` | HIZ<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-217 | `0x05D4B` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-218 | `0x05D4C` | <FF> | 0 |  | - | 0 | - | STATIC_ONLY |
| EN-PRE-220 | `0x05D51` | ODD<FF> | 0 |  | - | 0 | - | STATIC_ONLY |
