# Resultados de la evaluación (20 preguntas)

Fecha: 2026-11-09T20:26:00  

| Bot | Correctas | Parciales | Incorrectas | Errores | Tiempo medio |
|---|---|---|---|---|---|
| prolog | 16/20 | 2 | 2 | 0 | 32 ms |

## P1. ¿Cuál es el límite de velocidad en zona urbana?
*Categoría:* límite de velocidad  
*Respuesta esperada:* 50 km/h para todo vehículo (Regla 2).

- **prolog** ✅ (correcta, 32 ms): En zona urbana el límite máximo es: 50 km/h para todo vehículo. (Regla 2)

## P2. ¿Qué velocidad máxima se permite en una zona escolar?
*Categoría:* límite de velocidad  
*Respuesta esperada:* 30 km/h (en horario de entrada y salida de alumnos).

- **prolog** ✅ (correcta, 33 ms): En zona escolar el límite máximo es: 30 km/h para todo vehículo. (rige en los horarios de entrada y salida de los alumnos) (Regla 2)

## P3. ¿A qué velocidad máxima puede circular un camión en zona rural?
*Categoría:* límite de velocidad  
*Respuesta esperada:* 90 km/h.

- **prolog** ✅ (correcta, 31 ms): En zona rural el límite máximo es: 90 km/h para camión. (camino con una pista por sentido) (Regla 2)

## P4. ¿Cuál es el límite de velocidad de una motocicleta en zona rural?
*Categoría:* límite de velocidad  
*Respuesta esperada:* 100 km/h.

- **prolog** ✅ (correcta, 31 ms): En zona rural el límite máximo es: 100 km/h para motocicleta. (camino con una pista por sentido) (Regla 2)

## P5. Un auto circula a 70 km/h en zona urbana. ¿Comete infracción?
*Categoría:* infracción por velocidad  
*Respuesta esperada:* Sí: excede el límite de 50 km/h en 20 km/h.

- **prolog** ✅ (correcta, 31 ms): Comete infracción: un auto circulando en zona urbana a 70 km/h excede el límite de 50 km/h en 20 km/h. (Regla 2)

## P6. ¿Comete infracción un auto que va exactamente a 50 km/h en zona urbana?
*Categoría:* infracción por velocidad  
*Respuesta esperada:* No: circular al límite no es infracción (v > l es estricto).

- **prolog** ✅ (correcta, 31 ms): No comete infracción: un auto circulando en zona urbana a 50 km/h está dentro del límite de 50 km/h. (Regla 2)

## P7. Un camión va a 95 km/h en zona rural. ¿Está infringiendo la norma?
*Categoría:* infracción por velocidad  
*Respuesta esperada:* Sí: el límite del camión es 90 km/h; excede en 5 km/h.

- **prolog** ✅ (correcta, 31 ms): Comete infracción: un camión circulando en zona rural a 95 km/h excede el límite de 90 km/h en 5 km/h. (Regla 2)

## P8. Una motocicleta circula a 35 km/h en zona escolar. ¿Es infracción?
*Categoría:* infracción por velocidad  
*Respuesta esperada:* Sí: el límite es 30 km/h; excede en 5 km/h.

- **prolog** ✅ (correcta, 33 ms): Comete infracción: una motocicleta circulando en zona escolar a 35 km/h excede el límite de 30 km/h en 5 km/h. (Regla 2)

## P9. ¿Qué debe hacer un auto al llegar a un disco pare?
*Categoría:* señales  
*Respuesta esperada:* Detenerse por completo (Regla 1).

- **prolog** ✅ (correcta, 31 ms): Un auto ante la señal Disco Pare debe detenerse por completo y continuar solo cuando sea seguro. (Regla 1)

## P10. Si un camión se encuentra frente a una luz roja, ¿qué debe hacer?
*Categoría:* señales  
*Respuesta esperada:* Detenerse (Regla 1).

- **prolog** ✅ (correcta, 31 ms): Un camión ante la señal Luz Roja debe detenerse por completo y continuar solo cuando sea seguro. (Regla 1)

## P11. ¿Qué debe hacer un auto frente a un ceda el paso?
*Categoría:* señales  
*Respuesta esperada:* Ceder el paso a los vehículos de la vía preferente (Regla 4).

- **prolog** ✅ (correcta, 36 ms): Un auto ante la señal Ceda el Paso debe ceder el paso a los vehículos que circulan por la vía preferente. (Regla 4)

## P12. ¿Puede avanzar una motocicleta cuando el semáforo está en verde?
*Categoría:* señales  
*Respuesta esperada:* Sí, con precaución y si el cruce está despejado (Regla 5).

- **prolog** ✅ (correcta, 31 ms): Una motocicleta ante la señal Luz Verde puede avanzar, siempre con precaución y si el cruce está despejado. (Regla 5)

## P13. ¿Qué señales obligan al conductor a detenerse?
*Categoría:* señales  
*Respuesta esperada:* Disco Pare y Luz Roja.

- **prolog** ✅ (correcta, 31 ms): Obligan a detenerse por completo: Disco Pare, Luz Roja. (Regla 1)

## P14. Un auto y una motocicleta llegan al mismo tiempo a un cruce sin señalizar y la motocicleta viene por la derecha. ¿Quién tiene preferencia?
*Categoría:* preferencia en cruces  
*Respuesta esperada:* La motocicleta (Regla 3).

- **prolog** ✅ (correcta, 31 ms): Tiene preferencia una motocicleta, porque se aproxima por la derecha de un auto al llegar ambos al mismo tiempo a un cruce sin señalizar. (Regla 3)

## P15. En un cruce sin señalizar, si dos vehículos llegan al mismo tiempo, ¿quién pasa primero?
*Categoría:* preferencia en cruces  
*Respuesta esperada:* El que se aproxima por la derecha del otro (Regla 3).

- **prolog** ✅ (correcta, 31 ms): En un cruce sin señalizar, si dos vehículos llegan al mismo tiempo, tiene preferencia el que se aproxima por la derecha del otro. (Regla 3) Dime qué vehículos son y cuál viene por la derecha.

## P16. Voy manejando mi camioneta por el centro de la ciudad a 60, ¿me pueden multar?
*Categoría:* parafraseo / jerga  
*Respuesta esperada:* Sí, 60 > 50 km/h en zona urbana (la camioneta no está modelada, pero el límite urbano aplica a todo vehículo).

- **prolog** 🟡 (parcial, 31 ms): Comete infracción: un auto circulando en zona urbana a 60 km/h excede el límite de 50 km/h en 10 km/h. (Regla 2)
  - Nota: El veredicto coincide por azar: no reconoce «camioneta» y asume «auto» sin avisarlo (vehículo por defecto).

## P17. Un camión circula a 80 km/h por la ciudad y luego a 80 km/h por un camino rural. ¿En cuál de los dos tramos comete infracción?
*Categoría:* dos zonas en una pregunta  
*Respuesta esperada:* Solo en la ciudad (80 > 50). En zona rural el límite del camión es 90, por lo que 80 no es infracción.

- **prolog** 🟡 (parcial, 32 ms): Comete infracción: un camión circulando en zona urbana a 80 km/h excede el límite de 50 km/h en 30 km/h. (Regla 2)
  - Nota: Solo evalúa la primera zona mencionada (urbana); ignora el tramo rural, que era la mitad de la pregunta.

## P18. ¿Cuál es el límite de velocidad en una autopista de dos pistas por sentido?
*Categoría:* fuera de la base (tránsito)  
*Respuesta esperada:* No está en la base de conocimiento (solo caminos rurales con una pista por sentido). Debe reconocerlo y no inventar.

- **prolog** ❌ (incorrecta, 31 ms): Límites máximos de velocidad (Regla 2):   - zona urbana: 50 km/h para todo vehículo   - zona rural: auto 100 km/h, camión 90 km/h, motocicleta 100 km/h   - zona escolar: 30 km/h para todo vehículo
  - Nota: No detecta que la consulta (autopista, dos pistas) está fuera de su conocimiento; responde con la tabla general de límites, que podría confundir.

## P19. ¿Cuánto es la multa por no respetar un disco pare?
*Categoría:* fuera de la base (tránsito)  
*Respuesta esperada:* No está en la base de conocimiento (no se modelan multas). Debe reconocerlo y no inventar.

- **prolog** ❌ (incorrecta, 31 ms): Un vehículo ante la señal Disco Pare debe detenerse por completo y continuar solo cuando sea seguro. (Regla 1)
  - Nota: Se guía por la palabra «disco pare» y responde la regla de detención; ignora que se preguntaba por la multa.

## P20. ¿Cuál es la capital de Francia?
*Categoría:* fuera del dominio  
*Respuesta esperada:* Fuera del dominio: debe rechazar la pregunta.

- **prolog** ✅ (correcta, 31 ms): No entendí tu pregunta. Puedo ayudarte con límites de velocidad, infracciones, señales (Disco Pare, Ceda el Paso, Luz Roja, Luz Verde) y preferencia en cruces. Escribe "ayuda" para ver ejemplos.
