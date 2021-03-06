# Releases

Dracon releases follow [Semantic Versioning](https://semver.org/)

We use annotated git tags to define a release by doing the following:

```
$ git tag --annotate <version>
e.g:
# git tag --annotate v0.1.0
# then push the tags
$ git push --tags
```

This lets us use `git desribe` to give us a descriptive version from any commit in the format `<version>-<commits since version>-<short-sha>`, e.g.:

- `v0.0.0` (when on the annotated commit (`git checkout v0.0.0`))
- `v0.0.0-3-g7487887`

## Creating a Release

1. Run `./pleasew run //scripts:tag-release` and follow the instructions. This will trigger a GitHub workflow that creates a pre-release with all the artifacts.
2. Once satisfied, promote the new pre-release to a release.
