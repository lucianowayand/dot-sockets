package dot

import (
	"fmt"
	"os"
	"path/filepath"
)

// DOT represents a Graph Description Language document
type DOT struct {
	Name    string `json:"name"`
	Content string `json:"content"`
}

// Save writes a DOT to a file in the specified directory
func (d *DOT) Save(dir string) error {
	// Create directory if it doesn't exist
	if err := os.MkdirAll(dir, 0755); err != nil {
		return fmt.Errorf("failed to create directory: %w", err)
	}

	filename := filepath.Join(dir, d.Name+".dot")
	return os.WriteFile(filename, []byte(d.Content), 0644)
}

// LoadDOT reads a DOT file from disk
func LoadDOT(path string) (*DOT, error) {
	content, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read DOT file: %w", err)
	}

	name := filepath.Base(path)
	// Remove extension if present
	if ext := filepath.Ext(name); ext != "" {
		name = name[:len(name)-len(ext)]
	}

	return &DOT{
		Name:    name,
		Content: string(content),
	}, nil
}

// ListDOTs returns all DOT files in the specified directory
func ListDOTs(dir string) ([]string, error) {
	// Create directory if it doesn't exist
	if err := os.MkdirAll(dir, 0755); err != nil {
		return nil, fmt.Errorf("failed to create directory: %w", err)
	}

	entries, err := os.ReadDir(dir)
	if err != nil {
		return nil, fmt.Errorf("failed to read directory: %w", err)
	}

	var dots []string
	for _, entry := range entries {
		if !entry.IsDir() && filepath.Ext(entry.Name()) == ".dot" {
			dots = append(dots, filepath.Base(entry.Name()))
		}
	}
	return dots, nil
} 