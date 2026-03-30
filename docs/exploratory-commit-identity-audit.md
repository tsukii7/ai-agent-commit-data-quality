# Exploratory Commit Identity Audit

This document is an exploratory supplement to the main report. It examines how six AI coding agents can be identified in GitHub commit metadata and how those identity choices affect search design, data collection, and interpretation.

All counts below are search snapshots from March 27, 2026. They should be treated as exploratory observations rather than stable benchmarks.

## Scope and Terms

| Term | Meaning |
|------|---------|
| `author-email:` search | Exact matching on the Git commit author field. This is the highest-precision way to detect commits authored directly by an agent. |
| `author:` search | GitHub commit search using either a user login or an app slug with `[bot]`. In several cases it is equivalent to a validated `author-email:` query. |
| Full-text search | Searching for a quoted string in the commit message body. This can capture co-author trailers and message references, but it is noisier than author-field search. |
| Bot noreply email | GitHub-generated bot email in the form `ID+LOGIN@users.noreply.github.com`. |
| Co-author email | Email written into a `Co-authored-by:` trailer by a tool or platform workflow. |
| GitHub App slug | The registered app name used in `author:` queries, for example `anthropic-code-agent[bot]`. |

## 1. Consolidated Identity Summary

The original internal note contained repeated per-agent bot/account details. In this repository version, the recurring identity structure is consolidated here and referenced later through search evidence.

| Agent | GitHub App bot(s) | User account(s) | Custom author email(s) | Co-author / message-level signal(s) | Key note |
|-------|-------------------|-----------------|------------------------|-------------------------------------|----------|
| Copilot | `Copilot`, slug `copilot-swe-agent`, bot email `198982749+Copilot@users.noreply.github.com` | None emphasized | None emphasized | `copilot@users.noreply.github.com` | Strong bot-author channel plus a large co-author channel |
| Claude | `Claude`, slug `anthropic-code-agent`, bot email `242468646+Claude@users.noreply.github.com` | `claude` | `noreply@anthropic.com` | `noreply@anthropic.com` | Bot-style and CLI-style identities coexist |
| Devin | `devin-ai-integration[bot]`, slug `devin-ai-integration`, bot email `158243242+devin-ai-integration[bot]@users.noreply.github.com` | `cognition-team` | None emphasized | `noreply@cognition.ai`, `"devin-ai-integration[bot]"` | The bot identity is much stronger than the originally used script email |
| Cursor | `cursor[bot]`, slug `cursor`, bot email `206951365+cursor[bot]@users.noreply.github.com` | None emphasized | `cursoragent@cursor.com`, `agent@cursor.com` | `cursoragent@cursor.com` | The same email appears in both author and co-author contexts |
| Codex | `Codex`, slug `openai-code-agent`, bot email `242516109+Codex@users.noreply.github.com`; `chatgpt-codex-connector[bot]`, slug `chatgpt-codex-connector`, bot email `199175422+chatgpt-codex-connector[bot]@users.noreply.github.com` | `codex` | `codex@openai.com` | `codex@openai.com`, `noreply@openai.com`, `"Co-authored-by: Codex"` | Multiple parallel identities, including bot, CLI, and trailer-level signals |
| Gemini | `gemini-code-assist[bot]`, slug `gemini-code-assist`, bot email `176961590+gemini-code-assist[bot]@users.noreply.github.com` | `gemini-cli`, `gemini-cli-robot` | `gemini@google.com` | `gemini-code-assist@google.com`, `"Co-authored-by: gemini"`, `"gemini-code-assist[bot]"` | Identity signals are heterogeneous and require filtering |

## 2. Representative Search Evidence by Agent

### 2.1 GitHub Copilot

| Query | Count |
|------|------:|
| `author-email:198982749+Copilot@users.noreply.github.com` | 2,887,035 |
| `author:copilot-swe-agent[bot]` | 2,887,035 |
| `"copilot-swe-agent[bot]"` | 204,000 |
| `"copilot@users.noreply.github.com"` | ~950,000 |

Copilot has a very large bot-author footprint, but it also has a substantial co-author or message-level footprint that should not be conflated with fully agent-authored commits.

### 2.2 Claude Code

| Query | Count |
|------|------:|
| `author-email:242468646+Claude@users.noreply.github.com` | 13,355 |
| `author:anthropic-code-agent[bot]` | 13,355 |
| `"anthropic-code-agent[bot]"` | 1,100 |
| `author-email:noreply@anthropic.com` | 3.3M |
| `author:Claude` | 3.3M |
| `"noreply@anthropic.com"` | 11.6M |

Claude spans both a bot-style autonomous identity and a user-style CLI identity. A dataset that uses only one of these channels captures only part of Claude-related activity.

### 2.3 Devin

| Query | Count |
|------|------:|
| `author-email:158243242+devin-ai-integration[bot]@users.noreply.github.com` | 168,790 |
| `author:devin-ai-integration[bot]` | 168,790 |
| `"devin-ai-integration[bot]"` | 121,000 |
| `"158243242+devin-ai-integration[bot]@users.noreply.github.com"` | 66,300 |
| `"noreply@cognition.ai"` | 1,300 |

The original note flagged Devin as a collection-design problem because `devin@cognition.ai` was not a useful identifier, whereas the validated bot identity and bot-login full-text query were much stronger.

### 2.4 Cursor

| Query | Count |
|------|------:|
| `author-email:cursoragent@cursor.com` | 400,000 |
| `"cursoragent@cursor.com"` | 766,000 |
| `author-email:agent@cursor.com` | 198 |
| `author-email:206951365+cursor[bot]@users.noreply.github.com` | 2,700 |

The gap between `author-email:cursoragent@cursor.com` and `"cursoragent@cursor.com"` implies that roughly 366,000 additional matches come from co-author or message-level usage. Cursor is therefore especially important for separating author-mode and co-author-mode interpretation.

### 2.5 OpenAI Codex

| Query | Count |
|------|------:|
| `author-email:codex@openai.com` | 11,200 |
| `"codex@openai.com"` | 12,100 |
| `author:codex` | 6,900 |
| `author-email:242516109+Codex@users.noreply.github.com` | 3,960 |
| `author:chatgpt-codex-connector[bot]` | 529 |
| `"noreply@openai.com"` | 17,900 |
| `"Co-authored-by: Codex"` | 39,600 |
| `"codex@example.com"` | 5,400 |

Two points from the original note matter here. First, `noreply@openai.com` was explicitly validated as a real Codex co-author trailer address. Second, `"Co-authored-by: Codex"` is much broader than either `codex@openai.com` or `noreply@openai.com`, so it should be read as an exploratory upper bound rather than a precise Codex measure.

### 2.6 Gemini

| Query | Count |
|------|------:|
| `author-email:gemini@google.com` | 11,400 |
| `author:gemini-cli` | 150 |
| `author:gemini-code-assist[bot]` | 59 |
| `author-email:gemini-code-assist@google.com` | 63 |
| `"Co-authored-by: gemini"` | 135,000 |
| `"gemini-code-assist[bot]"` | 117,000 |
| `"gemini-cli-robot"` | 5,100 |
| `"gemini-cli@users.noreply.github.com"` | 847 |
| `"gemini-code-assist@google.com"` | 108 |

The internal note explicitly marked `gemini@google.com` as source-mixed rather than a clean Gemini CLI identifier. It also identified `gemini-cli-robot` as a release automation account rather than ordinary user-side coding-agent activity.

## 3. Aggregated Search Summaries

### 3.1 Author-Field Summary

These are the strongest author-side signals preserved from the original audit.

| Agent | Identity | Query form | Count |
|-------|----------|------------|------:|
| Claude | CLI user | `author-email:noreply@anthropic.com` or `author:Claude` | 3,300,000 |
| Copilot | SWE Agent bot | `author-email:198982749+Copilot@users.noreply.github.com` | 2,887,035 |
| Cursor | Editor agent | `author-email:cursoragent@cursor.com` | 400,000 |
| Devin | Bot | `author-email:158243242+devin-ai-integration[bot]@users.noreply.github.com` | 168,790 |
| Claude | App bot | `author-email:242468646+Claude@users.noreply.github.com` | 13,355 |
| Gemini | Mixed CLI-side signal | `author-email:gemini@google.com` | 11,400 |
| Codex | CLI | `author-email:codex@openai.com` | 11,200 |
| Codex | User account | `author:codex` | 6,900 |
| Codex | New bot | `author-email:242516109+Codex@users.noreply.github.com` | 3,960 |
| Cursor | Bot noreply | `author-email:206951365+cursor[bot]@users.noreply.github.com` | 2,700 |
| Codex | Legacy connector | `author:chatgpt-codex-connector[bot]` | 529 |
| Cursor | Background agent | `author-email:agent@cursor.com` | 198 |
| Gemini | CLI user | `author:gemini-cli` | 150 |
| Gemini | Code Assist bot | `author:gemini-code-assist[bot]` | 59 |

### 3.2 Full-Text Summary

These searches operate on commit-message text and therefore capture co-author trailers plus other message-level references.

| Agent | Search string | Count | Notes |
|-------|---------------|------:|------|
| Claude | `"noreply@anthropic.com"` | 11,600,000 | Very broad; includes co-author trailers and other message references |
| Copilot | `"copilot@users.noreply.github.com"` | ~950,000 | Broad co-author-style signal |
| Cursor | `"cursoragent@cursor.com"` | 766,000 | Includes author plus co-author usage |
| Gemini | `"Co-authored-by: gemini"` | 135,000 | Very broad; includes multiple Gemini variants |
| Devin | `"devin-ai-integration[bot]"` | 121,000 | Best broad Devin text-level signal |
| Gemini | `"gemini-code-assist[bot]"` | 117,000 | Broad bot-login text match |
| Devin | `"158243242+devin-ai-integration[bot]@users.noreply.github.com"` | 66,300 | Broad text match on bot email |
| Codex | `"Co-authored-by: Codex"` | 39,600 | Wide net across multiple email forms |
| Copilot | `"copilot-swe-agent[bot]"` | 204,000 | Bot-login full-text match |
| Codex | `"noreply@openai.com"` | 17,900 | Validated Codex trailer signal |
| Codex | `"codex@openai.com"` | 12,100 | Includes author plus trailer usage |
| Codex | `"codex@example.com"` | 5,400 | Placeholder-like address, unresolved attribution |
| Gemini | `"gemini-cli-robot"` | 5,100 | Release automation account |
| Devin | `"noreply@cognition.ai"` | 1,300 | Weak compared with bot-login search |
| Gemini | `"gemini-cli@users.noreply.github.com"` | 847 | Weak CLI-specific signal |
| Gemini | `"gemini-code-assist@google.com"` | 108 | Narrow trailer signal |

### 3.3 Validation of the Existing Collection Configuration

The original note compared the emails used in `collect-data.sh` against the strongest validated identifiers available at the time.

| Agent | Email used by the script | Better validated signal | Status | Interpretation |
|-------|--------------------------|-------------------------|--------|----------------|
| Claude Code | `noreply@anthropic.com` | `noreply@anthropic.com` | Valid | The script captured a real Claude CLI channel. |
| Copilot | `copilot@users.noreply.github.com` | `copilot@users.noreply.github.com` | Valid | The script captured a real co-author-style channel. |
| Codex | `codex@openai.com` | `codex@openai.com` | Valid | The script captured a meaningful Codex CLI channel. |
| Gemini | `gemini-code-assist@google.com` | `gemini-code-assist@google.com` or broader bot-login text search | Weak | Valid but too small to represent broader Gemini-related activity. |
| Devin | `devin@cognition.ai` | `noreply@cognition.ai` or, better, validated bot signals | Invalid | The original email was poor; better identifiers existed. |
| Cursor | `cursor@anysphere.io` | `cursoragent@cursor.com` | Invalid | The original email returned no meaningful results. |

The strongest collection-design failures in the original setup were Devin and Cursor. This matters because those failures can make a low-count series look like a real empirical result when it is actually an identifier problem.

## 4. Author Mode Versus Co-Author Mode

### 4.1 Commit-Field Logic

At the Git level, author and co-author information live in different places.

```text
Author: Alice <alice@example.com>
Committer: GitHub <noreply@github.com>
Co-authored-by: Claude <noreply@anthropic.com>
```

The author field belongs to the commit metadata itself. The co-author line is message text. This distinction matters because the two fields support different levels of confidence and different interpretations of AI involvement.

### 4.2 Mode A: Agent as Author

This mode occurs when the agent is written directly into the commit author field. The original note described two common paths:

1. A GitHub App bot creates the commit with an installation token.
2. A CLI or local tool sets a custom author email before `git commit`.

Typical workflow:

1. A user triggers an agent in a cloud platform or local CLI/editor workflow.
2. The agent modifies repository content.
3. The agent creates a commit using either a GitHub App identity or a custom author email.
4. The author field in the commit metadata directly records the AI identity.
5. API-generated bot commits may also carry a verified signature.

Recommended search method: `author-email:` with validated bot noreply emails or trusted custom author emails. In some cases, `author:` is an equivalent cross-check.

### 4.3 Mode B: Agent as Co-Author

This mode occurs when a human-owned commit includes a `Co-authored-by:` trailer or another textual reference to the agent in the commit message.

Typical workflow:

1. A user works locally in a terminal or editor with AI assistance.
2. The agent edits files, but the final commit uses the human's Git identity.
3. The tool or platform appends a `Co-authored-by:` trailer to the commit message.
4. The AI identity is visible in message text, not in the author field itself.

Recommended search method: quoted full-text searches such as `"email@domain"` or `"Co-authored-by: Name"`. These are broader than author-field queries and therefore more vulnerable to ambiguity and overcounting.

### 4.4 Coexistence of the Two Modes

The original note explicitly compared author-mode and co-author-mode footprints by agent.

| Agent | Author mode | Co-author / message mode | Interpretation |
|-------|-------------|--------------------------|----------------|
| Copilot | SWE Agent bot: 2,887,035 | `copilot@users.noreply.github.com`: ~950,000 | Large autonomous bot channel plus large assistive channel |
| Claude Code | App bot: 13,355; CLI author: 3.3M | `"noreply@anthropic.com"`: 11.6M | Strong CLI author presence plus a very large message-level footprint |
| Cursor | `cursoragent@cursor.com`: 400,000; `agent@cursor.com`: 198 | `"cursoragent@cursor.com"` exceeds author count by roughly 366,000 | Author and co-author signals share the same address |
| Devin | Bot author: 168,790 | `"devin-ai-integration[bot]"`: 121,000; `"noreply@cognition.ai"`: 1,300 | Bot-login text is more informative than email trailer search |
| Codex | New bot: 3,960; legacy connector: 529; CLI author: 11,200 | `"noreply@openai.com"`: 17,900; `"Co-authored-by: Codex"`: 39,600 | Multiple trailer-level forms coexist with author-side channels |
| Gemini | Code Assist bot: 59; mixed-source `gemini@google.com`: 11,400 | `"gemini-code-assist[bot]"`: 117,000; `"Co-authored-by: gemini"`: 135,000 | Broad message-level signals far exceed validated bot-author counts |

### 4.5 Implications for Research Data Collection

| Dimension | Author mode | Co-author mode |
|-----------|-------------|----------------|
| Search precision | Very high for validated bot noreply emails; high for trusted custom author emails | Moderate to low depending on the search string |
| Coverage | Only commits where the agent is the author | Commits where the agent appears in message-level metadata |
| Typical volume | Depends on the agent | Often larger than author mode |
| Semantic meaning | Agent-led or agent-executed commit production | Human-led work with AI assistance or message-level reference |
| GitHub API support | Strong | Weak; often requires full-text search |

The internal recommendation was to report author mode and co-author mode separately. They represent different degrees of AI participation and should not be merged into a single headline count.

## 5. Detection Method Taxonomy

The original note organized search methods by precision and scope.

| Detection method | Example | Precision | Coverage | Best use |
|------------------|---------|-----------|----------|----------|
| Bot noreply `author-email:` | `author-email:198982749+Copilot@users.noreply.github.com` | Very high | Bot-authored commits only | Best default for validated bot identities |
| Custom `author-email:` | `author-email:codex@openai.com` | High | Commits authored under one custom address | Best for trusted CLI-style identities |
| App slug `author:` | `author:anthropic-code-agent[bot]` | High | Equivalent to bot author identity in some cases | Useful cross-check for bot identities |
| User login `author:` | `author:Claude` | High | Commits by the user account | Useful for CLI-style user identities |
| Quoted email full-text | `"noreply@anthropic.com"` | Moderate | Any message containing the address | Good exploratory supplement, not a final count |
| Quoted bot login full-text | `"devin-ai-integration[bot]"` | Moderate | Any message containing the bot string | Helpful when bot-name references exceed email references |
| `"Co-authored-by: Name"` full-text | `"Co-authored-by: Codex"` | Low | Broad name-level sweep | Exploratory upper bound only |
| Contributors API | `/repos/{owner}/{repo}/contributors` | Very high | Repository-level presence | Good for repository validation rather than global counting |

One concrete finding from the original audit was that quoted bot-login full-text searches were unusually effective for Devin and Gemini. In both cases they covered much more than the narrow trailer-email alternatives.

## 6. Claude as a Special Case

Claude was treated separately in the original note because its identity structure creates overlapping but non-equivalent search sets.

Three representative Claude searches on March 27, 2026:

| Label | Query | Count | Search time |
|-------|-------|------:|------------:|
| A | `author-email:242468646+Claude@users.noreply.github.com` or `author:anthropic-code-agent[bot]` | 13,355 | 819 ms |
| B | `author-email:noreply@anthropic.com` or `author:Claude` | 3,300,000 | 880 ms |
| C | `"noreply@anthropic.com"` | 11,600,000 | 2 s |

Recorded overlaps in the original note:

| Overlap | Count | Interpretation |
|---------|------:|----------------|
| A ∩ C | 246 | Some bot commits also mention the Anthropic CLI email in the message |
| B ∩ C | 177,000 | Some CLI-authored commits also contain that address in message text |
| A ∩ B | Not measured | The author emails differ, so the sets should not overlap in author-field terms |

The original note also emphasized an equivalence relation:

| Identity | Account | `author:` form | `author-email:` form | Observed equivalence |
|----------|---------|----------------|----------------------|----------------------|
| GitHub App bot | `Claude` (`242468646`, bot) | `author:anthropic-code-agent[bot]` | `author-email:242468646+Claude@users.noreply.github.com` | Same count: 13,355 |
| CLI user account | `claude` (`81847`, user) | `author:Claude` | `author-email:noreply@anthropic.com` | Same count: 3.3M |

This matters because full-text search does not index the author field. It indexes message text. Claude therefore provides a concrete example of why author-field counts and message-field counts should never be treated as interchangeable.

The original note also documented a verification example using commit `34bffdae` in `johannhartmann/stencilify`. That commit used:

```text
Author: Claude <noreply@anthropic.com>
Committer: Claude <noreply@anthropic.com>
```

It had no `Co-authored-by:` trailer and no verified bot signature, which placed it in the CLI author set rather than the app-bot set or the message-text set.

## 7. Email Provenance and Evidence Chain

### 7.1 Bot Noreply Email Format

The original note anchored bot-email derivation in GitHub's email-address reference. GitHub documents the noreply pattern as:

> If you created your account after July 18, 2017, your `noreply` email address is an ID number and your username in the form of `ID+USERNAME@users.noreply.github.com`.

The same structural pattern is used for GitHub App bot accounts. Once a bot login and numeric ID are known, the corresponding bot noreply email can be derived as:

`ID + "+" + Login + "@users.noreply.github.com"`

### 7.2 Bot Identity Verification

The original note described two main API verification patterns:

```text
GET https://api.github.com/user/{id}
```

This works well for newer bots such as Copilot, Claude, Codex, and Cursor.

```text
GET https://api.github.com/users/{login}%5Bbot%5D
```

This works for older or bracketed bot logins such as Devin and Gemini Code Assist.

Once a bot identity is verified through the GitHub API, the derived noreply email can be checked through `author-email:` search. A non-zero and coherent commit result strengthens confidence that the identity is operationally meaningful.

### 7.3 Co-Author Email Provenance

Co-author emails are not assigned by GitHub in the same way as bot noreply emails. The original note treated them as tool-level or workflow-level values that are written into commit-message trailers.

| Agent or mode | When the value is written | Email or string |
|---------------|---------------------------|-----------------|
| Claude Code CLI | Trailer added during commit creation | `noreply@anthropic.com` |
| Cursor editor agent | Used as trailer or, in some cases, as author | `cursoragent@cursor.com` |
| Cursor background agent | Used directly as author email | `agent@cursor.com` |
| Copilot | Platform-generated co-author-style metadata | `copilot@users.noreply.github.com` |
| Codex CLI | Used as author email or trailer | `codex@openai.com` |
| Codex trailer variant | Observed and validated in trailer form | `noreply@openai.com` |
| Gemini Code Assist | Observed as trailer-level email | `gemini-code-assist@google.com` |
| Gemini CLI | Observed author-side but not cleanly attributable | `gemini@google.com` |

This provenance distinction matters because bot noreply emails are structurally grounded in GitHub account metadata, whereas trailer emails are workflow artifacts and therefore need stronger contextual validation.

## 8. Methodological Limitations

The original note listed several limitations that remain important.

1. Large GitHub Search result sets can be approximate. When the result volume becomes large, browser-visible counts and API-returned counts may diverge, and API responses may carry `incomplete_results: true`.
2. Full-text searches can overcount because they match any commit-message occurrence of the string, not only `Co-authored-by:` trailers. For example, `"devin-ai-integration[bot]"` may also match PR descriptions or other message references.
3. Bot noreply emails are GitHub-assigned and therefore highly trustworthy, but custom author emails such as `cursoragent@cursor.com` are, in principle, spoofable through local git configuration.
4. All counts are time-sensitive snapshots. Longitudinal comparisons must record the collection date explicitly.
5. Several identity attributions remained uncertain even after the audit:
   - `noreply@openai.com` was resolved and accepted as a Codex co-author trailer address.
   - `codex@example.com` remained unresolved.
   - `gemini@google.com` was marked as source-mixed rather than cleanly attributable to Gemini CLI activity.
   - `"Co-authored-by: Codex"` and `"Co-authored-by: gemini"` were treated as broad name-level searches that may include non-target uses.

## 9. Reference Resources

The original note cited the following resources as the main verification base:

1. GitHub Email Addresses Reference  
   [https://docs.github.com/en/account-and-profile/reference/email-addresses-reference](https://docs.github.com/en/account-and-profile/reference/email-addresses-reference)

2. `powerset-co/github-coding-agent-tracker`  
   [https://github.com/powerset-co/github-coding-agent-tracker](https://github.com/powerset-co/github-coding-agent-tracker)

3. GitHub REST API user lookup  
   `https://api.github.com/user/{ID}`  
   `https://api.github.com/users/{login}`

4. GitHub REST API contributors endpoint  
   `https://api.github.com/repos/{owner}/{repo}/contributors`

5. GitHub commit search  
   `https://github.com/search?q=...&type=commits`

6. Repository-level verification example  
   The original note used `github/gh-aw` as a contributor-level example where Copilot, Claude bot, and Codex bot could be confirmed at repository scope.

## 10. Use in This Repository

This document is included because identity selection is part of the measurement problem, not a separate side issue. The main report in `report/agent-commit-data-quality.qmd` studies the reliability of sampled commit-count series. This supplement explains why those series can also be biased before any sampling noise appears: the search design itself may point to the wrong identity channel.

For that reason, this note should be read as methodological support for the main report, especially when interpreting low-count agents, comparing author-mode and co-author-mode activity, or revising future collection scripts.
