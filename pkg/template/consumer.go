package template

// non-runtime
import (
	"fmt"
	"strings"
)

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

func (consumer) SpecInputParams() string {
	res := []string{}
	for _, p := range params {
		res = append(res,
			fmt.Sprintf(
				`{name: "%s", type: "%s"}`,
				p.name, p.pType,
			),
		)
	}
	return strings.Join(res, ",")
}

func (consumer) EnvVars() string {
	res := []string{}
	for _, p := range params {
		res = append(res,
			fmt.Sprintf(
				`{name: "%s", value: "%s"}`,
				p.name, fmt.Sprintf("$(inputs.params.%s)"+p.name),
			),
		)
	}
	return strings.Join(res, ",")
}
