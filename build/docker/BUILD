subinclude("@pleasings//docker")

# Can be used to build Dracon if you don't want to set up a build environment
docker_image(
    name = "dracon-builder",
    dockerfile = "Dockerfile-dracon-builder",
    image = "dracon/builder-go",
)

docker_image(
    name = "dracon-base-go",
    dockerfile = "Dockerfile-base-go",
    image = "dracon/base-go",
    visibility = ["PUBLIC"],
)
