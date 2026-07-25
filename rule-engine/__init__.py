"""PayVerify AI - Deterministic Rule Engine (Malaysia).

Every calculator module in this package implements one payroll statutory
component and returns a `rule_engine.base.RuleResult`. No module in this
package may call an LLM or depend on network access - see project principle
"AI is only used for explanation, never runtime calculation".
"""
