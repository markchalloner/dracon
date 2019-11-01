/*
Copyright © 2019 Thought Machine

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/
package template

import (
	"bytes"
	"path/filepath"
	tt "text/template"
	"time"

	"github.com/speps/go-hashids"
)

// Templater represents Dracon CLI's templating engine
type Templater struct {
	text             *tt.Template
	Producer         producer
	Consumer         consumer
	Pipeline         pipeline
	PipelineResource pipelineResource
	PipelineRun      pipelineRun
	Enrichment       enrichment
	ID               string
}

// NewTemplater returns a new templater
func NewTemplater() *Templater {

	return &Templater{
		Producer:         newProducer(),
		Consumer:         newConsumer(),
		Pipeline:         newPipeline(),
		PipelineResource: newPipelineResource(),
		PipelineRun:      newPipelineRun(),
		Enrichment:       newEnrichment(),
	}
}

// Load loads a single yaml to template
func (t *Templater) Load(path string) error {
	text, err := tt.ParseFiles(path)
	t.text = text
	return err
}

// LoadAll loads all of the yamls in a directory to template
func (t *Templater) LoadAll(path string) error {
	pattern := filepath.Join(path, "*.yaml")
	var err error
	t.text, err = tt.ParseGlob(pattern)
	return err
}

// String returns a string of all the executed templates
func (t *Templater) String() (string, error) {
	buf := &bytes.Buffer{}
	for _, tmpl := range t.text.Templates() {
		if err := tmpl.Execute(buf, t); err != nil {
			return "", err
		}
	}
	return buf.String(), nil
}

func getID() string {
	hd := hashids.NewData()
	hd.Alphabet = "abcdefghijklmnopqrstuvwxyz1234567890"
	hd.Salt = "dracon"
	hd.MinLength = 4
	h, _ := hashids.NewWithData(hd)
	e, _ := h.EncodeInt64([]int64{time.Now().UnixNano()})
	return e
}
