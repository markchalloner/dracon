package template

// non-runtime
import (
	"fmt"
	"strings"
)

var (
	PipelineNamePrefix = "dracon"
)

type pipeline struct {
	SourceResource          string
	EnricherResource        string
	TaskSourceResource      string
	TaskEnricherOutResource string
}

func newPipeline() pipeline {
	return pipeline{
		SourceResource:          fmt.Sprintf("{type: storage, name: %s}", SourceResource),
		EnricherResource:        fmt.Sprintf("{type: storage, name: %s}", EnricherResource),
		TaskSourceResource:      fmt.Sprintf("{name: %[1]s, resource: %[1]s}", SourceResource),
		TaskEnricherOutResource: fmt.Sprintf("{name: %[1]s, resource: %[1]s}", EnricherResource),
	}
}

func (pipeline) Name(n string) string {
	return fmt.Sprintf("dracon-%s", n)
}

func (pipeline) ProducerResources(names ...string) string {
	for i, s := range names {
		names[i] = fmt.Sprintf("  - {type: storage, name: %s-%s}", ProducerResource, s)
	}
	names[0] = strings.TrimPrefix(names[0], "  - ")
	return strings.Join(names, "\n")
}

func (pipeline) TaskProducerOutResource(name string) string {
	return fmt.Sprintf("{name: %s, resource: %s-%s}", ProducerResource, ProducerResource, name)
}

func (pipeline) TaskEnricherInputResources(names ...string) string {
	for i, s := range names {
		names[i] = fmt.Sprintf("{name: %[1]s-%[2]s, resource: %[1]s-%[2]s}", ProducerResource, s)
	}
	return strings.Join(names, ",")
}
