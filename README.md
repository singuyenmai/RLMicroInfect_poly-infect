# Adaptive control of  polymicrobial infectious communities with reinforcement learning

In the context of polymicrobial urinary tract infections (UTIs),

- How do ecological interactions between microbes impact the effectiveness of a drug policy?
- If there is an impact, then how do we adapt our drug policy to various ecological contexts? and Can the reinforcement learning approach enable adaptive drug control?

# Implementation

Parameters from (de Vos *et al.*, 2017): directory `params_deVos2017`

Qualitative analyses on 2-species model without drug - different regimes of species abundance for varying inter-species interaction strengths

```bash
cd qualitative_analysis
python qualitative_analyses.py # (or run Jupyter Notebook `qualitative_analyses.ipynb`)
```

Rational drug policy on different ecological contexts

```bash
cd Rational
bash main.sh
```

Q-learning on different ecological contexts

```bash
cd QLearning_stateE
bash main.sh
```

## References

**de Vos MGJ**, **Zagorski M**, **McNally A**, **Bollenbach T**. Interaction networks, ecological stability, and collective antibiotic tolerance in polymicrobial infections. *Proc Natl Acad Sci*. 2017;114: 10666–10671. doi:10.1073/PNAS.1713372114

http://www.antimicrobe.org/h04c.files/history/PK-PD%20Quint.asp

https://www.medicines.org.uk/emc/product/5752/smpc#gref

https://go.drugbank.com/drugs/DB00440