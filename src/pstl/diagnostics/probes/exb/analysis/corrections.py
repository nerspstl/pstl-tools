import numpy as np

class Xenon():
    def __init__(self,E):
        # Where E is beam ion energy in eV
        self.sigmas = []
        self.calc_sigmas(E)

    def calc_sigmas(self,E):
        self.sigmas[0] = self.calc_sigma1(E)
        self.sigmas[1] = self.calc_sigma2(E)
        self.sigmas[2] = self.calc_sigma3()
        self.sigmas[3] = self.calc_sigma4(E)
        self.sigmas[4] = self.calc_sigma5(E)

    def calc_sigma1(self, E):
        # Where E is beam ion energy in eV
        return 87.3-13.6*np.log(E)
    def calc_sigma2(self, E):
        # Where E is beam ion energy in eV
        return 45.7-8.9*np.log(E)
    def calc_sigma3(self):
        return 2
    def calc_sigma4(self, E):
        # Where E is beam ion energy in eV
        return self.calc_sigma1(E)
    def calc_sigma5(self, E):
        # Where E is beam ion energy in eV
        return 16.9-3*np.log(E)
        
    def calc_j1(self,n,z):
        # n: density
        # E: Beam ion energy in eV
        # z: distance in meters from thruster plane to probe
        return np.exp(
            np.multiply(
            np.multiply(
            -n,
            self.sigmas[0]),
            z
            ))
    def calc_j2(self,n,z): # make this a regular func that does not need n,z
        # n: density
        # E: Beam ion energy in eV
        # z: distance in meters from thruster plane to probe
        return np.exp(np.multiply(np.multiply(-n,self.sigmas[0]),z))