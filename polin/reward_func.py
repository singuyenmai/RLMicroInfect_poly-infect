import numpy as np

def minED(action, sSol, tSol, **kwargs):
    
    Din = action[0]
    init_E = sSol[0, 0]
    E = sSol[-1, 0]
    
    w_E = kwargs["w_E"]
    Din_max = kwargs["Din_max"]
    w_D = kwargs["w_D"]

    reward = w_E * (1.0 - E/init_E) - w_D * Din / Din_max

    done = True if E == init_E else False # this is to enforce the QLearning controller to 
                                          # presribe drug from the beginning of simulation &
                                          # also implying treatment failure if E goes back to initial density

    return reward, done