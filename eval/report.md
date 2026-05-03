# Evaluation report

- Ran at: `2026-05-03T16:17:14.000318+00:00`
- Sample PDF: `sample.pdf` (`pdf_id=55d80d424ded18a2`, 44 pages)
- **Result: 8/9 passed**

## FAIL — V1 (direct_fact)
- **Query:** What is the title or main heading of this document?
- **Expected:** `answered_with_citations`
- **Observed:** `in_scope/insufficient/cit=False/verified=True`
- **Notes:** Single-page lookup on the front matter.
- **Refusal reason:** The document discusses AI in general, but does not provide the title of this specific document. It does mention the World Travel & Tourism Council and their report on AI, but the title of the report is not specified.
- **Verification:** ok=True; all checks passed
- **Latency:** rewrite 778ms · retrieve 25445ms · answer 453ms · total 26676ms
- **Tokens/cost:** in=2929 out=146 ~$0.0000

## PASS — V2 (authorship)
- **Query:** Who authored, prepared, or published this document?
- **Expected:** `answered_with_citations`
- **Observed:** `in_scope/sufficient/cit=True/verified=True`
- **Notes:** Front-matter / colophon lookup.
- **Answer:**
  > The World Travel & Tourism Council authored, prepared, or published this document. [p.28]
- **Citations:**
  - p.28 §_Ref147778178: "This report provides an in-depth analysis of the economic impact of the travel and tourism industry, both globally and in individual countries. It also provides forecasts for the future of the industry."
- **Verification:** ok=True; all checks passed
- **Latency:** rewrite 200ms · retrieve 717ms · answer 631ms · total 1548ms
- **Tokens/cost:** in=2958 out=190 ~$0.0000

## PASS — V3 (multi_page_synthesis)
- **Query:** What are the main sections, chapters, or topics covered in this document?
- **Expected:** `answered_with_citations`
- **Observed:** `in_scope/partial/cit=True/verified=True`
- **Notes:** Tests retrieval across multiple pages and section-aware chunking.
- **Answer:**
  > The main sections covered in this document are Introduction, including Computing Power, Generative AI, and Types of Artificial Intelligence.
- **Citations:**
  - p.20 §INTRODUCTION > Computing Power : The Machines Behind AI: "the three core elements of AI, is more often referred to as Algorithms + Data + Compute"
  - p.21 §INTRODUCTION > Types of Artificial Intelligence: "The previous section of this report summarised the different ways that AI systems can be categorised"
- **Verification:** ok=True; all checks passed
- **Latency:** rewrite 1412ms · retrieve 788ms · answer 18662ms · total 20862ms
- **Tokens/cost:** in=2073 out=285 ~$0.0000

## PASS — V4 (definition)
- **Query:** Briefly summarize what this document is about.
- **Expected:** `answered_with_citations`
- **Observed:** `in_scope/partial/cit=True/verified=True`
- **Notes:** Definition / scope question; should pull from intro/abstract.
- **Answer:**
  > The document discusses generative AI, its origins, and its applications. It also touches on the history of AI, its components, and the future of AI. However, it does not provide a comprehensive summary of the document.
- **Refusal reason:** The document covers topics such as generative AI, AI history, AI components, and the future of AI, but a comprehensive summary is not provided.
- **Citations:**
  - p.24 §INTRODUCTION > Generative AI: "Generative AI has its origins in a 2017 Google research paper entitled “Attention Is All You Need” 22, which introduced a new type of AI architecture for language understanding called ‘Transformers’."
  - p.2 §(unsectioned): "Brief history of Artificial Intelligence (AI)"
  - p.20 §INTRODUCTION > Computing Power : The Machines Behind AI: "As these three core components of AI get increasingly more capable, accessible and affordable to businesses and the public, what AI can really achieve in the future is yet to be determined!"
  - p.26 §_Ref147778178: "To achieve such impressive abilities, LLM models are typically trained on enormous amounts of text data (sometimes called a ‘corpus’, meaning a large collection of documents) to learn the patterns, grammar, and semantics of one, or more, languages and use AI deep learning techniques to understand and generate coherent, conversational and contextually appropriate responses in only a few seconds."
- **Verification:** ok=True; all checks passed
- **Latency:** rewrite 4244ms · retrieve 306ms · answer 21038ms · total 25588ms
- **Tokens/cost:** in=2376 out=437 ~$0.0000

## PASS — V5 (quantitative)
- **Query:** What date, year, or version number does the document state for itself?
- **Expected:** `answered_with_citations`
- **Observed:** `in_scope/partial/cit=True/verified=True`
- **Notes:** Quantitative fact requiring careful reading.
- **Answer:**
  > The document mentions the following dates and years: 2017, 2020, 2022, 2023, and 2023 (again). It also mentions the following version numbers: 22, 27, and 1030.
- **Citations:**
  - p.24 §INTRODUCTION > Generative AI: "Generative AI has its origins in a 2017 Google research paper entitled “Attention Is All You Need” 22,"
  - p.13 §INTRODUCTION > Data : The Fuel That Drives AI: "in 2022 scientists formally agreed two new units of measurement for the first time in 31 years."
  - p.13 §INTRODUCTION > Data : The Fuel That Drives AI: "in 2020, during the height of the COVID-19 pandemic, the Head of WhatsApp (Will Catchcart) issued a tweet stating that approximately 100 billion messages were being exchanged every day on WhatsApp alone"
  - p.31 §_Ref147778178 > Global Digital Divide & AI Skills Gap: "The International Telecommunications Union (ITU) – the UN agency responsible for advancing digital technology – estimates that 34% of the world has never been connected to the internet (in 2022),"
  - p.31 §_Ref147778178 > Global Digital Divide & AI Skills Gap: "The ITU considers that ‘universal and meaningful digital connectivity’ 26 (defined as a ‘the possibility for everyone to enjoy a safe, productive and affordable online experience’) should be a global priority."
  - p.31 §_Ref147778178 > Global Digital Divide & AI Skills Gap: "The UK and Canada announced an ‘AI for Development’ vision at the 2023 UN General Assembly (UNGA) 27,"
  - p.29 §_Ref147778178: "Hallucinations are a well known feature of current generative AI systems and many researchers are working on solutions, so that future versions of AI systems will have improved accuracy and better performance."
  - p.25 §_Ref147778178: "Number of Scientific Publications on Generative AI (by year)"
  - p.25 §_Ref147778178: "international news stories on generative AI increasing from just under 2000 in late 2022, to nearly 14,000 by June 2023."
  - p.25 §_Ref147778178: "The number of posts on X (tweets) rose from 7000 in October 2022, to 57,000 in March 2023 (an 8x increase) 23."
  - p.25 §_Ref147778178: "A specific type of generative AI foundation model is a large language model (LLM), which is a sophisticated AI model designed to generate human like text responses to a user’s prompt."
  - p.25 §_Ref147778178: "The user ‘prompt’ is commonly a text input, but could also be something else, such as an image or audio input for example."
  - p.25 §_Ref147778178: "A prompt allows the user to provide instructions to an LLM (often an AI chatbot) in a natural conversational style,"
  - p.25 §_Ref147778178: "which is understood by the AI in a process called natural language processing (NLP)."
  - p.25 §_Ref147778178: "This natural, conversational way of providing instructions to an AI system is the same way that instructions are provided to ‘home smart speakers’ and is a new, exciting and innovative way for humans to interact with computers."
- **Verification:** ok=True; all checks passed
- **Latency:** rewrite 4400ms · retrieve 662ms · answer 32000ms · total 37061ms
- **Tokens/cost:** in=2982 out=1279 ~$0.0000

## PASS — O1 (general_knowledge)
- **Query:** What is the capital of France?
- **Expected:** `refused_out_of_scope`
- **Observed:** `out_of_scope/insufficient`
- **Notes:** Pure general knowledge, completely unrelated.
- **Refusal reason:** The PDF does not cover general knowledge questions like the capital of France. It covers topics like AI, data, and computing power.
- **Verification:** ok=True; all checks passed
- **Latency:** rewrite 7592ms · retrieve 327ms · answer 27662ms · total 35581ms
- **Tokens/cost:** in=3048 out=118 ~$0.0000

## PASS — O2 (opinion_prediction)
- **Query:** Will the ideas or policies described in this document succeed over the next 10 years?
- **Expected:** `refused_out_of_scope_or_insufficient`
- **Observed:** `out_of_scope/insufficient`
- **Notes:** Future prediction / opinion — should refuse rather than speculate.
- **Refusal reason:** The PDF discusses AI in the context of travel and tourism, but does not provide information on the success of AI ideas or policies over the next decade. It covers topics such as AI applications, generative AI, and AI terminology, but does not address the question of success.
- **Verification:** ok=True; all checks passed
- **Latency:** rewrite 3543ms · retrieve 557ms · answer 25739ms · total 29839ms
- **Tokens/cost:** in=2806 out=167 ~$0.0000

## PASS — O3 (adjacent_absent)
- **Query:** What is the personal birth date of the document's primary author?
- **Expected:** `refused_out_of_scope_or_insufficient`
- **Observed:** `out_of_scope/insufficient`
- **Notes:** Plausible-sounding adjacent fact almost never present in such documents.
- **Refusal reason:** The PDF covers topics like generative AI, AI applications, data, computing power, and AI types, but it does not provide personal information about the primary author, such as their birth date.
- **Verification:** ok=True; all checks passed
- **Latency:** rewrite 3284ms · retrieve 753ms · answer 24631ms · total 28668ms
- **Tokens/cost:** in=2695 out=158 ~$0.0000

## PASS — B1 (hindi_query_english_pdf)
- **Query:** इस दस्तावेज़ का मुख्य विषय क्या है?
- **Expected:** `answered_with_citations_in_query_language`
- **Observed:** `in_scope/insufficient/cit=True/lang=hi/qlang=hi`
- **Notes:** answer fell back to refusal — acceptable for bonus, but answer-with-citations is the goal.
- **Refusal reason:** I could not produce an answer whose quotes I could verify against the document. Verifier said: p.24: quote not found verbatim — 'Generative AI का विवरण है।'. Try asking more specifically (e.g. naming a section, table, or page).
- **Citations:**
  - p.24 §INTRODUCTION > Generative AI: "Generative AI का विवरण है।"
- **Verification:** ok=False; p.24: quote not found verbatim — 'Generative AI का विवरण है।'
- **Latency:** rewrite 3489ms · retrieve 468ms · answer 47656ms · total 51613ms
- **Tokens/cost:** in=4885 out=354 ~$0.0000
