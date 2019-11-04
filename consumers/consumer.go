package consumers

import (
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"strings"

	"github.com/gogo/protobuf/proto"
	v1 "github.com/thought-machine/dracon/pkg/genproto/v1"
)

var (
	inResults string
	// Raw represents if the non-enriched results should be used
	Raw bool
)

func init() {
	flag.StringVar(&inResults, "in", "", "the directory where dracon producer/enricher outputs are")
	flag.BoolVar(&Raw, "raw", false, "if the non-enriched results should be used")
}

// ParseFlags will parse the input flags for the producer and perform simple validation
func ParseFlags() error {
	flag.Parse()
	if len(inResults) < 1 {
		return fmt.Errorf("in is undefined")
	}
	return nil
}

// LoadToolResponse loads raw results from producers
func LoadToolResponse() ([]*v1.LaunchToolResponse, error) {
	responses := []*v1.LaunchToolResponse{}
	if err := filepath.Walk(inResults, func(path string, f os.FileInfo, err error) error {
		if !f.IsDir() && (strings.HasSuffix(f.Name(), ".pb")) {
			pbBytes, err := ioutil.ReadFile(path)
			if err != nil {
				return err
			}
			res := v1.LaunchToolResponse{}
			if err := proto.Unmarshal(pbBytes, &res); err != nil {
				log.Printf("skipping %s as unable to unmarshal", path)
			} else {
				responses = append(responses, &res)
			}
		}
		return nil
	}); err != nil {
		return responses, err
	}
	return responses, nil
}

// LoadEnrichedToolResponse loads enriched results from the enricher
func LoadEnrichedToolResponse() ([]*v1.EnrichedLaunchToolResponse, error) {
	responses := []*v1.EnrichedLaunchToolResponse{}
	if err := filepath.Walk(inResults, func(path string, f os.FileInfo, err error) error {
		if !f.IsDir() && (strings.HasSuffix(f.Name(), ".pb")) {
			pbBytes, err := ioutil.ReadFile(path)
			if err != nil {
				return err
			}
			res := v1.EnrichedLaunchToolResponse{}
			if err := proto.Unmarshal(pbBytes, &res); err != nil {
				log.Printf("skipping %s as unable to unmarshal", path)
			} else {
				responses = append(responses, &res)
			}
		}
		return nil
	}); err != nil {
		return responses, err
	}
	return responses, nil
}
