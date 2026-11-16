% ============================================================
%  consulta.pl
%  API no interactiva del chatbot: texto de entrada -> respuesta.
%  La usan el backend Python y el script de evaluación.
% ============================================================
:- module(consulta, [consultar/3]).
:- use_module(interprete).
:- use_module(respuestas).

%% consultar(+Texto, -Intencion, -Respuesta)
%  Nunca falla ni lanza excepciones: ante cualquier problema
%  devuelve la intención `error` y un mensaje genérico.
consultar(Texto, Intencion, Respuesta) :-
    catch(consultar_(Texto, Intencion, Respuesta), _Error,
          ( Intencion = error,
            Respuesta = 'Ocurrió un error interno al procesar tu pregunta.' )).

consultar_(Texto, Intencion, Respuesta) :-
    interpretar(Texto, Intencion),
    (   responder(Intencion, R) -> Respuesta = R
    ;   responder(desconocida, Respuesta)
    ).
