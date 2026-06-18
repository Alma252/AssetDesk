from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .models import Ticket, TicketComment
from .forms import (
    TicketForm,
    TicketUpdateForm,
    TicketAssignForm,
    TicketCommentForm,
)


class CanManageTicketsMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.request.user.is_staff_member


class TicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = "tickets/ticket_list.html"
    context_object_name = "tickets"
    paginate_by = 20

    def get_queryset(self):

        qs = (
            Ticket.objects
            .select_related(
                "created_by",
                "assigned_to",
                "asset",
            )
            .order_by("-created_at")
        )

        user = self.request.user

        if not user.is_staff_member:
            qs = qs.filter(created_by=user)

        status = self.request.GET.get("status")
        priority = self.request.GET.get("priority")
        search = self.request.GET.get("search")

        if status:
            qs = qs.filter(status=status)

        if priority:
            qs = qs.filter(priority=priority)

        if search:
            qs = qs.filter(
                Q(ticket_no__icontains=search)
                | Q(title__icontains=search)
                | Q(description__icontains=search)
            )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["status_choices"] = Ticket.Status.choices
        context["priority_choices"] = Ticket.Priority.choices

        context["current_status"] = self.request.GET.get(
            "status",
            "",
        )

        context["current_priority"] = self.request.GET.get(
            "priority",
            "",
        )

        context["search"] = self.request.GET.get(
            "search",
            "",
        )

        return context


class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = "tickets/ticket_detail.html"
    context_object_name = "ticket"

    def get_queryset(self):
        return (
            Ticket.objects
            .select_related(
                "created_by",
                "assigned_to",
                "asset",
            )
            .prefetch_related(
                Prefetch(
                    "comments",
                    queryset=TicketComment.objects.select_related(
                        "author"
                    )
                )
            )
        )

    def dispatch(self, request, *args, **kwargs):

        ticket = self.get_object()

        if (
            not request.user.is_staff_member
            and ticket.created_by != request.user
        ):
            messages.error(
                request,
                "You do not have access to this ticket.",
            )
            return redirect("ticket-list")

        return super().dispatch(
            request,
            *args,
            **kwargs,
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["comment_form"] = TicketCommentForm()

        if self.request.user.is_staff_member:
            context["assign_form"] = TicketAssignForm(
                instance=self.object
            )

        return context


class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = "tickets/ticket_form.html"

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user

        return kwargs

    def form_valid(self, form):

        form.instance.created_by = self.request.user

        messages.success(
            self.request,
            "Ticket created successfully.",
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "ticket-detail",
            kwargs={
                "pk": self.object.pk
            },
        )


class TicketUpdateView(
    LoginRequiredMixin,
    CanManageTicketsMixin,
    UpdateView,
):
    model = Ticket
    form_class = TicketUpdateForm
    template_name = "tickets/ticket_form.html"

    def form_valid(self, form):

        messages.success(
            self.request,
            "Ticket updated successfully.",
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "ticket-detail",
            kwargs={
                "pk": self.object.pk
            },
        )


class TicketDeleteView(
    LoginRequiredMixin,
    CanManageTicketsMixin,
    DeleteView,
):
    model = Ticket
    template_name = "tickets/ticket_confirm_delete.html"
    success_url = reverse_lazy("ticket-list")

    def form_valid(self, form):

        messages.success(
            self.request,
            f"Ticket {self.object.ticket_no} deleted.",
        )

        return super().form_valid(form)


class TicketAssignView(
    LoginRequiredMixin,
    CanManageTicketsMixin,
    View,
):

    def post(self, request, pk):

        ticket = get_object_or_404(
            Ticket,
            pk=pk,
        )

        form = TicketAssignForm(
            request.POST,
            instance=ticket,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Ticket updated successfully.",
            )

        else:

            messages.error(
                request,
                "Please select a valid assignee.",
            )

        return redirect(
            "ticket-detail",
            pk=pk,
        )


class TicketResolveView(
    LoginRequiredMixin,
    CanManageTicketsMixin,
    View,
):

    def post(self, request, pk):

        ticket = get_object_or_404(
            Ticket,
            pk=pk,
        )

        if not ticket.assigned_to:

            messages.error(
                request,
                "Cannot resolve a ticket without assignee.",
            )

            return redirect(
                "ticket-detail",
                pk=pk,
            )

        ticket.status = Ticket.Status.RESOLVED
        ticket.save()

        messages.success(
            request,
            "Ticket resolved successfully.",
        )

        return redirect(
            "ticket-detail",
            pk=pk,
        )


class TicketCloseView(
    LoginRequiredMixin,
    View,
):

    def post(self, request, pk):

        ticket = get_object_or_404(
            Ticket,
            pk=pk,
        )

        if (
            ticket.created_by != request.user
            and not request.user.is_staff_member
        ):
            messages.error(
                request,
                "Permission denied.",
            )

            return redirect(
                "ticket-detail",
                pk=pk,
            )

        ticket.status = Ticket.Status.CLOSED
        ticket.save()

        messages.success(
            request,
            "Ticket closed successfully.",
        )

        return redirect(
            "ticket-detail",
            pk=pk,
        )


class TicketCommentCreateView(
    LoginRequiredMixin,
    View,
):

    def post(self, request, pk):

        ticket = get_object_or_404(
            Ticket,
            pk=pk,
        )

        if (
            not request.user.is_staff_member
            and ticket.created_by != request.user
        ):
            messages.error(
                request,
                "Permission denied.",
            )

            return redirect(
                "ticket-list",
            )

        form = TicketCommentForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            comment = form.save(
                commit=False
            )

            comment.ticket = ticket
            comment.author = request.user

            comment.save()

            messages.success(
                request,
                "Comment added successfully.",
            )

        else:

            messages.error(
                request,
                "Comment could not be added.",
            )

        return redirect(
            "ticket-detail",
            pk=pk,
        )