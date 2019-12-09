python_binary(
    name = "stdout_json",
    main = "stdout_json.py",
    deps = [
        "//api/proto:dracon",
        "//third_party/python:protobuf",
    ],
)

python_test(
    name = "stdout_json_test",
    srcs = [
        "stdout_json.py",
        "stdout_json_test.py",
    ],
    deps = [
        "//api/proto:dracon",
        "//third_party/python:protobuf",
    ],
)
