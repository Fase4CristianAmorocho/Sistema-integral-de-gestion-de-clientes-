from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import ClassVar


class SistemaFJError(Exception):
    """Excepcion base para todos los errores controlados del sistema."""


class ValidacionError(SistemaFJError):
    pass


class ServicioNoDisponibleError(SistemaFJError):
    pass


class ReservaError(SistemaFJError):
    pass


class CalculoCostoError(SistemaFJError):
    pass


class LoggerEventos:
    def __init__(self, ruta: str = "software_fj_eventos.log") -> None:
        self._ruta = Path(ruta)

    def registrar(self, nivel: str, mensaje: str) -> None:
        marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"[{marca_tiempo}] [{nivel.upper()}] {mensaje}\n"
        try:
            with self._ruta.open("a", encoding="utf-8") as archivo:
                archivo.write(linea)
        except OSError as exc:
            print(f"No fue posible escribir en el log: {exc}")


logger = LoggerEventos()


class EntidadSistema(ABC):
    _contador_ids: ClassVar[int] = 1

    def __init__(self, nombre: str) -> None:
        self._id = EntidadSistema._contador_ids
        EntidadSistema._contador_ids += 1
        self.nombre = nombre

    @property
    def id(self) -> int:
        return self._id

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ValidacionError("El nombre debe ser texto y tener minimo 3 caracteres.")
        self._nombre = valor.strip()

    @abstractmethod
    def describir(self) -> str:
        pass


class Cliente(EntidadSistema):
    def __init__(self, nombre: str, documento: str, correo: str, telefono: str) -> None:
        super().__init__(nombre)
        self.documento = documento
        self.correo = correo
        self.telefono = telefono

    @property
    def documento(self) -> str:
        return self.__documento

    @documento.setter
    def documento(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip().isdigit() or len(valor.strip()) < 6:
            raise ValidacionError("El documento debe contener solo numeros y minimo 6 digitos.")
        self.__documento = valor.strip()

    @property
    def correo(self) -> str:
        return self.__correo

    @correo.setter
    def correo(self, valor: str) -> None:
        if not isinstance(valor, str) or "@" not in valor or "." not in valor.split("@")[-1]:
            raise ValidacionError("El correo electronico no tiene un formato valido.")
        self.__correo = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        limpio = str(valor).replace(" ", "").replace("-", "")
        if not limpio.isdigit() or len(limpio) < 7:
            raise ValidacionError("El telefono debe tener minimo 7 digitos.")
        self.__telefono = limpio

    def describir(self) -> str:
        return f"Cliente #{self.id}: {self.nombre} - {self.correo}"


class Servicio(EntidadSistema, ABC):
    def __init__(self, nombre: str, tarifa_base: float, disponible: bool = True) -> None:
        super().__init__(nombre)
        self.tarifa_base = tarifa_base
        self.disponible = disponible

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, valor: float) -> None:
        try:
            tarifa = float(valor)
        except (TypeError, ValueError) as exc:
            raise ValidacionError("La tarifa base debe ser numerica.") from exc

        if tarifa <= 0:
            raise ValidacionError("La tarifa base debe ser mayor que cero.")
        self._tarifa_base = tarifa

    def validar_disponibilidad(self) -> None:
        if not self.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{self.nombre}' no esta disponible.")

    @abstractmethod
    def validar_parametros(self, duracion: float) -> None:
        pass

    @abstractmethod
    def calcular_costo(self, duracion: float, impuesto: float = 0.0, descuento: float = 0.0) -> float:
        pass


class ReservaSala(Servicio):
    def __init__(self, nombre: str, tarifa_base: float, capacidad: int, disponible: bool = True) -> None:
        super().__init__(nombre, tarifa_base, disponible)
        if capacidad < 1:
            raise ValidacionError("La capacidad de la sala debe ser mayor que cero.")
        self.capacidad = capacidad

    def validar_parametros(self, duracion: float) -> None:
        if duracion <= 0 or duracion > 12:
            raise ValidacionError("La reserva de sala debe durar entre 1 y 12 horas.")

    def calcular_costo(self, duracion: float, impuesto: float = 0.0, descuento: float = 0.0) -> float:
        self.validar_parametros(duracion)
        subtotal = self.tarifa_base * duracion
        recargo_capacidad = 1.15 if self.capacidad > 20 else 1.0
        return calcular_total(subtotal * recargo_capacidad, impuesto, descuento)

    def describir(self) -> str:
        return f"Sala '{self.nombre}', capacidad {self.capacidad}, tarifa ${self.tarifa_base:,.0f}/hora"


class AlquilerEquipo(Servicio):
    def __init__(self, nombre: str, tarifa_base: float, tipo_equipo: str, disponible: bool = True) -> None:
        super().__init__(nombre, tarifa_base, disponible)
        if not tipo_equipo or len(tipo_equipo.strip()) < 3:
            raise ValidacionError("El tipo de equipo es obligatorio.")
        self.tipo_equipo = tipo_equipo.strip()

    def validar_parametros(self, duracion: float) -> None:
        if duracion <= 0 or duracion > 30:
            raise ValidacionError("El alquiler de equipos debe durar entre 1 y 30 dias.")

    def calcular_costo(self, duracion: float, impuesto: float = 0.0, descuento: float = 0.0) -> float:
        self.validar_parametros(duracion)
        subtotal = self.tarifa_base * duracion
        descuento_larga_duracion = 0.08 if duracion >= 7 else 0.0
        return calcular_total(subtotal, impuesto, descuento + descuento_larga_duracion)

    def describir(self) -> str:
        return f"Equipo '{self.nombre}' ({self.tipo_equipo}), tarifa ${self.tarifa_base:,.0f}/dia"


class AsesoriaEspecializada(Servicio):
    def __init__(self, nombre: str, tarifa_base: float, especialidad: str, disponible: bool = True) -> None:
        super().__init__(nombre, tarifa_base, disponible)
        if not especialidad or len(especialidad.strip()) < 4:
            raise ValidacionError("La especialidad debe tener minimo 4 caracteres.")
        self.especialidad = especialidad.strip()

    def validar_parametros(self, duracion: float) -> None:
        if duracion <= 0 or duracion > 8:
            raise ValidacionError("La asesoria especializada debe durar entre 1 y 8 horas.")

    def calcular_costo(self, duracion: float, impuesto: float = 0.0, descuento: float = 0.0) -> float:
        self.validar_parametros(duracion)
        subtotal = self.tarifa_base * duracion
        recargo_especializado = 1.25
        return calcular_total(subtotal * recargo_especializado, impuesto, descuento)

    def describir(self) -> str:
        return f"Asesoria '{self.nombre}' en {self.especialidad}, tarifa ${self.tarifa_base:,.0f}/hora"


def calcular_total(subtotal: float, impuesto: float = 0.0, descuento: float = 0.0) -> float:
    """Simula sobrecarga mediante parametros opcionales: base, impuesto y descuento."""
    try:
        subtotal = float(subtotal)
        impuesto = float(impuesto)
        descuento = float(descuento)
    except (TypeError, ValueError) as exc:
        raise CalculoCostoError("Los valores del calculo deben ser numericos.") from exc

    if subtotal < 0:
        raise CalculoCostoError("El subtotal no puede ser negativo.")
    if not 0 <= impuesto <= 1:
        raise CalculoCostoError("El impuesto debe estar entre 0 y 1.")
    if not 0 <= descuento <= 1:
        raise CalculoCostoError("El descuento debe estar entre 0 y 1.")

    total = subtotal * (1 + impuesto) * (1 - descuento)
    if total < 0:
        raise CalculoCostoError("El calculo produjo un total inconsistente.")
    return round(total, 2)


class Reserva:
    ESTADOS_VALIDOS = {"creada", "confirmada", "cancelada", "procesada"}

    def __init__(self, cliente: Cliente, servicio: Servicio, duracion: float) -> None:
        if not isinstance(cliente, Cliente):
            raise ReservaError("La reserva requiere un cliente valido.")
        if not isinstance(servicio, Servicio):
            raise ReservaError("La reserva requiere un servicio valido.")
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "creada"

        try:
            self.servicio.validar_disponibilidad()
            self.servicio.validar_parametros(self.duracion)
        except SistemaFJError as exc:
            raise ReservaError("No fue posible crear la reserva.") from exc

    def confirmar(self) -> None:
        try:
            if self.estado != "creada":
                raise ReservaError("Solo se pueden confirmar reservas en estado creada.")
            self.servicio.validar_disponibilidad()
        except SistemaFJError as exc:
            logger.registrar("ERROR", f"Fallo al confirmar reserva: {exc}")
            raise
        else:
            self.estado = "confirmada"
            logger.registrar("INFO", f"Reserva confirmada para {self.cliente.nombre}: {self.servicio.nombre}")
        finally:
            logger.registrar("INFO", f"Revision de confirmacion finalizada. Estado actual: {self.estado}")

    def cancelar(self, motivo: str = "No especificado") -> None:
        if self.estado == "procesada":
            raise ReservaError("No se puede cancelar una reserva ya procesada.")
        self.estado = "cancelada"
        logger.registrar("INFO", f"Reserva cancelada. Motivo: {motivo}")

    def procesar(self, impuesto: float = 0.19, descuento: float = 0.0) -> float:
        try:
            if self.estado != "confirmada":
                raise ReservaError("Solo se pueden procesar reservas confirmadas.")
            total = self.servicio.calcular_costo(self.duracion, impuesto, descuento)
        except SistemaFJError as exc:
            logger.registrar("ERROR", f"Fallo al procesar reserva: {exc}")
            raise
        else:
            self.estado = "procesada"
            logger.registrar("INFO", f"Reserva procesada por ${total:,.2f}")
            return total
        finally:
            logger.registrar("INFO", f"Revision de procesamiento finalizada. Estado actual: {self.estado}")

    def describir(self) -> str:
        return (
            f"Reserva [{self.estado}] - Cliente: {self.cliente.nombre}, "
            f"Servicio: {self.servicio.nombre}, Duracion: {self.duracion}"
        )


class SistemaSoftwareFJ:
    def __init__(self) -> None:
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []

    def registrar_cliente(self, nombre: str, documento: str, correo: str, telefono: str) -> Cliente | None:
        try:
            cliente = Cliente(nombre, documento, correo, telefono)
        except SistemaFJError as exc:
            logger.registrar("ERROR", f"Cliente invalido: {exc}")
            print(f"Cliente no registrado: {exc}")
            return None
        else:
            self.clientes.append(cliente)
            logger.registrar("INFO", f"Cliente registrado: {cliente.describir()}")
            print(f"Cliente registrado: {cliente.describir()}")
            return cliente

    def agregar_servicio(self, servicio: Servicio) -> None:
        try:
            if not isinstance(servicio, Servicio):
                raise ValidacionError("El objeto recibido no es un servicio del sistema.")
        except SistemaFJError as exc:
            logger.registrar("ERROR", f"Servicio invalido: {exc}")
            print(f"Servicio no agregado: {exc}")
        else:
            self.servicios.append(servicio)
            logger.registrar("INFO", f"Servicio agregado: {servicio.describir()}")
            print(f"Servicio agregado: {servicio.describir()}")

    def crear_reserva(self, cliente: Cliente | None, servicio: Servicio | None, duracion: float) -> Reserva | None:
        try:
            reserva = Reserva(cliente, servicio, duracion)  # type: ignore[arg-type]
        except SistemaFJError as exc:
            logger.registrar("ERROR", f"Reserva fallida: {exc}")
            causa = f" Causa: {exc.__cause__}" if exc.__cause__ else ""
            print(f"Reserva no creada: {exc}.{causa}")
            return None
        else:
            self.reservas.append(reserva)
            logger.registrar("INFO", reserva.describir())
            print(f"Reserva creada: {reserva.describir()}")
            return reserva


def ejecutar_operacion(numero: int, descripcion: str, accion) -> None:
    print(f"\nOperacion {numero}: {descripcion}")
    try:
        accion()
    except SistemaFJError as exc:
        logger.registrar("ERROR", f"Operacion {numero} controlada: {exc}")
        print(f"Error controlado: {exc}")
    except Exception as exc:
        logger.registrar("CRITICAL", f"Operacion {numero} produjo un error inesperado: {exc}")
        print(f"Error inesperado controlado: {exc}")
    else:
        logger.registrar("INFO", f"Operacion {numero} completada correctamente.")
    finally:
        logger.registrar("INFO", f"Operacion {numero} finalizada.")


def main() -> None:
    Path("software_fj_eventos.log").write_text("", encoding="utf-8")
    sistema = SistemaSoftwareFJ()

    cliente_valido = None
    cliente_secundario = None
    sala = None
    equipo = None
    asesoria = None
    reserva_exitosa = None

    def op1() -> None:
        nonlocal cliente_valido
        cliente_valido = sistema.registrar_cliente("Laura Martinez", "1020304050", "laura@empresa.com", "3001234567")

    def op2() -> None:
        sistema.registrar_cliente("Ana", "ABC123", "ana.sin.correo", "12")

    def op3() -> None:
        nonlocal cliente_secundario
        cliente_secundario = sistema.registrar_cliente("Carlos Gomez", "99887766", "carlos@softwarefj.com", "6015557788")

    def op4() -> None:
        nonlocal sala
        sala = ReservaSala("Sala Ejecutiva Norte", 85000, 25)
        sistema.agregar_servicio(sala)

    def op5() -> None:
        ReservaSala("Sala Invalida", -20000, 0)

    def op6() -> None:
        nonlocal equipo
        equipo = AlquilerEquipo("Portatil Lenovo ThinkPad", 60000, "Computador")
        sistema.agregar_servicio(equipo)

    def op7() -> None:
        nonlocal asesoria
        asesoria = AsesoriaEspecializada("Arquitectura Cloud", 160000, "Cloud Computing", disponible=False)
        sistema.agregar_servicio(asesoria)

    def op8() -> None:
        nonlocal reserva_exitosa
        reserva_exitosa = sistema.crear_reserva(cliente_valido, sala, 4)
        if reserva_exitosa:
            reserva_exitosa.confirmar()
            total = reserva_exitosa.procesar(impuesto=0.19, descuento=0.05)
            print(f"Total procesado: ${total:,.2f}")

    def op9() -> None:
        sistema.crear_reserva(cliente_secundario, asesoria, 2)

    def op10() -> None:
        reserva = sistema.crear_reserva(cliente_valido, equipo, 40)
        if reserva:
            reserva.confirmar()

    def op11() -> None:
        reserva = sistema.crear_reserva(cliente_secundario, equipo, 5)
        if reserva:
            reserva.procesar()

    def op12() -> None:
        if reserva_exitosa:
            reserva_exitosa.cancelar("Solicitud posterior al procesamiento")

    operaciones = [
        ("Registrar cliente valido", op1),
        ("Intentar registrar cliente con datos invalidos", op2),
        ("Registrar segundo cliente valido", op3),
        ("Crear servicio valido de reserva de sala", op4),
        ("Intentar crear servicio con tarifa y capacidad invalidas", op5),
        ("Crear servicio valido de alquiler de equipo", op6),
        ("Crear asesoria especializada no disponible", op7),
        ("Crear, confirmar y procesar reserva exitosa", op8),
        ("Intentar reservar un servicio no disponible", op9),
        ("Intentar reservar equipo con duracion invalida", op10),
        ("Intentar procesar reserva sin confirmar", op11),
        ("Intentar cancelar reserva ya procesada", op12),
    ]

    for indice, (descripcion, accion) in enumerate(operaciones, start=1):
        ejecutar_operacion(indice, descripcion, accion)

    print("\nResumen final")
    print(f"Clientes registrados: {len(sistema.clientes)}")
    print(f"Servicios agregados: {len(sistema.servicios)}")
    print(f"Reservas creadas: {len(sistema.reservas)}")
    print("Log generado: software_fj_eventos.log")


if __name__ == "__main__":
    main()

