from django.contrib import admin, messages
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.translation import gettext_lazy as _, gettext
from django_object_actions import DjangoObjectActions, action


class SimpleOrderingModelAdminMixin(DjangoObjectActions, admin.ModelAdmin):
    list_editable = ()
    changelist_actions = ("regenerate_ordering",)

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        if isinstance(list_display, tuple):
            list_display = list(list_display)
        if "ordering" not in list_display:
            list_display.append("ordering")
        return list_display

    def get_exclude(self, request, obj=None):
        exclude = super().get_exclude(request, obj)
        if exclude is None:
            return ("ordering",)

        if isinstance(exclude, tuple):
            exclude = list(exclude)
        if "ordering" not in exclude:
            exclude.append("ordering")
        return exclude

    def changelist_view(self, request, extra_context=None):
        self.list_editable = self.get_list_editable()

        return super().changelist_view(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        urls.insert(
            0,
            path(
                "regenerate-ordering/",
                self.admin_site.admin_view(self.regenerate_ordering_view),
                name=f"{self.opts.app_label}_{self.opts.model_name}_regenerate_ordering",
            ),
        )
        return urls

    def get_changelist_actions(self, request):
        changelist_actions = super().get_changelist_actions(request)
        if isinstance(changelist_actions, tuple):
            changelist_actions = list(changelist_actions)
        if (
            not self.has_change_permission(request)
            and "regenerate_ordering" in changelist_actions
        ):
            changelist_actions.remove("regenerate_ordering")
        return changelist_actions

    def _get_tool_dict(self, tool_name):
        tool_dict = super()._get_tool_dict(tool_name)
        if tool_dict["name"] == "regenerate_ordering":
            tool_dict["label"] = tool_dict["label"] % {
                "model_verbose_name_plural": self.opts.verbose_name_plural.title()
            }
        return tool_dict

    def _get_button_attrs(self, tool):
        tool_name = tool.__name__
        if tool_name == "regenerate_ordering":
            tool_method = getattr(self.__class__, tool_name)
            tool_method.short_description = tool_method.short_description % {
                "model_verbose_name_plural": self.opts.verbose_name_plural
            }

        return super()._get_button_attrs(tool)

    def get_list_editable(self):
        list_editable = self.list_editable
        if isinstance(list_editable, tuple):
            list_editable = list(list_editable)
        if "ordering" not in list_editable:
            list_editable.append("ordering")
        return list_editable

    @action(
        label=_("Regenerate %(model_verbose_name_plural)s Ordering"),
        description=_(
            "This process assigns new ordering numbers with a gap of 100 to %(model_verbose_name_plural)s "
            "without touching their current order to simplify inserting and moving "
            "them."
        ),
        permissions=("change",),
    )
    def regenerate_ordering(self, _request, _queryset):
        return redirect(admin_urlname(self.opts, "regenerate_ordering"))

    def regenerate_ordering_view(self, request):
        if not self.has_change_permission(request):
            raise PermissionDenied

        allowed_methods = ("GET", "POST")
        if request.method not in allowed_methods:
            return HttpResponseNotAllowed(permitted_methods=allowed_methods)

        if request.method == "GET":
            context = {
                "opts": self.opts,
                "title": gettext("Regenerate %(model_verbose_name_plural)s Ordering")
                % {
                    "model_verbose_name_plural": self.opts.verbose_name_plural.title(),
                },
                **self.admin_site.each_context(request),
            }
            return TemplateResponse(
                request,
                "django_simple_ordering/admin/ordering_regenerate_confirmation.html",
                context,
            )

        self.model.objects.regenerate_ordering()
        self.message_user(
            request,
            gettext(
                "%(model_verbose_name_plural)s ordering numbers were successfully "
                "regenerated."
            )
            % {"model_verbose_name_plural": self.opts.verbose_name_plural.title()},
            messages.SUCCESS,
        )
        return redirect(admin_urlname(self.opts, "changelist"))
