package template

// non-runtime
import "fmt"

var (
	SourceResource            = "source"
	SourceRuntimeResource     = fmt.Sprintf("%s-%s", RuntimePrefix, SourceResource)
	ProducerRef               = "producer"
	ProducerResource          = ProducerRef
	ProducerNamePrefix        = fmt.Sprintf("dracon-%s", ProducerRef)
	RuntimeProducerNamePrefix = fmt.Sprintf("%s-%s", RuntimePrefix, ProducerRef)
)

type producer struct {
	InResource  string
	OutResource string
	SpecVolume  string
	StepSetup   string
	StepExtras  string
	SourcePath  string
	ToolOutPath string
	OutPath     string
}

func newProducer() producer {
	return producer{
		InResource:  fmt.Sprintf("{name: %s, type: storage}", SourceResource),
		OutResource: fmt.Sprintf("{name: %s, type: storage}", ProducerResource),
		SpecVolume:  "{emptyDir: {}, name: dracon-ws}",
		StepSetup: fmt.Sprintf(`# dracon: extract source and setup
    name: extract-source
    image: busybox:latest
    command: ["sh"]
    args: ["-c",
      "mkdir -p /dracon/source && tar -C /dracon/source -xzf /workspace/%s/source.tgz && chown -R 1000:1000 /workspace/output/%s /dracon"
    ]
    volumeMounts: [{mountPath: /dracon, name: dracon-ws}]`, SourceResource, ProducerResource),
		StepExtras: `# dracon: extras
    volumeMounts: [{mountPath: /dracon, name: dracon-ws}]`,
		SourcePath:  "/dracon/source",
		ToolOutPath: "/dracon/results",
		OutPath:     fmt.Sprintf("/workspace/output/%s/results.pb", ProducerResource),
	}
}

func (producer) Name(name string) string {
	return fmt.Sprintf("%s-%s", ProducerNamePrefix, name)
}
