subinclude("@pleasings//docker")

go_binary(
    name = "elasticsearch_c",
    srcs = [
        "main.go",
    ],
    static = True,
    deps = [
        "//consumers",
        "//api/proto:dracon",
        "//third_party/go:elastic_go-elasticsearch_v6",
        "//third_party/go:protobuf",
    ],
)

docker_image(
    name = "image",
    srcs = [
        ":elasticsearch_c",
    ],
    base_image = "//build/docker:dracon-base-go",
    image = "dracon-consumer-elasticsearch",
)
