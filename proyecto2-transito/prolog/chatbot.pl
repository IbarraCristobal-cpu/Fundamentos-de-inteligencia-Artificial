% ============================================================
%  chatbot.pl  --  TransitoBot (punto de entrada)
%  Uso:   swipl chatbot.pl        (arranca el chat)
%         o bien  swipl -s chatbot.pl  y luego  ?- chatear.
% ============================================================
:- use_module(interprete).
:- use_module(respuestas).

:- initialization(chatear, main).

chatear :-
    configurar_consola,
    responder(saludo, Saludo),
    format('Bot> ~w~n', [Saludo]),
    bucle.

configurar_consola :-
    set_stream(user_input,  encoding(utf8)),
    set_stream(user_output, encoding(utf8)).

bucle :-
    format('Tú> '), flush_output,
    read_line_to_string(user_input, Linea),
    (   Linea == end_of_file
    ->  true
    ;   split_string(Linea, "", " \t", [Limpia]), Limpia == ""
    ->  bucle
    ;   atender(Linea, Continuar),
        ( Continuar == si -> bucle ; true )
    ).

% Atiende una línea; protege el bucle ante cualquier error inesperado.
atender(Linea, Continuar) :-
    catch(procesar(Linea, Respuesta, Continuar), Error,
          ( print_message(silent, Error),
            Respuesta = 'Ocurrió un error interno al procesar tu pregunta.',
            Continuar = si )),
    format('Bot> ~w~n', [Respuesta]).

procesar(Linea, Respuesta, Continuar) :-
    interpretar(Linea, Intencion),
    (   responder(Intencion, Respuesta0) -> Respuesta = Respuesta0
    ;   responder(desconocida, Respuesta)
    ),
    ( Intencion == salir -> Continuar = no ; Continuar = si ).
