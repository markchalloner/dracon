package producers

import (
	"io/ioutil"
	"log"
	"os"
	"testing"

	"github.com/gogo/protobuf/proto"
	"github.com/stretchr/testify/assert"
	v1 "github.com/thought-machine/dracon/pkg/genproto/v1"
)

func TestWriteDraconOut(t *testing.T) {
	tmpFile, err := ioutil.TempFile("", "dracon-test")
	assert.Nil(t, err)
	defer os.Remove(tmpFile.Name())
	outFile = tmpFile.Name()
	err = WriteDraconOut(
		"dracon-test",
		[]*v1.Issue{
			&v1.Issue{
				Target:      "/dracon/source/foobar",
				Title:       "/dracon/source/barfoo",
				Description: "/dracon/source/example.yaml",
			},
		},
	)
	assert.Nil(t, err)

	pBytes, err := ioutil.ReadFile(tmpFile.Name())
	res := v1.LaunchToolResponse{}
	err = proto.Unmarshal(pBytes, &res)
	assert.Nil(t, err)

	assert.Equal(t, "dracon-test", res.GetToolName())
	assert.Equal(t, "./foobar", res.GetIssues()[0].GetTarget())
	assert.Equal(t, "./barfoo", res.GetIssues()[0].GetTitle())
	assert.Equal(t, "./example.yaml", res.GetIssues()[0].GetDescription())
}

func ExampleParseFlags() {
	if err := ParseFlags(); err != nil {
		log.Fatal(err)
	}
}

func ExampleParseInFileJSON() {
	type GoSecOut struct {
		Issues []struct {
			Severity   string `json:"severity"`
			Confidence string `json:"confidence"`
			RuleID     string `json:"rule_id"`
			Details    string `json:"details"`
			File       string `json:"file"`
			Code       string `json:"code"`
			Line       string `json:"line"`
			Column     string `json:"column"`
		} `json:"Issues"`
	}
	var results GoSecOut
	if err := ParseInFileJSON(&results); err != nil {
		log.Fatal(err)
	}
}

func ExampleWriteDraconOut() {
	issues := []*v1.Issue{}
	if err := WriteDraconOut(
		"gosec",
		issues,
	); err != nil {
		log.Fatal(err)
	}
}
