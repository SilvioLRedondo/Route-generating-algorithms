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


def visualizar_metricas(metrics: dict, *, dt: float, save_dir: str | None = None, show: bool = True):
    # 1 ───────────────────────────────────────────────
    # Serie temporal de ocupación máxima de pasillos
    pasos = len(metrics["max_corridor_occupancy"])
    tiempo = [i * dt for i in range(pasos)]
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.plot(tiempo, metrics["max_corridor_occupancy"], linewidth=1.5)
    ax1.set_title("Ocupación máxima de pasillos")
    ax1.set_xlabel("Tiempo (s)")
    ax1.set_ylabel("Robots simultáneos")
    _save(fig1, "01_pasillos_tiempo", save_dir)
    if show:
        plt.show()
    else:
        plt.close(fig1)

    # 2 ───────────────────────────────────────────────
    # Histograma de tiempos de tránsito de paquetes
    if metrics["packet_transit_times"]:
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        ax2.hist(metrics["packet_transit_times"], bins="auto", rwidth=0.9)
        ax2.set_title("Distribución de tiempos de tránsito de paquetes")
        ax2.set_xlabel("Segundos")
        ax2.set_ylabel("Número de paquetes")
        _save(fig2, "02_hist_transito_paquetes", save_dir)
        if show:
            plt.show()
        else:
            plt.close(fig2)

    # 3 ───────────────────────────────────────────────
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

    # 4 ───────────────────────────────────────────────
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

    # 5 ───────────────────────────────────────────────
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

    # 6 ───────────────────────────────────────────────
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

    # if metrics["blockages"]["timestamps"]:
    #     eventos.extend(metrics["blockages"]["timestamps"])
    #     etiquetas.extend(["Bloqueo"] * len(metrics["blockages"]["timestamps"]))
    # if metrics["recharge_usage"]["timestamps"]:
    #     eventos.extend(metrics["recharge_usage"]["timestamps"])
    #     etiquetas.extend(["Recarga"] * len(metrics["recharge_usage"]["timestamps"]))

    # if eventos:
    #     fig6, ax6 = plt.subplots(figsize=(8, 3))
    #     colores = {"Bloqueo": "red", "Recarga": "green"}
    #     ax6.scatter(eventos, [0] * len(eventos), c=[colores[e] for e in etiquetas], marker="|", s=200)
    #     ax6.set_title("Timestamps de bloqueos y recargas")
    #     ax6.set_xlabel("Tiempo (s)")
    #     ax6.axes.get_yaxis().set_visible(False)
    #     _save(fig6, "06_eventos_bloqueo_recarga", save_dir)
    #     if show:
    #         plt.show()
    #     else:
    #         plt.close(fig6)

    # 7 ───────────────────────────────────────────────
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
