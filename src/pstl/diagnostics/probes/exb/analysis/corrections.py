import numpy as np
import numpy.typing as npt

from pstl.utls.helpers import ideal_gas_law_pressure_to_density

class Xenon():
    def __init__(
            self, 
            E:int | float, n: int | float, z: int | float, js:npt.ArrayLike, *args, 
            Tgas: int | float = 300, pressure: bool = False,
            **kwargs):
        """
        This class solves for correction factors and the curent densities at thruster exit plane using
        E: energy of ions in eV
        n: background neutral density in m^-3 (current version assumes uniform constant density) if pressure is True, then it is assumed n to be given as pressure in Torr
        z: is disntance downstream of thruster exit plane in m
        js: is an arraylike of current densities of single, double, [triple] given in arbitry units
        Attributes:
        dictionaries start with keys of 1 till 3 for single, doubles, triples respectivley.
        js: dict of current densities provided at distance z downstream
        j0s: dict of corrected current densities at thruster exit plane
        cfs: dict of correction factors 

        Reference source:
        Rohit Shastry, Richard R. Hofer, Bryan M. Reid, Alec D. Gallimore; Method for analyzing ExB probe spectra from Hall thruster plumes. Rev. Sci. Instrum. 1 June 2009; 80 (6): 063502. https://doi.org/10.1063/1.3152218
        """
        self.z = z
        if pressure is True:
            n = ideal_gas_law_pressure_to_density(n,T_gas=Tgas)
            self.n = n
        elif pressure is False:
            self.n = n
        self.E = E

        self.js = self._organize_js(js)
        self.sigmas = self.calc_sigmas(E)
        self.cfs = self.calc_correction_factors(n, z)
        self.j0s = self.correct_current_densitites(self.js)


    def _organize_js(self,js):
        js_new = {}
        if isinstance(js, dict):
            for species, j in js.items():
                js_new[species] = j
        else:
            for k, j in enumerate(js):
                species = k+1
                js_new[species] = j
        return js_new

    def calc_sigmas(self,E):
        sigmas = {}
        sigmas[1] = self.calc_sigma1(E)
        sigmas[2] = self.calc_sigma2(E)
        sigmas[3] = self.calc_sigma3()
        sigmas[4] = self.calc_sigma4(E)
        sigmas[5] = self.calc_sigma5(E)
        return sigmas

    def calc_sigma1(self, E):
        # Where E is beam ion energy in eV
        return (87.3-13.6*np.log10(E))*1e-20
    def calc_sigma2(self, E):
        # Where E is beam ion energy in eV
        return (45.7-8.9*np.log10(E))*1e-20
    def calc_sigma3(self):
        return 2*1e-20
    def calc_sigma4(self, E):
        # Where E is beam ion energy in eV
        return self.calc_sigma1(E)
    def calc_sigma5(self, E):
        # Where E is beam ion energy in eV
        return (16.9-3*np.log10(E))*1e-20
        
    def calc_j1_j10(self,n,z):
        # n: density
        # E: Beam ion energy in eV
        # z: distance in meters from thruster plane to probe
        nz = np.multiply(n,z)
        term1 = np.multiply(-nz, self.sigmas[1])
        j1_j10 = np.exp(term1)
        return j1_j10
    def calc_j2_j20(self,n,z): # make this a regular func that does not need n,z
        # n: density
        # E: Beam ion energy in eV
        # z: distance in meters from thruster plane to probe
        nz = np.multiply(n,z)
        term1 = np.multiply(-nz, np.add(self.sigmas[2],self.sigmas[3]))
        j2_j20 = np.exp(term1)
        return j2_j20
    def calc_j3_j20(self,n,z): # make this a regular func that does not need n,z
        # n: density
        # E: Beam ion energy in eV
        # z: distance in meters from thruster plane to probe
        nz = np.multiply(n,z)
        term1 = np.exp(np.multiply(-nz,self.sigmas[4]))
        term2 = np.exp(np.multiply(-nz,np.add(self.sigmas[2],self.sigmas[3])))
        numerator = np.subtract(term1,term2)
        denominator = np.sum([self.sigmas[2],self.sigmas[3],-self.sigmas[4]])
        j3_j20 = np.multiply(
            self.sigmas[3]/2,
            np.divide(numerator,denominator)
        )
        return j3_j20
    
    def calc_correction_factors(self, n, z):
        cf = {}
        cf[1] = self.calc_correction_factor_for_singles(n, z)
        cf[2] = self.calc_correction_factor_for_doubles(n, z)
        cf[3] = self.calc_correction_factor_for_triples(n, z)
        return cf
    
    def calc_correction_factor_for_singles(self, n, z):
        cf = self.calc_j1_j10(n,z)
        return cf
    def calc_correction_factor_for_doubles(self, n, z):
        term1 = self.calc_j2_j20(n,z)
        term2 = self.calc_j3_j20(n,z)
        cf = np.add(term1, term2)
        return cf
    def calc_correction_factor_for_triples(self, n, z):
        nz = np.multiply(n,z)
        cf = np.exp(np.multiply(-nz,self.sigmas[5]))
        return cf
    
    def correct_current_densitites(self, js):
        j0s = {}
        if isinstance(js, dict):
            for species, j in js.items():
                j0s[species] = np.divide(j,self.cfs[species])
        else:
            for k, j in enumerate(js):
                species = k+1
                j0s[species] = np.divide(j,self.cfs[species])
        return j0s
