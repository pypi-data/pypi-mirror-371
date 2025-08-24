from django.db import models
from django.db.models.expressions import Window, F
from django.db.models.functions.window import RowNumber
from django.utils.translation import gettext_lazy as _


class SimpleOrderingManagerMixin(models.Manager):

    def regenerate_ordering(self):
        queryset = (
            self.get_queryset()
            .exclude(ordering__isnull=True)
            .alias(row_number=Window(expression=RowNumber(), order_by="ordering"))
            .annotate(new_ordering=F("row_number") * 100)
        )
        for obj in queryset:
            obj.ordering = obj.new_ordering

        self.bulk_update(queryset, fields=("ordering",), batch_size=1000)


class SimpleOrderingModelMixin(models.Model):
    ordering = models.PositiveBigIntegerField(
        _("ordering"), db_index=True, null=True, blank=True
    )

    objects = SimpleOrderingManagerMixin()

    class Meta:
        ordering = ("ordering",)
        abstract = True
