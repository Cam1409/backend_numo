from apps.categories.models import CategoriUsuario, Categoria
from rest_framework import serializers
from django.db.models.functions import ExtractWeekDay
from django.db.models import Sum
from datetime import timedelta
from django.utils import timezone
from django.db.models.functions import ExtractMonth


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__"


class ResumenSemanalSerializer(serializers.Serializer):
    total_gastos = serializers.SerializerMethodField()
    dia_mayor_gasto = serializers.SerializerMethodField()
    ultimo_ingreso_semana = serializers.SerializerMethodField()
    dia_ultimo_ingreso = serializers.SerializerMethodField()
    categoria_mayor_gasto_dia = serializers.SerializerMethodField()
    categoria_menor_gasto_dia = serializers.SerializerMethodField()
    ultimo_gasto_dia = serializers.SerializerMethodField()
    ultimo_ingreso_dia = serializers.SerializerMethodField()
    gasto_categoria = serializers.SerializerMethodField()

    class Meta:
        model = CategoriUsuario
        fields = "__all__"

    def _rango_semana_actual(self):
        """📅 Devuelve el rango (inicio_semana, fin_semana) para esta semana."""
        hoy = timezone.now()
        inicio_semana = hoy - timedelta(days=hoy.weekday())  # Lunes
        fin_semana = inicio_semana + timedelta(days=6, hours=23, minutes=59, seconds=59)
        return inicio_semana, fin_semana

    def get_total_gastos(self, obj):
        usuario = obj.usuario
        inicio_semana, fin_semana = self._rango_semana_actual()

        gastos = CategoriUsuario.objects.filter(
            usuario=usuario,
            categoria__tipo_categoria="Gasto",
            fecha__range=[inicio_semana, fin_semana],
        )

        total = sum(g.monto or 0 for g in gastos)
        return round(total, 2)

    def get_dia_mayor_gasto(self, obj):
        usuario = obj.usuario
        inicio_semana, fin_semana = self._rango_semana_actual()

        gastos_por_dia = (
            CategoriUsuario.objects.filter(
                usuario=usuario,
                categoria__tipo_categoria="Gasto",
                fecha__range=[inicio_semana, fin_semana],
            )
            .annotate(dia_semana=ExtractWeekDay("fecha"))
            .values("dia_semana")
            .annotate(total=Sum("monto"))
            .order_by("-total")
        )

        if not gastos_por_dia:
            return "No tiene"

        dias_semana = {
            1: "Domingo",
            2: "Lunes",
            3: "Martes",
            4: "Miércoles",
            5: "Jueves",
            6: "Viernes",
            7: "Sábado",
        }

        mayor = gastos_por_dia[0]
        return dias_semana.get(mayor["dia_semana"], "Desconocido")

    def get_ultimo_ingreso_semana(self, obj):
        usuario = obj.usuario
        inicio_semana, fin_semana = self._rango_semana_actual()

        ultimo = (
            CategoriUsuario.objects.filter(
                usuario=usuario,
                categoria__tipo_categoria="Ingreso",
                fecha__range=[inicio_semana, fin_semana],
            )
            .order_by("-fecha")
            .select_related("categoria")
            .first()
        )

        if not ultimo or ultimo.monto is None:
            return "No tiene"

        return round(ultimo.monto, 2)

    def get_dia_ultimo_ingreso(self, obj):
        usuario = obj.usuario
        inicio_semana, fin_semana = self._rango_semana_actual()

        ultimo = (
            CategoriUsuario.objects.filter(
                usuario=usuario,
                categoria__tipo_categoria="Ingreso",
                fecha__range=[inicio_semana, fin_semana],
            )
            .order_by("-fecha")
            .first()
        )

        if not ultimo or not ultimo.fecha:
            return "No tiene"

        dias_semana = {
            0: "Lunes",
            1: "Martes",
            2: "Miércoles",
            3: "Jueves",
            4: "Viernes",
            5: "Sábado",
            6: "Domingo",
        }

        return dias_semana.get(ultimo.fecha.weekday(), "Desconocido")

    def get_categoria_mayor_gasto_dia(self, obj):
        usuario = obj.usuario
        inicio_semana, fin_semana = self._rango_semana_actual()

        gastos_por_dia = (
            CategoriUsuario.objects.filter(
                usuario=usuario,
                categoria__tipo_categoria="Gasto",
                fecha__range=[inicio_semana, fin_semana],
            )
            .annotate(dia_semana=ExtractWeekDay("fecha"))
            .values("dia_semana")
            .annotate(total=Sum("monto"))
            .order_by("-total")
        )

        if not gastos_por_dia:
            return "No tiene"

        dia_mayor = gastos_por_dia[0]["dia_semana"]

        gastos_dia = (
            CategoriUsuario.objects.filter(
                usuario=usuario,
                categoria__tipo_categoria="Gasto",
                fecha__range=[inicio_semana, fin_semana],
                fecha__week_day=dia_mayor,
            )
            .values("categoria__nombre")
            .annotate(total=Sum("monto"))
            .order_by("-total")
        )

        if not gastos_dia:
            return "No tiene"

        return gastos_dia[0]["categoria__nombre"]

    def get_categoria_menor_gasto_dia(self, obj):
        usuario = obj.usuario
        inicio_semana, fin_semana = self._rango_semana_actual()

        gastos_por_dia = (
            CategoriUsuario.objects.filter(
                usuario=usuario,
                categoria__tipo_categoria="Gasto",
                fecha__range=[inicio_semana, fin_semana],
            )
            .annotate(dia_semana=ExtractWeekDay("fecha"))
            .values("dia_semana")
            .annotate(total=Sum("monto"))
            .order_by("total")
        )

        if not gastos_por_dia:
            return "No tiene"

        dia_menor = gastos_por_dia[0]["dia_semana"]

        gastos_dia = (
            CategoriUsuario.objects.filter(
                usuario=usuario,
                categoria__tipo_categoria="Gasto",
                fecha__range=[inicio_semana, fin_semana],
                fecha__week_day=dia_menor,
            )
            .values("categoria__nombre")
            .annotate(total=Sum("monto"))
            .order_by("total")
        )

        if not gastos_dia:
            return "No tiene"

        return gastos_dia[0]["categoria__nombre"]

    def get_ultimo_gasto_dia(self, obj):
        usuario = obj.usuario
        hoy = timezone.now().date()
        inicio_dia = timezone.make_aware(
            timezone.datetime.combine(hoy, timezone.datetime.min.time())
        )
        fin_dia = timezone.make_aware(
            timezone.datetime.combine(hoy, timezone.datetime.max.time())
        )

        gasto = (
            CategoriUsuario.objects.filter(
                usuario=usuario,
                categoria__tipo_categoria="Gasto",
                fecha__range=[inicio_dia, fin_dia],
            )
            .order_by("-fecha")
            .first()
        )

        if not gasto:
            return {"monto": 0, "fecha": timezone.now()}

        return {"monto": round(gasto.monto or 0, 2), "fecha": gasto.fecha}

    def get_ultimo_ingreso_dia(self, obj):
        usuario = obj.usuario
        hoy = timezone.now().date()
        inicio_dia = timezone.make_aware(
            timezone.datetime.combine(hoy, timezone.datetime.min.time())
        )
        fin_dia = timezone.make_aware(
            timezone.datetime.combine(hoy, timezone.datetime.max.time())
        )

        ingreso = (
            CategoriUsuario.objects.filter(
                usuario=usuario,
                categoria__tipo_categoria="Ingreso",
                fecha__range=[inicio_dia, fin_dia],
            )
            .order_by("-fecha")
            .first()
        )

        if not ingreso:
            return {"monto": 0, "fecha": timezone.now()}

        return {"monto": round(ingreso.monto or 0, 2), "fecha": ingreso.fecha}

    def get_gasto_categoria(self, obj):
        usuario = obj.usuario

        # Agrupamos por mes y sumamos los montos de las categorías tipo "Gasto"
        gastos_mensuales = (
            CategoriUsuario.objects.filter(
                usuario=usuario,
                categoria__tipo_categoria="Gasto",
                fecha__isnull=False
            )
            .annotate(mes=ExtractMonth("fecha"))
            .values("mes")
            .annotate(total=Sum("monto"))
            .order_by("mes")
        )

        # Diccionario base de meses (todos inicializados en 0)
        meses = {
            1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
            5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
            9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
        }

        gasto_categoria = {nombre: 0.0 for nombre in meses.values()}

        # Actualizamos con los valores reales si existen
        for item in gastos_mensuales:
            mes_nombre = meses.get(item["mes"])
            gasto_categoria[mes_nombre] = round(item["total"] or 0, 2)

        return gasto_categoria



class CategoriUsuarioSerializer(serializers.ModelSerializer):
    nombre_categoria = serializers.CharField(source="categoria.nombre", read_only=True)

    class Meta:
        model = CategoriUsuario
        fields = "__all__"

    def get_nombre_categoria(self, obj):
        return obj.categoria.nombre if obj.categoria else None

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # Reemplaza el id por el nombre en la respuesta
        rep["categoria"] = instance.categoria.nombre if instance.categoria else None
        return rep
