package template

// non-runtime
import (
	"fmt"
	"strings"
)

var (
	EnricherResource        = "enricher"
	EnricherRuntimeResource = fmt.Sprintf("%s-%s", RuntimePrefix, EnricherResource)
	EnricherOutPath         = fmt.Sprintf("/workspace/output/%s", EnricherResource)
)

type enrichment struct {
	Name        string
	OutResource string
	StepSetup   string
	OutPath     string
}

func newEnrichment() enrichment {
	return enrichment{
		Name:        "dracon-enricher",
		OutResource: EnricherResource,
		OutPath:     EnricherOutPath,
		StepSetup: fmt.Sprintf(`# dracon: enricher setup
    name: setup-permissions
    image: busybox:latest
    command: ["chown"]
    args: ["-R", "1000:1000", "%s"]`, EnricherOutPath),
	}
}

func (enrichment) InResources(names ...string) string {
	for i, s := range names {
		names[i] = fmt.Sprintf("{name: %s-%s, type: storage}", ProducerResource, s)
	}
	names[0] = strings.TrimPrefix(names[0], "  - ")
	return strings.Join(names, ",")
}
