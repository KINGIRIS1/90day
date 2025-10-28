STRICT 75 PERCENT RULE (updated from 80%)

Summary
- Tier 1 fuzzy title threshold is now 75% (was 80%).
- Rationale: tolerate common OCR typos (diacritics loss, swapped characters) while keeping safeguards.

Safeguards retained
- Uppercase gate: titles with uppercase ratio <70% are ignored for fuzzy matching.
- Exact/regex matches still take priority over fuzzy.
- Keyword confirmation remains in Tier 2 when similarity is 50–75%.
- Administrative headers are filtered out before scoring.

What this improves
- Documents like “GIẤY TIẾP NHẬN HỒ SƠ VÀ HẸN TRẢ KẾT QUẢ” often suffer small OCR mistakes (HỒ→HỎ, KẾT→KÉT). 75% captures these true positives without raising false positives.

Action note
- Keep adding title templates for frequent forms to further strengthen Tier 1.
