# Guía práctica / Practice guide

Ejercicios **offline y locales** sobre cadenas. No se ejecuta ningún proceso
ni cmd.exe. *English summary at the end.*

## Objetivos

1. Leer `args.rs` de 1.77.1 y 1.77.2 y reproducir a mano sus salidas.
2. Entender por qué el escape estilo MSVCRT (`\"`) no sirve para cmd.exe.
3. Ver qué cambió en 1.77.2 (comillas duplicadas, hack de `%`, CR/LF).
4. Separar con rigor lo que el modelo dice de lo que se sabe de cmd.exe.

## Prerrequisitos

Python 3.10+. Lectura: advisory de Rust CVE-2024-24576; `args.rs` en ambas
versiones; página `cmd` de Microsoft (ver [SOURCES.md](SOURCES.md)).

## Comandos locales

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m rust_bat_args_model 'a\"b' '%PATH%'
python3 scripts/gen_results.py /tmp/out && diff -r results /tmp/out
```

## Ejercicios graduados

**Nivel 1 — a mano.** Sin ejecutar, escribe la línea para `hello world` y
`a\` en ambas versiones. Compara con `fixtures/expected.json`.

**Nivel 2 — barras y comillas.** Explica la regla 2n+1 de 1.77.1 y la de 2n
+ comilla duplicada de 1.77.2 con `test_backslash_counts`.

**Nivel 3 — el caso 03.** Recorre el verificador paso a paso para 03 en
1.77.1: ¿en qué posición queda `&` fuera de comillas *en el modelo*? ¿Por
qué no ocurre en 1.77.2?

**Nivel 4 — `%`.** ¿Por qué 1.77.1 citaba `%` y aun así el modelo lo marca?
Explica el hack con el comentario del código y por qué el modelo lo deja en
`UNKNOWN`.

**Nivel 5 — límites del modelo.** Elige un comportamiento de cmd que el
verificador no modela (por ejemplo `^` o `call`) y escribe un test que
documente el hueco, marcado como limitación, sin afirmar el resultado real.

**Nivel 6 — código.** Amplía el corpus de `gen_results.py` (por ejemplo,
longitud 5 sobre un alfabeto reducido) y registra los conteos. Explica qué
puedes y qué no puedes concluir.

**Nivel 7 — defensa propia.** Para una herramienta tuya que invoque scripts,
escribe una función de validación que **rechace** en lugar de escapar
(lista blanca de caracteres), con tests. Compárala con la estrategia de
1.77.2.

## Vínculo modelo ↔ CVE

| Caso real | En el código |
|---|---|
| `Command::new("x.bat").arg(untrusted)` en Rust < 1.77.2 | `make_bat_command_line("1.77.1", ...)` |
| Fix de 1.77.2 | `make_bat_command_line("1.77.2", ...)` |
| `raw_arg` como responsabilidad del usuario | `Arg(raw=True)` |
| "no solution ... in all cases" | `real_cmd_behaviour = UNKNOWN` |

---

## English summary

Offline string exercises only; nothing is executed. Levels: (1) derive the
command lines by hand; (2) backslash/quote rules in both versions; (3) step
the checker through case 03; (4) the `%` hack and why it stays UNKNOWN;
(5) document a cmd behaviour the checker does not model; (6) extend the
corpus and state what can be concluded; (7) write a reject-not-escape
validator for your own tool.
