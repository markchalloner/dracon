package template

// runtime
import "fmt"

var (
	// RuntimePrefix represents the prefix for a PipelineResource which are usually created at runtime thus need UIDs
	RuntimePrefix = fmt.Sprintf("dracon-%s", getID())
)

type pipelineResource struct{}

func newPipelineResource() pipelineResource {
	return pipelineResource{}
}

func (pipelineResource) SourceID() string {
	return fmt.Sprintf("%s-%s", RuntimePrefix, SourceResource)
}

func (pipelineResource) ProducerID(name string) string {
	return fmt.Sprintf("%s-%s-%s", RuntimePrefix, ProducerResource, name)
}

func (pipelineResource) EnricherID() string {
	return fmt.Sprintf("%s-%s", RuntimePrefix, EnricherResource)
}

func (pipelineResource) ID(detail string) string {
	return fmt.Sprintf("%s-%s", RuntimePrefix, detail)
}
