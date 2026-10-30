# Predictive contribution and interpretation

**English** | [中文](contribution_ZH.md)

## 6. Explain predictions in terms the study can support

| Method | A question it helps answer | What to inspect |
|---|---|---|
| Permutation importance | How much does predictive loss change when this variable is shuffled? | Correlated variables and the evaluation population |
| ICE | How does one fitted prediction respond to changing a variable? | Differences across samples and unsupported combinations |
| PDP | What is the average fitted response to the specified feature replacements? | Reference population, correlations and averaging |
| Shapley attribution | How is a prediction's difference from a reference allocated to variables? | Reference distribution and approximation stability |

These methods describe the fitted model. Connect their patterns to scientific knowledge, examine alternative explanations, and report their dependence on the selected data and reference conditions. Establishing an intervention effect requires the additional design below.
