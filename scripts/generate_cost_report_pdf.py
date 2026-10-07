import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @page {
    size: A4 portrait;
    margin: 18mm 16mm 18mm 16mm;
    @bottom-right {
      content: "Page " counter(page) " of " counter(pages);
      font-family: 'Helvetica Neue', Arial, sans-serif;
      font-size: 8pt;
      color: #718096;
    }
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #1a202c;
    background: #ffffff;
    font-size: 9.5pt;
    line-height: 1.45;
  }

  .header {
    border-bottom: 2px solid #4f46e5;
    padding-bottom: 12px;
    margin-bottom: 18px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }
  .title-area h1 {
    font-size: 18pt;
    font-weight: 800;
    color: #1e1b4b;
    letter-spacing: -0.02em;
    margin-bottom: 3px;
  }
  .title-area p {
    font-size: 9pt;
    color: #4b5563;
    font-weight: 500;
  }
  .meta-badge {
    text-align: right;
    font-size: 8pt;
    color: #6b7280;
    line-height: 1.35;
  }
  .meta-badge strong {
    color: #4f46e5;
    font-size: 8.5pt;
  }

  h2 {
    font-size: 12pt;
    font-weight: 700;
    color: #1e1b4b;
    margin-top: 16px;
    margin-bottom: 8px;
    padding-bottom: 4px;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  h3 {
    font-size: 10pt;
    font-weight: 700;
    color: #374151;
    margin-top: 10px;
    margin-bottom: 5px;
  }

  p { margin-bottom: 8px; color: #374151; }

  /* Callout box */
  .callout {
    background: #f8fafc;
    border-left: 3.5px solid #4f46e5;
    border-radius: 4px;
    padding: 8px 12px;
    margin: 10px 0;
    font-size: 8.5pt;
    color: #334155;
  }
  .callout-title {
    font-weight: 700;
    color: #1e1b4b;
    margin-bottom: 2px;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0 14px;
    font-size: 8.5pt;
  }
  th {
    background: #f1f5f9;
    color: #1e293b;
    font-weight: 700;
    text-align: left;
    padding: 6px 8px;
    border: 1px solid #cbd5e1;
    font-size: 8pt;
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }
  td {
    padding: 5px 8px;
    border: 1px solid #e2e8f0;
    color: #334155;
    vertical-align: middle;
  }
  tr:nth-child(even) td {
    background: #f8fafc;
  }
  .highlight-row td {
    background: #eef2ff !important;
    font-weight: 600;
    color: #312e81;
  }

  .text-right { text-align: right; }
  .text-center { text-align: center; }
  .bold { font-weight: 700; }
  .badge-free {
    display: inline-block;
    background: #dcfce7;
    color: #15803d;
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 7.5pt;
    font-weight: 700;
  }
  .badge-speed {
    display: inline-block;
    background: #e0e7ff;
    color: #3730a3;
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 7.5pt;
    font-weight: 600;
  }

  /* Grid boxes */
  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin: 10px 0;
  }
  .box {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 10px 12px;
  }
  .box h4 {
    font-size: 9.5pt;
    font-weight: 700;
    color: #1e1b4b;
    margin-bottom: 4px;
  }
  .box p {
    font-size: 8.5pt;
    margin-bottom: 0;
    color: #4b5563;
  }

  .page-break {
    page-break-before: always;
  }

  .summary-card {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
    color: #ffffff;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 12px 0 16px;
  }
  .summary-card h3 {
    color: #ffffff;
    font-size: 11pt;
    margin-top: 0;
    margin-bottom: 4px;
  }
  .summary-card p {
    color: #e0e7ff;
    font-size: 8.5pt;
    margin-bottom: 0;
  }
  .stat-row {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
    padding-top: 8px;
    border-top: 1px solid rgba(255,255,255,0.15);
  }
  .stat-item {
    text-align: center;
  }
  .stat-val {
    font-size: 13pt;
    font-weight: 800;
    color: #38bdf8;
  }
  .stat-lbl {
    font-size: 7.5pt;
    color: #cbd5e1;
    text-transform: uppercase;
  }
</style>
</head>
<body>

<!-- Header -->
<div class="header">
  <div class="title-area">
    <h1>Agentic Lead Intelligence</h1>
    <p>Comprehensive Token Economics, Cost Estimation & Multi-Provider Benchmark</p>
  </div>
  <div class="meta-badge">
    <strong>Executive Financial Report</strong><br>
    Currency Baseline: <strong>$1.00 USD = ₹85.00 INR</strong><br>
    Architecture: LangGraph Multi-Agent
  </div>
</div>

<!-- Executive Summary Banner -->
<div class="summary-card">
  <h3>Executive Summary & Financial Viability</h3>
  <p>The Lead Intelligence Platform achieves enterprise-grade extraction efficiency through deterministic 0-token early stages (RSS ingestion, SHA-256 deduplication, and regex filtering) and early-exit relevance routing. Operating on <strong>Google Gemini 2.0 Flash</strong> or <strong>Groq GPT-OSS 20B</strong>, the total cost to process 5 full luxury interior design articles is <strong>$0.0034 (~₹0.29 INR)</strong>, and <strong>$0.00 (100% Free)</strong> under standard daily developer quotas.</p>
  <div class="stat-row">
    <div class="stat-item">
      <div class="stat-val">$0.00069 (₹0.06)</div>
      <div class="stat-lbl">Cost / Valid Article (Gemini/Groq)</div>
    </div>
    <div class="stat-item">
      <div class="stat-val">31,750</div>
      <div class="stat-lbl">Tokens / 5 Valid Articles</div>
    </div>
    <div class="stat-item">
      <div class="stat-val">~450-750 t/s</div>
      <div class="stat-lbl">Groq LPU Inference Speed</div>
    </div>
    <div class="stat-item">
      <div class="stat-val">350,000+</div>
      <div class="stat-lbl">Leads on Neon Free DB</div>
    </div>
  </div>
</div>

<!-- Section 1 -->
<h2>1. Multi-Agent Token Consumption Mechanics</h2>
<p>Articles entering the system traverse discrete deterministic and agentic phases. Non-residential articles exit after Node 1, preventing up to 80% of unnecessary token consumption.</p>

<table>
  <thead>
    <tr>
      <th>Stage / Agent Node</th>
      <th>Agent Role & Extraction Target</th>
      <th class="text-center">Input Tokens</th>
      <th class="text-center">Output Tokens</th>
      <th class="text-center">Total Tokens</th>
      <th class="text-center">Execution Cost</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Stages 1–3 (Pre-Filter)</strong></td>
      <td>RSS Parser, SHA-256 Dedup, Keyword Regex</td>
      <td class="text-center">0</td>
      <td class="text-center">0</td>
      <td class="text-center bold">0</td>
      <td class="text-center"><span class="badge-free">FREE ($0.00)</span></td>
    </tr>
    <tr>
      <td><strong>Node 1: Relevance Classifier</strong></td>
      <td>Filters residential spaces vs product reviews</td>
      <td class="text-center">~1,200</td>
      <td class="text-center">~100</td>
      <td class="text-center bold">~1,300</td>
      <td class="text-center">Runs for ALL articles</td>
    </tr>
    <tr>
      <td><strong>Node 2: Project Intelligence</strong></td>
      <td>Extracts designer, studio, owner, square footage</td>
      <td class="text-center">~1,600</td>
      <td class="text-center">~350</td>
      <td class="text-center bold">~1,950</td>
      <td class="text-center">Valid residential only</td>
    </tr>
    <tr>
      <td><strong>Node 3: Rug Intelligence</strong></td>
      <td>Evaluates bespoke rug opportunities & materials</td>
      <td class="text-center">~1,700</td>
      <td class="text-center">~250</td>
      <td class="text-center bold">~1,950</td>
      <td class="text-center">Valid residential only</td>
    </tr>
    <tr>
      <td><strong>Node 4: Public Verifier</strong></td>
      <td>Verifies studio website & Instagram profiles</td>
      <td class="text-center">~900</td>
      <td class="text-center">~250</td>
      <td class="text-center bold">~1,150</td>
      <td class="text-center">Valid residential only</td>
    </tr>
    <tr>
      <td><strong>Node 5: Scorer & Persistence</strong></td>
      <td>0–100 Scoring Algorithm & PostgreSQL Write</td>
      <td class="text-center">0</td>
      <td class="text-center">0</td>
      <td class="text-center bold">0</td>
      <td class="text-center"><span class="badge-free">FREE ($0.00)</span></td>
    </tr>
  </tbody>
</table>

<div class="grid-2">
  <div class="box">
    <h4>🚫 Invalid / Irrelevant Article Profile</h4>
    <p>• <strong>1 LLM Call</strong> (Exits at Node 1)<br>
    • <strong>Input Tokens:</strong> ~1,200 | <strong>Output Tokens:</strong> ~100<br>
    • <strong>Total Consumption:</strong> <strong>~1,300 tokens</strong><br>
    • <strong>Cost (Gemini/Groq):</strong> <strong>$0.00012 (~₹0.010 INR)</strong></p>
  </div>
  <div class="box">
    <h4>✅ Valid Luxury Residential Article Profile</h4>
    <p>• <strong>4 LLM Calls</strong> (Full Multi-Agent Suite)<br>
    • <strong>Input Tokens:</strong> ~5,400 | <strong>Output Tokens:</strong> ~950<br>
    • <strong>Total Consumption:</strong> <strong>~6,350 tokens</strong><br>
    • <strong>Cost (Gemini/Groq):</strong> <strong>$0.00069 (~₹0.059 INR)</strong></p>
  </div>
</div>

<!-- Page Break for Clean Layout -->
<div class="page-break"></div>

<!-- Section 2 -->
<h2>2. Universal LLM Provider Benchmark & Cost Matrix</h2>
<p>Below is the comprehensive price, speed, and token cost comparison across all supported providers. Calculations use the standard batch of <strong>5 Valid Residential Articles (27,000 Input + 4,750 Output = 31,750 Total Tokens)</strong>.</p>

<table>
  <thead>
    <tr>
      <th>Provider & Model</th>
      <th class="text-center">Speed</th>
      <th class="text-center">Pricing / 1M (In / Out)</th>
      <th class="text-center">Cost / 1 Valid Article</th>
      <th class="text-center">Cost / 5 Valid Articles (USD)</th>
      <th class="text-center">Cost / 5 Valid Articles (INR ₹)</th>
      <th class="text-center">Daily Free Cap</th>
    </tr>
  </thead>
  <tbody>
    <tr class="highlight-row">
      <td><strong>Google Gemini 2.0 Flash</strong><br><small>Recommended Default</small></td>
      <td class="text-center"><span class="badge-speed">~220 t/s</span></td>
      <td class="text-center">$0.075 / $0.30</td>
      <td class="text-center">$0.00069</td>
      <td class="text-center bold">$0.00345</td>
      <td class="text-center bold">₹0.293</td>
      <td class="text-center"><span class="badge-free">15 RPM / 1M TPM</span></td>
    </tr>
    <tr class="highlight-row">
      <td><strong>Groq (GPT-OSS 20B)</strong><br><small>OpenAI Architecture on LPU</small></td>
      <td class="text-center"><span class="badge-speed">~450 t/s</span></td>
      <td class="text-center">$0.075 / $0.30</td>
      <td class="text-center">$0.00069</td>
      <td class="text-center bold">$0.00345</td>
      <td class="text-center bold">₹0.293</td>
      <td class="text-center"><span class="badge-free">200k TPD (~31 articles)</span></td>
    </tr>
    <tr>
      <td><strong>Groq (Llama 3.1 8B Instant)</strong><br><small>Maximum Throughput</small></td>
      <td class="text-center"><span class="badge-speed">~750 t/s</span></td>
      <td class="text-center">$0.050 / $0.08</td>
      <td class="text-center">$0.00035</td>
      <td class="text-center bold">$0.00173</td>
      <td class="text-center bold">₹0.147</td>
      <td class="text-center"><span class="badge-free">500k TPD (~78 articles)</span></td>
    </tr>
    <tr>
      <td><strong>Groq (Llama 3.3 70B Versatile)</strong><br><small>High-Reasoning Open Model</small></td>
      <td class="text-center"><span class="badge-speed">~280 t/s</span></td>
      <td class="text-center">$0.590 / $0.79</td>
      <td class="text-center">$0.00394</td>
      <td class="text-center bold">$0.01968</td>
      <td class="text-center bold">₹1.673</td>
      <td class="text-center"><span class="badge-free">100k TPD (~15 articles)</span></td>
    </tr>
    <tr>
      <td><strong>OpenRouter (DeepSeek V3)</strong><br><small>Cost-Effective Frontier Class</small></td>
      <td class="text-center"><span class="badge-speed">~70 t/s</span></td>
      <td class="text-center">$0.140 / $0.28</td>
      <td class="text-center">$0.00102</td>
      <td class="text-center bold">$0.00511</td>
      <td class="text-center bold">₹0.434</td>
      <td class="text-center">Pay-as-you-go</td>
    </tr>
    <tr>
      <td><strong>OpenAI (GPT-4o-mini)</strong><br><small>Standard Commercial Baseline</small></td>
      <td class="text-center"><span class="badge-speed">~140 t/s</span></td>
      <td class="text-center">$0.150 / $0.60</td>
      <td class="text-center">$0.00138</td>
      <td class="text-center bold">$0.00690</td>
      <td class="text-center bold">₹0.587</td>
      <td class="text-center">Pay-as-you-go</td>
    </tr>
    <tr>
      <td><strong>Anthropic (Claude 3.5 Haiku)</strong><br><small>High Precision Nuance</small></td>
      <td class="text-center"><span class="badge-speed">~110 t/s</span></td>
      <td class="text-center">$0.800 / $4.00</td>
      <td class="text-center">$0.00812</td>
      <td class="text-center bold">$0.04060</td>
      <td class="text-center bold">₹3.451</td>
      <td class="text-center">Pay-as-you-go</td>
    </tr>
    <tr>
      <td><strong>OpenAI (GPT-4o Standard)</strong><br><small>Flagship Reasoning</small></td>
      <td class="text-center"><span class="badge-speed">~90 t/s</span></td>
      <td class="text-center">$2.500 / $10.00</td>
      <td class="text-center">$0.02300</td>
      <td class="text-center bold">$0.11500</td>
      <td class="text-center bold">₹9.775</td>
      <td class="text-center">Pay-as-you-go</td>
    </tr>
    <tr>
      <td><strong>Anthropic (Claude 3.5 Sonnet)</strong><br><small>Top Benchmark Intelligence</small></td>
      <td class="text-center"><span class="badge-speed">~65 t/s</span></td>
      <td class="text-center">$3.000 / $15.00</td>
      <td class="text-center">$0.03045</td>
      <td class="text-center bold">$0.15225</td>
      <td class="text-center bold">₹12.941</td>
      <td class="text-center">Pay-as-you-go</td>
    </tr>
    <tr>
      <td><strong>Ollama (Local Offline)</strong><br><small>Llama 3.2 / Mistral / Qwen</small></td>
      <td class="text-center"><span class="badge-speed">Hardware</span></td>
      <td class="text-center">$0.00 / $0.00</td>
      <td class="text-center">$0.00000</td>
      <td class="text-center bold">$0.00000</td>
      <td class="text-center bold">₹0.000</td>
      <td class="text-center"><span class="badge-free">UNLIMITED ($0)</span></td>
    </tr>
  </tbody>
</table>

<!-- Section 3 -->
<h2>3. Cloud Infrastructure & Ancillary Services Cost</h2>

<div class="grid-2">
  <div class="box">
    <h4>🐘 Neon Serverless PostgreSQL Database</h4>
    <p>• <strong>Free Tier:</strong> 0.5 GiB storage, 100 CU-hrs/mo, SSL connection pooling.<br>
    • <strong>Lead Capacity:</strong> Each lead record uses ~1.5 KB. The free tier comfortably holds <strong>350,000+ lead records</strong>.<br>
    • <strong>Cost:</strong> <strong>$0.00 / month (₹0.00)</strong>.<br>
    • <strong>Scale Tier (>500MB):</strong> $0.15 / GB-month (~₹12.75 / GB-month).</p>
  </div>
  <div class="box">
    <h4>🔍 Tavily AI Public Search API</h4>
    <p>• <strong>Free Tier:</strong> 1,000 search credits / month (covers 1,000 designer checks).<br>
    • <strong>Cost on Free Tier:</strong> <strong>$0.00 / month (₹0.00)</strong>.<br>
    • <strong>Paid Usage:</strong> $0.005 / search credit (~₹0.425 / search).<br>
    • <strong>Mock Search Mode:</strong> Built-in zero-key fallback with <strong>$0.00 cost</strong>.</p>
  </div>
</div>

<div class="box" style="margin-top:8px">
  <h4>☁️ Application Web Hosting (Render / Dockerless Cloud)</h4>
  <p>• <strong>Render Free Tier:</strong> 512 MB RAM, Shared CPU, automatic spin-down on idle $\rightarrow$ <strong>$0.00 / month (₹0.00)</strong>.<br>
  • <strong>Render Starter Tier (24/7 Always-On):</strong> $7.00 / month (~₹595.00 INR / month) for uninterrupted cron scheduled pipelines.</p>
</div>

<!-- Section 4 -->
<h2>4. Total Cost of Ownership (TCO) Projections</h2>

<table>
  <thead>
    <tr>
      <th>Monthly Operational Tier</th>
      <th class="text-center">Articles / Month</th>
      <th class="text-center">LLM Tokens</th>
      <th class="text-center">Tavily Searches</th>
      <th class="text-center">Total Monthly Cost (USD)</th>
      <th class="text-center">Total Monthly Cost (INR ₹)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Tier 1: Free Developer / Pilot</strong><br><small>Runs daily 5-10 article batches</small></td>
      <td class="text-center">~250 articles</td>
      <td class="text-center">~1.2M tokens</td>
      <td class="text-center">~150 searches</td>
      <td class="text-center bold" style="color:#15803d">$0.00 / mo</td>
      <td class="text-center bold" style="color:#15803d">₹0.00 / mo</td>
    </tr>
    <tr>
      <td><strong>Tier 2: Active Production (Gemini/Groq)</strong><br><small>Processes full magazine issues continuously</small></td>
      <td class="text-center">2,500 articles</td>
      <td class="text-center">~12.5M tokens</td>
      <td class="text-center">~1,500 searches</td>
      <td class="text-center bold">$3.40 / mo</td>
      <td class="text-center bold">₹289.00 / mo</td>
    </tr>
    <tr>
      <td><strong>Tier 3: Enterprise Scale + Always-On VM</strong><br><small>Includes $7 Render VM + 10k articles</small></td>
      <td class="text-center">10,000 articles</td>
      <td class="text-center">~50.0M tokens</td>
      <td class="text-center">~6,000 searches</td>
      <td class="text-center bold">$38.60 / mo</td>
      <td class="text-center bold">₹3,281.00 / mo</td>
    </tr>
  </tbody>
</table>

<div class="callout">
  <div class="callout-title">💡 Final Economic Takeaway & Provider Recommendation</div>
  For commercial deployment, <strong>Google Gemini 2.0 Flash</strong> and <strong>Groq GPT-OSS 20B</strong> offer the ideal combination of zero cost on free tiers, ultra-fast 450+ t/s latency, 128k+ context windows, and fraction-of-a-cent scaling costs (₹0.29 per 5 valid articles).
</div>

</body>
</html>
"""

async def generate_pdf():
    pdf_path = Path("Agentic_Lead_Intelligence_Cost_and_Token_Benchmark.pdf")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(HTML_CONTENT, wait_until="networkidle")
        await page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            margin={"top": "14mm", "bottom": "14mm", "left": "14mm", "right": "14mm"}
        )
        await browser.close()
    print(f"PDF successfully generated at: {pdf_path.resolve()}")

if __name__ == "__main__":
    asyncio.run(generate_pdf())
