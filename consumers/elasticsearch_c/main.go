package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"time"

	elasticsearch "github.com/elastic/go-elasticsearch/v7"
	"github.com/golang/protobuf/ptypes"
	"github.com/thought-machine/dracon/consumers"
	v1 "github.com/thought-machine/dracon/pkg/genproto/v1"
)

var (
	dryRun  bool
	esURL   string
	esIndex string
)

func init() {
	flag.BoolVar(&dryRun, "dry-run", false, "")
	flag.StringVar(&esIndex, "es-index", "", "")
}

func parseFlags() error {
	if err := consumers.ParseFlags(); err != nil {
		return err
	}
	if len(esIndex) < 1 {
		return fmt.Errorf("es-index is undefined")
	}
	return nil
}

func main() {
	if err := consumers.ParseFlags(); err != nil {
		log.Fatal(err)
	}

	es, err := elasticsearch.NewDefaultClient()
	if err != nil {
		log.Fatal(err)
	}

	if consumers.Raw {
		responses, err := consumers.LoadToolResponse()
		if err != nil {
			log.Fatal(err)
		}
		for _, res := range responses {
			scanStartTime, _ := ptypes.Timestamp(res.GetScanInfo().GetScanStartTime())
			for _, iss := range res.GetIssues() {
				b, err := getRawIssue(scanStartTime, res, iss)
				if err != nil {
					log.Fatal(err)
				}
				esPush(es, b)
			}
		}
	} else {
		responses, err := consumers.LoadEnrichedToolResponse()
		if err != nil {
			log.Fatal(err)
		}
		for _, res := range responses {
			scanStartTime, _ := ptypes.Timestamp(res.GetOriginalResults().GetScanInfo().GetScanStartTime())
			for _, iss := range res.GetIssues() {
				b, err := getEnrichedIssue(scanStartTime, res, iss)
				if err != nil {
					log.Fatal(err)
				}
				esPush(es, b)
			}
		}
	}
}

func getRawIssue(scanStartTime time.Time, res *v1.LaunchToolResponse, iss *v1.Issue) ([]byte, error) {
	jBytes, err := json.Marshal(&esDocument{
		ScanStartTime: scanStartTime,
		ScanID:        res.GetScanInfo().GetScanUuid(),
		ToolName:      res.GetToolName(),
		Target:        iss.GetTarget(),
		Type:          iss.GetType(),
		Severity:      iss.GetSeverity(),
		CVSS:          iss.GetCvss(),
		Confidence:    iss.GetConfidence(),
		Description:   iss.GetDescription(),
		FirstFound:    scanStartTime,
		FalsePositive: false,
	})
	if err != nil {
		return []byte{}, err
	}
	return jBytes, nil
}

func getEnrichedIssue(scanStartTime time.Time, res *v1.EnrichedLaunchToolResponse, iss *v1.EnrichedIssue) ([]byte, error) {
	firstSeenTime, _ := ptypes.Timestamp(iss.GetFirstSeen())
	jBytes, err := json.Marshal(&esDocument{
		ScanStartTime: scanStartTime,
		ScanID:        res.GetOriginalResults().GetScanInfo().GetScanUuid(),
		ToolName:      res.GetOriginalResults().GetToolName(),
		Target:        iss.GetRawIssue().GetTarget(),
		Type:          iss.GetRawIssue().GetType(),
		Severity:      iss.GetRawIssue().GetSeverity(),
		CVSS:          iss.GetRawIssue().GetCvss(),
		Confidence:    iss.GetRawIssue().GetConfidence(),
		Description:   iss.GetRawIssue().GetDescription(),
		FirstFound:    firstSeenTime,
		FalsePositive: iss.GetFalsePositive(),
	})
	if err != nil {
		return []byte{}, err
	}
	return jBytes, nil
}

func esPush(es *elasticsearch.Client, b []byte) error {
	resp, err := es.Index(esIndex, bytes.NewBuffer(b))
	if err != nil {
		return err
	}

	log.Println(resp)
	return nil
}

type esDocument struct {
	ScanStartTime time.Time     `json:"scan_start_time"`
	ScanID        string        `json:"scan_id"`
	ToolName      string        `json:"tool_name"`
	Target        string        `json:"target"`
	Type          string        `json:"type"`
	Title         string        `json:"title"`
	Severity      v1.Severity   `json:"severity"`
	CVSS          float64       `json:"cvss"`
	Confidence    v1.Confidence `json:"confidence"`
	Description   string        `json:"description"`
	FirstFound    time.Time     `json:"first_found"`
	FalsePositive bool          `json:"false_positive"`
}
