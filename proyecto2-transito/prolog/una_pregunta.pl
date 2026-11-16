% ============================================================
%  una_pregunta.pl
%  Lee UNA pregunta desde la entrada estándar (UTF-8) y escribe:
%     línea 1: intención detectada
%     resto  : respuesta del chatbot
%  Uso:  echo "¿Límite en zona urbana?" | swipl una_pregunta.pl
% ============================================================
:- use_module(consulta).

:- initialization(principal, main).

principal :-
    set_stream(user_input,  encoding(utf8)),
    set_stream(user_output, encoding(utf8)),
    (   read_line_to_string(user_input, Linea), Linea \== end_of_file
    ->  consultar(Linea, Intencion, Respuesta)
    ;   consultar("", Intencion, Respuesta)
    ),
    format('~q~n~w', [Intencion, Respuesta]).
