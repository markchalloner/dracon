package template

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
)

func GeneratePipelineResourceDocs() ([][]byte, error) {
	resDocs := [][]byte{}
	resources := []PipelineTask{}
	resources = append(resources, TemplateVars.PipelineTaskProducers...)
	resources = append(resources, TemplateVars.PipelineTaskEnrichers...)
	// resources = append(resources, TemplateVars.PipelineTaskConsumers...)
	resources = append(resources, PipelineTask{
		Name:  "source",
		Index: 0,
	})
	for _, t := range resources {
		buf := bytes.Buffer{}
		pR := pipelineResource{
			APIVersion: "tekton.dev/v1alpha1",
			Kind:       "PipelineResource",
			Metadata: pipelineResourceMetadata{
				Name: fmt.Sprintf("%s-%s", TemplateVars.RunID, t.Name),
				Labels: map[string]string{
					"project": "dracon",
				},
			},
			Spec: pipelineResourceSpec{
				Type: "storage",
				Params: []pipelineResourceSpecParam{
					pipelineResourceSpecParam{
						Name:  "location",
						Value: fmt.Sprintf("s3://dracon/%s-%d-%s", TemplateVars.RunID, t.Index, t.Name),
					},
					pipelineResourceSpecParam{
						Name:  "type",
						Value: "gcs",
					},
					pipelineResourceSpecParam{
						Name:  "dir",
						Value: "y",
					},
				},
				Secrets: []pipelineResourceSpecSecret{
					pipelineResourceSpecSecret{
						FieldName:  "BOTO_CONFIG",
						SecretName: "dracon-storage",
						SecretKey:  "boto_config",
					},
				},
			},
		}

		yamlBytes, err := json.Marshal(pR)
		if err != nil {
			return nil, err
		}
		buf.Write(yamlBytes)
		// buf.WriteString(fmt.Sprintf("---\n%s\n", yamlBytes))
		resDocs = append(resDocs, buf.Bytes())
		log.Println(string(buf.Bytes()))
	}

	return resDocs, nil
}

type pipelineResource struct {
	APIVersion string                   `json:"apiVersion"`
	Metadata   pipelineResourceMetadata `json:"metadata"`
	Kind       string                   `json:"kind"`
	Spec       pipelineResourceSpec     `json:"spec"`
}

type pipelineResourceMetadata struct {
	Name   string            `json:"name"`
	Labels map[string]string `json:"labels"`
}

type pipelineResourceSpec struct {
	Type    string                       `json:"type"`
	Params  []pipelineResourceSpecParam  `json:"params"`
	Secrets []pipelineResourceSpecSecret `json:"secrets"`
}

type pipelineResourceSpecParam struct {
	Name  string `json:"name"`
	Value string `json:"value"`
}

type pipelineResourceSpecSecret struct {
	FieldName  string `json:"fieldName"`
	SecretName string `json:"secretName"`
	SecretKey  string `json:"secretKey"`
}
