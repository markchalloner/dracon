subinclude("@third_party/subrepos/pleasings//docker")

go_binary(
    name = "typescript_tslint",
    srcs = [
        "main.go",
    ],
    deps = [
        "//api/proto:v1",
        "//producers",
        "//producers/typescript_tslint/types:tslint-issue"

    ],
)

go_test(
    name = "typescript_tslint_test",
    srcs = [
        "main.go",
        "main_test.go",
    ],
    deps = [
        "//api/proto:v1",
        "//producers",
        "//third_party/go:stretchr_testify",
        "//producers/typescript_tslint/types:tslint-issue"
    ],
)

docker_image(
    name = "dracon-producer-tslint",
    srcs = [
        ":typescript_tslint",
    ],
    base_image = "//build/docker:dracon-base-go",
    image = "dracon-producer-tslint",
)
