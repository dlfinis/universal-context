# 🏗️ Universal Context Architect

### *Because AI is only as smart as the context you give it.*

## 📌 The Pitch

You're a system engineer/vibe coder. You know the drill: You're halfway through a complex refactor or a deep dive into an AI-generated nightmare, and you need a Chat of any LLM to help. But copying and pasting 40 files manually is a soul-crushing task that leads to **"Context Drift."**

**Universal Context** is a surgical tool designed to crawl your project, ignore the junk (looking at you, `node_modules`), respect your `.gitignore` laws, and package your entire logic into a single, beautifully structured Markdown file.

**It’s not just a file merger; it’s a token-optimized context injector.**

---

## 🛠️ Engineered Features

* **🗜️ Compact Folder Logic:** Tired of clicking through `src/main/java/com/org/project/app/service`? We flatten empty nested directories into a single line (`src/main/.../service`), giving you a clean, IDE-like explorer.
* **🧠 Smart Cleaning:** Includes a multi-stage "Wash Cycle":
* **Full:** The raw truth.
* **Light:** Removes comments (standard dev noise).
* **Smart:** Strips imports, packages, and logs. Your AI doesn't need to see 50 `import` statements to understand your logic.


* **🤖 Target Awareness:** Specially tuned for Java/Spring environments. It pierces through the `.gitignore` to let you select those elusive `target/generated-sources` files that define your API.
* **🗄️ Categorized Grouping:** It doesn't just dump code. It groups it logically:
* *Generated/OpenAPI* first.
* *Models & Data* structures.
* *API Layers* vs *Business Logic*.


* **💾 Persistent Memory:** Uses a local `.context_config.json` to remember your last directory. Because re-typing paths is for interns.
* **🧮 Token Estimation:** A real-time gauge to tell you if your prompt is a "Light Snack" (under 8k tokens) or a "System Meltdown" (over 100k tokens).

---

```markdown
## 🚀 Getting Started

This project is optimized for [**uv**](https://github.com/astral-sh/uv), the modern, blazingly fast Python package manager. It ensures deterministic builds, sub-second dependency resolution, and seamless environment management.

### 1. Prerequisites

First, ensure you have `uv` installed on your system. It’s a single binary and doesn't require a pre-existing Python installation to get started.

**macOS/Linux:**
```bash
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh

```

**Windows:**

```powershell
powershell -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"

```

### 2. Installation & Setup

Clone the repository and synchronize the environment. `uv` will automatically detect the required Python version, create a virtual environment (`.venv`), and install all dependencies defined in the `uv.lock` file.

```bash
git clone repo
cd universal-context
```

# Synchronize the environment (Deterministic and FAST)
```bash
uv sync

```

### 3. Execution

You can run the application directly using the `uv run` command. This ensures the script execution is wrapped within the managed virtual environment.

**Standard Streamlit Execution:**

```bash
uv run streamlit run universal_context.py
```

---

## 🛠️ Engineering Standards

As a system-engineer-focused tool, we adhere to high operational standards:

* **Dependency Groups:** We use the modern `[dependency-groups]` standard for development tools. To install including dev tools (like `ruff` for linting), use:
```bash
uv sync --group dev

```

---

## 📐 The "System Engineer" Disclaimer

This tool assumes you know where your code lives. It uses `pathspec` for gitwildmatch patterns, meaning it behaves like your terminal. If you tell it to ignore `*.java`, don't be surprised when your Java files disappear.

### ☕ The Java/OpenAPI Special

We know that in the enterprise world, the most important code is often hidden in a `target` folder. We’ve hardcoded a "whitelist" bypass for `target/generated-sources`. We’ve got your back.

---

## 🎮 Special Detail: The "Coffee-to-Context" Ratio

As an engineer, I’ve noticed a direct correlation between the amount of coffee consumed and the depth of the folder structure.

> **Current Project Depth Alert:** > If your path is more than 8 levels deep (e.g., `com/org/service/impl/util/handler/internal/etc`), the app will automatically apply a **"Mental Load Protection"** (Compact Folders) to prevent your brain from leaking out of your ears.

---

## 🤝 Contribution

If you find a bug or want to add an icon for an even more obscure file extension (looking at you, `.fortran`), feel free to tweak the `ContextEngine`.

**Stay caffeinated. Keep your context focused.** 🚀

---