import numpy as np
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
# 2. PARÁMETROS (LIMPIOS: Solo físicos aquí)
# =====================================================================
Lx, Ly = 2, 3  # <-- EL FIX FÍSICO: Ly=3 garantiza 4 sectores topológicos
model_params_base = {
    'Lx': Lx, 'Ly': Ly,
    'bc_MPS': 'infinite', 'bc_y': 'periodic',
    'conserve': 'None'
}

# =====================================================================
# 3. INICIALIZACIÓN
# =====================================================================
print("--- Preparando Modelo y MPS ---")
model_params_pert = dict(model_params_base, hx=0.2, hz=0.2)
M_pert = PerturbedToricCode(model_params_pert)

# El dtype va en la creación del MPS, no en el modelo
sites = M_pert.lat.mps_sites()
psi = MPS.from_product_state(sites, ["up"] * len(sites), bc='infinite', dtype=np.float32)

print(f"MPS L: {psi.L}. H_MPO L: {M_pert.H_MPO.L}")

# =====================================================================
# 4. FASE 1: Relajación con Perturbación
# =====================================================================
print("\n--- FASE 1: Relajación con Perturbación ---")
dmrg_params_1 = {
    'mixer': True,
    'mixer_params': {'amplitude': 1e-4, 'decay': 2.0},
    # LA LEY DE TENPY 1.1.0: chi_max y eps VAN DENTRO DE trunc_params
    'trunc_params': {
        'chi_max': 8, 
        'eps': 1e-8
    },
    'max_sweeps': 15,
    'verbose': 0 # Quitado el verbose=1 para que el output sea limpio
}
eng1 = dmrg.TwoSiteDMRGEngine(psi, M_pert, dmrg_params_1)
E1, psi = eng1.run()
print(f"Energía perturbada: {E1:.6f}")

# =====================================================================
# 5. FASE 2: PROYECCIÓN TOPOLÓGICA PURA
# =====================================================================
print("\n--- FASE 2: Proyección al TC puro ---")
M_pure = ToricCode(model_params_base)

dmrg_params_2 = {
    'mixer': False,  # <-- SIN MIXER en la proyección
    'trunc_params': {
        'chi_max': 4, # <-- EL FIX DE PROYECCIÓN: Forzar el subespacio d=4
        'eps': 1e-12
    },
    'max_sweeps': 3,  
    'verbose': 0
}
eng2 = dmrg.TwoSiteDMRGEngine(psi, M_pure, dmrg_params_2)
E_pure, psi_final = eng2.run()
print(f"Energía pura: {E_pure:.6f}")
print(f"Bond dimension final: {psi_final.chi}")

# =====================================================================
# 6. FASE 3: Extracción del Espectro
# =====================================================================
print("\n--- FASE 3: Extracción del Espectro ---")
chi_actual = psi_final.chi[0]

if chi_actual == 4:
    # El estado ya debería estar en 0.5 por la proyección, pero forzamos por seguridad
    psi_final._S[0] = np.full(chi_actual, 1.0 / np.sqrt(chi_actual))
    print("Valores singulares en el subespacio topológico.")
else:
    print(f"Advertencia: Se esperaba chi=4, se obtuvo chi={chi_actual}.")

lambdas = psi_final._S[0]
epsilon_spectrum = -np.log(lambdas)

print("\nEspectro de entrelazamiento (-ln(lambda)):")
for eps_val in epsilon_spectrum:
    print(f"  {eps_val:.6f}  (Esperado: {np.log(2):.6f})")
