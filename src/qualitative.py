import numpy as np
from typing import List, Dict, Tuple
import json
import sys

class Quali():

    def __init__(self, param_file):
        with open(param_file) as f:
            param_dict = json.load(f)
        
        self.set_params(param_dict)
    
    def set_params(self, param_dict: Dict) -> None:
        self.rE = param_dict['rE']
        self.cE = param_dict['cE']
        self.rZ = param_dict['rZ']
        self.cZ = param_dict['cZ']

        self.n_alphas = param_dict['n_alphas']

        self.growth_bound = param_dict['growth_bound']

    def ODEsys(self, x, alphas):
        E, Z = x
        alpha_EZ, alpha_ZE = alphas

        dEdt = E * (self.rE - self.rE/self.cE * E + alpha_EZ * Z)
        dZdt = Z * (self.rZ - self.rZ/self.cZ * Z + alpha_ZE * E)

        return [dEdt, dZdt]

    def analyze_across_alphas(self, out_filename: str) -> Dict:
        
        result = dict()

        outfile = out_filename + ".tsv"
        with open(outfile, 'w') as f:
            f.write(f'alpha_EZ\talpha_ZE\teqE\teqZ\teqEZ')

        alphas_EZ, crit_EZ = self.alphas_arr(which="EZ", n=self.n_alphas)
        alphas_ZE, crit_ZE = self.alphas_arr(which="ZE", n=self.n_alphas)

        for a1 in alphas_EZ:
            for a2 in alphas_ZE:
                
                alphas = (a1, a2)

                if (a1 == crit_EZ) & (a2 == crit_ZE):
                    continue # skip bifurcation point
                else:
                    result[alphas] = self.sys_bio_stability(alphas)

                    with open(outfile, 'a') as f:
                        f.write(f'\n{alphas[0]}\t{alphas[1]}\t{result[alphas][0]}\t{result[alphas][1]}\t{result[alphas][2]}')
        
        return result
    
    def alphas_arr(self, which: str, n: int) -> [np.ndarray, float]:
        
        if which == "EZ":
            crit_point = - self.rE / self.cZ
        elif which == "ZE":
            crit_point = - self.rZ / self. cE
        
        quarter = int(n*0.25)
        
        alpha_neg1 = np.linspace(crit_point, 0.0, n - quarter*2)
        
        step_size = alpha_neg1[1] - alpha_neg1[0]

        alpha_neg2 = np.arange(0, quarter)*(-step_size) + (crit_point - step_size)
        alpha_pos = np.arange(0, quarter)*step_size + step_size

        alphas_arr = np.append(alpha_neg2, alpha_neg1)
        alphas_arr = np.append(alphas_arr, alpha_pos)

        return [alphas_arr, crit_point]
    
    def sys_bio_stability(self, alphas: Tuple) -> List[str]:
        
        eql = self.equilibria(alphas)
        eqE, eqZ, eqEZ = eql
        eqE_sta, eqZ_sta, eqEZ_sta = [self.stability(x, alphas) for x in eql]
        
        eqEZ_bounded = True if 0.0 < np.round(eqEZ[0], 5) <= self.growth_bound and 0.0 < np.round(eqEZ[1], 5) <= self.growth_bound else False

        if eqEZ_bounded or eqEZ_sta == "unstable":
            return [eqE_sta, eqZ_sta, eqEZ_sta]
        else:
            return [eqE_sta, eqZ_sta, "unbounded"]
    
    def equilibria(self, alphas: Tuple) -> List[np.ndarray]:
        alpha_EZ, alpha_ZE = alphas
        
        eqE = np.array([self.cE, 0.0])
        eqZ = np.array([0.0, self.cZ])

        eqEZ = np.array([(self.cE * self.rE * self.rZ + self.cE * self.cZ * self.rZ * alpha_EZ) / (self.rE * self.rZ - self.cE * self.cZ * alpha_EZ * alpha_ZE),
                        (self.cZ * self.rE * self.rZ + self.cE * self.cZ * self.rE * alpha_ZE) / (self.rE * self.rZ - self.cE * self.cZ * alpha_EZ * alpha_ZE)])

        return [eqE, eqZ, eqEZ]

    def stability(self, eq: np.ndarray, alphas: Tuple) -> str:
        
        E = eq[0]
        Z = eq[1]

        alpha_EZ, alpha_ZE = alphas

        jacob = np.array([[self.rE - (2 * E * self.rE / self.cE) + Z * alpha_EZ, E * alpha_EZ], 
                        [Z * alpha_ZE, self.rZ - (2 * Z * self.rZ / self.cZ) + E * alpha_ZE]])
        
        eigen = np.linalg.eigvals(jacob)
        # print(f'Eigenvalues: {eigen}')

        s = "stable"

        if np.iscomplex(eigen[0]):
            if eigen[0].real == 0.0:
                s = "centre"
            elif eigen[0].real > 0.0:
                s = "unstable"
        else:
            if np.round(eigen[0], 10) > 0.0 or np.round(eigen[1], 10) > 0.0:
                s = "unstable"
        
        return s

if __name__ == '__main__':
    param_file = sys.argv[1]
    Q = Quali(param_file)
    Q_result = Q.analyze_across_alphas(out_filename="qualitative_results")