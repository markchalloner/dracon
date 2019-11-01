package template

// runtime
import (
	"fmt"
	"strings"
)

var ()

type pipelineRun struct{}

func newPipelineRun() pipelineRun {
	return pipelineRun{}
}

func (pipelineRun) Name(name string) string {
	return fmt.Sprintf("%s-%s", RuntimePrefix, name)
}

func (pipelineRun) ResourceSource() string {
	sourceID := pipelineResource{}.SourceID()
	return fmt.Sprintf("{name: %s, resourceRef: {name: %s}}", SourceResource, sourceID)
}

func (pipelineRun) ResourceProducers(names ...string) string {
	for i, s := range names {
		producerID := pipelineResource{}.ProducerID(s)
		names[i] = fmt.Sprintf("  - {name: %s-%s, resourceRef: {name: %s}}", ProducerResource, s, producerID)
	}
	names[0] = strings.TrimPrefix(names[0], "  - ")
	return strings.Join(names, "\n")
}

func (pipelineRun) ResourceEnricher() string {
	enricherID := pipelineResource{}.EnricherID()
	return fmt.Sprintf("{name: %s, resourceRef: {name: %s}}", EnricherResource, enricherID)
}
