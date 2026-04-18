import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# =====================================================================
# CONFIGURACIÓN DE ESTILO PHYSICAL REVIEW (PRB / PRL)
# =====================================================================
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times', 'Times New Roman', 'DejaVu Serif'],
    'font.size': 10,
    'axes.linewidth': 1.2,        # Bordes de los ejes gruesos
    'lines.linewidth': 1.5,       # Líneas de los gráficos gruesas
    'xtick.major.width': 1.2,
    'ytick.major.width': 1.2,
    'xtick.direction': 'in',      # Ticks hacia adentro
    'ytick.direction': 'in',
    'xtick.top': True,            # Ticks en los bordes superior y derecho
    'ytick.right': True,
    'axes.labelsize': 11,
    'legend.frameon': False,      # Leyendas sin caja
    'figure.dpi': 300             # Alta resolución
})

# =====================================================================
# FIGURA 1: ESQUEMA DE CORTE TOPOLOGICO 2D (Ly=3)
# =====================================================================
fig1, ax1 = plt.subplots(1, 1, figsize=(4, 3.5))

# Dibujar la red (Líneas grises claras)
for i in range(4):
    ax1.plot([i, i], [0, 3], color='lightgray', zorder=1)
    ax1.plot([0, 3], [i, i], color='lightgray', zorder=1)

# Dibujar el corte de entrelazamiento (Línea roja punteada)
ax1.axvline(x=1.5, color='crimson', linestyle='--', linewidth=2, label='Entanglement Cut', zorder=2)

# Resaltar los 3 enlaces que cruza el corte (Círculos azules)
# En un Toric Code los enlaces están en medio de las líneas de la red.
intersections_y = [0.5, 1.5, 2.5]
for y in intersections_y:
    circle = plt.Circle((1.5, y), 0.15, color='royalblue', ec='black', linewidth=1.2, zorder=3)
    ax1.add_patch(circle)

# Anotaciones
ax1.annotate(r'$L_y = 3$', xy=(3.2, 1.5), fontsize=12, va='center')
ax1.text(1.8, 2.8, r'$N_{cut} = 3$', fontsize=11, color='crimson', weight='bold')

# Caja de texto con la fórmula topológica
textstr = r'$d = 2^{N_{cut}-1} = 4$' '\n' r'Sectors: $\{1, e, m, \epsilon\}$'
props = dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor='black', alpha=0.9)
ax1.text(0.2, 2.8, textstr, fontsize=10, verticalalignment='top', bbox=props)

ax1.set_xlim(-0.5, 4)
ax1.set_ylim(-0.5, 3.5)
ax1.set_aspect('equal')
ax1.axis('off') # Sin ejes para un diagrama esquemático

fig1.tight_layout()
fig1.savefig('fig1_topology_cut.pdf', format='pdf', bbox_inches='tight')
plt.close()
print("Figura 1 guardada: fig1_topology_cut.pdf")

# =====================================================================
# FIGURA 2: ESPECTRO DE ENTRELAZAMIENTO 2D (Degeneración 4-fold)
# =====================================================================
fig2, ax2 = plt.subplots(1, 1, figsize=(3.5, 3))

# Datos exactos obtenidos del script
sectores = [r'$1$', r'$e$', r'$m$', r'$\epsilon$']
epsilon = [np.log(2)] * 4

# Gráfico de barras
bars = ax2.bar(sectores, epsilon, width=0.5, color='royalblue', edgecolor='black', linewidth=1.2)

# Línea de referencia teórica
ax2.axhline(y=np.log(2), color='crimson', linestyle='--', linewidth=1.5, label=r'$\ln(2)$ (Theory)')

# Formateo
ax2.set_ylabel(r'$\epsilon_i = -\ln(\lambda_i)$', fontsize=12)
ax2.set_ylim(0, 1.0)
ax2.set_yticks([0, 0.25, 0.5, 0.693, 1.0])
ax2.set_yticklabels(['0', '0.25', '0.50', r'$\ln(2)$', '1.0'])
ax2.legend(loc='upper right', fontsize=10)

fig2.tight_layout()
fig2.savefig('fig2_entanglement_spectrum.pdf', format='pdf', bbox_inches='tight')
plt.close()
print("Figura 2 guardada: fig2_entanglement_spectrum.pdf")

# =====================================================================
# FIGURA 3: EL MURO DE LA LEY DE ÁREA 3D (Chi Saturado)
# =====================================================================
fig3, ax3 = plt.subplots(1, 1, figsize=(3.5, 3))

# Datos teóricos vs Simulados
labels = ['Simulated\n($\\chi_{max}$ limit)', 'Theoretical Min.\n($\\chi_{req}$)']
chi_values = [15, 81]
colors = ['royalblue', 'gray']

bars = ax3.bar(labels, chi_values, width=0.5, color=colors, edgecolor='black', linewidth=1.2, alpha=0.8)

# Línea que indica el límite de hardware
ax3.axhline(y=15, color='crimson', linestyle='-.', linewidth=1.5, label='Hardware Limit (12GB RAM)')

# Anotación del colapso
ax3.annotate('OOM\nCrash', xy=(1, 81), xytext=(1.2, 60),
            fontsize=10, weight='bold', color='crimson',
            arrowprops=dict(facecolor='crimson', shrink=0.05, width=1.5, headwidth=8))

# Formateo
ax3.set_ylabel(r'Bond Dimension ($\chi$)', fontsize=12)
ax3.set_ylim(0, 100)
ax3.legend(loc='upper left', fontsize=9)

# Fórmula en la esquina
ax3.text(0.95, 0.95, r'$\chi_{req} >= q^{L_y L_z} = 3^4 = 81$',
         transform=ax3.transAxes, fontsize=9,
         verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='white', edgecolor='black', alpha=0.9))

fig3.tight_layout()
fig3.savefig('fig3_area_law_wall.pdf', format='pdf', bbox_inches='tight')
plt.close()
print("Figura 3 guardada: fig3_area_law_wall.pdf")