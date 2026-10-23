---
titulo: RAG vs Fine-Tuning: When to Use Each (and When Not To)
fecha: 2026-05-27
autores: David Petrocelli
categoria: tecnicos
tema: ia
idioma: en
resumen: A decision framework based on what you actually want the model to do, not what's trending
etiqueta: Generative AI
slug: rag-vs-fine-tuning-when-to-use-each
codigo: si
---

<p>If you're building anything with LLMs in production, this question shows up in week one and never really goes away. The internet has a lot of bad takes on it. Here's what actually matters.</p>
<h2>The 30-second answer</h2>
<ul>
<li><strong>RAG</strong> = "give the model fresh information at inference time"</li>
<li><strong>Fine-tuning</strong> = "change how the model behaves or speaks"</li>
</ul>
<p>They solve different problems. Most teams need RAG. A few teams need fine-tuning. A small minority need both.</p>
<h2>When you need RAG</h2>
<p>Use RAG when the bottleneck is <strong>knowledge the model doesn't have</strong>.</p>
<p>Examples:
- A customer support bot that needs to know your product docs (which update weekly)
- A legal assistant searching internal contracts
- A coding agent that needs to read the current state of a repo
- Any chatbot that should never confidently make up facts</p>
<p>The pattern is always the same:</p>
<pre><code>user query
    ↓
embed query
    ↓
search vector DB (top 5-20 chunks)
    ↓
inject chunks into prompt
    ↓
LLM generates answer grounded in chunks
</code></pre>
<p>The model itself doesn't change. You're just feeding it the right context at the right time.</p>
<p><strong>Cost reality</strong>: a well-tuned RAG pipeline with <code>gpt-4.1-mini</code> or <code>claude-haiku-4-5</code> runs ~$0.001-0.005 per query at scale. The infrastructure (vector DB, embeddings, orchestration) is the real engineering work.</p>
<h2>When you need fine-tuning</h2>
<p>Use fine-tuning when the bottleneck is <strong>how the model behaves</strong>.</p>
<p>Examples:
- You need it to always answer in a specific JSON schema (and prompt engineering keeps failing on edge cases)
- You need it to mimic a specific writing style across thousands of generations
- You need it to handle a specialized vocabulary (medical, legal, internal jargon) without constantly explaining terms
- You need a smaller, cheaper model to behave like a bigger one for a narrow task (distillation)</p>
<p>The pattern:</p>
<pre><code>collect 500-5.000 high-quality examples of (input, ideal output)
    ↓
fine-tune base model on those examples
    ↓
deploy the new model
    ↓
serve it like any other model
</code></pre>
<p><strong>Cost reality</strong>: fine-tuning an open model (Llama 3.3, Mistral) costs $50-500 in compute. Hosting it costs ~$0.50-3/hour depending on size and provider. Fine-tuning a frontier closed model (OpenAI, Anthropic) is more expensive but the operational simplicity is worth it for small teams.</p>
<h2>When you absolutely don't need either</h2>
<p>Be honest: a lot of "AI projects" are just <strong>prompt engineering problems wearing a costume</strong>.</p>
<p>Before reaching for RAG or fine-tuning, try:</p>
<ol>
<li>A better system prompt with explicit examples</li>
<li>Tool use (function calling) instead of forcing the model to know everything</li>
<li>A smaller model with a cleaner prompt instead of a bigger one with a sloppy one</li>
</ol>
<p>If GPT-4.1 with a 200-word system prompt does the job, that <em>is</em> the production answer. Adding RAG or fine-tuning to feel sophisticated is technical debt with extra steps.</p>
<h2>The decision matrix</h2>
<table>
<thead>
<tr>
<th>Symptom</th>
<th>First try</th>
<th>If that fails</th>
</tr>
</thead>
<tbody>
<tr>
<td>"It hallucinates facts about our domain"</td>
<td>RAG</td>
<td>Fine-tune for grounding</td>
</tr>
<tr>
<td>"It doesn't follow our output format"</td>
<td>Better prompt + examples</td>
<td>Fine-tune for format</td>
</tr>
<tr>
<td>"It's too expensive at scale"</td>
<td>Smaller model + RAG</td>
<td>Distill via fine-tuning</td>
</tr>
<tr>
<td>"It doesn't know about events after its cutoff"</td>
<td>RAG with web search</td>
<td>(Don't fine-tune for facts. Ever.)</td>
</tr>
<tr>
<td>"It writes in the wrong tone"</td>
<td>System prompt with style guide</td>
<td>Fine-tune on tone examples</td>
</tr>
<tr>
<td>"It can't reason about long documents"</td>
<td>RAG with hierarchical chunking</td>
<td>Long-context model</td>
</tr>
</tbody>
</table>
<h2>The combined pattern (real production systems)</h2>
<p>The mature setup in most production LLM stacks looks like:</p>
<ol>
<li><strong>Fine-tuned smaller model</strong> as the "router" (cheap, fast, specialized)</li>
<li><strong>RAG pipeline</strong> for any domain-specific knowledge</li>
<li><strong>Frontier model</strong> for the hard cases the router escalates</li>
</ol>
<p>Example: a customer support agent might use a fine-tuned Llama 3.3 8B for 80% of queries (template responses, simple lookups), with a Claude or GPT-4.1 fallback for the 20% that need real reasoning. RAG over the docs feeds both.</p>
<p>This is overkill for an MVP. It's the right architecture once you're handling 100k+ queries/month and need to control costs.</p>
<h2>What I tell teams starting out</h2>
<p>Build the dumbest thing that works first. Track where it fails. Let the failures tell you whether you need RAG (model doesn't know things) or fine-tuning (model doesn't behave correctly) or just a better prompt.</p>
<p>Most teams reach for fine-tuning when RAG would have solved it. RAG is reversible, debuggable, and your data stays in your control. Fine-tuning bakes assumptions into a model — it's harder to roll back.</p>
<h2>One more thing: evaluation matters more than the technique</h2>
<p>Whatever you choose, you need a <strong>regression test suite of 50-200 representative queries</strong> with expected behaviors. Without that, you can't tell if a change made things better or worse. This single discipline separates production-grade LLM systems from demos that work on Tuesday and break on Wednesday.</p>
<p>We dedicate an entire module of the curriculum to evaluation methodology because it's the unsexy skill that determines whether anything else you build is actually working.</p>

          <div class="post-cta">
            <h3>Want to go deeper?</h3>
            <p>This article is a small slice of what we teach in the Generative AI Development Diploma at UNLu. The full program covers RAG architectures, fine-tuning, evaluation frameworks, MLOps for LLMs, and production deployment.</p>
            <a href="/dev-ia/">Explore the IA Diploma</a>
          </div>
