package producers

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"strings"
	"time"

	"github.com/golang/protobuf/proto"
	"github.com/golang/protobuf/ptypes"
	"github.com/google/uuid"
	v1 "github.com/thought-machine/dracon/pkg/genproto/v1"
)

var (
	inResults string
	outFile   string
)

const sourceDir = "/dracon/source"

func init() {
	flag.StringVar(&inResults, "in", "", "")
	flag.StringVar(&outFile, "out", "", "")
}

// ParseFlags will parse the input flags for the producer and perform simple validation
func ParseFlags() error {
	flag.Parse()
	if len(inResults) < 0 {
		return fmt.Errorf("in is undefined")
	}
	if len(outFile) < 0 {
		return fmt.Errorf("out is undefined")
	}
	return nil
}

// ParseInFileJSON provides a generic method to parse a tool's JSON results into a given struct
func ParseInFileJSON(structure interface{}) error {
	inBytes, err := ioutil.ReadFile(inResults)
	if err != nil {
		return err
	}
	if err := json.Unmarshal(inBytes, structure); err != nil {
		return err
	}
	return nil
}

// WriteDraconOut provides a generic method to write the resulting protobuf to the output file
func WriteDraconOut(
	toolName string,
	scanStartTime time.Time,
	issues []*v1.Issue,
) error {
	cleanIssues := []*v1.Issue{}
	for _, iss := range issues {
		iss.Description = strings.Replace(iss.Description, sourceDir, ".", -1)
		iss.Title = strings.Replace(iss.Title, sourceDir, ".", -1)
		iss.Target = strings.Replace(iss.Target, sourceDir, ".", -1)
		cleanIssues = append(cleanIssues, iss)
	}
	protoTime, err := ptypes.TimestampProto(scanStartTime)
	if err != nil {
		return err
	}
	out := v1.LaunchToolResponse{
		ScanInfo: &v1.ScanInfo{
			ScanUuid:      uuid.New().String(),
			ScanStartTime: protoTime,
		},
		ToolName: toolName,
		Issues:   issues,
	}

	outBytes, err := proto.Marshal(&out)
	if err != nil {
		return err
	}

	if err := ioutil.WriteFile(outFile, outBytes, 0644); err != nil {
		return err
	}

	log.Printf("parsed %d issues from %s to %s", len(issues), inResults, outFile)
	return nil
}
