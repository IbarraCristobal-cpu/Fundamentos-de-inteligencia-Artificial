# Base de conocimiento: Reglamento de Tránsito (Ley 18.290, Chile) — examen teórico

Este documento contiene el MISMO conocimiento que modela `prolog/conocimiento.pl`
(formalizado en lógica de primer orden en el informe). Es la única fuente de
verdad del chatbot con LLM.

## Entidades
- Vehículos: auto, camión, motocicleta.
- Señales: Disco Pare, Ceda el Paso, Luz Roja, Luz Verde.
- Zonas viales: zona urbana, zona rural, zona escolar.

## Límites máximos de velocidad (Regla 2)
| Zona | Vehículo | Límite máximo |
|---|---|---|
| Zona urbana | auto, camión, motocicleta | 50 km/h |
| Zona rural (camino con una pista por sentido) | auto, motocicleta | 100 km/h |
| Zona rural (camino con una pista por sentido) | camión | 90 km/h |
| Zona escolar (en horario de entrada y salida de alumnos) | auto, camión, motocicleta | 30 km/h |

Regla 2 (infracción): si un vehículo circula en una zona a una velocidad MAYOR que
su límite máximo en esa zona, comete una infracción. Circular exactamente al límite
NO es infracción. El exceso es la velocidad menos el límite.

## Señales
- Regla 1: frente a un Disco Pare o a una Luz Roja, el vehículo debe detenerse por completo.
- Regla 4: frente a un Ceda el Paso, el vehículo debe ceder el paso a los vehículos de la vía preferente.
- Regla 5: frente a una Luz Verde, el vehículo puede avanzar, con precaución y si el cruce está despejado.

## Derecho a vía en cruces sin señalizar (Regla 3)
Si dos vehículos llegan al mismo tiempo a un cruce sin señalizar, tiene preferencia el
que se aproxima por la derecha del otro.

## Fuera del alcance de este conocimiento
No están modelados: montos de multas y sanciones, tipos de licencia, documentación del
conductor, alcohol, cinturón de seguridad, estacionamiento, caminos rurales con dos o más
pistas por sentido, autopistas, buses ni otros tipos de vehículo, ni temas ajenos al tránsito.
