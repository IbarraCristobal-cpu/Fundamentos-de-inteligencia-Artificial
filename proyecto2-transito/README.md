# TransitoBot — Proyecto N°2, Fundamentos de IA (UNAB)

Chatbot sobre el **Reglamento de Tránsito chileno (Ley 18.290)** orientado al examen teórico de conducción, implementado de dos formas con el mismo conocimiento:

| Versión | Tecnología | Conocimiento |
|---|---|---|
| 1 | Lógica de primer orden en **SWI-Prolog** | `prolog/conocimiento.pl` |
| 2 | **LLM** + Python | `conocimiento/transito.md` (inyectado en el prompt) |

Ambas se usan desde una **interfaz web** (Flask) que permite preguntar a una, a la otra o a ambas a la vez.

## Instalación
1. Instalar **SWI-Prolog 9.x**: https://www.swi-prolog.org/Download.html (debe quedar `swipl` en el PATH, o definir `SWIPL_PATH`).
2. Instalar dependencias de Python 3.10+:
   ```
   python -m venv .venv
   .venv\Scripts\activate        # Windows   (Linux/Mac: source .venv/bin/activate)
   pip install -r requirements.txt
   ```
3. Configurar el LLM: copiar `.env.example` a `.env` y completar la API key (ver opciones dentro del archivo).

## Uso
```
python run.py                      # web en http://127.0.0.1:5000
swipl prolog/chatbot.pl            # chat de Prolog por consola
python -m evaluacion.evaluar       # corre las 20 preguntas en ambos bots
python -m pytest                   # pruebas automáticas
```
La web funciona aunque falte la API key: el modo Prolog responde y el modo LLM muestra un aviso claro.

## Estructura
```
prolog/        chatbot Prolog (conocimiento.pl, interprete.pl, respuestas.pl, chatbot.pl,
               consulta.pl + una_pregunta.pl = interfaz no interactiva usada por Python)
conocimiento/  transito.md: el mismo conocimiento en lenguaje natural, para el LLM
backend/       prolog_bot.py, llm_bot.py, llm_providers.py, knowledge.py, app.py (API Flask), config.py
frontend/      index.html (interfaz web)
evaluacion/    preguntas.json (20 preguntas), evaluar.py, resultados.json/.md, revision_manual.json
tests/         pruebas automáticas (pytest)
docs/          informe de entrega
```

## Cómo se conectan las piezas
```
navegador ──POST /api/chat──► Flask (backend/app.py)
                                 ├─► PrologBot ──subproceso──► swipl prolog/una_pregunta.pl
                                 └─► LLMBot ──HTTPS──► API del LLM (prompt = instrucciones + transito.md)
```

## Modificar el conocimiento (útil en la interrogación)
- **Prolog:** editar `prolog/conocimiento.pl` (hechos/reglas) y, si hay vocabulario nuevo, `prolog/interprete.pl` (diccionario `entidad/3`) y `prolog/respuestas.pl` (nombres para mostrar). Cada pregunta relanza `swipl`, así que **no hay que reiniciar** nada.
- **LLM:** editar `conocimiento/transito.md`. Se relee automáticamente cuando cambia el archivo.
- Mantener ambos conocimientos **coherentes** entre sí.

## Evaluación
`python -m evaluacion.evaluar` guarda `evaluacion/resultados.json` y `resultados.md`. El puntaje automático es una heurística (palabras clave); los ajustes tras leer las respuestas se registran en `evaluacion/revision_manual.json`.
