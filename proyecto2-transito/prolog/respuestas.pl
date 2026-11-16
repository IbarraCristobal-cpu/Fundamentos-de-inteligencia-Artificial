% ============================================================
%  respuestas.pl
%  Convierte una intención en una respuesta en español,
%  consultando (y razonando con) la base de conocimiento.
%  Cada respuesta cita la regla de LPO que la justifica.
% ============================================================
:- module(respuestas, [responder/2]).
:- use_module(conocimiento).
:- discontiguous responder/2.

% ---------- Escenarios temporales ---------------------------
% Carga hechos de situación, ejecuta la consulta y los retira
% (aunque la consulta falle o lance una excepción).
con_escenario(Hechos, Meta) :-
    setup_call_cleanup(
        maplist(cargar, Hechos),
        once(Meta),
        maplist(retirar, Hechos)).

cargar(H)  :- assertz(conocimiento:H).
retirar(H) :- retractall(conocimiento:H).

% ---------- Nombres para mostrar ----------------------------
vehiculo_txt(auto,        'un auto').
vehiculo_txt(camion,      'un camión').
vehiculo_txt(motocicleta, 'una motocicleta').
vehiculo_txt(ninguno,     'un vehículo').

vehiculo_nom(auto, 'auto').
vehiculo_nom(camion, 'camión').
vehiculo_nom(motocicleta, 'motocicleta').

zona_txt(zona_urbana,  'zona urbana').
zona_txt(zona_rural,   'zona rural').
zona_txt(zona_escolar, 'zona escolar').

senial_txt(disco_pare,   'Disco Pare').
senial_txt(ceda_el_paso, 'Ceda el Paso').
senial_txt(luz_roja,     'Luz Roja').
senial_txt(luz_verde,    'Luz Verde').

cap(A, C) :-
    sub_atom(A, 0, 1, _, F), sub_atom(A, 1, _, 0, R),
    upcase_atom(F, U), atom_concat(U, R, C).

unir(Lista, Texto) :- atomic_list_concat(Lista, ', ', Texto).

% ---------- Respuestas por intención ------------------------
responder(saludo, '¡Hola! Soy TransitoBot. Respondo preguntas del examen teórico de conducción (señales, velocidades y preferencia en cruces). Escribe "ayuda" para ver ejemplos.').
responder(salir,  '¡Hasta luego! Conduce con precaución.').
responder(ayuda,  'Puedes preguntarme, por ejemplo:\n  - ¿Cuál es el límite de velocidad en zona urbana?\n  - ¿Comete infracción un camión a 95 km/h en zona rural?\n  - ¿Qué debe hacer un auto frente a un disco pare?\n  - ¿Qué señales obligan a detenerse?\n  - ¿Quién tiene preferencia si un auto viene por la derecha de un camión?\n  - ¿Qué zonas conoces?').

responder(listar(vehiculos), R) :-
    findall(N, (vehiculo(V), vehiculo_nom(V, N)), L), unir(L, T),
    format(atom(R), 'Conozco estos vehículos: ~w.', [T]).
responder(listar(senales), R) :-
    findall(N, (senial(S), senial_txt(S, N)), L), unir(L, T),
    format(atom(R), 'Conozco estas señales: ~w.', [T]).
responder(listar(zonas), R) :-
    findall(N, (zona(Z), zona_txt(Z, N)), L), unir(L, T),
    format(atom(R), 'Conozco estas zonas viales: ~w.', [T]).

% Señales que obligan a detenerse (Regla 1), obtenidas por inferencia
responder(senales_que_detienen, R) :-
    findall(N, ( senial(S),
                 con_escenario([enfrenta(auto, S)], debe_detenerse(auto)),
                 senial_txt(S, N) ), L),
    unir(L, T),
    format(atom(R), 'Obligan a detenerse por completo: ~w. (Regla 1)', [T]).

% Límite de velocidad (Regla 2)
responder(limite(ninguna, V), R) :-
    findall(Linea, ( zona(Z), zona_txt(Z, ZN),
                     texto_limite_zona(Z, V, TL),
                     format(atom(Linea), '~w: ~w', [ZN, TL]) ), Lineas),
    atomic_list_concat(Lineas, '\n  - ', Cuerpo),
    format(atom(R), 'Límites máximos de velocidad (Regla 2):\n  - ~w', [Cuerpo]).
responder(limite(Z, V), R) :-
    Z \== ninguna,
    zona_txt(Z, ZN),
    texto_limite_zona(Z, V, TL),
    nota_zona(Z, Nota),
    format(atom(R), 'En ~w el límite máximo es: ~w.~w (Regla 2)', [ZN, TL, Nota]).

texto_limite_zona(Z, V, Texto) :-
    (   vehiculo_nom(V, N), limite_velocidad(V, Z, L)
    ->  format(atom(Texto), '~w km/h para ~w', [L, N])
    ;   findall(V1-L1, ( vehiculo(V1), limite_velocidad(V1, Z, L1) ), Pares),
        pares_unicos(Pares, Texto)
    ).

pares_unicos(Pares, Texto) :-
    findall(L, member(_-L, Pares), Ls), sort(Ls, [Unico]), !,
    format(atom(Texto), '~w km/h para todo vehículo', [Unico]).
pares_unicos(Pares, Texto) :-
    findall(S, ( member(V-L, Pares), vehiculo_nom(V, N),
                 format(atom(S), '~w ~w km/h', [N, L]) ), Ss),
    unir(Ss, Texto).

nota_zona(zona_escolar, ' (rige en los horarios de entrada y salida de los alumnos)') :- !.
nota_zona(zona_rural,   ' (camino con una pista por sentido)') :- !.
nota_zona(_, '').

% Infracción por velocidad (Regla 2)
responder(infraccion(_, ninguna, Vel), R) :-
    format(atom(R), 'Para saber si ~w km/h es infracción necesito la zona: ¿urbana, rural o escolar?', [Vel]).
responder(infraccion(V, Z, Vel), R) :-
    Z \== ninguna,
    vehiculo_txt(V, VT), zona_txt(Z, ZN),
    limite_velocidad(V, Z, L),
    (   con_escenario([circula_en(V, Z), velocidad(V, Vel)], infraccion(V))
    ->  Exceso is Vel - L,
        format(atom(R), 'Comete infracción: ~w circulando en ~w a ~w km/h excede el límite de ~w km/h en ~w km/h. (Regla 2)',
               [VT, ZN, Vel, L, Exceso])
    ;   format(atom(R), 'No comete infracción: ~w circulando en ~w a ~w km/h está dentro del límite de ~w km/h. (Regla 2)',
               [VT, ZN, Vel, L])
    ).

% Señales de tránsito (Reglas 1, 4 y 5)
responder(senal(S, V), R) :-
    senial_txt(S, SN),
    ( V == ninguno -> Veh = auto ; Veh = V ),
    vehiculo_txt(V, VT), cap(VT, VTC),
    (   con_escenario([enfrenta(Veh, S)], debe_detenerse(Veh))
    ->  Accion = 'debe detenerse por completo y continuar solo cuando sea seguro', Regla = 1
    ;   con_escenario([enfrenta(Veh, S)], debe_ceder(Veh))
    ->  Accion = 'debe ceder el paso a los vehículos que circulan por la vía preferente', Regla = 4
    ;   con_escenario([enfrenta(Veh, S)], puede_avanzar(Veh))
    ->  Accion = 'puede avanzar, siempre con precaución y si el cruce está despejado', Regla = 5
    ),
    format(atom(R), '~w ante la señal ~w ~w. (Regla ~w)', [VTC, SN, Accion, Regla]).

% Derecho a vía (Regla 3)
responder(preferencia(derecha(W, L)), R) :-
    (   con_escenario([llegan_mismo_tiempo(W, L), aproxima_por_derecha(W, L)],
                      tiene_preferencia(W))
    ->  vehiculo_txt(W, WT), vehiculo_txt(L, LT),
        format(atom(R), 'Tiene preferencia ~w, porque se aproxima por la derecha de ~w al llegar ambos al mismo tiempo a un cruce sin señalizar. (Regla 3)', [WT, LT])
    ).
responder(preferencia(sin_datos), 'En un cruce sin señalizar, si dos vehículos llegan al mismo tiempo, tiene preferencia el que se aproxima por la derecha del otro. (Regla 3) Dime qué vehículos son y cuál viene por la derecha.').

responder(desconocida, 'No entendí tu pregunta. Puedo ayudarte con límites de velocidad, infracciones, señales (Disco Pare, Ceda el Paso, Luz Roja, Luz Verde) y preferencia en cruces. Escribe "ayuda" para ver ejemplos.').
