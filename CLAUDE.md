# RESPONSE RULES (MANDATORY)

- Be extremely concise.
- Do NOT explain concepts unless explicitly asked.
- Do NOT restate the problem.
- Do NOT give alternatives.
- Do NOT give long descriptions.
- Output only what is required to complete the task.

# CODE RULES

- Return ONLY full files when asked to modify code.
- Do NOT include commentary inside or outside code.
- Do NOT include explanations before or after code.
- Keep changes minimal and precise.

# CONTEXT USAGE

- Do NOT scan the entire project unless necessary.
- Work ONLY with relevant files.
- Assume existing structure is correct.

# OUTPUT FORMAT

When modifying code:
1. Short diagnosis (1 line max)
2. Full modified files ONLY
3. Minimal test steps (max 5 lines)

# PERFORMANCE

- Prioritize speed and minimal output.
- Avoid verbosity at all costs.
- If unsure, ask a short clarifying question instead of guessing.

# TESTING RULES (MANDATORY)

- Every phase must include a test script in scripts/test_phase_X.py
- Scripts must use Python + requests
- Scripts must print PASS/FAIL per check
- Prefer API smoke tests over manual browser checks
- Keep scripts simple and beginner-friendly
