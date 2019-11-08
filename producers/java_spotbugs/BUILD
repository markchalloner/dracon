subinclude("@pleasings//docker")

go_binary(
    name = "java_spotbugs",
    srcs = [
        "main.go",
    ],
    deps = [
        "//api/proto:dracon",
        "//producers",
    ],
)

docker_image(
    name = "image",
    srcs = [
        ":java_spotbugs",
    ],
    base_image = "//build/docker:dracon-base-go",
    image = "dracon-producer-java_spotbugs",
)
