/*
Copyright © 2019 Thought Machine

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/
package cmd

import (
	"fmt"
	"log"
	"os"

	"github.com/spf13/cobra"

	"github.com/thought-machine/dracon/pkg/kubernetes"
	"github.com/thought-machine/dracon/pkg/template"
)

var runOpts struct {
	Path string
}

// runCmd represents the setup command
var runCmd = &cobra.Command{
	Use:   "run",
	Short: "Run Dracon Pipeline",
	Long:  `Use run to execute a Dracon pipeline-run.`,
	RunE: func(cmd *cobra.Command, args []string) error {
		tmpl := template.NewTemplater()
		err := tmpl.Load(runOpts.Path)
		if err != nil {
			return err
		}
		c, err := tmpl.String()
		if err != nil {
			return err
		}
		log.Println(c)
		err = kubernetes.Apply(c)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Failed to apply templates: %s\n", err)
			os.Exit(2)
		}
		return nil
	},
}

func init() {
	rootCmd.AddCommand(runCmd)

	runCmd.Flags().StringVarP(&runOpts.Path, "path", "p", "", "Path to load template from")
	runCmd.MarkFlagRequired("path")
}
