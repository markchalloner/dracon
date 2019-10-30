package producers

import (
	"io/ioutil"
	"os"
	"testing"
	"time"

	"github.com/gogo/protobuf/proto"
	"github.com/golang/protobuf/ptypes"
	"github.com/stretchr/testify/assert"
	v1 "github.com/thought-machine/dracon/pkg/genproto/v1"
)

func TestWriteDraconOut(t *testing.T) {
	tmpFile, err := ioutil.TempFile("", "dracon-test")
	assert.Nil(t, err)
	defer os.Remove(tmpFile.Name())
	outFile = tmpFile.Name()
	startTime := time.Now().UTC()
	err = WriteDraconOut(
		"dracon-test",
		startTime,
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
	aT, err := ptypes.Timestamp(res.GetScanInfo().GetScanStartTime())
	assert.Nil(t, err)
	assert.Equal(t, startTime, aT)
	assert.Equal(t, "/foobar", res.GetIssues()[0].GetTarget())
	assert.Equal(t, "/barfoo", res.GetIssues()[0].GetTitle())
	assert.Equal(t, "/example.yaml", res.GetIssues()[0].GetDescription())
}
