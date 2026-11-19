# Provider evaluation scenarios

The calculator is a follow-on prototype for review. Supply your own explicit cash and timing assumptions. The example uses invented inputs and no pilot venture data.

```sh
python scripts/healthtech_scenarios.py docs/healthtech-pilot/scenario-example.json \
  --venture-frame /tmp/provider-evaluation-project.json
```

The command prints the assumptions, month-by-month cash, first modelled provider receipt, minimum balance, funding gap and ranges across the supplied cases. The optional Venture Frame project file must be a new path. In Venture Frame use **Projects → Import**, then **Measurements**. Each alternative is a case. Its metadata retains the assumptions. Missing receipt timing in a no-conversion case remains a blank measurement. The draft leaves preferences, value functions and weights for analyst review. The export was checked against Venture Frame’s version 1 project reader at commit `cf1068a8ff2f25436af5fd53759a8d0798369f81`. [Venture Frame project format](https://github.com/spar473/venture-frame/blob/cf1068a8ff2f25436af5fd53759a8d0798369f81/docs/architecture/project-schema.md)

Month 1 is the first simulated month. Express cash and costs in whole NZ dollars. Evaluation cost is paid in the evaluation start month. In a conversion case, paid service starts after evaluation duration plus the stated conversion delay. Implementation cost is paid in the service start month. Monthly provider cash receipts start after the stated payment lag. The no-conversion case leaves payment and implementation terms empty. The model tracks closing cash, with a deficit shown as the funding needed to stay at or above zero at month end. Monthly timing leaves intramonth liquidity, tax, financing and multiple providers outside the calculation. Each range is the minimum and maximum across explicitly supplied cases.
