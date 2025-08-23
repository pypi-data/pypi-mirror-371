from hatchling.plugin import hookimpl

from hatch_project_name.build_hook import ProjectNameBuildHook


@hookimpl
def hatch_register_build_hook():
    return ProjectNameBuildHook
