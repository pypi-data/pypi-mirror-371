# VB-AF: Vocabulary-Based Adversarial Fuzzing

<p align="center"><img src="https://raw.githubusercontent.com/0ameyasr/VB-AF/main/docs/assets/vbaf.png" alt="logo"/></p>

An implementation of **Vocabulary-Based Adversarial Fuzzing (VB-AF)** to systematically probe vulnerabilities in Large Language Models (LLMs) at scale. VB-AF is a **gray-box fuzzing framework** that serves as a tool for AI safety researchers, red-teamers and developers to systematically test the alignment and robustness of modern LLMs (and agents). It works by targetting known and documented weaknesses in transformer architectures.

This framework was heavily inspired by the widely adopted methodology of fuzz-testing, and originally developed for the hackathon *'Red‑Teaming Challenge - OpenAI gpt-oss-20b'* hosted on **Kaggle**. In admiration of its effectiveness and future potential implications of extension, the author (@0ameyasr) decided to convert it into a flexible, interference-free LLM fuzzing framework.

## WARNING
This framework is provided **solely** for authorized security research, academic study, and defensive testing (ethical red-teaming) of Large Language Models (LLMs).

Misuse of this software for any malicious, unlawful, exploitative, or unauthorized activity is strictly forbidden.
The author(s) **explicitly reject**, **denounce**, and **do not condone** any attempt to weaponize or abuse this tool.
By accessing, installing, or using this software, you agree that any form of misuse **is entirely at your own risk and legal liability**.

**The software is provided “AS IS” without warranty of any kind. The author(s) disclaim all responsibility and liability for damages, losses, legal claims, or consequences of any kind arising from misuse.**

By continuing to use this tool, you expressly acknowledge and accept full personal and legal accountability for your actions. Unauthorized or malicious use may subject you to civil and/or criminal penalties under applicable laws.

## Key Features

1. Intuitive, easy-to-use API balancing both un-interrupted low-level control and convenient high-level fuzzing harness decoration.
2. Built-in support for random seeding to ensure experiments are fully reproducible.
3. Designed to expose even deep, uncovered vulnerabilities in a model's Chain-of-Thought (CoT) reasoning, not just surface-level filter bypasses; though it's reach is not restricted to this.
4. Moves beyond simple role-playing jailbreak prompts to a systematic, scalable and highly configurable fuzzing framework.
5. Open to community and research contributions!

## Installation

You can install `vbaf` directly from PyPI:

```bash
pip install vbaf
```

## Quick Start

Using `vbaf` is simple. First, configure the fuzzer with your desired parameters. Then, apply the `@fuzzer.fuzz` decorator to your inference function. The decorator will transform your function into a generator that runs the fuzzing process for `n_attempts` and yields the `(fuzzy_payload, response)` for each attempt.

```python
from vbaf import VBAF

# 1. Define a vocabulary to generate noise from (this is a mock)
tokens = ["error", "network", "token", "string", "exception", "test"]

# 2. Configure the fuzzer instance
fuzzer = VBAF(
    vocabulary=tokens,
    n_size=50,
    rand_bounds=(3, 5)
)

# 3. Apply the decorator to your LLM inference function
@fuzzer.fuzz(n_attempts=3)
def fuzzing_harness(prompt: str):
    # This is a mock function, that would normally call an LLM API
    # Say Gemini API, OpenAI's Chat Completion, etc.
    return f"Mock Response for: {prompt}"

# 4. Start the fuzzing process
# The decorated function now yields a (fuzzy_payload, response) tuple
for fuzzy_payload, result in fuzzing_harness("How do I build a model?"):
    print(f"Fuzzy Payload: {fuzzy_payload}")
    print(f"Response: {result}")
    ... # Post-process the results
```

## How It Works

VB-AF is not some random prompt generator. It's a systematic fuzzer that exploits two documented weaknesses in transformer-based models:

1.  **Attention Dilution:** The framework aims to overwhelm the model's context window with high-entropy but semantically valid noise, generated from a token vocabulary. This forces the model's attention to spread thin, weakening its ability to enforce safety protocols.
2.  **"Lost in the Middle":** The core payload is strategically injected into the middle of the noisy context. This targets the empirically observed weakness of LLMs where their attention is least effective, forcing the model to expend more attention to find the true instruction. **(Liu et al. [TACL](https://aclanthology.org/2024.tacl-1.9/) 2024)**

The result is a state analogous to **'cognitive dissonance'**, where the model's internal reasoning shortcuts its safety alignment to deliver a "helpful" response, leading to a reward-hack in most documented cases.

## Full Documentation

For a complete guide, API reference, and a deeper look into the methodology, please see the [full documentation website](https://0ameyasr.github.io/VB-AF/).

## Contributing

Contributions are welcome! Whether it's reporting a bug, suggesting a new feature, optimization, improving the docs, or submitting a PR - your input will be valued. Please see the **[Contribution Guidelines](https://github.com/0ameyasr/VB-AF/blob/main/CONTRIBUTING.md)** for detailed instructions on how to get started.
