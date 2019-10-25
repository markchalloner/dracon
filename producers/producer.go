package producers

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"time"

	"github.com/golang/protobuf/proto"
	"github.com/golang/protobuf/ptypes/timestamp"
	v1 "github.com/thought-machine/dracon/pkg/genproto/v1"
)

var (
	inResults string
	outFile   string
)

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
	scanUUID string,
	scanStartTime time.Time,
	issues []*v1.Issue,
) error {
	out := v1.LaunchToolResponse{
		ScanInfo: &v1.ScanInfo{
			ScanUuid:      scanUUID,
			ScanStartTime: &timestamp.Timestamp{},
		},
		ToolName: "bandit",
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
