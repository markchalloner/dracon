package kubernetes

import (
	"fmt"
	"io"
	"log"
	"os/exec"
)

// Apply config using kubectl
func Apply(config string) error {
	cmd := exec.Command("kubectl", "apply", "-f", "-")
	stdin, err := cmd.StdinPipe()
	if err != nil {
		return err
	}
	go func() {
		defer stdin.Close()
		io.WriteString(stdin, config)
	}()

	output, err := cmd.CombinedOutput()
	if err != nil {
		return err
	}
	log.Printf("out: %s", output)
	if !cmd.ProcessState.Success() {
		return fmt.Errorf("failed to apply: %s", output)
	}
	return nil
}
