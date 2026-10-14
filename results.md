# Results

| Task | Plain answer correct | Confidence | Harness action | Trap named |
|---|---|---|---|---|
| Ambiguous dates | False | 1.00 | flag | True |
| Missing values | True | 0.50 | defer | True |
| Unknown exchange rate | False | 0.95 | flag | True |
| Unclear time frame | False | 1.00 | flag | True |
| Unit mismatch | True | 1.00 | flag | True |

Model: gemini-3.5-flash-lite
Tasks scored: 5
Silent mistakes in plain runs: 3
Surfaced by the harness (not 'continue'): 3
