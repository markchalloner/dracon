subinclude("@pleasings//docker")

go_binary(
    name = "enricher",
    srcs = [
        "main.go",
    ],
    static = True,
    deps = [
        "//pkg/enrichment",
        "//pkg/enrichment/db",
        "//api/proto:dracon",
        "//pkg/putil",
        "//third_party/go:spf13_cobra",
        "//third_party/go:spf13_viper",
    ],
)

docker_image(
    name = "image",
    srcs = [
        ":enricher",
    ],
    base_image = "//build/docker:dracon-base-go",
    image = "dracon/enricher",
)
