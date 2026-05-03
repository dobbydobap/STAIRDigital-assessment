# Evaluation report

- Ran at: `2026-05-03T16:22:48.802512+00:00`
- Sample PDF: `sample.pdf` (`pdf_id=55d80d424ded18a2`, 44 pages)
- **Result: 0/9 passed**

## FAIL — V1 (direct_fact)
- **Query:** What is the title or main heading of this document?
- **Expected:** `answered_with_citations`
- **Observed:** `error: RateLimitError: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kqpz8jkmfa8sxntee9vtdd97` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 98511, Requested 4140. Please try again in 38m10.464s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}`
- **Notes:** Exception during chat turn.

## FAIL — V2 (authorship)
- **Query:** Who authored, prepared, or published this document?
- **Expected:** `answered_with_citations`
- **Observed:** `error: RateLimitError: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kqpz8jkmfa8sxntee9vtdd97` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 98504, Requested 4170. Please try again in 38m30.336s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}`
- **Notes:** Exception during chat turn.

## FAIL — V3 (multi_page_synthesis)
- **Query:** What are the main sections, chapters, or topics covered in this document?
- **Expected:** `answered_with_citations`
- **Observed:** `error: RateLimitError: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kqpz8jkmfa8sxntee9vtdd97` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 98498, Requested 3280. Please try again in 25m36.192s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}`
- **Notes:** Exception during chat turn.

## FAIL — V4 (definition)
- **Query:** Briefly summarize what this document is about.
- **Expected:** `answered_with_citations`
- **Observed:** `error: RateLimitError: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kqpz8jkmfa8sxntee9vtdd97` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 98493, Requested 3589. Please try again in 29m58.848s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}`
- **Notes:** Exception during chat turn.

## FAIL — V5 (quantitative)
- **Query:** What date, year, or version number does the document state for itself?
- **Expected:** `answered_with_citations`
- **Observed:** `error: RateLimitError: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kqpz8jkmfa8sxntee9vtdd97` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 98487, Requested 4189. Please try again in 38m32.064s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}`
- **Notes:** Exception during chat turn.

## FAIL — O1 (general_knowledge)
- **Query:** What is the capital of France?
- **Expected:** `refused_out_of_scope`
- **Observed:** `error: RateLimitError: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kqpz8jkmfa8sxntee9vtdd97` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 98481, Requested 4263. Please try again in 39m30.816s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}`
- **Notes:** Exception during chat turn.

## FAIL — O2 (opinion_prediction)
- **Query:** Will the ideas or policies described in this document succeed over the next 10 years?
- **Expected:** `refused_out_of_scope_or_insufficient`
- **Observed:** `error: RateLimitError: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kqpz8jkmfa8sxntee9vtdd97` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 98475, Requested 4011. Please try again in 35m47.904s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}`
- **Notes:** Exception during chat turn.

## FAIL — O3 (adjacent_absent)
- **Query:** What is the personal birth date of the document's primary author?
- **Expected:** `refused_out_of_scope_or_insufficient`
- **Observed:** `error: RateLimitError: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kqpz8jkmfa8sxntee9vtdd97` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 98469, Requested 3904. Please try again in 34m10.272s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}`
- **Notes:** Exception during chat turn.

## FAIL — B1 (hindi_query_english_pdf)
- **Query:** इस दस्तावेज़ का मुख्य विषय क्या है?
- **Expected:** `answered_with_citations_in_query_language`
- **Observed:** `error: RateLimitError: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kqpz8jkmfa8sxntee9vtdd97` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 98464, Requested 3738. Please try again in 31m42.528s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}`
- **Notes:** Exception during chat turn.
