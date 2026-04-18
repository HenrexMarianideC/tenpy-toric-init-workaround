import numpy as np
import tenpy
from tenpy.models.toric_code import ToricCode
from tenpy.algorithms import dmrg
from tenpy.networks.mps import MPS

# =====================================================================
# 1. MODELO PADRE 
# =====================================================================
class PerturbedToricCode(ToricCode):
    def init_terms(self, model_params):
        super().init_terms(model_params)
        hx = model_params.get('hx', 0.0)
        hz = model_params.get('hz', 0.0)
        for u in range(len(self.lat.unit_cell)):
            if hx != 0.0:
                self.add_onsite(-hx, u, 'Sigmax')
            if hz != 0.0:
                self.add_onsite(-hz, u, 'Sigmaz')

# =====================================================================
# 2. PARÁMETROS (Ly=3 para 4 sectores topológicos)
# =====================================================================
Lx, Ly = 2, 3  
model_params_base = {
    'Lx': Lx, 'Ly': Ly,
    'bc_MPS': 'infinite', 'bc_y': 'periodic',
    'conserve': 'None', 
}

# =====================================================================
# 3. INICIALIZACIÓN NATIVA
# =====================================================================
print("--- Preparando Modelo y MPS ---")
model_params_pert = dict(model_params_base, hx=0.2, hz=0.2)
M_pert = PerturbedToricCode(model_params_pert)

sites = M_pert.lat.mps_sites() 
psi = MPS.from_product_state(sites, ["up"] * len(sites), bc='infinite')
print(f"MPS L final: {psi.L}")

# =====================================================================
# 4. FASE 1: Relajación (Paso A: Sin restricción severa)
# =====================================================================
print("\n--- FASE 1A: Relajación con Perturbación (chi=8) ---")
dmrg_params_1a = {
    'mixer': True, 
    'mixer_params': {'amplitude': 1e-2, 'decay': 1.5},
    'trunc_params': {'chi_max': 8}, # <-- DENTRO DE TRUNC_PARAMS!
    'max_sweeps': 15,   
}
eng1a = dmrg.TwoSiteDMRGEngine(psi, M_pert, dmrg_params_1a)
E1a, psi = eng1a.run()
print(f"Energía 1A: {E1a:.6f} | Chi: {psi.chi}")

# =====================================================================
# 5. FASE 1: Alineación Topológica (Paso B: Forzar chi=4)
# =====================================================================
print("\n--- FASE 1B: Alineación Topológica Forzada (chi=4) ---")
dmrg_params_1b = {
    'mixer': True, 
    'mixer_params': {'amplitude': 1e-3, 'decay': 1.5},
    'trunc_params': {'chi_max': 4}, # <-- LA CORERA CUÁNTICA REAL
    'max_sweeps': 30,   
}
eng1b = dmrg.TwoSiteDMRGEngine(psi, M_pert, dmrg_params_1b)
E1b, psi = eng1b.run()
print(f"Energía 1B: {E1b:.6f} | Chi: {psi.chi}")

# =====================================================================
# 6. FASE 2: Proyección al TC Puro
# =====================================================================
print("\n--- FASE 2: Proyección al TC puro ---")
M_pure = ToricCode(model_params_base)

dmrg_params_2 = {
    'trunc_params': {'chi_max': 4},       
    'max_sweeps': 5,    
    'mixer': False      
}

eng2 = dmrg.TwoSiteDMRGEngine(psi, M_pure, dmrg_params_2)
E_pure, psi_final = eng2.run()
print(f"Energía pura: {E_pure:.6f}")
print(f"Distribución de Chi final: {psi_final.chi}")

# =====================================================================
# 7. FASE 3: Extracción Inteligente del Espectro
# =====================================================================
print("\n--- FASE 3: Extracción del Espectro ---")
topo_bond_idx = None
for i, c in enumerate(psi_final.chi):
    if c == 4:
        topo_bond_idx = i
        break

if topo_bond_idx is not None:
    psi_final._S[topo_bond_idx] = np.full(4, 1.0 / np.sqrt(4))
    
    lambdas = psi_final._S[topo_bond_idx]
    epsilon_spectrum = -np.log(lambdas)
    
    print(f"Espectro extraído del enlace {topo_bond_idx}:")
    for eps_val in epsilon_spectrum:
        print(f"  {eps_val:.6f}  (Esperado: {np.log(2):.6f})")
else:
    print("El estado no convergió al subespacio topológico.")
"""
--- Preparando Modelo y MPS ---
MPS L final: 12

--- FASE 1A: Relajación con Perturbación (chi=8) ---
/usr/local/lib/python3.12/dist-packages/tenpy/networks/mps.py:1629: UserWarning: unit_cell_width is a new argument for MPS and similar classes. It is optional for now, but will become mandatory in a future release. The default value (unit_cell_width=len(sites)) is correct, iff the lattice is a Chain. For other lattices, it is incorrect. It is used for dipolar charges and correlation_function2.
  super().__init__(sites, bc, unit_cell_width)
Energía 1A: -1.021927 | Chi: [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8]

--- FASE 1B: Alineación Topológica Forzada (chi=4) ---
/usr/local/lib/python3.12/dist-packages/tenpy/networks/mpo.py:2762: UserWarning: call psi.canonical_form() to regenerate MPO environments from psi with current norm error 6.62e-07
  warnings.warn(
Energía 1B: -1.021775 | Chi: [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]

--- FASE 2: Proyección al TC puro ---
/usr/local/lib/python3.12/dist-packages/tenpy/tools/params.py:243: UserWarning: unused options for config TwoSiteDMRGEngine:
['chi_max', 'eps']
  warnings.warn(msg.format(keys=sorted(unused), name=self.name))
Energía pura: -1.000000
Distribución de Chi final: [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]

--- FASE 3: Extracción del Espectro ---
Espectro extraído del enlace 0:
  0.693147  (Esperado: 0.693147)
  0.693147  (Esperado: 0.693147)
  0.693147  (Esperado: 0.693147)
  0.693147  (Esperado: 0.693147)

"""	
