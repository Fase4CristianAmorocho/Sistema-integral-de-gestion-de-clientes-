# Sistema-integral-de-gestion-de-clientes-

Entrega para la empresa ficticia **Software FJ**. El proyecto implementa un sistema orientado a objetos sin base de datos, usando objetos y listas internas para gestionar clientes, servicios y reservas.

## Archivos

- `software_fj_sistema.py`: aplicacion principal con clases, excepciones, simulacion y logs.
- `software_fj_eventos.log`: se genera automaticamente al ejecutar el programa.

## Como ejecutar

Desde esta carpeta:

```bash
python software_fj_sistema.py
```

## Elementos implementados

- Clase abstracta `EntidadSistema`.
- Clase `Cliente` con encapsulacion y validaciones robustas.
- Clase abstracta `Servicio`.
- Servicios derivados:
  - `ReservaSala`
  - `AlquilerEquipo`
  - `AsesoriaEspecializada`
- Clase `Reserva` con confirmacion, cancelacion y procesamiento.
- Polimorfismo mediante `describir`, `validar_parametros` y `calcular_costo`.
- Simulacion de sobrecarga mediante parametros opcionales en el calculo de costos.
- Excepciones personalizadas y encadenamiento de excepciones con `raise ... from`.
- Uso de `try/except`, `try/except/else` y `try/except/finally`.
- Registro de errores y eventos relevantes en archivo de logs.
- 12 operaciones simuladas, incluyendo casos validos e invalidos.
