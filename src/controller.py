from typing import List, Dict, Tuple
import numpy as np
import math

class RationalAgent():
    '''
    Rational drug policy: Drug in at a constant concentration & frequency, whenever the targeted density (state) > 0.0
    '''
    def __init__(self, Din = 100.0, drug_time = 60.0*3):
        self.type_name = "Rational"
        self.Din = Din
        self.drug_time = drug_time
    
    def get_action(self, state: float) -> Tuple:
        '''
        Returns action based on observed state
        Parameters:
            state (float): the most recent (continuous) density of the targeted species 
        Returns:
            action (tuple): action chosen by the controller, 
                            in the form of (Din (float): "flow in" drug concentration, drug_time (float): time for "flow in" of drug)
        '''
        if state > 0.0:
            action = (self.Din, self.drug_time)
        else:
            action = (0.0, self.drug_time)

        return action