import numpy as np

def minED(action, sSol, tSol, **kwargs):
    
    Din = action[0]
    init_E = sSol[0, 0]
    E = sSol[-1, 0]
    
    w_E = kwargs["w_E"]
    Din_max = kwargs["Din_max"]
    w_D = kwargs["w_D"]

    reward = w_E * (1.0 - E/init_E) - w_D * Din / Din_max

    done=False

    return reward, done