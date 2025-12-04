from decimal import Decimal, ROUND_HALF_UP

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db.models import Sum, F

from apps.categories.models import CategoriUsuario, Categoria
from apps.categories.choices import TipoCategoriaChoices
from apps.resultados.models import PorcentajeEjecucion, ControlConsumo
from apps.tarea.models import Tarea


def _to_decimal(value) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal("0")


# ===================== PORCENTAJE DE EJECUCIÓN =====================

def _recalcular_porcentaje(usuario):
    """
    Recalcula para un usuario:
      - montoPlanificado: suma de montos de categorías tipo Gasto
      - montoEjecutado:   suma de montos de categorías tipo Gasto_Fijo
      - porcentaje:       (ejecutado / planificado) * 100, tope 100
    """
    if not usuario:
        #print("⛔ Usuario vacío, no se recalcula nada.")
        return

    #print(f"\n🔄 [PORCENTAJE] Recalculando para usuario ID={usuario.pk} ...")

    agregados_gasto = CategoriUsuario.objects.filter(
        usuario=usuario,
        categoria__tipo_categoria=TipoCategoriaChoices.GAS,
    ).aggregate(total=Sum("monto"))

    agregados_gasto_fijo = CategoriUsuario.objects.filter(
        usuario=usuario,
        categoria__tipo_categoria=TipoCategoriaChoices.GAS_FIJO,
    ).aggregate(total=Sum("monto"))

    #print(f"📌 [PORCENTAJE] Gasto planificado: {agregados_gasto}")
    #print(f"📌 [PORCENTAJE] Gasto fijo ejecutado: {agregados_gasto_fijo}")

    planificado = _to_decimal(agregados_gasto.get("total") or 0)
    ejecutado = _to_decimal(agregados_gasto_fijo.get("total") or 0)

    #print(f"➡️ [PORCENTAJE] Monto planificado = {planificado}")
    #print(f"➡️ [PORCENTAJE] Monto ejecutado   = {ejecutado}")

    if planificado > 0:
        porcentaje = (ejecutado / planificado) * Decimal("100")
        #print(f"🔢 [PORCENTAJE] Porcentaje calculado (sin tope) = {porcentaje}")

        if porcentaje > Decimal("100"):
            #print("⚠️ [PORCENTAJE] > 100, se limita a 100.")
            porcentaje = Decimal("100")

        porcentaje = porcentaje.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        #print(f"✔️ [PORCENTAJE] Porcentaje final redondeado = {porcentaje}")
    else:
        #print("⚠️ [PORCENTAJE] Planificado es 0 → porcentaje = 0.00")
        porcentaje = Decimal("0.00")

    pe, creado = PorcentajeEjecucion.objects.get_or_create(usuario=usuario)
    #print(f"📘 [PORCENTAJE] Registro existente? {'Sí' if not creado else 'No, se creó uno nuevo.'}")

    pe.montoPlanificado = planificado.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    pe.montoEjecutado = ejecutado.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    pe.porcentaje = porcentaje

    #print(f"💾 [PORCENTAJE] Guardando:")
    #print(f"   - montoPlanificado = {pe.montoPlanificado}")
    #print(f"   - montoEjecutado   = {pe.montoEjecutado}")
    #print(f"   - porcentaje       = {pe.porcentaje}")

    pe.save()
    #print("✅ [PORCENTAJE] Guardado correctamente.\n")


# ===================== CONTROL DEL CONSUMO =====================

def _recalcular_control_consumo(usuario, delta_ajuste=0):
    """
    Recalcula y guarda ControlConsumo del usuario.
    """
    if not usuario:
        #print("⛔ [CONTROL] Usuario vacío, no se recalcula nada.")
        return

    #print(f"\n🔄 [CONTROL] Recalculando para usuario ID={usuario.pk} ...")

    qs_tareas_usuario = Tarea.objects.filter(usuario=usuario)
    total_tareas = qs_tareas_usuario.count()
    realizadas_en_fecha = qs_tareas_usuario.filter(
        fechaProgramada__isnull=False,
        fechaEjecutada__isnull=False,
        fechaProgramada=F("fechaEjecutada"),
    ).count()

    #print(f"📌 [CONTROL] total_tareas = {total_tareas}")
    #print(f"📌 [CONTROL] realizadas_en_fecha = {realizadas_en_fecha}")
    #print(f"📌 [CONTROL] delta_ajuste recibido = {delta_ajuste}")

    if total_tareas > 0:
        porcentaje = (Decimal(realizadas_en_fecha) / Decimal(total_tareas)) * Decimal("100")
        porcentaje = porcentaje.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    else:
        porcentaje = Decimal("0.00")

    cc, _ = ControlConsumo.objects.get_or_create(usuario=usuario)

    if delta_ajuste:
        cc.n_ajustesPresupuestales = (cc.n_ajustesPresupuestales or 0) + int(delta_ajuste)

    cc.tareasRealizadasEnFecha = realizadas_en_fecha
    cc.totalTareasProgramadas = total_tareas
    cc.porcentaje = porcentaje

    #print(f"💾 [CONTROL] Guardando:")
    #print(f"   - n_ajustesPresupuestales = {cc.n_ajustesPresupuestales}")
    #print(f"   - tareasRealizadasEnFecha = {cc.tareasRealizadasEnFecha}")
    #print(f"   - totalTareasProgramadas  = {cc.totalTareasProgramadas}")
    #print(f"   - porcentaje              = {cc.porcentaje}")

    cc.save()
    #print("✅ [CONTROL] Guardado correctamente.\n")


# ===================== SEÑALES =====================

@receiver(pre_save, sender=CategoriUsuario)
def categoriusuario_pre_save(sender, instance: CategoriUsuario, **kwargs):
    """
    Marca en instance._monto_changed si el monto cambió respecto al valor anterior.
    Solo marca True si la categoría ACTUAL es Gasto_Fijo.
    """
    instance._monto_changed = False
    if not instance.pk:
        return  # creación: no cuenta como ajuste

    try:
        prev = CategoriUsuario.objects.select_related("categoria").get(pk=instance.pk)
    except CategoriUsuario.DoesNotExist:
        return

    es_gasto_fijo_actual = (
        instance.categoria and instance.categoria.tipo_categoria == TipoCategoriaChoices.GAS_FIJO
    )
    if not es_gasto_fijo_actual:
        return

    prev_monto = prev.monto or 0
    nuevo_monto = instance.monto or 0

    if float(prev_monto) != float(nuevo_monto):
        #print(f"✏️ [CONTROL] Cambio de monto detectado en CategoriUsuario ID={instance.pk}")
        instance._monto_changed = True


@receiver(post_save, sender=CategoriUsuario)
def categoriusuario_post_save(sender, instance: CategoriUsuario, created, **kwargs):
    #print(f"🟩 [SIGNAL] post_save CategoriUsuario ID={instance.pk}, created={created}")

    # 1. Siempre recalculamos porcentaje de ejecución
    _recalcular_porcentaje(instance.usuario)

    # 2. Ajuste en control de consumo SOLO si hubo cambio de monto en gasto fijo
    delta = 1 if (not created and getattr(instance, "_monto_changed", False)) else 0
    _recalcular_control_consumo(instance.usuario, delta_ajuste=delta)


@receiver(post_delete, sender=CategoriUsuario)
def categoriusuario_post_delete(sender, instance: CategoriUsuario, **kwargs):
    #print(f"🟥 [SIGNAL] post_delete CategoriUsuario ID={instance.pk}")

    # Al eliminar: recalculamos porcentaje y control (sin sumar ajustes)
    _recalcular_porcentaje(instance.usuario)
    _recalcular_control_consumo(instance.usuario, delta_ajuste=0)


@receiver(post_save, sender=Tarea)
def tarea_post_save(sender, instance: Tarea, **kwargs):
    #print(f"🟦 [SIGNAL] post_save Tarea ID={instance.pk}")
    _recalcular_control_consumo(instance.usuario, delta_ajuste=0)


@receiver(post_delete, sender=Tarea)
def tarea_post_delete(sender, instance: Tarea, **kwargs):
    #print(f"🟪 [SIGNAL] post_delete Tarea ID={instance.pk}")
    _recalcular_control_consumo(instance.usuario, delta_ajuste=0)
