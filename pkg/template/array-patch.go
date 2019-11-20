package template

import (
	"bytes"
	"encoding/json"
	"fmt"
	"strings"

	jsonpatch "github.com/evanphx/json-patch"
)

func patchArrayGlob(op jsonpatch.Operation, targetJSON []byte) []jsonpatch.Operation {
	path, err := op.Path()
	if err != nil || !strings.Contains(path, `/*/`) {
		return []jsonpatch.Operation{op}
	}
	return resolveArrayGlobOps(op, targetJSON)
}

func resolveArrayGlobOps(op jsonpatch.Operation, targetJSON []byte) []jsonpatch.Operation {
	resOps := []jsonpatch.Operation{}
	path, _ := op.Path()

	getLengthOfPath := func() int {
		var objMap map[string]*json.RawMessage
		err := json.Unmarshal(targetJSON, &objMap)
		if err != nil {
			panic(err)
		}

		pathParts := strings.Split(path, "/")
		pathParts = pathParts[1:]
		for i, key := range pathParts {
			if rawJSON, ok := objMap[key]; ok {
				if pathParts[i+1] == "*" {
					var objArr []*json.RawMessage
					json.Unmarshal(*rawJSON, &objArr)
					return len(objArr)
				}
				err := json.Unmarshal(*rawJSON, &objMap)
				if err != nil {
					panic(err)
				}
			}
		}
		return 0
	}

	resolvedLength := getLengthOfPath()

	for i := 0; i < resolvedLength; i++ {
		newOp := copyOperation(op)
		newPath := json.RawMessage(bytes.Replace(*newOp["path"], []byte(`/*/`), []byte(fmt.Sprintf("/%d/", i)), 1))
		newOp["path"] = &newPath
		resOps = append(resOps, newOp)
	}

	return resOps
}
