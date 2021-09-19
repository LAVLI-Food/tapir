from django import template
from django.utils.translation import gettext as _

from tapir.shifts.models import (
    Shift,
    ShiftTemplate,
    WEEKDAY_CHOICES,
    ShiftAttendance,
)

register = template.Library()


@register.inclusion_tag("shifts/user_shifts_overview_tag.html", takes_context=True)
def user_shifts_overview(context, user):
    context["user"] = user
    return context


@register.inclusion_tag("shifts/shift_block_tag.html", takes_context=True)
def shift_block(context, shift: Shift, fill_parent=False):
    context["shift"] = shift_to_block_object(shift, fill_parent)
    return context


@register.inclusion_tag("shifts/shift_block_tag.html", takes_context=True)
def shift_template_block(context, shift_template: ShiftTemplate, fill_parent=False):
    context["shift"] = shift_template_to_block_object(shift_template, fill_parent)
    return context


def shift_name_as_class(shift_name: str) -> str:
    return shift_name.replace(" ", "_").lower()


def shift_to_block_object(shift: Shift, fill_parent: bool):
    attendances = {}
    has_looking_for_stand_in = False

    filter_classes = set()

    num_valid_attendance_on_required_slots = 0
    for slot in shift.slots.all():
        slot_name = slot.name
        if slot_name == "":
            slot_name = _("General")
        if slot_name not in attendances:
            attendances[slot_name] = []

        attendance = None
        for a in slot.attendances.all():
            if a.is_valid():
                attendance = a
                break

        if attendance and not slot.optional:
            num_valid_attendance_on_required_slots += 1

        if attendance:
            if attendance.state == ShiftAttendance.State.LOOKING_FOR_STAND_IN:
                has_looking_for_stand_in = True
                filter_classes.add("standin_any")
                filter_classes.add("standin_" + shift_name_as_class(slot.name))
                filter_classes.add("freeslot_any")
                filter_classes.add("freeslot_" + shift_name_as_class(slot.name))

                state = "standin"
            elif (
                slot.slot_template is not None
                and hasattr(slot.slot_template, "attendance_template")
                and slot.slot_template.attendance_template.user == attendance.user
            ):
                state = "regular"
            else:
                state = "single"
        else:
            filter_classes.add("freeslot_any")
            filter_classes.add("freeslot_" + shift_name_as_class(slot.name))
            if slot.optional:
                state = "optional"
            else:
                state = "empty"

        attendances[slot_name].append(state)

    template_group = None
    if shift.shift_template:
        template_group = template_group_name_to_character(
            shift.shift_template.group.name
        )

    num_required_slots = (
        len([_ for slot in shift.slots.all() if not slot.optional]) or 1
    )

    perc_slots_occupied = (
        num_valid_attendance_on_required_slots / float(num_required_slots)
        if num_required_slots
        else 1
    )

    background = "success"
    if perc_slots_occupied < 0.5:
        background = "danger"
    elif perc_slots_occupied < 1.0 or has_looking_for_stand_in:
        background = "warning"

    style = ""
    if fill_parent:
        style = "height:100%; width: 100%;"

    return {
        "attendances": attendances,
        "name": shift.name,
        "start_time": shift.start_time,
        "end_time": shift.end_time,
        "start_date": shift.start_time,
        "weekday": None,
        "template_group": template_group,
        "background": background,
        "style": style,
        "id": shift.id,
        "is_template": False,
        "filter_classes": filter_classes,
    }


def shift_template_to_block_object(shift_template: ShiftTemplate, fill_parent: bool):
    attendances = {}
    nb_attendances_in_required_slots = 0
    for slot_template in shift_template.slot_templates.all():
        slot_name = slot_template.name
        if slot_template.name == "":
            slot_name = _("General")
        if slot_name not in attendances:
            attendances[slot_name] = []

        if slot_template.get_attendance_template() is not None:
            nb_attendances_in_required_slots += 1

        if slot_template.get_attendance_template():
            state = "regular"
        else:
            if slot_template.optional:
                state = "optional"
            else:
                state = "empty"

        attendances[slot_name].append(state)

    num_required_slots = len(
        [_ for slot in shift_template.slot_templates.all() if not slot.optional]
    )
    perc_slots_occupied = (
        nb_attendances_in_required_slots / float(num_required_slots)
        if num_required_slots
        else 1
    )

    background = "success"
    if perc_slots_occupied < 0.5:
        background = "danger"
    elif perc_slots_occupied < 1.0:
        background = "warning"

    style = ""
    if fill_parent:
        style = "height:100%; width: 100%;"

    return {
        "attendances": attendances,
        "name": shift_template.name,
        "start_time": shift_template.start_time,
        "end_time": shift_template.end_time,
        "start_date": None,
        "weekday": WEEKDAY_CHOICES[shift_template.weekday][1],
        "template_group": template_group_name_to_character(shift_template.group.name),
        "background": background,
        "style": style,
        "id": shift_template.id,
        "is_template": True,
    }


def template_group_name_to_character(name: str):
    if name[-1] == "A":
        return "Ⓐ"
    if name[-1] == "B":
        return "Ⓑ"
    if name[-1] == "C":
        return "Ⓒ"
    if name[-1] == "D":
        return "Ⓓ"
    return None
