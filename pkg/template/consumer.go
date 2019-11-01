package template

// non-runtime
import "fmt"

var (
	ConsumerRef               = "consumer"
	ConsumeResource           = ConsumerRef
	ConsumerNamePrefix        = fmt.Sprintf("dracon-%s", ConsumerRef)
	RuntimeConsumerNamePrefix = fmt.Sprintf("%s-%s", RuntimePrefix, ConsumerRef)
)

type consumer struct {
	SpecInputResource string
	SourcePath        string
}

func newConsumer() consumer {
	return consumer{
		SpecInputResource: fmt.Sprintf("{name: %s, type: storage}", EnricherResource),
		SourcePath:        "/workspace/",
	}
}

func (consumer) Name(name string) string {
	return fmt.Sprintf("%s-%s", ConsumerNamePrefix, name)
}
