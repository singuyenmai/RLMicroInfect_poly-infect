Why tiny density = $10^{-4}$, but not $10^{-5}$ when E is considered to be eliminated: because looking at the simulation when $MIC_Z = 100$, for most positive interactions, the system appeared to already reached (cyclic) stable state but E could never reach $10^{-5}$ (note that once it reaches it, density E will be converted to zero and the controller will stop "taking" drug).

Cost of drug usage: 

- assumed linear relationship between drug concentration selected and penalty. 
- penalized for each "drug prescription" --> also related to the amount of time drug conc. stay high (?)

**Community changes the effect of treatment on pathogen population dynamics**

- **---> changes selection pressure**
- **---> impacts evolution**

**Drug here is modelled in a very general manner. Can be any agent that has bacterialcidal effects, e.g. bacteriocins, phages.**

Assumptions:

- effect on interactions only on population growth
- interaction strengths are not affected by drug
- no impact of bacteria on the killing effects of drug are cr
- ---> Results tell that growth interactions alone can change drug effects on the targeted population, in a linear effect: (+) interactions --> worse for treatment; (-) interactions --> better for treatment.

$\alpha_{EZ}$ negative & $Z$ is more sensitive

- example case: Z is a beneficial commensal that restrict pathogen E. If Z is more sensitive to the drug, then when the drug conc. is below the MIC of E, then E would be able to grow better.
- Compared to when there is no interaction, long-term outcome is similar, but the population dynamics are different.

**Possible structural identifiability in the system:**

- **Tweaking the MIC of E when in mono-culture / co-culture with no interactions could give similar results as when Z is more resistant and $\alpha_{EZ}$ varies. --> Effects of interactions could make the targeted population appeared to have different MICs.**

**Compared to the Hansen's problem:**

- **Difference/Contrast: No drug-resistant of targeted pathogen. Even Z could be more resistant, it's density is not of concern. --> The goal is to eliminate as fast as possible. --> Could be useful to avoid long time and sufficient populaiton density for mutant emergence?**
- **Yet, similarity: no evolution processes taken into account. --> Difficult to say about the impact on evolution.**

Q-learning dit not perform very well

- It is sensitive to initial conditions: strength when Z is more resistant, but weakness when Z has same MIC as E. (When Z has same MIC as E, changing microbial interactions did not affect the fixed rational drug policy, but it did affected the Q-learning)
- Reward function: no significant increase from a very tiny E to elimination of E
- Agent did not account much for long-term return --> Change discount factor?
- Add Z to observable state, but larger state space --> more training, more time required
- Multiple policies with similar return when there is no interactions
- More training episodes might also help (Neythen)

Maxium total supplied drug:

- Rational (testing with 96h): $D_{in}=100.0$ all the times, 1440 $\mu$g. Max return (always get 1.0 for E density and 0 drug penalty): $96/6 = 16.0$
- Q-learning (testing with 96h): $D_{in}=120.0$ all the times, 1728 $\mu$g. Max return (always get 1.0 for E density and 0 drug penalty): $96/6 = 16.0$
- Q-learning (training with 120h): $D_{in}=120.0$ all the times, 2160 $\mu$g. Max return (always get 1.0 for E density and 0 drug penalty): $120/6 = 20.0$

#### Useful scripts

```bash
JOB_SCRIPT="/home/singuyen/Study/SCB/1.MSc_projects/Second_project/polyInfect/run_experiment.py"

cd QLearning_stateE/qlearning_micZ140

python $JOB_SCRIPT -f qlearning_micZ140.2/params.qlearning_micZ140.2.json --test_only
```
