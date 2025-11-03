from decimal import Decimal, ROUND_HALF_UP

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db.models import Sum, Count, Q, F

from apps.budget import models
from apps.categories.models import CategoriUsuario, Categoria
from apps.categories.choices import TipoCategoriaChoices
from apps.resultados.models import PorcentajeEjecucion
from apps.users.models import Usuario  # si lo necesitas para los tipos
from apps.tarea.models import Tarea
from apps.tarea.choices import TipoEstado
from apps.resultados.models import ControlConsumo

def _to_decimal(value) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal("0")


def _recalcular_porcentaje(usuario):
    """
    Recalcula para un usuario:
      - montoPlanificado: suma de montos de categorías tipo Gasto
      - montoEjecutado:   suma de montos de categorías tipo Gasto_Fijo
      - porcentaje:       (ejecutado / planificado) * 100, tope 100
    """
    if not usuario:
        return

    agregados_gasto = CategoriUsuario.objects.filter(
        usuario=usuario,
        categoria__tipo_categoria=TipoCategoriaChoices.GAS,
    ).aggregate(total=Sum("monto"))

    agregados_gasto_fijo = CategoriUsuario.objects.filter(
        usuario=usuario,
        categoria__tipo_categoria=TipoCategoriaChoices.GAS_FIJO,
    ).aggregate(total=Sum("monto"))

    planificado = _to_decimal(agregados_gasto.get("total") or 0)
    ejecutado = _to_decimal(agregados_gasto_fijo.get("total") or 0)

    if planificado > 0:
        porcentaje = (ejecutado / planificado) * Decimal("100")
        # Limitar a 100 para evitar porcentajes > 100%
        if porcentaje > Decimal("100"):
            porcentaje = Decimal("100")
        porcentaje = porcentaje.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    else:
        porcentaje = Decimal("0.00")

    pe, _ = PorcentajeEjecucion.objects.get_or_create(usuario=usuario)
    pe.montoPlanificado = planificado.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    pe.montoEjecutado = ejecutado.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    pe.porcentaje = porcentaje
    pe.save()


@receiver(post_save, sender=CategoriUsuario)
def categoriusuario_post_save(sender, instance: CategoriUsuario, **kwargs):
    _recalcular_porcentaje(instance.usuario)


@receiver(post_delete, sender=CategoriUsuario)
def categoriusuario_post_delete(sender, instance: CategoriUsuario, **kwargs):
    _recalcular_porcentaje(instance.usuario)


def _recalcular_control_consumo(usuario, delta_ajuste=0):
    """
    Recalcula y guarda ControlConsumo del usuario:
      - n_ajustesPresupuestales: SÓLO se incrementa si delta_ajuste != 0 (no se recalcula).
      - tareasRealizadasEnFecha: tareas con fechaProgramada == fechaEjecutada (ambas no nulas).
      - totalTareasProgramadas: total de tareas del usuario.
      - porcentaje: (realizadas / total) * 100, redondeado a 2 decimales.
    """
    if not usuario:
        return

    # 1) Métricas de tareas
    qs_tareas_usuario = Tarea.objects.filter(usuario=usuario)
    total_tareas = qs_tareas_usuario.count()
    realizadas_en_fecha = qs_tareas_usuario.filter(
        fechaProgramada__isnull=False,
        fechaEjecutada__isnull=False,
        fechaProgramada=F("fechaEjecutada"),
    ).count()

    if total_tareas > 0:
        porcentaje = (Decimal(realizadas_en_fecha) / Decimal(total_tareas)) * Decimal("100")
        porcentaje = porcentaje.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    else:
        porcentaje = Decimal("0.00")

    # 2) Upsert y actualización selectiva
    cc, _ = ControlConsumo.objects.get_or_create(usuario=usuario)

    # Incremento de ajustes SOLO cuando corresponde
    if delta_ajuste:
        cc.n_ajustesPresupuestales = (cc.n_ajustesPresupuestales or 0) + int(delta_ajuste)

    # Actualizamos siempre las métricas de tareas y el porcentaje
    cc.tareasRealizadasEnFecha = realizadas_en_fecha
    cc.totalTareasProgramadas = total_tareas
    cc.porcentaje = porcentaje
    cc.save()


# ---------- Detectar si cambió el monto (antes de guardar) ----------
@receiver(pre_save, sender=CategoriUsuario)
def categoriusuario_pre_save(sender, instance: CategoriUsuario, **kwargs):
    """
    Marca en instance._monto_changed si el monto cambió respecto al valor anterior.
    Solo marca True si la categoría ACTUAL es Gasto_Fijo.
    """
    instance._monto_changed = False  # default
    if not instance.pk:
        return  # creación: no cuenta como ajuste

    try:
        prev = CategoriUsuario.objects.select_related("categoria").get(pk=instance.pk)
    except CategoriUsuario.DoesNotExist:
        return

    # Solo consideramos ajustes si la CATEGORÍA ACTUAL es GAS_FIJO
    es_gasto_fijo_actual = (
        instance.categoria and instance.categoria.tipo_categoria == TipoCategoriaChoices.GAS_FIJO
    )

    if not es_gasto_fijo_actual:
        return

    prev_monto = prev.monto or 0
    nuevo_monto = instance.monto or 0
    # Compara numéricamente (float/Decimal). Si prefieres estrictamente Decimal, castea.
    if float(prev_monto) != float(nuevo_monto):
        instance._monto_changed = True


# ---------- Disparadores por cambios en CategoriUsuario ----------
@receiver(post_save, sender=CategoriUsuario)
def categoriusuario_post_save(sender, instance: CategoriUsuario, created, **kwargs):
    # Si fue update y cambió el monto en un Gasto_Fijo -> +1 ajuste
    delta = 1 if (not created and getattr(instance, "_monto_changed", False)) else 0
    _recalcular_control_consumo(instance.usuario, delta_ajuste=delta)


@receiver(post_delete, sender=CategoriUsuario)
def categoriusuario_post_delete(sender, instance: CategoriUsuario, **kwargs):
    # Al borrar una categoría de usuario NO se ajusta n_ajustesPresupuestales (histórico),
    # pero sí recalculamos métricas de tareas/porcentaje.
    _recalcular_control_consumo(instance.usuario, delta_ajuste=0)


# ---------- Disparadores por cambios en Tarea (afectan métricas de tareas) ----------
@receiver(post_save, sender=Tarea)
def tarea_post_save(sender, instance: Tarea, **kwargs):
    _recalcular_control_consumo(instance.usuario, delta_ajuste=0)


@receiver(post_delete, sender=Tarea)
def tarea_post_delete(sender, instance: Tarea, **kwargs):
    _recalcular_control_consumo(instance.usuario, delta_ajuste=0)