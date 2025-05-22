from projecthub.projects.models import ProjectMembership


def get_project_membership_with_role(role, project_id, tenant):
    return ProjectMembership.objects.filter(
        role=role,
        project__tenant=tenant,
        project_id=project_id,
    ).first()


def get_role_value(role):
    return {
        ProjectMembership.Role.OWNER: 5,
        ProjectMembership.Role.SUPERVISOR: 4,
        ProjectMembership.Role.RESPONSIBLE: 3,
        ProjectMembership.Role.USER: 2,
        ProjectMembership.Role.GUEST: 1,
        ProjectMembership.Role.READER: 0,
    }.get(role)