# Plan de Corrección Integral y Post-Procesado Avanzado: Circuito 3 (Marina Bay F1)

Plan de ingeniería para erradicar los fallos críticos de geometría y colisiones del **Circuito 3 (Marina Bay Street Circuit)** y construir un pipeline de post-procesado nocturno de simulación fotorrealista de alto nivel basado en la arquitectura del Circuito 1, garantizando 60–120 FPS estables sin alterar los Circuitos 1 y 2.

---

### Diagnóstico Exhaustivo de los Problemas Actuales

Tras una auditoría minuciosa del código y los subsistemas de renderizado y físicas, se han identificado 5 fallos estructurales que provocaban el comportamiento anómalo:

1. **Superposición de Trazado (Plegado de 180° en Meta)**:
   - *Causa*: Los nodos de la Recta de Meta (X: -50 a +185, Z: -135) y los nodos del enlace final de Curvas 16 a 19 (X: 112 a -50, Z: -130 a -148) estaban trazados sobre el mismo plano espacial en direcciones opuestas. Al cruzar la curva 19, el monoplaza se invertía 180° y colisionaba con el propio asfalto y barreras del sentido contrario.
2. **Barreras Unilaterales Incompletas y Huecos de Colisión**:
   - *Causa*: El bucle de muros de contención solo levantaba bloques en el lado exterior (`+normX`), dejando el interior completamente vacío. La normal entre segmentos discretizados no mantenía continuidad $\mathcal{C}^1$, creando picos y huecos invisibles donde el coche quedaba atrapado.
3. **Artefacto de Sol Fantasma en el Environment Map Nocturno**:
   - *Causa*: En `DynamicSkySystem.generateEnvironmentMap`, aunque `isNight = true`, el código continuaba dibujando un disco solar diurno incandescente de 420 píxeles de radio con gradiente naranja. Como resultado, la carrocería del monoplaza y el asfalto nocturno reflejaban un sol de atardecer en mitad de la noche de Singapur.
4. **Post-Procesado Nocturno Básico y Desconectado del Circuito 1**:
   - *Causa*: `CinematicPostEffect.ts` en modo noche aplicaba una onda senoidal estática genérica (`sin(uv.x * 24.0)`). Carecía de la halación anamórfica de proyectores de 5600K, bloom de asfalto pulido, viñeteado de lente broadcast de alta apertura y grano de sensor CMOS calibrado para evitar el *color banding* de 8 bits en sombras.
5. **Detección de Sectores Desincronizada**:
   - *Causa*: Los disparadores de sector en `SingaporeCircuitConfig.ts` dependían de coordenadas del trazado anterior, fallando en el conteo de vueltas y deltas de tiempo.

---

### Solución Propuesta y Decisiones Confirmadas

> [!IMPORTANT]
> - **Trazado Canónico No Superpuesto a Escala Completa**: Separación física de más de 85 metros entre la recta de meta (Este/Oeste) y el complejo técnico de entrada (T16-T19), garantizando un circuito cerrado $\mathcal{C}^1$ continuo sin pliegues y con curvatura real de las 19 curvas.
> - **Muros Dobles FIA con Detección en Ambos Lados**: Barreras continuas de hormigón y vallas metálicas en ambos márgenes (+halfW y -halfW) registradas en `staticObstacles` para el motor de colisiones de 120 Hz.
> - **Pipeline Completo de Post-Procesado Nocturno F1**:
>   1. **Halación Anamórfica 5600K**: Destellos horizontales ópticos que reaccionan a las líneas de proyectores de estadio.
>   2. **Micro-Dither CMOS Sensor**: Grano analógico dinámico para eliminar banding en cielos oscuros y sombras profundas.
>   3. **Viñeteado Óptico Broadcast**: Caída de luminosidad periférica adaptada a la relación de aspecto.
>   4. **IBL Nocturno Limpio**: Supresión total del sol diurno en `generateEnvironmentMap`, sustituido por la bóveda celeste índigo, la cúpula de proyectores de xenón y el resplandor urbano del skyline de Singapur.
> - **Aislamiento Absoluto**: Circuitos 1 y 2 permanecen 100% inalterados.

---

## 1. Arquitectura del Trazado y Geometría Canónica

El trazado respetará con exactitud el mapa oficial de 19 curvas (2023-presente) con orientación fluida antihoraria:

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        TRAZADO CANÓNICO MARINA BAY 19C                     │
│                                                                            │
│                       [T7 Memorial Corner - 90° Left]                      │
│                             ┌──────────────────┐                           │
│                            /                    \                          │
│     [T8-T9 Stamford]      /    Raffles Blvd      \  [T6 Kink]              │
│            ┌─────────────┘     (DRS Zona 1)       \                        │
│            │                   355+ km/h           \                       │
│     [T10-T11 Padang]                                \                      │
│            │                                         │  [T5 Slingshot]     │
│            │                                         │                     │
│     [Anderson Bridge]                                │  [T4 Republic Blvd] │
│          (T12-T13)                                   │                     │
│            │                                         │  [T1-T2-T3 Sheares] │
│            └───────────────┐                         │     ┌───────┐       │
│               Esplanade    │   Bahía de Singapur     │     │       │       │
│               (T14-T15)    │   (Espejo de agua)      │     │       │       │
│                            │                         │     │  ▲    │       │
│                            └─────────────────────────┘     │  │    │       │
│                               Recta Rápida T15-T16         │ Recta Meta    │
│                                    (390m)                  [SALIDA / META] │
│                                       │                           │        │
│                                       └──────[T16-T19]────────────┘        │
│                                        (Separado por 90m de Meta)          │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Pipeline de Post-Procesado e Iluminación Nocturna

### A. Cinemática Broadcast 5600K (`CinematicPostEffect.ts`)
- **Shader Óptico Avanzado**:
  - Eliminación de la onda sinusoidal artificial.
  - Implementación de destellos anamórficos de lente horizontal inspirados en las ópticas Cooke/Panavision de retransmisiones nocturnas de F1, activándose dinámicamente según la velocidad y el ángulo de visión de las torretas de luz.
  - Micro-grano de sensor CMOS con dither pseudo-aleatorio de alta frecuencia para evitar cualquier escalonamiento en gradientes oscuros.
  - Viñeta anamórfica de contorno esférico corregida por aspecto (`uAspect`).

### B. Corrección de IBL y Cúpula Celeste (`DynamicSkySystem.ts`)
- **Limpieza del Environment Map**:
  - Cuando `isNight = true`, se desactiva el gradiente radial del sol diurno.
  - Se genera una banda de radiación perimetral de proyectores de xenón 5600K (`#f1f5f9` y `#38bdf8`) en el horizonte, lo que dota a las carrocerías, alerones y asfalto de reflejos de luz de estadio puros sin tonos ocres o rojizos del atardecer.

### C. Asfalto Especular y Muros Dobles (`SingaporeTrackBuilder.ts`)
- **Muros de Contención Bilaterales**:
  - Muros exteriores e interiores con alturas calibradas (1.2m hormigón + 2.5m valla metálica) y conexión continua en vértices.
  - Registro de ambos márgenes en el sistema de colisiones para evitar cualquier fuga o atravesamiento.
- **Pianos de Singapur 3D**:
  - Perfilado físico en las 19 curvas con alternancia azul/blanco y respuesta de fricción.

---

## 3. Plan de Componentes y Archivos a Modificar

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Archivos Involucrados                           │
│                                                                        │
│   src/game/circuits/singapore/SingaporeWaypoints.ts                    │
│   └── 38 nodos de control canónicos no superpuestos (4.927 km)         │
│                                                                        │
│   src/game/circuits/singapore/SingaporeCircuitConfig.ts                │
│   └── Sincronización de sectores, minimapa SVG y cajas DRS             │
│                                                                        │
│   src/game/circuits/singapore/SingaporeTrackBuilder.ts                 │
│   └── Muros dobles perimetrales, asfalto especular, hitos arquitect.   │
│                                                                        │
│   src/game/effects/CinematicPostEffect.ts                              │
│   └── Pipeline broadcast nocturno: anamórfico 5600K + grano CMOS       │
│                                                                        │
│   src/game/environment/DynamicSkySystem.ts                             │
│   └── Supresión del sol diurno en IBL nocturno + resplandor xenón      │
│                                                                        │
│   src/game/RacingGameEngine.ts                                         │
│   └── Exposición y niebla nocturna calibrada en applyCircuitAtmosphere │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Fases de Ejecución

1. **Paso 1: Corrección de Topología de Spline (`SingaporeWaypoints.ts`)**
   - Redefinir los 38 nodos de control eliminando la inversión en la recta de meta.
   - Verificar la orientación y continuidad matemática del spline de 850 waypoints.

2. **Paso 2: Muros Dobles y Registro de Colisiones (`SingaporeTrackBuilder.ts`)**
   - Implementar la generación de muros en ambos márgenes (`side = -1` y `side = +1`).
   - Registrar todos los segmentos en `staticObstacles`.
   - Ajustar el asfalto y pianos para que encajen con la nueva topología.

3. **Paso 3: IBL Nocturno y Shader de Cielo (`DynamicSkySystem.ts`)**
   - Eliminar el sol diurno cuando `isNight = true` en `generateEnvironmentMap`.
   - Añadir la corona de proyectores de xenón nocturnos para reflejos realistas en la carrocería.

4. **Paso 4: Post-Procesado Óptico Avanzado (`CinematicPostEffect.ts`)**
   - Actualizar el shader de fragmentos para incorporar la halación anamórfica de 5600K y el micro-dither CMOS.
   - Mantener el comportamiento diurno del Circuito 1 sin tocarlo.

5. **Paso 5: Configuración de Circuito y Minimapa (`SingaporeCircuitConfig.ts`)**
   - Actualizar el SVG del minimapa y los sectores para el nuevo trazado canónico.

6. **Paso 6: Verificación y Validación**
   - Ejecutar `lint_applet` y `compile_applet`.
   - Verificar 60/120 FPS sin allocations en bucles de animación.
