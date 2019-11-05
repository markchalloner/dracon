package template

// non-runtime
import (
	"fmt"
	"strings"
	"time"
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

var params = []pipelineParam{
	{
		"DRACON_SCAN_ID",
		"Dracon: Unique Scan ID",
		"string",
		RuntimePrefix,
	},
	{
		"DRACON_SCAN_TIME",
		"Dracon: Scan start time",
		"string",
		time.Now().UTC().Format(time.RFC3339),
	},
}

type pipelineParam struct {
	name        string
	description string
	pType       string

	value string
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

func (pipeline) Params() string {
	res := []string{}
	for _, p := range params {
		res = append(res,
			fmt.Sprintf(
				`{name: "%s", description: "%s", type: "%s"}`,
				p.name, p.description, p.pType,
			),
		)
	}
	return strings.Join(res, ",")
}

func (pipeline) ConsumerParams() string {
	res := []string{}
	for _, p := range params {
		res = append(res,
			fmt.Sprintf(
				`{name: "%s", value: "%s"}`,
				p.name, fmt.Sprintf("$(params.%s)", p.name),
			),
		)
	}
	return strings.Join(res, ",")
}
