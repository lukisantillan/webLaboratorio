---
titulo: The Real Costs of Serving an LLM in Production (2026 Edition)
fecha: 2026-05-27
autores: David Petrocelli
categoria: tecnicos
tema: ia
idioma: en
resumen: What you actually pay per million tokens — broken down by API providers, self-hosted, and the hidden costs nobody mentions
etiqueta: Generative AI
slug: real-costs-of-serving-an-llm-in-production
---

<p>LLM pricing pages list "$X per million tokens" and let you draw your own conclusions. In production, that number is a fraction of what you actually spend. Here's the breakdown nobody publishes.</p>
<h2>The headline numbers (December 2025)</h2>
<p>Per million tokens, input/output, frontier models:</p>
<table>
<thead>
<tr>
<th>Model</th>
<th>Input</th>
<th>Output</th>
</tr>
</thead>
<tbody>
<tr>
<td>GPT-4.1</td>
<td>$2.50</td>
<td>$10.00</td>
</tr>
<tr>
<td>GPT-4.1-mini</td>
<td>$0.15</td>
<td>$0.60</td>
</tr>
<tr>
<td>Claude Opus 4.7</td>
<td>$15.00</td>
<td>$75.00</td>
</tr>
<tr>
<td>Claude Sonnet 4.6</td>
<td>$3.00</td>
<td>$15.00</td>
</tr>
<tr>
<td>Claude Haiku 4.5</td>
<td>$0.80</td>
<td>$4.00</td>
</tr>
<tr>
<td>Gemini 2.5 Pro</td>
<td>$1.25</td>
<td>$5.00</td>
</tr>
<tr>
<td>Llama 3.3 70B (self-hosted on AWS g5.12xlarge)</td>
<td>~$0.30</td>
<td>~$0.30</td>
</tr>
</tbody>
</table>
<p>These are sticker prices. Your actual cost per query depends on factors that matter much more.</p>
<h2>The 4 multipliers that actually determine cost</h2>
<h3>1. Output:input ratio</h3>
<p>A query with 200 input tokens and 1.500 output tokens on Claude Sonnet costs $0.023 — and 95% of that is output. Engineers optimize prompts (input) when they should be optimizing response length (output).</p>
<p><strong>Lesson</strong>: cap <code>max_tokens</code>. Use structured outputs that force concision. Bullet points instead of paragraphs in agent responses.</p>
<h3>2. Retry rate</h3>
<p>If your structured outputs fail JSON parsing 8% of the time and you retry, that's effectively a 1.08x multiplier on your bill. Some systems I've audited had 30%+ retry rates because of brittle prompts.</p>
<p><strong>Lesson</strong>: invest in robust output parsing with auto-repair logic before throwing more compute at it.</p>
<h3>3. Context bloat</h3>
<p>Every long-running conversation adds history to the prompt. A chat that's been going for 40 turns might be sending 15.000 tokens of context with every new message — and you pay for all of it, every time.</p>
<p><strong>Lesson</strong>: summarize old context aggressively. Use semantic memory (not raw history). Truncate or compress conversations &gt;20 turns.</p>
<h3>4. Embedding storage and re-embedding</h3>
<p>A 10-million-chunk vector DB on Pinecone Standard is ~$280/month. On pgvector + RDS, ~$120/month. Self-hosted on a single beefy box, ~$30/month plus your time.</p>
<p>Add the cost of re-embedding when you change the embedding model (it happens twice a year on average), and the operational cost of the vector DB often <strong>exceeds the inference cost</strong> for read-heavy RAG systems.</p>
<h2>Worked example: a customer support agent</h2>
<p>Let's price a real workload.</p>
<p><strong>Assumptions:</strong>
- 100.000 conversations per month
- Average conversation: 4 turns
- Each turn: 800 input tokens (system prompt + history + retrieved chunks) + 250 output tokens
- 70% handled by Claude Haiku, 30% escalated to Sonnet
- RAG over 50.000 chunks, embedded with text-embedding-3-small</p>
<p><strong>Inference cost:</strong></p>
<table>
<thead>
<tr>
<th>Component</th>
<th>Calculation</th>
<th>Monthly</th>
</tr>
</thead>
<tbody>
<tr>
<td>Haiku tokens: 70k convs × 4 turns × (800 in + 250 out)</td>
<td>280M in, 70M out @ Haiku rates</td>
<td>$504</td>
</tr>
<tr>
<td>Sonnet tokens: 30k convs × 4 turns × (800 in + 250 out)</td>
<td>96M in, 30M out @ Sonnet rates</td>
<td>$738</td>
</tr>
<tr>
<td><strong>Inference total</strong></td>
<td></td>
<td><strong>$1.242</strong></td>
</tr>
</tbody>
</table>
<p><strong>Infrastructure cost:</strong></p>
<table>
<thead>
<tr>
<th>Component</th>
<th>Monthly</th>
</tr>
</thead>
<tbody>
<tr>
<td>Pinecone Standard (5M vectors)</td>
<td>$140</td>
</tr>
<tr>
<td>Embedding generation (50k chunks × $0.02/M tokens, avg 400 tokens each)</td>
<td>$0.40</td>
</tr>
<tr>
<td>Re-embedding on query (400k embed calls × ~30 tokens)</td>
<td>$0.24</td>
</tr>
<tr>
<td>Backend infra (1 small ECS service + RDS Postgres)</td>
<td>$180</td>
</tr>
<tr>
<td>Logging &amp; monitoring (Langfuse self-hosted)</td>
<td>$40</td>
</tr>
<tr>
<td><strong>Infra total</strong></td>
<td></td>
</tr>
</tbody>
</table>
<p><strong>Hidden costs:</strong></p>
<table>
<thead>
<tr>
<th>Component</th>
<th>Monthly</th>
</tr>
</thead>
<tbody>
<tr>
<td>Engineer time on retry/error handling (~3hrs/week × $100/hr)</td>
<td>$1.200</td>
</tr>
<tr>
<td>Evaluation runs (weekly regression test on 500 queries)</td>
<td>$80</td>
</tr>
<tr>
<td>Failed experiments / A/B tests</td>
<td>$200</td>
</tr>
<tr>
<td><strong>Hidden total</strong></td>
<td></td>
</tr>
</tbody>
</table>
<p><strong>Grand total: $3.082/month</strong> for 100k conversations = <strong>$0.031 per conversation</strong>.</p>
<p>The inference is 40% of the bill. Infra is 12%. Engineering time and operations are 48% — which is the part vendor pricing pages never mention.</p>
<h2>Where teams overspend</h2>
<p>Patterns I see consistently:</p>
<ol>
<li><strong>Using Opus/GPT-4.1 for everything.</strong> Most queries don't need it. Routing 80% to a cheaper model usually cuts costs 5-10x.</li>
<li><strong>Not caching.</strong> Identical queries hit the LLM. Even a 15% cache hit rate is a 15% bill reduction.</li>
<li><strong>Streaming as a default.</strong> Streaming has UX value but adds overhead. For batch jobs, disable it.</li>
<li><strong>Forgetting about embedding re-runs.</strong> If you change models or chunking strategy, you pay to re-embed everything.</li>
<li><strong>Storing context in the prompt instead of the retrieval layer.</strong> Long prompts feel productive but compound costs across every turn.</li>
</ol>
<h2>Where to self-host</h2>
<p>Self-hosting an open model (Llama 3.3 70B on AWS g5.12xlarge) hits cost parity with frontier APIs at roughly <strong>5M output tokens per day, sustained</strong>. Below that, you're paying for idle GPU. Above that, self-hosting can be 60-80% cheaper.</p>
<p>What people forget:
- Self-hosting needs ML/SRE skills. Budget 0.5 FTE just for the inference stack.
- vLLM, TGI, and llama.cpp have very different throughput profiles. Benchmark for your actual workload.
- Open models lag frontier by 6-12 months on the hardest reasoning tasks. Match the model to the job.</p>
<h2>The cheap-but-correct stack for 2026</h2>
<p>If you're building a new LLM product today and want to keep costs sane:</p>
<ul>
<li><strong>Default model</strong>: Claude Haiku 4.5 or GPT-4.1-mini (cheap, fast, good enough for 80% of queries)</li>
<li><strong>Escalation model</strong>: Claude Sonnet 4.6 (smart, reasonable cost)</li>
<li><strong>Embeddings</strong>: OpenAI text-embedding-3-small or Cohere embed-multilingual-v3</li>
<li><strong>Vector DB</strong>: pgvector if you have &lt;2M chunks, Qdrant or Weaviate for larger</li>
<li><strong>Observability</strong>: Langfuse (open source, self-hostable)</li>
<li><strong>Orchestration</strong>: simple Python or LangGraph (avoid frameworks that hide the cost of every call)</li>
</ul>
<p>This stack runs production workloads at $0.005-0.05 per query for most use cases.</p>
<h2>The number that actually matters</h2>
<p>Forget cost per million tokens. The number to optimize is <strong>cost per successful task completion</strong>. A $0.10 query that solves a problem is cheaper than a $0.005 query that requires three retries and a human escalation.</p>
<p>That's the metric we teach our students to track. It's the only one that maps directly to whether your LLM product is profitable.</p>

          <div class="post-cta">
            <h3>Want to go deeper?</h3>
            <p>This article is a small slice of what we teach in the Generative AI Development Diploma at UNLu. The full program covers RAG architectures, fine-tuning, evaluation frameworks, MLOps for LLMs, and production deployment.</p>
            <a href="/dev-ia/">Explore the IA Diploma</a>
          </div>
