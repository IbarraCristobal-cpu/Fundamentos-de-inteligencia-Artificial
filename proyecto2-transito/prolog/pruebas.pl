% Ejecuta preguntas de ejemplo sin interacción:  swipl -q -s pruebas.pl -g probar -t halt
:- use_module(interprete).
:- use_module(respuestas).

pregunta("¿Cuál es el límite de velocidad en zona urbana?").
pregunta("¿A qué velocidad máxima puede ir un camión en zona rural?").
pregunta("¿Qué velocidad se permite en una zona escolar?").
pregunta("¿Comete infracción un auto a 70 km/h en zona urbana?").
pregunta("¿Comete infracción una motocicleta a 100 km/h en zona rural?").
pregunta("Un camión va a 95 km/h en un camino rural, ¿le pueden cursar una multa?").
pregunta("Voy a 40 km/h en zona de escuela, ¿está bien?").
pregunta("Voy a 60 km/h, ¿es infracción?").
pregunta("¿Qué debe hacer un auto frente a un disco pare?").
pregunta("¿Qué significa la luz roja?").
pregunta("¿Qué debe hacer un camión ante un ceda el paso?").
pregunta("¿Puede avanzar una motocicleta con luz verde?").
pregunta("¿Qué señales obligan a detenerse?").
pregunta("¿Quién tiene preferencia si un auto viene por la derecha de un camión?").
pregunta("Un auto y un camión llegan al mismo tiempo a un cruce sin señalizar, el camión viene por la derecha. ¿Quién pasa primero?").
pregunta("Un auto viene por la izquierda de una motocicleta en un cruce. ¿Quién tiene prioridad?").
pregunta("¿Qué pasa en un cruce sin señales?").
pregunta("¿Qué vehículos conoces?").
pregunta("¿Qué zonas existen?").
pregunta("¿Qué puedes hacer?").
pregunta("¿Cuál es la capital de Francia?").
pregunta("Adiós").

probar :-
    forall(pregunta(P),
           ( format('~nTú> ~s~n', [P]),
             interpretar(P, I),
             format('   [intención: ~q]~n', [I]),
             ( responder(I, R) -> true ; R = '(sin respuesta)' ),
             format('Bot> ~w~n', [R]) )).
