subinclude("@third_party/subrepos/pleasings//docker")

go_binary(
    name = "semgrep",
    srcs = [
        "main.go",
    ],
    deps = [
        "//api/proto:v1",
        "//producers",
        "//producers/semgrep/types:semgrep-issue"
    ],
)

go_test(
    name = "semgrep_test",
    srcs = [
        "main.go",
        "main_test.go",
    ],
    deps = [
        "//api/proto:v1",
        "//producers",
        "//third_party/go:stretchr_testify",
        "//producers/semgrep/types:semgrep-issue",
    ],
)

docker_image(
    name = "image",
    srcs = [
        ":semgrep",
    ],
    base_image = "//build/docker:dracon-base-go",
    image = "dracon-producer-semgrep",
)
