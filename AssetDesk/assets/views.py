from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import AssetForm, AssetAssignmentForm
from .models import Asset, AssetCategory, AssetAssignment


class CanManageAssetsMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.can_manage_assets


class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = "assets/asset_list.html"
    context_object_name = "assets"
    paginate_by = 20

    def get_queryset(self):

        qs = (
            Asset.objects
            .select_related(
                "category",
                "department",
            )
            .order_by("asset_code")
        )

        user = self.request.user

        # فقط Asset های خود کارمند
        if not user.can_manage_assets:
            qs = qs.filter(
                assignments__employee=user,
            ).distinct()

        status = self.request.GET.get("status")
        category = self.request.GET.get("category")
        search = self.request.GET.get("search")

        if status:
            qs = qs.filter(status=status)

        if category:
            qs = qs.filter(category_id=category)

        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(asset_code__icontains=search)
                | Q(serial_number__icontains=search)
                | Q(brand__icontains=search)
                | Q(model__icontains=search)
            )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = AssetCategory.objects.order_by("name")
        context["status_choices"] = Asset.AssetStatus.choices
        context["current_status"] = self.request.GET.get("status", "")
        context["current_category"] = self.request.GET.get("category", "")
        context["search"] = self.request.GET.get("search", "")
        return context


class AssetDetailView(
    LoginRequiredMixin,
    DetailView
):
    model = Asset
    template_name = "assets/asset_detail.html"
    context_object_name = "asset"

    def get_queryset(self):

        return (
            Asset.objects
            .select_related(
                "category",
                "department",
            )
            .prefetch_related(
                Prefetch(
                    "assignments",
                    queryset=(
                        AssetAssignment.objects
                        .select_related("employee")
                        .order_by("-assigned_at")
                    ),
                )
            )
        )

    def dispatch(
        self,
        request,
        *args,
        **kwargs
    ):

        asset = self.get_object()

        if request.user.can_manage_assets:
            return super().dispatch(
                request,
                *args,
                **kwargs,
            )

        has_access = asset.assignments.filter(
            employee=request.user
        ).exists()

        if not has_access:

            messages.error(
                request,
                "You do not have access to this asset."
            )

            return redirect(
                "asset-list"
            )

        return super().dispatch(
            request,
            *args,
            **kwargs,
        )

    def get_context_data(
        self,
        **kwargs
    ):
        context = super().get_context_data(
            **kwargs
        )

        context["assignments"] = (
            self.object.assignments.all()
        )

        context["current_holder"] = (
            self.object.current_holder
        )

        context["current_assignment"] = (
            self.object.current_assignment
        )

        return context

class AssetCreateView(LoginRequiredMixin, CanManageAssetsMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = "assets/asset_form.html"
    success_url = reverse_lazy("asset-list")

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Asset «{form.instance.name}» created successfully."
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Add New Asset"
        context["btn_label"] = "Create Asset"
        return context


class AssetUpdateView(LoginRequiredMixin, CanManageAssetsMixin, UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = "assets/asset_form.html"
    success_url = reverse_lazy("asset-list")

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Asset «{form.instance.name}» updated successfully."
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = f"Edit Asset — {self.object.asset_code}"
        context["btn_label"] = "Save Changes"
        return context


class AssetDeleteView(LoginRequiredMixin, CanManageAssetsMixin, DeleteView):
    model = Asset
    template_name = "assets/asset_confirm_delete.html"
    success_url = reverse_lazy("asset-list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        asset_name = self.object.name
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"Asset «{asset_name}» deleted.")
        return response


class AssetAssignView(LoginRequiredMixin, CanManageAssetsMixin, View):
    template_name = "assets/asset_assign.html"

    def get(self, request, pk):
        asset = get_object_or_404(Asset.objects.select_related("category", "department"), pk=pk)

        if not asset.is_available:
            messages.error(request, f"Asset «{asset.name}» is not available for assignment.")
            return redirect("asset-detail", pk=pk)

        form = AssetAssignmentForm(asset=asset)
        return render(
            request,
            self.template_name,
            {
                "asset": asset,
                "form": form,
            },
        )

    def post(self, request, pk):
        asset = get_object_or_404(Asset.objects.select_related("category", "department"), pk=pk)

        if not asset.is_available:
            messages.error(request, f"Asset «{asset.name}» is not available for assignment.")
            return redirect("asset-detail", pk=pk)

        form = AssetAssignmentForm(data=request.POST, asset=asset)

        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {
                    "asset": asset,
                    "form": form,
                },
            )

        try:
            with transaction.atomic():
                assignment = form.save(commit=False)
                assignment.asset = asset
                assignment.save()

            messages.success(
                request,
                f"Asset «{asset.name}» assigned successfully."
            )
            return redirect("asset-detail", pk=pk)

        except Exception as e:
            form.add_error(None, str(e))
            return render(
                request,
                self.template_name,
                {
                    "asset": asset,
                    "form": form,
                },
            )


class AssetReturnView(LoginRequiredMixin, CanManageAssetsMixin, View):
    def post(self, request, pk):
        with transaction.atomic():
            assignment = get_object_or_404(
                AssetAssignment.objects.select_related("asset", "employee"),
                pk=pk,
                returned_at__isnull=True,
            )
            assignment.returned_at = timezone.now()
            assignment.save()

        messages.success(
            request,
            f"Asset «{assignment.asset.name}» returned successfully."
        )
        return redirect("asset-detail", pk=assignment.asset.pk)