"""Custom Bazel rules for building Sphinx documentation."""

def _sphinx_html_impl(ctx):
    output_dir = ctx.actions.declare_directory(ctx.attr.output_dir_name)

    inputs = depset(
        direct = ctx.files.srcs + [ctx.file.config],
    )

    dashboard_dir = "{}/dashboard".format(output_dir.path)
    dashboard_html = "{}/index.html".format(dashboard_dir)
    dashboard_history = "{}/quality_history.json".format(dashboard_dir)

    command = """
set -euo pipefail
"{builder}" -b html -W --keep-going "{sphinx_dir}" "{output_dir}"
"{dashboard_builder}" --html "{dashboard_html}" --history "{dashboard_history}"
""".format(
        builder = ctx.executable.builder.path,
        sphinx_dir = ctx.file.config.dirname,
        output_dir = output_dir.path,
        dashboard_builder = ctx.executable.dashboard_builder.path,
        dashboard_html = dashboard_html,
        dashboard_history = dashboard_history,
    )

    ctx.actions.run_shell(
        command = command,
        inputs = inputs,
        outputs = [output_dir],
        tools = [
            ctx.attr.builder[DefaultInfo].files_to_run,
            ctx.attr.dashboard_builder[DefaultInfo].files_to_run,
        ],
        mnemonic = "SphinxHtmlBuild",
        progress_message = "Building Sphinx documentation for {}".format(ctx.label),
    )

    return [
        DefaultInfo(
            files = depset([output_dir]),
            runfiles = ctx.runfiles(files = [output_dir]),
        ),
    ]


sphinx_html = rule(
    implementation = _sphinx_html_impl,
    attrs = {
        "builder": attr.label(
            executable = True,
            cfg = "exec",
            mandatory = True,
        ),
        "config": attr.label(
            allow_single_file = True,
            mandatory = True,
        ),
        "dashboard_builder": attr.label(
            executable = True,
            cfg = "exec",
            mandatory = True,
        ),
        "output_dir_name": attr.string(
            default = "_build",
        ),
        "srcs": attr.label_list(
            allow_files = True,
        ),
    },
)