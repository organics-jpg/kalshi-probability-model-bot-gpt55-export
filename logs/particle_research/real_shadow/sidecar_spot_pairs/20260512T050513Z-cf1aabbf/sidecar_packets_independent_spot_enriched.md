# Paired Sidecar Spot Packet Enrichment

Research-only enrichment of sidecar packet rows with independent public BTC spot ticks available at or before each packet decision timestamp.

## Summary

- Generated UTC: `2026-05-12T05:06:03.733778+00:00`
- Run id: `20260512T050513Z-cf1aabbf`
- Promotion allowed: `False`
- Enrichment ready: `False`
- Packet rows read: `2342`
- Matching packet rows: `0`
- Enriched packet rows: `0`
- Issue count: `0`
- Spot ticks: `79`

## Rows

| market | side | candidate | decision ts | independent spot | age ms | delta vs candle bps | ready | issue |
|---|---|---|---|---:|---:|---:|---|---|
|  |  |  |  |  |  |  | `False` | `no matching packet rows` |

## Read

- This artifact does not modify frozen sidecar rows or any live bot state.
- It is input-quality evidence only; probability, EV ranking, PnL, and promotion gates remain separate.
