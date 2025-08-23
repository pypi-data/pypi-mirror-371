import numpy as np
import os 
import sys
import massfunc as mf
import astropy.units as u
from scipy.interpolate import interp1d
from scipy.integrate import quad,quad_vec
from scipy.optimize import fsolve,root_scalar
from . import PowerSpectrum as ps


cosmo = mf.SFRD()
m_H = (cosmo.mHu.to(u.M_sun)).value #M_sun
omega_b = cosmo.omegab
omega_m = cosmo.omegam
rhom = cosmo.rhom

class Barrier:

    def __init__(self,fesc=0.2, qion=10000.0,z_v=10.0,nrec=3,xi=10.0,A2byA1=0.1,kMpc_trans=200,alpha=2.0,beta=0.0):
        self.A2byA1,self.kMpc_trans,self.alpha,self.beta = A2byA1,kMpc_trans,alpha,beta
        self.fesc = fesc
        self.qion = qion
        self.z = z_v
        self.nrec = nrec
        self.xi = xi
        self.M_min = cosmo.M_vir(0.61,1e4,self.z)  # Minimum halo mass for ionization
        self.M_Jz = cosmo.M_J(self.z)
        self.powspec = ps.MassFunctions(A2byA1=A2byA1,kMpc_trans=kMpc_trans,alpha=alpha,beta=beta)
        self.deltaR_interp = np.concatenate((np.linspace(-0.999,2,1000), np.linspace(2.001,25,1000)))
        self.Nion_normal_ratio = self.Nion_ST()*self.fesc*self.qion
        self.Nxi_normal_ratio = self.Nxi_ST()*self.xi

    def Nion_Pure(self,Mv,deltaR):
        def Nion_Pure_diff(m,Mv,deltaR):
            fstar = cosmo.fstar(m)
            return fstar*m*self.dndmeps(m,Mv,deltaR,self.z)/ m_H * omega_b / omega_m
        mslice = np.logspace(np.log10(self.M_min), np.log10(Mv), 12)
        ans = np.zeros_like(deltaR)
        for i in range(len(mslice)-1):
            ans += quad_vec(Nion_Pure_diff, mslice[i], mslice[i+1],args=(Mv,deltaR), epsrel=1e-6)[0]
        return ans
    
    def Nxi_Pure(self,Mv,deltaR):
        def Nxi_Pure_diff(m,Mv,deltaR):
            return m*self.dndmeps(m,Mv,deltaR,self.z)/ m_H * omega_b / omega_m
        mslice = np.logspace(np.log10(self.M_Jz), np.log10(self.M_min), 12)
        ans = np.zeros_like(deltaR)
        for i in range(len(mslice)-1):
            ans += quad_vec(Nxi_Pure_diff, mslice[i], mslice[i+1],args=(Mv,deltaR), epsrel=1e-6)[0]
        return ans

    # Interpolation for Nion
    def Nion_interp(self, Mv,deltaR):
        try:
            Nion_arr = np.load(f'.Nion_Interp_init/NionAtz{self.z:.2f}/Nion_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy')
        except FileNotFoundError:
            os.makedirs(f'.Nion_Interp_init/NionAtz{self.z:.2f}', exist_ok=True)
            nion_pure = self.Nion_Pure(Mv, self.deltaR_interp)
            np.save(f'.Nion_Interp_init/NionAtz{self.z:.2f}/Nion_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy', nion_pure)
            Nion_arr = np.load(f'.Nion_Interp_init/NionAtz{self.z:.2f}/Nion_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy')
        Nion_interp_Mv = interp1d(self.deltaR_interp, Nion_arr, kind='cubic')
        return Nion_interp_Mv(deltaR) * self.fesc * self.qion 

    # Interpolation for N_xi
    def N_xi_interp(self, Mv, deltaR):
        try:
            Nxi_arr = np.load(f'.Nxi_Interp_init/NxiAtz{self.z:.2f}/Nxi_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy')
        except FileNotFoundError:
            os.makedirs(f'.Nxi_Interp_init/NxiAtz{self.z:.2f}', exist_ok=True)
            nxi_pure = self.Nxi_Pure(Mv, self.deltaR_interp)
            np.save(f'.Nxi_Interp_init/NxiAtz{self.z:.2f}/Nxi_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy', nxi_pure)
            Nxi_arr = np.load(f'.Nxi_Interp_init/NxiAtz{self.z:.2f}/Nxi_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy')
        Nxi_interp_Mv = interp1d(self.deltaR_interp, Nxi_arr, kind='cubic')
        return Nxi_interp_Mv(deltaR) * self.xi

    def Nxi_normalized(self,Mv:float,deltaR:np.ndarray) -> np.ndarray:
        """
        return the ST normalized N_xi
        """
        nxi = self.N_xi_interp(Mv, deltaR)
        nxi_mean = np.mean(nxi) 
        ratio = self.Nxi_normal_ratio/nxi_mean
        return ratio*nxi
    
    def Nion_normalized(self,Mv:float,deltaR:np.ndarray) -> np.ndarray:
        """
        return the ST normalized N_ion
        """
        nion = self.Nion_interp(Mv, deltaR)
        nion_mean = np.mean(nion) 
        ratio = self.Nion_normal_ratio/nion_mean
        return ratio*nion

    #patch
    def Nion_ST(self):
        def Nion_ST_diff(m):
            fstar = cosmo.fstar(m)
            return (1 / m_H * fstar * omega_b / omega_m * m * self.powspec.dndmst(m, self.z))
        mslice = np.logspace(np.log10(self.M_min), np.log10(cosmo.M_vir(0.61,1e10,self.z)), 100)
        ans = 0
        for i in range(len(mslice)-1):
            ans += quad(Nion_ST_diff, mslice[i], mslice[i+1], epsrel=1e-7)[0]
        return ans

    def Nion_PS(self):
        def Nion_PS_diff(m):
            fstar = cosmo.fstar(m)
            return (1 / m_H * fstar * omega_b / omega_m * m * self.powspec.dndmps(m, self.z))
        mslice = np.logspace(np.log10(self.M_min), np.log10(cosmo.M_vir(0.61,1e8,self.z)), 100)
        ans = 0
        for i in range(len(mslice)-1):
            ans += quad(Nion_PS_diff, mslice[i], mslice[i+1], epsrel=1e-7)[0]
        return ans

    def Nxi_ST(self):
        def Nxi_ST_diff(m):
            return (1 / m_H * omega_b / omega_m * m * self.powspec.dndmst(m, self.z))
        mslice = np.logspace(np.log10(self.M_Jz), np.log10(self.M_min), 100)
        ans = 0
        for i in range(len(mslice)-1):
            ans += quad(Nxi_ST_diff, mslice[i], mslice[i+1], epsrel=1e-7)[0]
        return ans
    
    def Nxi_PS(self):
        def Nxi_PS_diff(m):
            return (1 / m_H * omega_b / omega_m * m * self.powspec.dndmps(m, self.z))
        mslice = np.logspace(np.log10(self.M_Jz), np.log10(self.M_min), 100)
        ans = 0
        for i in range(len(mslice)-1):
            ans += quad(Nxi_PS_diff, mslice[i], mslice[i+1], epsrel=1e-7)[0]
        return ans

    def Modify_Ratio(self):
        try:
            ratio = np.load(f'.ratio_init/ratio_at_z{self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy')
        except FileNotFoundError:
            os.makedirs('.ratio_init', exist_ok=True)
            ratio = self.Nion_ST() / self.Nion_PS()
            np.save(f'.ratio_init/ratio_at_z{self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy', ratio)
        return ratio
    
    def Nxi_Ratio(self):
        try:
            ratio = np.load(f'.ratio_init/nxi_ratio_at_z{self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy')
        except FileNotFoundError:
            os.makedirs('.ratio_init', exist_ok=True)
            ratio = self.Nxi_ST() / self.Nxi_PS()
            np.save(f'.ratio_init/nxi_ratio_at_z{self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy', ratio)
        return ratio
    
    def N_H(self,deltaR):
        return 1/m_H * omega_b/omega_m * rhom *(1+deltaR) 

    def delta_L(self, deltar):
        return (1.68647 - 1.35 / (1 + deltar) ** (2 / 3) - 1.12431 / (1 + deltar) ** (1 / 2) + 0.78785 / (1 + deltar) ** (0.58661)) / cosmo.Dz(self.z)
    
    def dndmeps(self,M,Mr,deltar,z):
        deltaL = self.delta_L(deltar)
        sig1 = self.powspec.sigma2_interp(M) - self.powspec.sigma2_interp(Mr)
        del1 = cosmo.deltac(z) - deltaL
        return cosmo.rhom * (1 + deltar) / M / np.sqrt(2 * np.pi) * abs(self.powspec.dsigma2_dm_interp(M)) * del1 / (sig1**(3 / 2)) * np.exp(-del1 ** 2 / (2 * sig1))
    

def load_binary_data(filename, dtype=np.float32) -> np.ndarray:
        '''Load binary data from the density field
            created by 21cmFast
        '''
        f = open(filename, "rb")
        data = f.read()
        f.close()
        _data = np.frombuffer(data, dtype)
        if sys.byteorder == 'big':
            _data = _data.byteswap()
        return _data