#!/bin/sh -e

srcDefs="${PWD}/api/proto"
uid=$(id -u)
gid=$(id -g)

do_gen() {
    local lang=$1
    local out=$2

    rm -rf "${out}"
    mkdir -p $(dirname "${out}")
    docker run --rm \
    -v "${srcDefs}:/defs" \
    --user "${uid}:${gid}" \
    namely/protoc-all \
    -d /defs -l "${lang}" -o gen
    mv "${srcDefs}/gen" "${out}"
    rm -rf "${srcDefs}/gen"
}

do_gen "go" "${PWD}/pkg/genproto/v1"
do_gen "python" "${PWD}/gen"
