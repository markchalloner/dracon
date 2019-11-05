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
	"os"

	"github.com/spf13/cobra"

	"github.com/thought-machine/dracon/pkg/kubernetes"
	"github.com/thought-machine/dracon/pkg/template"
)

var setupOpts struct {
	Path string
}

// setupCmd represents the setup command
var setupCmd = &cobra.Command{
	Use:   "setup",
	Short: "Setup a new Dracon Pipeline",
	Long:  `Use setup to help with setting up a new Dracon pipeline.`,
	RunE: func(cmd *cobra.Command, args []string) error {
		tmpl := template.NewTemplater()
		err := tmpl.LoadAll(setupOpts.Path)
		if err != nil {
			return err
		}
		c, err := tmpl.String()
		if err != nil {
			return err
		}
		err = kubernetes.Apply(c)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Failed to apply templates: %s\n", err)
			os.Exit(2)
		}
		return nil
	},
}

func init() {
	rootCmd.AddCommand(setupCmd)

	setupCmd.Flags().StringVarP(&setupOpts.Path, "path", "p", "", "Path to load templates from")
	setupCmd.MarkFlagRequired("path")
}
