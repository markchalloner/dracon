package(default_visibility = ['PUBLIC'])


def protoc_binary(name, version, hashes=None, deps=None, visibility=None):
    """Temporary override until the fix here is upstreamed."""
    download_rule = remote_file(
        name = name,
        _tag = 'download',
        url = f'https://github.com/google/protobuf/releases/download/v{version}/protoc-{version}-$XOS-$XARCH.zip',
        out = f'protoc-{version}.zip',
        hashes = hashes,
        deps = deps,
    )
    # The well-known types are included in the same zipfile.
    wkt = build_rule(
        name = name,
        tag = 'wkt',
        srcs = [download_rule],
        outs = ['google'],
        tools = [CONFIG.JARCAT_TOOL],
        cmd = '$TOOL x $SRCS --strip_prefix include',
        labels = [
            'protoc:-I$TMP_DIR/' + package_name(),
            'protoc:-I$TMP_DIR',
        ],
    )
    return genrule(
        name = name,
        srcs = [download_rule],
        outs = ['protoc'],
        tools = [CONFIG.JARCAT_TOOL],
        binary = True,
        cmd = '$TOOL x $SRCS bin/protoc',
        visibility = visibility,
        provides = {'proto': wkt},
    )

protoc_binary(
    name = "protoc",
    version = "3.10.1",
)
