# Fragility Policy Epistemic Rationale

## 1. The Variance of Survival
Traditional strategy optimizations focus on the *mean* or *median* trade. Fragility Policy focuses on the **tails**.
A trading system dies in the tails (Liquidity Crisis, Flash Crash, Correlation Break).
Therefore, logic handling these states must be separate from, and superior to, the core strategy logic.

## 2. "Conditions for Existence" vs "Conditions for Profit"
*   **Decision Policy**: "Can we make money?"
*   **Fragility Policy**: "Can we survive?"
Survival is the prerequisite for profit. Therefore, Fragility is a **subtracting filter**.

## 3. Why Subtractive Only?
If the Fragility Layer could *add* permissions (e.g., "Panic Buy the Crash"), it would become a Strategy.
To maintain **Cognitive Clarify**, we enforce separation:
*   Strategies Generate Intent.
*   Fragility Removes Dangerous Intents.
*   Fragility **Never** Generates Intent.

## 4. The Visibility of Fear
We explicitly visualize stress states on the dashboard.
If the system is not trading because of "Liquidity Stress", the operator must see exactly that.
Hiding this logic inside a "Score < 0.5" black box creates mistrust.
"Systemic Stress: VIX > 40" is a transparent, honest reason to sit on cash.
