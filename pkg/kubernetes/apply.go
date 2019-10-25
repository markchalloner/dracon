package kubernetes

import (
	"fmt"
	"io"
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
	return fmt.Errorf("%s", output)
}
