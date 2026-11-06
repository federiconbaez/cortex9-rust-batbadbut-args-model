# cortex9-rust-batbadbut-args-model

[English](README.md) · [Guía práctica](PRACTICE.md)

Port en Python, solo con cadenas, de cómo la biblioteca estándar de Rust
arma la línea de `cmd.exe` cuando `std::process::Command` ejecuta un archivo
batch en Windows, en **1.77.1** (vulnerable, CVE-2024-24576 "BatBadBut") y
**1.77.2** (corregida), más un verificador simplificado de estado de comillas.

**Aquí nada ejecuta procesos, llama a cmd.exe ni toca Windows.** Los
codificadores producen cadenas; el verificador es **el modelo de este
proyecto**, no cmd.exe. El comportamiento real de cmd siempre figura como
`UNKNOWN`. El propio advisory de Rust dice que no encontraron una solución
que escape correctamente en todos los casos. Este proyecto **no** promete
escape universal. Ver [LIMITATIONS.md](LIMITATIONS.md).

## Qué se porta y de dónde

`library/std/src/sys/pal/windows/args.rs` en 1.77.1 y 1.77.2: prefijo con
`/e:ON /v:OFF`, reglas de comillas, comillas internas (2n+1 barras vs 2n
barras y comilla duplicada), `%` → `%%cd:~,%`, rechazo de CR/LF, NUL y
`raw_arg`. Tabla completa en [README.md](README.md).

## Ejecutar

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m rust_bat_args_model '"&echo X' 'hello world'
python3 scripts/gen_results.py /tmp/out && diff -r results /tmp/out
```

## Resultados

- Los 18 casos coinciden con líneas derivadas a mano del código de Rust.
- En el corpus de 37777 cadenas: 1.77.1 tiene 11565 con hallazgos en el
  modelo y 7150 que terminan dentro de comillas; 1.77.2 tiene 0 y 8016 cuyo
  único hallazgo es el hack (`UNKNOWN`).
- Es una afirmación sobre **este verificador en este corpus**, no una prueba
  de que 1.77.2 sea seguro en cmd.exe.

Licencia: Apache-2.0.
