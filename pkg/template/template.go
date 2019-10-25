package template

import (
	"bytes"
	"path/filepath"
	tt "text/template"
)

type Template struct {
	template *tt.Template
}

func (t *Template) LoadAll(path string) error {
	pattern := filepath.Join(path, "*.yaml")
	var err error
	t.template, err = tt.ParseGlob(pattern)
	return err
}

func (t *Template) String() (string, error) {
	buf := &bytes.Buffer{}
	err := t.template.Execute(buf, nil)
	return buf.String(), err
}
