# Agentik (A CLI‑First Modular Agent Framework)

Agentik is a developer‑friendly framework for building LLM agents that run via **OpenRouter**. It emphasizes: clean YAML configs, a batteries‑included CLI, pluggable tools with safety policies, rich JSONL transcripts, and a **dev watcher** for rapid inner‑loop iteration.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configure OpenRouter](#configure-openrouter)
4. [Verify Setup](#verify-setup)
5. [Quick Start](#quick-start)
6. [Configuration Primer](#configuration-primer)
7. [CLI Reference (with Windows PowerShell and macOS/Linux examples)](#cli-reference)

   * version, self-test, init
   * new (agent|tool)
   * template (list|apply|pull)
   * run
   * dev watch
   * keys (set|show)
   * models list
   * tools (list|info|run)
   * validate file
   * batch run
   * memory (init|recall|summarize|clear|path)
   * eval run
   * config path
8. [Built‑in Tools & Policies](#built-in-tools--policies)
9. [Transcripts & Cost Estimation](#transcripts--cost-estimation)
10. [Quick Reference Table](#Quick-Reference-Table)
10. [Troubleshooting](#troubleshooting)
11. [Development](#development)

---

## Prerequisites

* **Python 3.10+**

---

## Installation

**Windows (PowerShell)**

```powershell
pip install agentik-framework
```

**macOS/Linux**

```bash
pip install agentik-framework
```

<!-- > Local editable install for contributing:
>
> ```bash
> pip install -e .[dev]
> ``` -->

---

## Configure OpenRouter

Agentik uses OpenRouter for LLM calls. Provide your key via env var or store it in Agentik’s RC.

**Windows (PowerShell)**

```powershell
setx OPENROUTER_API_KEY "sk-or-XXXXXXXXXXXXXXXX"
# Close & reopen PowerShell so the env var is available in new sessions
```

**macOS/Linux (bash/zsh)**

```bash
echo 'export OPENROUTER_API_KEY="sk-or-XXXXXXXXXXXXXXXX"' >> ~/.bashrc
source ~/.bashrc   # or: source ~/.zshrc
```

**Store via Agentik RC (either scope):**

```powershell
agentik keys set openrouter sk-or-XXXXXXXXXXXXXXXX --global
# or
agentik keys set openrouter sk-or-XXXXXXXXXXXXXXXX --local
```

---

## Verify Setup

**Windows (PowerShell)**

```powershell
agentik self-test
agentik models list --filter gpt --refresh   # optional
```

**macOS/Linux**

```bash
agentik self-test
agentik models list --filter gpt --refresh
```

---

## Quick Start

1. **Initialize a project**

**PowerShell**

```powershell
mkdir my-agent; cd my-agent
agentik init . --template basic --name "My Agent Project"
```

**macOS/Linux**

```bash
mkdir my-agent && cd my-agent
agentik init . --template basic --name "My Agent Project"
```

2. **Scaffold an agent**

**PowerShell**

```powershell
agentik new agent research `
  --template basic `
  --tools http_fetch,html_to_text,write_file `
  --with-tests `
  --to .
```

**macOS/Linux**

```bash
agentik new agent research \
  --template basic \
  --tools http_fetch,html_to_text,write_file \
  --with-tests \
  --to .
```

3. **Minimal config (save as `agents/agent.yaml`)**

```yaml
agent:
  name: ResearchBot
  goal: "Research and summarize information."
  loop:
    max_steps: 3
    reflect: true

llm:
  model: openai/gpt-4o-mini
  temperature: 0.3

memory:
  type: json
  path: ./memory/research.json

policies:
  allow_network: true
  allow_filesystem: true

tools:
  - http_fetch
  - html_to_text
  - write_file
```

4. **Run your agent**

**PowerShell**

```powershell
agentik run .\agents\agent.yaml `
  -p "Summarize the main differences between GPT-4o and small LLMs in 5 bullets." `
  --profile fast `
  --stream `
  --save-transcript .\runs\first-run.jsonl
```

**macOS/Linux**

```bash
agentik run ./agents/agent.yaml \
  -p "Summarize the main differences between GPT-4o and small LLMs in 5 bullets." \
  --profile fast \
  --stream \
  --save-transcript ./runs/first-run.jsonl
```

5. **Use the dev watcher (auto re‑run on save)**

> PowerShell tip: **quote your globs** (e.g., `'**/*.py'`) so the shell doesn’t expand them.

**PowerShell**

```powershell
agentik dev watch .\agents\agent.yaml `
  --prompt "Summarize this project in 3 bullets." `
  --path . `
  --include '**/*.py' --include '**/*.yaml' --include 'templates/**' `
  --exclude '.venv/**' --exclude 'runs/**' `
  --save-transcripts .\runs `
  --profile dev `
  --stream
```

**macOS/Linux**

```bash
agentik dev watch ./agents/agent.yaml \
  --prompt "Summarize this project in 3 bullets." \
  --path . \
  --include '**/*.py' --include '**/*.yaml' --include 'templates/**' \
  --exclude '.venv/**' --exclude 'runs/**' \
  --save-transcripts ./runs \
  --profile dev \
  --stream
```

---

## Configuration Primer

* **YAML config** defines the agent (goal, loop), LLM (model, temperature), memory store, policies, and tools.
* **Profiles** (CLI `--profile`) apply overrides:

  * `fast`: `{max_steps=2, reflect=false, temperature=0.2}`
  * `thorough`: `{max_steps=6, reflect=true, temperature=0.3}`
  * `deterministic`: `{temperature=0.0, reflect=false}`
  * `creative`: `{temperature=0.9, reflect=false}`
  * `cheap`: `{temperature=0.2}` (keeps configured model)
  * `dev`: `{max_steps=3, reflect=false, temperature=0.3}`
* **Precedence**: YAML → RC/env → **CLI overrides** → **profile overrides**.

---

## CLI Reference

Below, every command shows a **signature** and examples for **Windows PowerShell** and **macOS/Linux**.

### Version & Environment

#### `agentik version`

Print CLI version.

**PowerShell**

```powershell
agentik version
```

**macOS/Linux**

```bash
agentik version
```

#### `agentik self-test`

Show Python/OS info, OpenRouter key presence, and RC location.

**PowerShell**

```powershell
agentik self-test
```

**macOS/Linux**

```bash
agentik self-test
```

---

### Project Scaffolding

#### `agentik init`

```
agentik init [PATH] --template TEXT --force --name TEXT
```

* `PATH` default `.`
* `--template` default `basic`
* `--force` overwrite existing files
* `--name` project name override

**PowerShell**

```powershell
agentik init . --template basic --name "Demo"
```

**macOS/Linux**

```bash
agentik init . --template basic --name "Demo"
```

#### `agentik new agent`

```
agentik new agent NAME \
  --template TEXT \
  --tools "t1,t2" \
  --memory [dict|json] \
  --memory-path PATH \
  --to DIR \
  --with-tests \
  --force
```

**PowerShell**

```powershell
agentik new agent helper `
  --template basic `
  --tools http_fetch,html_to_text `
  --memory json `
  --memory-path .\memory\agent.json `
  --to . `
  --with-tests `
  --force
```

**macOS/Linux**

```bash
agentik new agent helper \
  --template basic \
  --tools http_fetch,html_to_text \
  --memory json \
  --memory-path ./memory/agent.json \
  --to . \
  --with-tests \
  --force
```

#### `agentik new tool`

```
agentik new tool NAME --template [python] --to DIR --with-tests --force
```

**PowerShell**

```powershell
agentik new tool web_fetcher --template python --to . --with-tests --force
```

**macOS/Linux**

```bash
agentik new tool web_fetcher --template python --to . --with-tests --force
```

---

### Templates

#### `agentik template list`

List built‑ins.

**PowerShell**

```powershell
agentik template list
```

**macOS/Linux**

```bash
agentik template list
```

#### `agentik template apply`

```
agentik template apply kind/name --to DIR --force --name TEXT
```

**PowerShell**

```powershell
agentik template apply agent/basic --to . --force --name MyBot
```

**macOS/Linux**

```bash
agentik template apply agent/basic --to . --force --name MyBot
```

#### `agentik template pull`

Pull a git repo or zip into `templates/third_party`.

**PowerShell**

```powershell
agentik template pull https://example.com/my-templates.zip --to .
```

**macOS/Linux**

```bash
agentik template pull https://example.com/my-templates.zip --to .
```

---

### Running Agents

#### `agentik run`

```
agentik run CONFIG \
  -p/--prompt TEXT \
  --model TEXT \
  --temperature FLOAT \
  --stream \
  --dry-run \
  --save-transcript PATH \
  --profile [fast|thorough|deterministic|creative|cheap|dev|none] \
  --tag TAG  (repeatable) \
  --note TEXT \
  --run-id TEXT \
  --obs-max-chars INT
```

**PowerShell**

```powershell
agentik run .\agents\agent.yaml `
  -p "Five bullet summary of topic X" `
  --profile fast `
  --stream `
  --save-transcript .\runs\out.jsonl
```

**macOS/Linux**

```bash
agentik run ./agents/agent.yaml \
  -p "Five bullet summary of topic X" \
  --profile fast \
  --stream \
  --save-transcript ./runs/out.jsonl
```

---

### Developer Watch Mode

#### `agentik dev watch`

```
agentik dev watch CONFIG \
  -p/--prompt TEXT \
  --prompt-file PATH \
  --path PATH          # repeatable; default "." \
  --include GLOB       # repeatable; default ["**/*.py", "**/*.yml", "**/*.yaml", "**/*.json", "**/*.md", "templates/**", "tools/**"] \
  --exclude GLOB       # repeatable \
  --interval FLOAT     # default 0.6 \
  --debounce FLOAT     # default 0.5 \
  --clear/--no-clear   # default clear \
  --stream/--no-stream # default stream \
  --profile dev        # default "dev" \
  --save-transcripts DIR \
  --obs-max-chars INT  # default 800 \
  --no-initial-run \
  --tag TAG            # repeatable; default ["dev"] \
  --note TEXT
```

**PowerShell**

```powershell
agentik dev watch .\agents\agent.yaml `
  --prompt "Echo the date" `
  --include '**/*.py' `
  --exclude '.venv/**' `
  --save-transcripts .\runs
```

**macOS/Linux**

```bash
agentik dev watch ./agents/agent.yaml \
  --prompt "Echo the date" \
  --include '**/*.py' \
  --exclude '.venv/**' \
  --save-transcripts ./runs
```

---

### Keys & Models

#### `agentik keys set openrouter`

Store an API key in RC.

**PowerShell**

```powershell
agentik keys set openrouter sk-or-... --global
# or
agentik keys set openrouter sk-or-... --local
```

**macOS/Linux**

```bash
agentik keys set openrouter sk-or-... --global
# or
agentik keys set openrouter sk-or-... --local
```

#### `agentik keys show`

Display masked key (env & RC) and RC scope/path.

**PowerShell**

```powershell
agentik keys show
```

**macOS/Linux**

```bash
agentik keys show
```

#### `agentik models list`

List OpenRouter models (with optional cache bypass).

**PowerShell**

```powershell
agentik models list --filter gpt --refresh
```

**macOS/Linux**

```bash
agentik models list --filter gpt --refresh
```

---

### Tools (Discovery & Direct Runs)

#### `agentik tools list`

List discoverable tools.

**PowerShell**

```powershell
agentik tools list
```

**macOS/Linux**

```bash
agentik tools list
```

#### `agentik tools info NAME`

Show class & description.

**PowerShell**

```powershell
agentik tools info http_fetch
```

**macOS/Linux**

```bash
agentik tools info http_fetch
```

#### `agentik tools run NAME`

Call a tool directly (no agent loop). Values auto‑coerce: `true/false` → bool; `1`→int; `1.2`→float; else string. Quote values with spaces/HTML.

**PowerShell**

```powershell
agentik tools run http_fetch --arg url=https://example.com --arg ttl=3600 --arg allow_network=true --json
agentik tools run html_to_text --arg "html=<p>Hello</p>" --arg keep_newlines=true --json
agentik tools run write_file --arg path=out\hello.txt --arg "content=Hello" --arg allow_filesystem=true --json
```

**macOS/Linux**

```bash
agentik tools run http_fetch --arg url=https://example.com --arg ttl=3600 --arg allow_network=true --json
agentik tools run html_to_text --arg 'html=<p>Hello</p>' --arg keep_newlines=true --json
agentik tools run write_file --arg path=out/hello.txt --arg 'content=Hello' --arg allow_filesystem=true --json
```

---

### Validation & Batch

#### `agentik validate file`

Validate YAML; optionally print **effective** config after CLI overrides.

**PowerShell**

```powershell
agentik validate file .\agents\agent.yaml `
  --show-effective `
  --model openai/gpt-4o-mini `
  --temperature 0.2 `
  --max-steps 2
```

**macOS/Linux**

```bash
agentik validate file ./agents/agent.yaml \
  --show-effective \
  --model openai/gpt-4o-mini \
  --temperature 0.2 \
  --max-steps 2
```

#### `agentik batch run`

Run prompts from CSV/JSONL and write JSONL results.

**PowerShell**

```powershell
agentik batch run .\prompts.jsonl `
  --column prompt `
  --out .\results.jsonl `
  --model openai/gpt-4o-mini `
  --temperature 0.2
```

**macOS/Linux**

```bash
agentik batch run ./prompts.jsonl \
  --column prompt \
  --out ./results.jsonl \
  --model openai/gpt-4o-mini \
  --temperature 0.2
```

---

### Memory Helpers

#### `agentik memory init`

Initialize store and add an initial record.

**PowerShell**

```powershell
agentik memory init --type json --path .\memory\agentik.json
```

**macOS/Linux**

```bash
agentik memory init --type json --path ./memory/agentik.json
```

#### `agentik memory recall`

**PowerShell**

```powershell
agentik memory recall --n 10 --config .\agents\agent.yaml
```

**macOS/Linux**

```bash
agentik memory recall --n 10 --config ./agents/agent.yaml
```

#### `agentik memory summarize`

**PowerShell**

```powershell
agentik memory summarize --n 20 --max-chars 1200 --config .\agents\agent.yaml
```

**macOS/Linux**

```bash
agentik memory summarize --n 20 --max-chars 1200 --config ./agents/agent.yaml
```

#### `agentik memory clear`

**PowerShell**

```powershell
agentik memory clear --config .\agents\agent.yaml
```

**macOS/Linux**

```bash
agentik memory clear --config ./agents/agent.yaml
```

#### `agentik memory path`

**PowerShell**

```powershell
agentik memory path --config .\agents\agent.yaml
```

**macOS/Linux**

```bash
agentik memory path --config ./agents/agent.yaml
```

---

### Lightweight Eval Harness

#### `agentik eval run`

Each JSONL line should have `prompt`, and optional `expect_contains[]` and/or `expect_regex`.

**PowerShell**

```powershell
agentik eval run .\tests.jsonl --config .\agents\agent.yaml --out .\eval_results.jsonl
```

**macOS/Linux**

```bash
agentik eval run ./tests.jsonl --config ./agents/agent.yaml --out ./eval_results.jsonl
```

---

### Config Helpers

#### `agentik config path`

Show the `.agentikrc` path for a scope.

**PowerShell**

```powershell
agentik config path --global
agentik config path --local
```

**macOS/Linux**

```bash
agentik config path --global
agentik config path --local
```

---

## Built‑in Tools & Policies

Selected built‑ins:

* `http_fetch(url, ttl, timeout, max_bytes, headers, allow_network)` → `{ok, data, error, meta}` (`data.text`, `data.status`, cache info)
* `html_to_text(html, keep_newlines, drop_links, max_chars)` → plaintext
* `write_file(path, content, encoding, overwrite, allow_abs, allow_filesystem)` → safe file writer

Policies are enforced by config:

```yaml
policies:
  allow_network: true | false
  allow_filesystem: true | false
```

If a tool requires a disabled capability, the call is blocked and recorded in observations/transcripts.

---

## Transcripts & Cost Estimation

Add `--save-transcript PATH` (single run) or `--save-transcripts DIR` (dev watch) to write JSONL transcripts. Summaries include steps, token counts, timings, and cost if available.

**Optional pricing overrides (USD / 1K tokens):**

**PowerShell**

```powershell
$env:AGENTIK_PRICE_PROMPT_PER_1K = "0.50"
$env:AGENTIK_PRICE_COMPLETION_PER_1K = "1.50"
```

**macOS/Linux**

```bash
export AGENTIK_PRICE_PROMPT_PER_1K="0.50"
export AGENTIK_PRICE_COMPLETION_PER_1K="1.50"
```

---

### Quick Reference Table

| Area      | Command                            | Key Options                                                                                                                                                                                              |           |       |         |           |
| --------- | ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ----- | ------- | --------- |
| Version   | `agentik version`                  | –                                                                                                                                                                                                        |           |       |         |           |
| Self‑test | `agentik self-test`                | –                                                                                                                                                                                                        |           |       |         |           |
| Init      | `agentik init [PATH]`              | `--template`, `--force`, `--name`                                                                                                                                                                        |           |       |         |           |
| Run       | `agentik run CONFIG`               | `-p`, `--model`, `--temperature`, `--stream`, `--dry-run`, `--save-transcript`, `--profile`, `--tag`, `--note`, `--run-id`, `--obs-max-chars`                                                            |           |       |         |           |
| Keys      | `agentik keys set openrouter`      | `--global` or `--local`                                                                                                                                                                                  |           |       |         |           |
| Keys      | `agentik keys show`                | –                                                                                                                                                                                                        |           |       |         |           |
| Models    | `agentik models list`              | `--filter`, `--refresh`                                                                                                                                                                                  |           |       |         |           |
| New       | `agentik new agent NAME`           | `--template`, `--tools`, `--memory`, `--memory-path`, `--to`, `--with-tests`, `--force`                                                                                                                  |           |       |         |           |
| New       | `agentik new tool NAME`            | `--template`, `--to`, `--with-tests`, `--force`                                                                                                                                                          |           |       |         |           |
| Templates | `agentik template list/apply/pull` | as above                                                                                                                                                                                                 |           |       |         |           |
| Tools     | `agentik tools list/info/run`      | `--arg`, `--json`                                                                                                                                                                                        |           |       |         |           |
| Validate  | `agentik validate file CONFIG`     | `--show-effective`, `--model`, `--temperature`, `--max-steps`                                                                                                                                            |           |       |         |           |
| Batch     | `agentik batch run FILE`           | `--column`, `--out`, `--model`, `--temperature`                                                                                                                                                          |           |       |         |           |
| Memory | `agentik memory {init recall summarize clear path}` | see above |
| Eval      | `agentik eval run FILE.jsonl`      | `--config`, `--out`                                                                                                                                                                                      |           |       |         |           |
| Dev       | `agentik dev watch CONFIG`         | `-p`/`--prompt-file`, `--path`, `--include`, `--exclude`, `--interval`, `--debounce`, `--clear`, `--stream`, `--profile`, `--save-transcripts`, `--obs-max-chars`, `--no-initial-run`, `--tag`, `--note` |           |       |         |           |
| Config    | `agentik config path`              | `--global` or `--local`                                                                                                                                                                                  |           |       |         |           |

---

**You’re set.** Keep this open while you iterate; pair it with `agentik dev watch` for the fastest edit‑run loop.

---

## Troubleshooting

* **“Network error talking to OpenRouter.”** Confirm your key in the current shell:

  * PowerShell: `echo $env:OPENROUTER_API_KEY`
  * macOS/Linux: `echo $OPENROUTER_API_KEY`
    Then try: `agentik models list --refresh`. Behind a proxy? Set `HTTP_PROXY`/`HTTPS_PROXY`.

* **Dev watcher: “unexpected extra arguments …”**

  * Quote globs in PowerShell: `--include '**/*.py'` (single quotes).

* **Auth error / missing key**: set `OPENROUTER_API_KEY` or run `agentik keys set openrouter ...`.
* **Rate limited**: add delays, batch, or upgrade your OpenRouter plan.
* **Network error**: check connectivity or proxy settings (`HTTP_PROXY`, `HTTPS_PROXY`).
* **PowerShell globbing**: quote globs, e.g. `--include '**/*.py'`.

---

## Development

* Lint/format: `ruff check .` and `black .`
* Tests: `pytest -q`
<!-- * Build: `python -m build`
* Publish: `twine upload dist/*` -->

---

**Happy building with Agentik!**
