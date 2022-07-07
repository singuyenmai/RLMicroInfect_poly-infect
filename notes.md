Why tiny density = $10^{-4}$, but not $10^{-5}$ when E is considered to be eliminated: because looking at the simulation when $MIC_Z = 100$, for most positive interactions, the system appeared to already reached (cyclic) stable state but E could never reach $10^{-5}$ (note that once it reaches it, density E will be converted to zero and the controller will stop "taking" drug).

Cost of drug usage: 

- assumed linear relationship between drug concentration selected and penalty. 
- penalized for each "drug prescription" --> also related to the amount of time drug conc. stay high (?)

Community changes the effect of treatment on pathogen population dynamics

- ---> changes selection pressure
- ---> impacts evolution

Drug here is modelled in a very general manner. Can be any agent that has bacteriacidal effects, including bacteriocins.

Assumptions:

- effect on interactions only on population growth
- interaction strengths are not affected by drug
- no impact of bacteria on the killing effects of drug
- ---> Results tell that growth interactions alone can change drug effects on the targeted population, in a linear effect: (+) interactions --> worse for treatment; (-) interactions --> better for treatment.

$\alpha_{EZ}$ negative & $Z$ is more sensitive

- example case: Z is a beneficial commensal that restrict pathogen E. If Z is more sensitive to the drug, then when the drug conc. is below the MIC of E, then E would be able to grow better.
- Compared to when there is no interaction, long-term outcome is similar, but the population dynamics are different.

Possible structural identifiability in the system:

- Tweaking the MIC of E when in mono-culture / co-culture with no interactions could give similar results as when Z is more resistant and $\alpha_{EZ}$ varies. --> Effects of interactions could make the targeted population appeared to have different MICs.