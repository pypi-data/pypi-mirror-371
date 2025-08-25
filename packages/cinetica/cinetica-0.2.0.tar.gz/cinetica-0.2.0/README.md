# Cinetica

Cinetica is a Python library designed to provide various modules for physics calculations and simulations.

## Installation

```bash
pip install cinetica
```

## Usage

### Movimiento Rectilíneo

El módulo `movimiento_rectilineo` proporciona la clase `MovimientoRectilineo` para calcular posición, velocidad y aceleración en Movimiento Rectilíneo Uniforme (MRU) y Movimiento Rectilíneo Uniformemente Variado (MRUV).

**Ejemplo de uso:**

```python
from cinetica.movimiento_rectilineo import MovimientoRectilineo

# MRU
mru = MovimientoRectilineo(posicion_inicial=10.0, velocidad_inicial=2.0)
posicion_mru = mru.mru_posicion(tiempo=5.0)
velocidad_mru = mru.mru_velocidad()
print(f"MRU - Posición a los 5s: {posicion_mru} m, Velocidad: {velocidad_mru} m/s")

# MRUV
mruv = MovimientoRectilineo(posicion_inicial=0.0, velocidad_inicial=10.0, aceleracion_inicial=2.0)
posicion_mruv = mruv.mruv_posicion(tiempo=3.0)
velocidad_mruv = mruv.mruv_velocidad(tiempo=3.0)
aceleracion_mruv = mruv.mruv_aceleracion()
print(f"MRUV - Posición a los 3s: {posicion_mruv} m, Velocidad: {velocidad_mruv} m/s, Aceleración: {aceleracion_mruv} m/s^2")

# MRUV sin tiempo
mruv_sin_tiempo = MovimientoRectilineo(posicion_inicial=0.0, velocidad_inicial=0.0, aceleracion_inicial=2.0)
velocidad_final_sin_tiempo = mruv_sin_tiempo.mruv_velocidad_sin_tiempo(posicion_final=16.0)
print(f"MRUV - Velocidad final sin tiempo (para posición 16m): {velocidad_final_sin_tiempo} m/s")
```

### Movimiento Parabólico

El módulo `movimiento_parabolico` proporciona la clase `MovimientoParabolico` para simular trayectorias, alcance y tiempo de vuelo de un proyectil.

**Ejemplo de uso:**

```python
from cinetica.movimiento_parabolico import MovimientoParabolico

# Lanzamiento con velocidad inicial de 20 m/s y ángulo de 45 grados
mp = MovimientoParabolico(velocidad_inicial=20.0, angulo_grados=45)

# Calcular posición a los 1.5 segundos
pos_x, pos_y = mp.posicion(tiempo=1.5)
print(f"MP - Posición a los 1.5s: x={pos_x:.2f} m, y={pos_y:.2f} m")

# Calcular velocidad a los 1.5 segundos
vel_x, vel_y = mp.velocidad(tiempo=1.5)
print(f"MP - Velocidad a los 1.5s: vx={vel_x:.2f} m/s, vy={vel_y:.2f} m/s")

# Calcular tiempo de vuelo, altura máxima y alcance máximo
tiempo_vuelo = mp.tiempo_vuelo()
altura_maxima = mp.altura_maxima()
alcance_maximo = mp.alcance_maximo()
print(f"MP - Tiempo de vuelo: {tiempo_vuelo:.2f} s")
print(f"MP - Altura máxima: {altura_maxima:.2f} m")
print(f"MP - Alcance máximo: {alcance_maximo:.2f} m")
```

## Contributing

Contributions are welcome! Please see the `CONTRIBUTING.md` for more details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
