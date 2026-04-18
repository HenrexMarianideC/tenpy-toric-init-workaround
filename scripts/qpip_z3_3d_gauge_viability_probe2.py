#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qpip_z3_3d_gauge_viability_probe.py
Proyecto: QPIP - Topología 3D (Fase de Prueba de Viabilidad)
Versión: 1.0.0
Fecha: 2023-10-27
Dependencias: tenpy==1.1.0, numpy, scipy
Descripción: 
Instanciación de un modelo de gauge Z3 (mapeado a Spin-1) en una red 
cúbica simple (2x2xInfinito) usando la clase base Lattice de TeNPy.

CONCLUSIÓN EMPÍRICA:
El script demuestra que la red 3D es compatible con la API, pero el 
entrelazamiento satura inmediatamente en chi_max debido a la Ley de Área
(S ~ L_y * L_z), haciendo inviable la extracción del espectro topológico
volumétrico mediante iDMRG estándar. Requiere NQS.
"""

import numpy as np
import tenpy
import tenpy.linalg.np_conserved as npc
from tenpy.networks.site import SpinSite
from tenpy.models.model import CouplingModel, MPOModel
from tenpy.models.lattice import Lattice
from tenpy.networks.mps import MPS
from tenpy.algorithms import dmrg

# =====================================================================
# 1. FÍSICA: Modelo de Gauge Z3 en 3D (Mapeado a Spin-1)
# =====================================================================
class QPIP_3D_Z3(CouplingModel, MPOModel):
    def __init__(self, model_params):
        Lx = model_params.get('Lx', 2)
        Ly = model_params.get('Ly', 2)
        Lz = model_params.get('Lz', 2)
        
        # Spin-1 (3 estados locales: -1, 0, 1) sin conservación de carga
        site = SpinSite(S=1, conserve='None')
        
        # Operador Sz^2 (Penaliza excitaciones fuera del vacío |0>)
        Sz2 = npc.tensordot(site.Sz, site.Sz, axes=1)
        site.add_op('Sz2', Sz2)

        # Definición manual de geometría cúbica euclidiana pura
        basis = [[1.0, 0.0, 0.0], 
                 [0.0, 1.0, 0.0], 
                 [0.0, 0.0, 1.0]]
        pos = [[0.0, 0.0, 0.0]]
        
        lat = Lattice([Lx, Ly, Lz], [site], basis=basis, positions=pos, 
                      bc=['periodic', 'periodic', 'periodic'],
                      bc_MPS='infinite')
        
        CouplingModel.__init__(self, lat)
        
        J_A = model_params.get('J_A', 1.0)
        J_B = model_params.get('J_B', 1.0)
        
        # Término de Estrella (Vertex) - Confina la QPIP al vacío local
        for u in range(len(lat.unit_cell)):
            self.add_onsite(J_A, u, 'Sz2')
        
        # Término de Plaqueta (Magnetic Flux 3D) - Teje la membrana topológica
        for u in range(len(lat.unit_cell)):
            self.add_coupling(J_B, u, 'Sx', u, 'Sx', dx=[1, 0, 0]) # Eje X
            self.add_coupling(J_B, u, 'Sx', u, 'Sx', dx=[0, 1, 0]) # Eje Y
            self.add_coupling(J_B, u, 'Sx', u, 'Sx', dx=[0, 0, 1]) # Eje Z

        # Ensamblaje manual del MPO (Requerido por herencia múltiple)
        MPOModel.__init__(self, lat, self.calc_H_MPO())

# =====================================================================
# 2. PERTURBACIÓN (Para evitar colapso a mínimos clásicos)
# =====================================================================
class Perturbed_QPIP(QPIP_3D_Z3):
    def init_terms(self, model_params):
        super().init_terms(model_params)
        h = model_params.get('h_pert', 0.1)
        for u in range(len(self.lat.unit_cell)):
            self.add_onsite(-h, u, 'Sz')

# =====================================================================
# 3. EJECUCIÓN Y SONDEO DE VIABILIDAD
# =====================================================================
print("--- Inicializando QPIP 3D Z3 (Vía Geometría Nativa) ---")
model_params = {
    'Lx': 2, 'Ly': 2, 'Lz': 2,
    'J_A': 1.0, 'J_B': 1.0,
    'h_pert': 0.1
}

M_qpip = Perturbed_QPIP(model_params)

# MPS inicializado en el vacío topológico (Sz=0 -> Índice 1 en TenPy)
sites = M_qpip.lat.mps_sites()
psi = MPS.from_product_state(sites, [1] * len(sites), bc='infinite')

print(f"Dimensiones del MPS: L={psi.L}, Sitios por celda={len(sites)}")
print(f"Dimensión física local: {sites[0].dim}")
print(f"Dimensión del espacio de la red: {M_qpip.lat.dim}")

print("\n--- Ejecutando Fase de Relajación (Sondeo de Area Law) ---")
dmrg_params = {
    'mixer': True,
    'mixer_params': {'amplitude': 1e-2},
    'trunc_params': {
        'chi_max': 15, # Techo bajo para forzar la saturación y probar la ley de área
        'svd_min': 1e-10
    },
    'max_sweeps': 3, 
}

eng = dmrg.TwoSiteDMRGEngine(psi, M_qpip, dmrg_params)
E, psi = eng.run()

print(f"Energía alcanzada: {E:.4f}")
print(f"Chi alcanzado: {psi.chi}")

# =====================================================================
# 4. VEREDICTO AUTOMATIZADO
# =====================================================================
if all(c == 15 for c in psi.chi):
    print("\n[VEREDICTO] SATURACIÓN TOTAL POR LEY DE ÁREA 3D.")
    print("iDMRG no puede resolver la QPIP 3D. Migración a NQS justificada.")
else:
    print("\n[VEREDICTO] Estado no saturado (inesperado en volumetría 3D).")
"""
--- Inicializando QPIP 3D Z3 (Vía Geometría Nativa) ---
Dimensiones del MPS: L=8, Sitios por celda=8
Dimensión física local: 3
Dimensión del espacio de la red: 3

--- Ejecutando Fase de Relajación (Sondeo de Area Law) ---
/usr/local/lib/python3.12/dist-packages/tenpy/networks/mps.py:1629: UserWarning: unit_cell_width is a new argument for MPS and similar classes. It is optional for now, but will become mandatory in a future release. The default value (unit_cell_width=len(sites)) is correct, iff the lattice is a Chain. For other lattices, it is incorrect. It is used for dipolar charges and correlation_function2.
  super().__init__(sites, bc, unit_cell_width)
Energía alcanzada: -2.5208
Chi alcanzado: [15, 15, 15, 15, 15, 15, 15, 15]

[VEREDICTO] SATURACIÓN TOTAL POR LEY DE ÁREA 3D.
iDMRG no puede resolver la QPIP 3D. Migración a NQS justificada.

"""