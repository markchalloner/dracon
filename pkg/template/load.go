package template

import (
	"bytes"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"strings"

	jsonpatch "github.com/evanphx/json-patch"
	"github.com/ghodss/yaml"
	"github.com/pkg/errors"
	"github.com/rakyll/statik/fs"

	// Statik bindata for Dracon patches
	_ "github.com/thought-machine/dracon/pkg/template/patches"
)

var (
	ErrNonYAMLFileEncountered = errors.New("non-yaml file found in directory")
)

// PipelineYAMLDocs stores all of the yaml docs found in a file in the format map[path][]doc
type PipelineYAMLDocs map[string][][]byte

// LoadPipelineYAMLFiles returns all of the PipelineYAMLDocs in a directory
func LoadPipelineYAMLFiles(sourcePath string) (PipelineYAMLDocs, error) {
	targets := map[string][][]byte{}
	err := filepath.Walk(sourcePath, func(path string, f os.FileInfo, err error) error {
		if !f.IsDir() && (strings.HasSuffix(f.Name(), ".yml") || strings.HasSuffix(f.Name(), ".yaml")) {
			docs, err := loadYAMLFile(path)
			if err != nil {
				return err
			}
			targets[path] = docs
		}
		return nil
	})
	return targets, err
}

func loadYAMLFile(path string) ([][]byte, error) {
	targetYAML, err := ioutil.ReadFile(path)
	if err != nil {
		return nil, errors.Wrapf(err, "could not read file at path %s", path)
	}
	resFileYamlDocs := [][]byte{}
	yamlParts := bytes.Split(targetYAML, []byte(`---`))
	yamlDocs := func(yamlParts [][]byte) [][]byte {
		yamlDocs := [][]byte{}
		for _, d := range yamlParts {
			if strings.TrimSpace(string(d)) != "" {
				yamlDocs = append(yamlDocs, d)
			}
		}
		return yamlDocs
	}(yamlParts)
	log.Printf("found %d yaml docs in %s", len(yamlDocs), path)
	for _, yDoc := range yamlDocs {
		yDocParsed, err := yaml.YAMLToJSON(yDoc)
		if err != nil {
			return nil, errors.Wrapf(err, "could not read YAML doc in path %s", path)
		}
		resFileYamlDocs = append(resFileYamlDocs, yDocParsed)
	}

	return resFileYamlDocs, nil
}

// PatchKindYAMLDocs stores all of the jsonpatch yaml docs found by type
type PatchKindYAMLDocs map[string][]jsonpatch.Patch

func loadStatikPatches() (PatchKindYAMLDocs, error) {
	statikFS, err := fs.New()
	if err != nil {
		return nil, errors.Wrap(err, "could not load statik filesystem")
	}
	patches := PatchKindYAMLDocs{}
	err = fs.Walk(statikFS, "/", func(path string, f os.FileInfo, err error) error {
		if !f.IsDir() {
			patchKind := getPatchKindFromPath(path)
			r, err := statikFS.Open(path)
			if err != nil {
				return errors.Wrap(err, "could not open statik file")
			}
			defer r.Close()
			contents, err := ioutil.ReadAll(r)
			patch, err := loadPatchFromYAML(contents)
			if err != nil {
				return errors.Wrap(err, "could load patch from YAML")
			}
			if _, ok := patches[patchKind]; !ok {
				patches[patchKind] = []jsonpatch.Patch{}
			}
			patches[patchKind] = append(patches[patchKind], patch)
		}
		return nil
	})

	return patches, err
}

// LoadPatchYAMLFiles returns the yaml docs by kind from a given directory
func LoadPatchYAMLFiles(sourcePath string) (PatchKindYAMLDocs, error) {
	patches, err := loadStatikPatches()
	if err != nil {
		return nil, err
	}
	if sourcePath != "" {
		err = filepath.Walk(sourcePath, func(path string, f os.FileInfo, err error) error {
			if !f.IsDir() && (strings.HasSuffix(f.Name(), ".yml") || strings.HasSuffix(f.Name(), ".yaml")) {
				patchKind := getPatchKindFromPath(path)
				patchYAML, err := ioutil.ReadFile(path)
				if err != nil {
					return errors.Wrap(err, "could not read file")
				}
				patch, err := loadPatchFromYAML(patchYAML)
				if err != nil {
					return errors.Wrap(err, "could load patch from YAML")
				}
				if _, ok := patches[patchKind]; !ok {
					patches[patchKind] = []jsonpatch.Patch{}
				}
				patches[patchKind] = append(patches[patchKind], patch)
			}
			return nil
		})
	}
	return patches, err
}

// getPatchKindFromPath returns the type of yaml file based on filename
func getPatchKindFromPath(path string) string {
	base := filepath.Base(path)
	parts := strings.Split(base, `.`)
	return parts[len(parts)-2]
}

func loadPatchFromYAML(contents []byte) (jsonpatch.Patch, error) {
	templatedPatchYAML, err := execTemplate(contents)
	if err != nil {
		return nil, err
	}
	patchJSON, err := yaml.YAMLToJSON(templatedPatchYAML)
	if err != nil {
		return nil, err
	}
	return jsonpatch.DecodePatch(patchJSON)
}
