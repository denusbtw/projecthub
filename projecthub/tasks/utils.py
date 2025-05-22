def resolve_task_id_from_view(view):
    if hasattr(view, "get_task_id"):
        return view.get_task_id()
    else:
        return view.kwargs.get("task_id")
