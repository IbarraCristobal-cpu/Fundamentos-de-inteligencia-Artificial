% ============================================================
%  conocimiento.pl
%  Base de conocimiento del dominio: Reglamento de Tránsito
%  (Ley 18.290, Chile) orientada al examen teórico de conducción.
%
%  Traducción directa de la formalización en Lógica de Primer
%  Orden (LPO) del informe: constantes -> átomos, predicados ->
%  hechos, reglas -> cláusulas de Horn.
% ============================================================
:- module(conocimiento, [
    % Hechos estáticos
    vehiculo/1, senial/1, zona/1,
    % Hechos de situación (se cargan temporalmente por cada pregunta)
    enfrenta/2, circula_en/2, velocidad/2,
    llegan_mismo_tiempo/2, aproxima_por_derecha/2,
    % Reglas
    limite_velocidad/3, debe_detenerse/1, debe_ceder/1,
    puede_avanzar/1, infraccion/1, tiene_preferencia/1
]).

% ---------- Hechos de situación (dinámicos) -----------------
% Describen el escenario concreto que plantea el usuario.
:- dynamic enfrenta/2, circula_en/2, velocidad/2,
           llegan_mismo_tiempo/2, aproxima_por_derecha/2.

% ---------- A. Constantes y tipos ---------------------------
% Vehiculo(x)
vehiculo(auto).
vehiculo(camion).
vehiculo(motocicleta).

% Senial(x)
senial(disco_pare).
senial(ceda_el_paso).
senial(luz_roja).
senial(luz_verde).

% Zona(x)
zona(zona_urbana).
zona(zona_rural).
zona(zona_escolar).

% ---------- C. Reglas ---------------------------------------

% Regla 1: Enfrenta(x,y) con y = DiscoPare  ∨  y = LuzRoja
%          -> DebeDetenerse(x)
% (la disyunción se escribe como dos cláusulas de Horn)
debe_detenerse(X) :-
    vehiculo(X), senial(Y), enfrenta(X, Y), Y = disco_pare.
debe_detenerse(X) :-
    vehiculo(X), senial(Y), enfrenta(X, Y), Y = luz_roja.

% Regla 2a-2c: LimiteVelocidad(x, z, l)  (km/h)
limite_velocidad(X, zona_urbana, 50)  :- vehiculo(X).
limite_velocidad(X, zona_escolar, 30) :- vehiculo(X).
limite_velocidad(X, zona_rural, 100)  :- vehiculo(X), X \= camion.
limite_velocidad(camion, zona_rural, 90).

% Regla 2: CirculaEn(x,z) ∧ Velocidad(x,v) ∧ LimiteVelocidad(x,z,l)
%          ∧ v > l -> Infraccion(x)
infraccion(X) :-
    vehiculo(X),
    circula_en(X, Z), zona(Z),
    velocidad(X, V),
    limite_velocidad(X, Z, L),
    V > L.

% Regla 3: LleganAlMismoTiempo(x,y) ∧ AproximaPorDerecha(x,y)
%          -> TienePreferencia(x)
tiene_preferencia(X) :-
    vehiculo(X), vehiculo(Y), X \== Y,
    llegan_mismo_tiempo(X, Y),
    aproxima_por_derecha(X, Y).

% Regla 4: Enfrenta(x, CedaElPaso) -> DebeCederElPaso(x)
debe_ceder(X) :-
    vehiculo(X), senial(ceda_el_paso), enfrenta(X, ceda_el_paso).

% Regla 5: Enfrenta(x, LuzVerde) -> PuedeAvanzar(x)
puede_avanzar(X) :-
    vehiculo(X), senial(luz_verde), enfrenta(X, luz_verde).
