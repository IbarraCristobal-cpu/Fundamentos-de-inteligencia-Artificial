% ============================================================
%  interprete.pl
%  Interpretación del lenguaje natural (español): convierte el
%  texto del usuario en una "intención" estructurada.
%  Técnica: normalización + extracción de entidades por
%  palabras clave + reglas de prioridad.
% ============================================================
:- module(interprete, [interpretar/2, normalizar/2]).
:- discontiguous intencion/2.

% ---------- Normalización -----------------------------------
normalizar(Texto, Tokens) :-
    string_lower(Texto, Min),
    string_chars(Min, Chars),
    maplist(sin_acento, Chars, Chars2),
    string_chars(Limpio, Chars2),
    split_string(Limpio, " ,.¿?¡!;:()\"", "", Partes),
    exclude(==(""), Partes, NoVacias),
    maplist(a_atomo, NoVacias, Tokens).

a_atomo(S, A) :- atom_string(A, S).

sin_acento(C, S) :- ( acento(C, S0) -> S = S0 ; S = C ).
acento('á', a). acento('é', e). acento('í', i).
acento('ó', o). acento('ú', u). acento('ü', u). acento('ñ', n).

% ---------- Diccionario de entidades ------------------------
% entidad(Tipo, Palabra, ConstanteDelDominio)
entidad(vehiculo, auto, auto).      entidad(vehiculo, autos, auto).
entidad(vehiculo, automovil, auto). entidad(vehiculo, coche, auto).
entidad(vehiculo, carro, auto).
entidad(vehiculo, camion, camion).  entidad(vehiculo, camiones, camion).
entidad(vehiculo, moto, motocicleta).
entidad(vehiculo, motos, motocicleta).
entidad(vehiculo, motocicleta, motocicleta).
entidad(vehiculo, motocicletas, motocicleta).

entidad(zona, urbana, zona_urbana).  entidad(zona, urbano, zona_urbana).
entidad(zona, urbanas, zona_urbana). entidad(zona, ciudad, zona_urbana).
entidad(zona, rural, zona_rural).    entidad(zona, rurales, zona_rural).
entidad(zona, campo, zona_rural).    entidad(zona, camino, zona_rural).
entidad(zona, carretera, zona_rural).
entidad(zona, escolar, zona_escolar). entidad(zona, escolares, zona_escolar).
entidad(zona, escuela, zona_escolar). entidad(zona, escuelas, zona_escolar).
entidad(zona, colegio, zona_escolar). entidad(zona, colegios, zona_escolar).

entidad(senial, pare, disco_pare).  entidad(senial, disco, disco_pare).
entidad(senial, ceda, ceda_el_paso).
entidad(senial, roja, luz_roja).    entidad(senial, rojo, luz_roja).
entidad(senial, verde, luz_verde).

% Primera entidad de un tipo mencionada en el texto
primera(Tipo, Tokens, Valor) :-
    member(T, Tokens), entidad(Tipo, T, Valor), !.

% Todas las menciones de vehículos con su posición: Pos-Vehiculo
vehiculos_con_pos(Tokens, Lista) :-
    findall(P-V, ( nth1(P, Tokens, T), entidad(vehiculo, T, V) ), Lista).

numero_en(Tokens, N) :-
    member(T, Tokens), atom_number(T, N), number(N), !.

alguna(Palabras, Tokens) :- member(P, Palabras), memberchk(P, Tokens), !.

% ---------- Intenciones (en orden de prioridad) -------------
interpretar(Texto, Intencion) :-
    normalizar(Texto, T),
    intencion(T, Intencion), !.

intencion(T, salir)  :- alguna([salir, adios, chao, chau, bye], T).
intencion(T, ayuda)  :- alguna([ayuda, ayudame, help], T).
intencion(T, ayuda)  :- alguna([puedes], T), alguna([hacer, responder], T).
intencion(T, saludo) :- alguna([hola, buenas, buenos], T), length(T, N), N =< 3.

% ¿Qué señal obliga a detenerse?
intencion(T, senales_que_detienen) :-
    alguna([senal, senales], T),
    alguna([detener, detenerse, detencion, parar, detiene, obliga], T).

% Derecho a vía en cruces
intencion(T, preferencia(Info)) :-
    alguna([preferencia, prioridad, derecha, izquierda, cruce,
            interseccion, esquina], T), !,
    info_preferencia(T, Info).

% ¿Qué señales/vehículos/zonas conoces?
intencion(T, listar(vehiculos)) :- alguna([vehiculos], T), pide_lista(T).
intencion(T, listar(senales))   :- alguna([senales, senaletica, senaleticas], T), pide_lista(T).
intencion(T, listar(zonas))     :- alguna([zonas], T), pide_lista(T).
pide_lista(T) :- alguna([cuales, que, lista, listame, conoces, existen], T).

% Velocidad: ¿infracción? (hay un número) o ¿cuál es el límite?
intencion(T, infraccion(V, Z, Vel)) :-
    numero_en(T, Vel),
    ( primera(zona, T, _) ; alguna([velocidad, km, kmh, 'km/h', infraccion,
                                    multa, exceso, rapido, voy, va, circula], T) ),
    ( primera(vehiculo, T, V) -> true ; V = auto ),
    ( primera(zona, T, Z) -> true ; Z = ninguna ).
intencion(T, limite(Z, V)) :-
    ( alguna([velocidad, limite, maxima, maximo, rapido, rapida, km, kmh, 'km/h'], T)
    ; primera(zona, T, _), \+ primera(senial, T, _) ),
    ( primera(zona, T, Z) -> true ; Z = ninguna ),
    ( primera(vehiculo, T, V) -> true ; V = ninguno ).

% Señales: ¿qué debe hacer / qué significa?
intencion(T, senal(S, V)) :-
    primera(senial, T, S),
    ( primera(vehiculo, T, V) -> true ; V = ninguno ).

intencion(_, desconocida).

% ---------- Preferencia: ¿cuál vehículo viene por la derecha?
% Heurística por posición de las palabras en la frase.
info_preferencia(T, derecha(W, L)) :-
    vehiculos_con_pos(T, Lista),
    Lista = [_-A | Resto],
    member(PB-B, Resto), B \== A, !,
    (   nth1(PD, T, derecha)
    ->  ( PD < PB -> W = A, L = B ; W = B, L = A )
    ;   nth1(PI, T, izquierda)
    ->  ( PI < PB -> W = B, L = A ; W = A, L = B )
    ).
info_preferencia(_, sin_datos).
