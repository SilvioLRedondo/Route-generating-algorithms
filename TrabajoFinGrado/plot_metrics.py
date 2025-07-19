# plot_metrics.py
"""
Visualiza todas las métricas devueltas por simulate_robots_continuous.

Uso básico desde main.py (después de la simulación):
    import plot_metrics as pm
    pm.visualizar_metricas(metrics, dt=tsam)     # ← tsam es el paso empleado

Parámetros importantes
----------------------
metrics  : dict      # diccionario devuelto por la simulación
dt       : float     # mismo paso de integración usado en simulate_robots_continuous
save_dir : str | None  Carpeta donde guardar los PNG. None => sólo mostrar
show     : bool        Mostrar los gráficos en pantalla (True por defecto)
"""

from __future__ import annotations
import os
import math
import matplotlib.pyplot as plt


def _bar(ax, data: dict[str, float], title: str, xlabel: str, ylabel: str):
    etiquetas = list(data.keys())
    valores = list(data.values())
    ax.bar(etiquetas, valores)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xticklabels(etiquetas, rotation=45, ha="right")


def _save(fig: plt.Figure, name: str, save_dir: str | None):
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        fig.savefig(os.path.join(save_dir, f"{name}.png"), bbox_inches="tight")



def visualizar_metricas(metrics: dict, *, tsim, dt: float, save_dir: str | None = None, show: bool = True):
    # --- Configuración general de estilo
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.titlesize': 16,
        'axes.labelsize': 14,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 12,
        'figure.dpi': 100,
        'font.family': 'sans-serif',
        'axes.titlepad': 14,
        'axes.labelpad': 8,
        'lines.linewidth': 2,
        'lines.markersize': 7,
    })

    figsize_general = (14, 9)
    color_general = "tab:blue"

    # Función auxiliar para guardar
    def _save(fig, name, save_dir):
        if save_dir:
            fig.tight_layout()
            fig.savefig(f"{save_dir}/{name}.png", bbox_inches="tight", dpi=150)

    # Función auxiliar de barras mejorada (etiquetas capitalizadas)
    def _bar(ax, data, title, xlabel, ylabel, color=color_general):
        labels = [str(label).capitalize() for label in data.keys()]
        values = list(data.values())
        bars = ax.bar(labels, values, color=color, edgecolor='black', alpha=0.85)
        ax.set_title(title.capitalize(), pad=15)
        ax.set_xlabel(xlabel.capitalize())
        ax.set_ylabel(ylabel.capitalize())
        ax.grid(axis='y', linestyle='--', linewidth=0.7, alpha=0.6)
        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f'{height:.0f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 5),
                textcoords="offset points",
                ha='center', va='bottom',
                fontsize=12, fontweight='bold'
            )
        plt.setp(ax.get_xticklabels(), rotation=10, ha="right")

    # 1. Serie temporal de ocupación máxima de pasillos
    # pasos = len(metrics["max_corridor_occupancy"])
    # tiempo = [i * dt for i in range(pasos)]
    # fig1, ax1 = plt.subplots(figsize=(10,5))
    # ax1.plot(tiempo, metrics["max_corridor_occupancy"], linewidth=2, color=color_general)
    # ax1.set_title("Ocupación máxima de pasillos (Robots simultáneos)".capitalize())
    # ax1.set_xlabel("Tiempo (s)".capitalize())
    # ax1.set_ylabel("N° de robots".capitalize())
    # ax1.set_xlim(0, tsim)
    # ax1.grid(axis="y", linestyle="--", linewidth=0.8, alpha=0.7)
    # for spine in ['top', 'right']:
    #     ax1.spines[spine].set_visible(False)
    # _save(fig1, "01_pasillos_tiempo", save_dir)
    # if show:
    #     plt.show()
    # else:
    #     plt.close(fig1)

    # 2. Barras: tiempo medio por ACTIVIDAD del robot
    fig3, ax3 = plt.subplots(figsize=figsize_general)
    _bar(ax3, metrics["robot_state_time"], "Tiempo por estado del robot", "Actividad", "Segundos acumulados", color=color_general)
    _save(fig3, "03_tiempo_por_actividad", save_dir)
    if show:
        plt.show()
    else:
        plt.close(fig3)

    # 3. Barras: tiempo por NIVEL DE BATERÍA
    fig4, ax4 = plt.subplots(figsize=figsize_general)
    _bar(ax4, metrics["battery_state_time"], "Tiempo por nivel de batería", "Nivel", "Segundos acumulados", color=color_general)
    _save(fig4, "04_tiempo_por_bateria", save_dir)
    if show:
        plt.show()
    else:
        plt.close(fig4)

    # 4. Barras: tiempo por NIVEL DE PRIORIDAD
    # fig5, ax5 = plt.subplots(figsize=figsize_general)
    # _bar(ax5, metrics["priority_state_time"], "Tiempo por nivel de prioridad", "Prioridad", "Segundos acumulados", color=color_general)
    # _save(fig5, "05_tiempo_por_prioridad", save_dir)
    # if show:
    #     plt.show()
    # else:
    #     plt.close(fig5)

    # 5. Serie temporal de bloqueos y recargas (dispersión)
    bloq  = metrics["blockages"]["timestamps"]
    recar = metrics["recharge_usage"]["timestamps"]
    fig6, ax6 = plt.subplots(figsize=figsize_general)
    ax6.eventplot([bloq, recar], colors=['tab:red', 'tab:green'], lineoffsets=[1, 0], linelengths=0.8)
    ax6.set_yticks([0, 1])
    ax6.set_yticklabels(['Recarga'.capitalize(), 'Bloqueo'.capitalize()])
    ax6.set_xlabel('Tiempo (s)'.capitalize())
    ax6.set_title('Línea temporal de bloqueos y recargas'.capitalize(), pad=12)
    for spine in ['top', 'right']:
        ax6.spines[spine].set_visible(False)
    ax6.grid(axis='x', linestyle='--', linewidth=0.6, alpha=0.5)
    _save(fig6, "06_eventos", save_dir)
    if show:
        plt.show()
    else:
        plt.close(fig6)

    # 6. Contadores globales en barra **vertical** (etiquetas capitalizadas)
    contadores = {
        "Paquetes procesados": metrics["total_packets_processed"],
        "Bloqueos": metrics["blockages"]["count"],
        "Recargas": metrics["recharge_usage"]["count"],
        "Recepciones": metrics["reception_events"],
        "Emisiones": metrics["emission_events"],
        "Replanificaciones": metrics["replanifications"],
    }
    fig7, ax7 = plt.subplots(figsize=figsize_general)
    nombres = [nombre.capitalize() for nombre in contadores.keys()]
    valores = list(contadores.values())
    bars = ax7.bar(nombres, valores, color=color_general, alpha=0.85, edgecolor='black')
    ax7.set_title("Resumen de contadores globales".capitalize())
    ax7.set_ylabel("Cantidad".capitalize())
    ax7.set_xlabel("Eventos".capitalize())
    ax7.grid(axis="y", linestyle="--", linewidth=0.7, alpha=0.5)
    for spine in ['top', 'right']:
        ax7.spines[spine].set_visible(False)
    for bar, v in zip(bars, valores):
        ax7.text(
            bar.get_x() + bar.get_width() / 2, v + max(valores)*0.01, str(v),
            ha="center", va="bottom", fontsize=12, fontweight='bold'
        )
    plt.setp(ax7.get_xticklabels(), rotation=15, ha="right")
    _save(fig7, "07_contadores_globales", save_dir)
    if show:
        plt.show()
    else:
        plt.close(fig7)

    # 8. Texto: porcentaje medio de ocupación de pasillos
    # porc = metrics.get("avg_corridor_occupation_pct", 0) * 100
    # print(f"\n\033[1mPorcentaje medio de ocupación de pasillos: {porc:.2f}%\033[0m\n")



def visualizar_metricas3(metrics: dict, *, tsim, dt: float, save_dir: str | None = None, show: bool = True):
    # --- Configuración general de estilo
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.titlesize': 16,
        'axes.labelsize': 14,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 12,
        'figure.dpi': 100,
        'font.family': 'sans-serif',
        'axes.titlepad': 14,
        'axes.labelpad': 8,
        'lines.linewidth': 2,
        'lines.markersize': 7,
    })

    # Función auxiliar para guardar
    def _save(fig, name, save_dir):
        if save_dir:
            fig.tight_layout()
            fig.savefig(f"{save_dir}/{name}.png", bbox_inches="tight", dpi=150)

    # Función auxiliar de barras mejorada (etiquetas capitalizadas)
    def _bar(ax, data, title, xlabel, ylabel, color="tab:blue"):
        labels = [str(label).capitalize() for label in data.keys()]
        values = list(data.values())
        bars = ax.bar(labels, values, color=color, edgecolor='black', alpha=0.85)
        ax.set_title(title, pad=15)
        ax.set_xlabel(xlabel.capitalize())
        ax.set_ylabel(ylabel.capitalize())
        ax.grid(axis='y', linestyle='--', linewidth=0.7, alpha=0.6)
        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f'{height:.0f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 5),
                textcoords="offset points",
                ha='center', va='bottom',
                fontsize=12, fontweight='bold'
            )
        plt.setp(ax.get_xticklabels(), rotation=10, ha="right")

    # 1. Serie temporal de ocupación máxima de pasillos
    pasos = len(metrics["max_corridor_occupancy"])
    tiempo = [i * dt for i in range(pasos)]
    fig1, ax1 = plt.subplots(figsize=(9, 4.5))
    ax1.plot(tiempo, metrics["max_corridor_occupancy"], linewidth=2, color="tab:blue")
    ax1.set_title("Ocupación máxima de pasillos (Robots simultáneos)".capitalize())
    ax1.set_xlabel("Tiempo (s)".capitalize())
    ax1.set_ylabel("N° de robots".capitalize())
    ax1.set_xlim(0, tsim)
    ax1.grid(axis="y", linestyle="--", linewidth=0.8, alpha=0.7)
    for spine in ['top', 'right']:
        ax1.spines[spine].set_visible(False)
    _save(fig1, "01_pasillos_tiempo", save_dir)
    if show:
        plt.show()
    else:
        plt.close(fig1)

    # 2. Barras: tiempo medio por ACTIVIDAD del robot
    fig3, ax3 = plt.subplots(figsize=(7, 4.5))
    _bar(ax3, metrics["robot_state_time"], "Tiempo por estado del robot", "Actividad", "Segundos acumulados", color="tab:orange")
    _save(fig3, "03_tiempo_por_actividad", save_dir)
    if show:
        plt.show()
    else:
        plt.close(fig3)

    # 3. Barras: tiempo por NIVEL DE BATERÍA
    fig4, ax4 = plt.subplots(figsize=(7, 4.5))
    _bar(ax4, metrics["battery_state_time"], "Tiempo por nivel de batería", "Nivel", "Segundos acumulados", color="tab:green")
    _save(fig4, "04_tiempo_por_bateria", save_dir)
    if show:
        plt.show()
    else:
        plt.close(fig4)

    # 4. Barras: tiempo por NIVEL DE PRIORIDAD
    fig5, ax5 = plt.subplots(figsize=(7, 4.5))
    _bar(ax5, metrics["priority_state_time"], "Tiempo por nivel de prioridad", "Prioridad", "Segundos acumulados", color="tab:red")
    _save(fig5, "05_tiempo_por_prioridad", save_dir)
    if show:
        plt.show()
    else:
        plt.close(fig5)

    # 5. Serie temporal de bloqueos y recargas (dispersión)
    bloq  = metrics["blockages"]["timestamps"]
    recar = metrics["recharge_usage"]["timestamps"]
    fig6, ax6 = plt.subplots(figsize=(9, 3.5))
    ax6.eventplot([bloq, recar], colors=['#e74c3c', '#27ae60'], lineoffsets=[1, 0], linelengths=0.8)
    # Etiquetas de eventos capitalizadas
    ax6.set_yticks([0, 1])
    ax6.set_yticklabels(['Recarga', 'Bloqueo'])  # Si quieres puedes hacer ['Recarga'.capitalize(), 'Bloqueo'.capitalize()]
    ax6.set_xlabel('Tiempo (s)'.capitalize())
    ax6.set_title('Línea temporal de bloqueos y recargas'.capitalize(), pad=12)
    for spine in ['top', 'right']:
        ax6.spines[spine].set_visible(False)
    ax6.grid(axis='x', linestyle='--', linewidth=0.6, alpha=0.5)
    _save(fig6, "06_eventos", save_dir)
    if show:
        plt.show()
    else:
        plt.close(fig6)

    # 6. Contadores globales en barra **vertical** (etiquetas capitalizadas)
    contadores = {
        "Paquetes procesados": metrics["total_packets_processed"],
        "Bloqueos": metrics["blockages"]["count"],
        "Recargas": metrics["recharge_usage"]["count"],
        "Recepciones": metrics["reception_events"],
        "Emisiones": metrics["emission_events"],
        "Replanificaciones": metrics["replanifications"],
    }
    fig7, ax7 = plt.subplots(figsize=(8.5, 4.5))
    nombres = [nombre.capitalize() for nombre in contadores.keys()]
    valores = list(contadores.values())
    bars = ax7.bar(nombres, valores, color="tab:purple", alpha=0.85, edgecolor='black')
    ax7.set_title("Resumen de contadores globales".capitalize())
    ax7.set_ylabel("Cantidad".capitalize())
    ax7.set_xlabel("Eventos".capitalize())
    ax7.grid(axis="y", linestyle="--", linewidth=0.7, alpha=0.5)
    for spine in ['top', 'right']:
        ax7.spines[spine].set_visible(False)
    for bar, v in zip(bars, valores):
        ax7.text(
            bar.get_x() + bar.get_width() / 2, v + max(valores)*0.01, str(v),
            ha="center", va="bottom", fontsize=12, fontweight='bold'
        )

    plt.setp(ax7.get_xticklabels(), rotation=15, ha="right")
    _save(fig7, "07_contadores_globales", save_dir)
    if show:
        plt.show()
    else:
        plt.close(fig7)

    # 8. Texto: porcentaje medio de ocupación de pasillos
    porc = metrics.get("avg_corridor_occupation_pct", 0) * 100
    print(f"\n\033[1mPorcentaje medio de ocupación de pasillos: {porc:.2f}%\033[0m\n")


def visualizar_metricas2(metrics: dict, *, tsim, dt: float, save_dir: str | None = None, show: bool = True):
    # --- Configuración general de estilo
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.titlesize': 16,
        'axes.labelsize': 14,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 12,
        'figure.dpi': 100,
        'font.family': 'sans-serif',
        'axes.titlepad': 14,
        'axes.labelpad': 8,
        'lines.linewidth': 2,
        'lines.markersize': 7,
    })

    # Función auxiliar para guardar
    def _save(fig, name, save_dir):
        if save_dir:
            fig.tight_layout()
            fig.savefig(f"{save_dir}/{name}.png", bbox_inches="tight", dpi=150)

    # Función auxiliar de barras mejorada
    def _bar(ax, data, title, xlabel, ylabel, color="tab:blue"):
        labels = list(data.keys())
        values = list(data.values())
        bars = ax.bar(labels, values, color=color, edgecolor='black', alpha=0.85)
        ax.set_title(title, pad=15)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(axis='y', linestyle='--', linewidth=0.7, alpha=0.6)
        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f'{height:.0f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 5),
                textcoords="offset points",
                ha='center', va='bottom',
                fontsize=12, fontweight='bold'
            )
        plt.setp(ax.get_xticklabels(), rotation=10, ha="right")

    # 1. Serie temporal de ocupación máxima de pasillos
    pasos = len(metrics["max_corridor_occupancy"])
    tiempo = [i * dt for i in range(pasos)]
    fig1, ax1 = plt.subplots(figsize=(9, 4.5))
    ax1.plot(tiempo, metrics["max_corridor_occupancy"], linewidth=2, color="tab:blue")
    ax1.set_title("Ocupación máxima de pasillos (Robots simultáneos)")
    ax1.set_xlabel("Tiempo (s)")
    ax1.set_ylabel("N° de Robots")
    ax1.set_xlim(0, tsim)
    ax1.grid(axis="y", linestyle="--", linewidth=0.8, alpha=0.7)
    for spine in ['top', 'right']:
        ax1.spines[spine].set_visible(False)
    _save(fig1, "01_pasillos_tiempo", save_dir)
    if show:
        plt.show()
    else:
        plt.close(fig1)

    # 2. Barras: tiempo medio por ACTIVIDAD del robot
    fig3, ax3 = plt.subplots(figsize=(7, 4.5))
    _bar(ax3, metrics["robot_state_time"], "Tiempo por estado del robot", "Actividad", "Segundos acumulados", color="tab:orange")
    _save(fig3, "03_tiempo_por_actividad", save_dir)
    ax3.set_xlabel("Actividad")
    if show:
        plt.show()
    else:
        plt.close(fig3)

    # 3. Barras: tiempo por NIVEL DE BATERÍA
    fig4, ax4 = plt.subplots(figsize=(7, 4.5))
    _bar(ax4, metrics["battery_state_time"], "Tiempo por nivel de batería", "Nivel", "Segundos acumulados", color="tab:green")
    _save(fig4, "04_tiempo_por_bateria", save_dir)
    if show:
        plt.show()
    else:
        plt.close(fig4)

    # 4. Barras: tiempo por NIVEL DE PRIORIDAD
    fig5, ax5 = plt.subplots(figsize=(7, 4.5))
    _bar(ax5, metrics["priority_state_time"], "Tiempo por nivel de prioridad", "Prioridad", "Segundos acumulados", color="tab:red")
    _save(fig5, "05_tiempo_por_prioridad", save_dir)
    if show:
        plt.show()
    else:
        plt.close(fig5)

    # 5. Serie temporal de bloqueos y recargas (dispersión)
    bloq  = metrics["blockages"]["timestamps"]
    recar = metrics["recharge_usage"]["timestamps"]
    fig6, ax6 = plt.subplots(figsize=(9, 3.5))
    ax6.eventplot([bloq, recar], colors=['#e74c3c', '#27ae60'], lineoffsets=[1, 0], linelengths=0.8)
    ax6.set_yticks([0, 1])
    ax6.set_yticklabels(['Recarga', 'Bloqueo'])
    ax6.set_xlabel('Tiempo (s)')
    ax6.set_title('Línea temporal de bloqueos y recargas', pad=12)
    for spine in ['top', 'right']:
        ax6.spines[spine].set_visible(False)
    ax6.grid(axis='x', linestyle='--', linewidth=0.6, alpha=0.5)
    _save(fig6, "06_eventos", save_dir)
    if show:
        plt.show()
    else:
        plt.close(fig6)

    # 6. Contadores globales en barra **vertical**
    contadores = {
        "Paquetes procesados": metrics["total_packets_processed"],
        "Bloqueos": metrics["blockages"]["count"],
        "Recargas": metrics["recharge_usage"]["count"],
        "Recepciones": metrics["reception_events"],
        "Emisiones": metrics["emission_events"],
        "Replanificaciones": metrics["replanifications"],
    }
    fig7, ax7 = plt.subplots(figsize=(8.5, 4.5))
    nombres = list(contadores.keys())
    valores = list(contadores.values())
    bars = ax7.bar(nombres, valores, color="tab:purple", alpha=0.85, edgecolor='black')

    ax7.set_title("Resumen de contadores globales")
    ax7.set_ylabel("Cantidad")
    ax7.set_xlabel("Eventos")
    ax7.grid(axis="y", linestyle="--", linewidth=0.7, alpha=0.5)
    for spine in ['top', 'right']:
        ax7.spines[spine].set_visible(False)
    for bar, v in zip(bars, valores):
        ax7.text(
            bar.get_x() + bar.get_width() / 2, v + max(valores)*0.01, str(v),
            ha="center", va="bottom", fontsize=12, fontweight='bold'
        )

    plt.setp(ax7.get_xticklabels(), rotation=15, ha="right")  # Un poco de inclinación para más claridad
    _save(fig7, "07_contadores_globales", save_dir)
    if show:
        plt.show()
    else:
        plt.close(fig7)

    # 8. Texto: porcentaje medio de ocupación de pasillos
    # porc = metrics.get("avg_corridor_occupation_pct", 0) * 100
    # print(f"\n\033[1mPorcentaje medio de ocupación de pasillos: {porc:.2f}%\033[0m\n")


def visualizar_metricas1(metrics: dict, *, tsim, dt: float, save_dir: str | None = None, show: bool = True):
    # 1 ───────────────────────────────────────────────
    # Serie temporal de ocupación máxima de pasillos
    pasos = len(metrics["max_corridor_occupancy"])
    tiempo = [i * dt for i in range(pasos)]
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.plot(tiempo, metrics["max_corridor_occupancy"], linewidth=1.5)
    ax1.set_title("Ocupación máxima de pasillos")
    ax1.set_xlabel("Tiempo (s)")
    ax1.set_ylabel("Robots simultáneos")
    ax1.set_xlim(0, tsim)
    _save(fig1, "01_pasillos_tiempo", save_dir)
    if show:
        plt.show()
    else:
        plt.close(fig1)


    # 2 ───────────────────────────────────────────────
    # Barras: tiempo medio por ACTIVIDAD del robot
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    _bar(
        ax3,
        metrics["robot_state_time"],
        "Tiempo por estado del robot",
        "Actividad",
        "Segundos acumulados",
    )
    _save(fig3, "03_tiempo_por_actividad", save_dir)
    if show:
        plt.show()
    else:
        plt.close(fig3)

    # 3 ───────────────────────────────────────────────
    # Barras: tiempo por NIVEL DE BATERÍA
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    _bar(
        ax4,
        metrics["battery_state_time"],
        "Tiempo por nivel de batería",
        "Nivel",
        "Segundos acumulados",
    )
    _save(fig4, "04_tiempo_por_bateria", save_dir)
    if show:
        plt.show()
    else:
        plt.close(fig4)

    # 4 ───────────────────────────────────────────────
    # Barras: tiempo por NIVEL DE PRIORIDAD
    fig5, ax5 = plt.subplots(figsize=(6, 4))
    _bar(
        ax5,
        metrics["priority_state_time"],
        "Tiempo por nivel de prioridad",
        "Prioridad",
        "Segundos acumulados",
    )
    _save(fig5, "05_tiempo_por_prioridad", save_dir)
    if show:
        plt.show()
    else:
        plt.close(fig5)

    # 5 ───────────────────────────────────────────────
    # Serie temporal de bloqueos y recargas (dispersión)
    eventos = []
    etiquetas = []
    bloq  = metrics["blockages"]["timestamps"]
    recar = metrics["recharge_usage"]["timestamps"]

    fig6, ax6 = plt.subplots(figsize=(8, 3))
    ax6.eventplot([bloq, recar],
                colors=['red', 'green'],
                lineoffsets=[1, 0],      # y-levels
                linelengths=0.8)

    ax6.set_yticks([0, 1])
    ax6.set_yticklabels(['Recarga', 'Bloqueo'])
    ax6.set_xlabel('Tiempo (s)')
    ax6.set_title('Línea temporal de bloqueos y recargas')

    # 6 ───────────────────────────────────────────────
    # Contadores globales en barra horizontal
    contadores = {
        "Paquetes procesados": metrics["total_packets_processed"],
        "Bloqueos": metrics["blockages"]["count"],
        "Recargas": metrics["recharge_usage"]["count"],
        "Recepciones": metrics["reception_events"],
        "Emisiones": metrics["emission_events"],
        "Replanificaciones": metrics["replanifications"],
    }
    fig7, ax7 = plt.subplots(figsize=(8, 4))
    nombres = list(contadores.keys())
    valores = list(contadores.values())
    ax7.barh(nombres, valores)
    ax7.set_title("Resumen de contadores globales")
    ax7.set_xlabel("Cantidad")
    for i, v in enumerate(valores):
        ax7.text(v + max(valores) * 0.01, i, str(v), va="center")
    _save(fig7, "07_contadores_globales", save_dir)
    if show:
        plt.show()
    else:
        plt.close(fig7)

    # 8 ───────────────────────────────────────────────
    # Texto: porcentaje medio de ocupación de pasillos
    porc = metrics.get("avg_corridor_occupation_pct", 0) * 100
    print(f"\nPorcentaje medio de ocupación de pasillos: {porc:.2f}%\n")
