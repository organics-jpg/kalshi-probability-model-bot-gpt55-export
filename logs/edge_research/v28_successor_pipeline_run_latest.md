# v28 Successor Research Pipeline Run

Research-only sequential refresh manifest. This report does not touch live bot state, orders, thresholds, secrets, or processes.

## Summary

- Generated UTC: `2026-05-12T07:30:55Z`
- Pipeline status: `pass`
- Dry run: `False`
- Steps run: `37` / `37`
- Failed steps: `[]`

## Steps

| step | status | seconds | purpose |
|---|---|---:|---|
| `seed_dataset` | `pass` | 0.537 | canonical posthoc diagnostic seed rows |
| `baseline_replay` | `pass` | 1.461 | audit logged/recomputed v28 baseline availability |
| `logged_event_dataset` | `pass` | 1.642 | logged v28 event diagnostic rows |
| `logged_event_api_replay` | `pass` | 1.579 | research-only v28 component replay |
| `seed_features` | `pass` | 0.178 | leakage-safe seed feature table |
| `logged_event_features` | `pass` | 0.625 | richer logged-event feature table |
| `seed_candidates` | `pass` | 2.162 | simple inspectable seed challengers |
| `logged_event_candidates` | `pass` | 5.563 | simple inspectable logged-event challengers |
| `passive_forward_snapshots` | `pass` | 0.792 | passive book staging rows |
| `forward_packet_contract` | `pass` | 0.154 | packet contract validation |
| `shadow_forward_packets` | `pass` | 3.255 | paired shadow packet bridge |
| `forward_packet_scoring` | `pass` | 0.923 | score packet-shaped rows with collection candidates |
| `forward_packet_adapter` | `pass` | 0.098 | sidecar packet adapter fixture |
| `public_rest_sidecar_bundle` | `pass` | 0.204 | one-shot public REST sidecar bundle builder fixture |
| `public_rest_sidecar_batch` | `pass` | 0.237 | batch public REST sidecar bundle builder fixture |
| `sidecar_bundle_replay` | `pass` | 2.903 | replay recorded sidecar market/book/BTC bundles through v28 |
| `sidecar_input_bundle_contract` | `pass` | 0.087 | sidecar input bundle template and contract |
| `sidecar_packet_collector` | `pass` | 0.098 | sidecar packet collector contract fixture |
| `sidecar_bundle_freeze_handoff` | `pass` | 0.119 | bundle-to-freeze one-command handoff |
| `sidecar_bundle_batch_handoff` | `pass` | 3.774 | batch bundle-to-freeze handoff |
| `sidecar_bundle_batch_settlement_labels` | `pass` | 30.054 | post-close settlement labels for sidecar batch frozen rows |
| `sidecar_bundle_batch_label_join` | `pass` | 0.323 | post-resolution label join for sidecar batch frozen rows |
| `sidecar_batch_evidence_score` | `pass` | 0.329 | probability-first scoring for sidecar batch evidence |
| `sidecar_collection_cycle` | `pass` | 34.467 | one-cycle sidecar freeze/label/score/audit refresh without new public capture |
| `forward_packet_freeze_handoff` | `pass` | 0.078 | validate/freeze/register sidecar packet handoff |
| `forward_freeze_preflight` | `pass` | 0.117 | freeze readiness preflight |
| `freeze_forward_candidates` | `pass` | 0.123 | strict frozen prediction ledger |
| `stage_sidecar_forward_evidence` | `pass` | 0.174 | stage valid sidecar frozen rows as canonical forward evidence inputs |
| `forward_registry` | `pass` | 0.285 | register strict frozen prediction ledger |
| `forward_label_join` | `pass` | 0.3 | post-resolution label join |
| `forward_evidence_score` | `pass` | 0.367 | settled forward candidate-vs-v28 score |
| `source_contract` | `pass` | 0.447 | source-quality contract |
| `forward_source_readiness` | `pass` | 1.274 | source coverage and joinability audit |
| `promotion_verifier` | `pass` | 0.13 | strict promotion verifier |
| `forward_collection_spec` | `pass` | 0.125 | future collection handoff |
| `goal_completion_audit` | `pass` | 0.203 | objective completion audit |
| `unit_tests` | `pass` | 7.4 | pipeline invariant tests |

## Key Artifacts

| artifact | exists | bytes | sha256 |
|---|---:|---:|---|
| `logs/edge_research/v28_successor_goal_completion_audit_latest.json` | True | 29025 | `3c2b5fb037113bf977c60bde07a16f9598547fc301d8fa6ec96d505eeecf1f75` |
| `logs/edge_research/v28_successor_source_contract_latest.json` | True | 50400 | `1ebcfd147f828e9a82fef0327222e2280e9531506911a46bc8c2a6ec303c1403` |
| `logs/edge_research/v28_successor_forward_source_readiness_latest.json` | True | 25316 | `18fb205877f8b1cd2aed698d028a21292572a72dfa41ab7d734e4c27a64ca27b` |
| `logs/edge_research/v28_successor_promotion_verifier_latest.json` | True | 87834 | `c9a25c88e16b9fd78cde9181db2793a617b40a90be8d2c1261229556ccbc7d4f` |
| `logs/edge_research/v28_successor_forward_registry_latest.json` | True | 4084 | `e830a9fd82e88eb5726524fe7bc2c0cba94fc6cf3f660a9fb32ebc402d1b460f` |
| `logs/edge_research/v28_successor_forward_evidence_score_latest.json` | True | 114777 | `276b35397a5dc61b2cfa0a51aa9da74c9e24623028568563fdc87487b2420a12` |
| `logs/edge_research/v28_successor_forward_label_join_latest.json` | True | 54130 | `a62d226d3f08fc60a6cec4232444ce03899ccfe97fb9522519263a7f677231ca` |
| `logs/edge_research/v28_successor_forward_packet_adapter_latest.json` | True | 35543 | `8593e2a16aa0dc9e126331ca408e3cd48b03c55eabf05763ab29dfcb1e46f410` |
| `logs/edge_research/v28_successor_public_rest_sidecar_bundle_latest.json` | True | 12758 | `dbfab1a602731fc45c469444201b7e929f9480d1e002e700a21eed6f0ec974fc` |
| `logs/edge_research/v28_successor_public_rest_sidecar_batch_latest.json` | True | 2063 | `296d1a4428223bc0ba754e55e963b3ed68807454b57df0936c9f76ace4ca330e` |
| `logs/edge_research/v28_successor_sidecar_bundle_replay_latest.json` | True | 172202 | `6b087788a4bb5fd76b81824a2fe7bae421c6be7dfc5bcfff31ec456b7759e37b` |
| `logs/edge_research/v28_successor_sidecar_input_bundle_contract_latest.json` | True | 80253 | `637faa5b0f8e638a72579ae019dc3a3d9c0fe56c9fcb46720d81682e53d268f6` |
| `logs/edge_research/v28_successor_sidecar_packet_collector_latest.json` | True | 70845 | `72e8b94da525e5bb2ca0165588b112d31d589c5a67f9d4059633f79173603bc9` |
| `logs/edge_research/v28_successor_sidecar_bundle_freeze_handoff_latest.json` | True | 97107 | `86ce3bd62e336c3533d6bb9ce34510db106c16ac29f225a095b5def02b94200e` |
| `logs/edge_research/v28_successor_sidecar_bundle_batch_handoff_latest.json` | True | 208106 | `77cb811847cd3e7411678e975688b7e0f565370ab712c1fb91e2a40863d9dc59` |
| `logs/edge_research/v28_successor_sidecar_bundle_batch_settlement_labels_latest.json` | True | 20411 | `522f646ed2c5ba6307c1c4814d4de8a3b5650c0baec26a7d9d0e5153c1f4e976` |
| `logs/edge_research/v28_successor_sidecar_bundle_batch_label_join_latest.json` | True | 55192 | `6f38ae3cb5e45abd471c796d1404b095f558430e9564c8d7ae6002345dd3e8d9` |
| `logs/edge_research/v28_successor_sidecar_batch_evidence_score_latest.json` | True | 114927 | `a613f8525a014e6035295b82772d767e2985aded0b68b1235e494539ddf0ba34` |
| `logs/edge_research/v28_successor_sidecar_collection_cycle_latest.json` | True | 33628 | `b1f8da3b70b790e923f4a76c29f13bc049ff616c474bfe39704dce6327fa2653` |
| `logs/edge_research/v28_successor_market_coverage_loop_latest.json` | True | 4679 | `5b695f04c716ce182ca0d60104180c03f6e3c9b6cdb58048d2d7ba7bc2562f73` |
| `logs/edge_research/v28_successor_forward_packet_freeze_handoff_latest.json` | True | 9166 | `9fcb0ff8a1bbf8cb0688b055177a62a2e0e332a830d8882ed57e65fe6cfc2652` |
| `logs/edge_research/v28_successor_forward_collection_spec_latest.json` | True | 115232 | `3657fca6eb9f1b6df967281703e7a034fe3c197919dbff3f7e40f794b9100ad2` |
| `logs/edge_research/v28_successor_frozen_forward_predictions_latest.json` | True | 1517 | `ffeef6eac9f646666bd85e2cdb66837b0c4ceb371a50d482be28b1f8bac38108` |
| `research_particle/v28_successor/candidate_manifests_logged_events_latest.json` | True | 55880 | `f779b3b24d0efd48cf259dc116b9d838fe063bb752a02a6f2b094ef7b99e1b1b` |
| `research_particle/v28_successor/public_rest_sidecar_bundle_demo_latest.json` | True | 131951 | `404cc736feabdab8d3bfff911c13dcda2503c79982c71c1016404bb7a771c871` |
| `research_particle/v28_successor/public_rest_sidecar_batch_demo_latest.json` | True | 296874 | `f70272cfad0f52feb0b3e91cc047c11d697af138ed225b140cb8ff8a6535523f` |
| `research_particle/v28_successor/sidecar_bundle_batch_settlement_labels_latest.csv` | True | 12124 | `fdfc425af182708140df50187af5462ae78d94cf4d87e0e82674604884b6b62f` |
| `research_particle/v28_successor/forward_labeled_predictions_latest.csv` | True | 2566471 | `969989c3e55436cd7160b616f8222beb9d039d69fc3e75dc8c91868704895d0d` |
| `research_particle/v28_successor/sidecar_bundle_batch_labeled_latest.csv` | True | 2566471 | `969989c3e55436cd7160b616f8222beb9d039d69fc3e75dc8c91868704895d0d` |
| `logs/edge_research/v28_successor_sidecar_batch_evidence_metrics_latest.csv` | True | 19494 | `c22600811db735b767a67fd102aee7a42310e4aa26be6d8923fbf2e684897c95` |
| `research_particle/v28_successor/frozen_forward_predictions_latest.csv` | True | 1781209 | `4ced86e35c80e6616e5420119efb653b5728763b46d16bfed714806eeb4e076c` |
| `research_particle/v28_successor/forward_registry_latest.csv` | True | 1503654 | `bdbca9e524756c95b613c032c4978750f6ddd9809099608e7cc8a0ea58b39d60` |
