/**
 * CodeDiff Component Tests
 * 
 * Tests for the CodeDiff component including:
 * - Basic rendering
 * - Syntax highlighting
 * - Inline comments
 * - Pagination for large diffs
 * - File expansion/collapse
 * 
 * **Validates: Requirements 3.1, 3.5**
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Mock Prism before importing CodeDiff
jest.mock('prismjs', () => ({
  __esModule: true,
  default: {
    highlight: jest.fn((code) => code),
    languages: {
      javascript: {},
      typescript: {},
      jsx: {},
      tsx: {},
      python: {},
      css: {},
      json: {},
      markdown: {},
      markup: {},
    },
  },
  highlight: jest.fn((code) => code),
  languages: {
    javascript: {},
    typescript: {},
    jsx: {},
    tsx: {},
    python: {},
    css: {},
    json: {},
    markdown: {},
    markup: {},
  },
}));

jest.mock('prismjs/themes/prism-tomorrow.css', () => ({}));
jest.mock('prismjs/components/prism-python', () => ({}));
jest.mock('prismjs/components/prism-javascript', () => ({}));
jest.mock('prismjs/components/prism-typescript', () => ({}));
jest.mock('prismjs/components/prism-jsx', () => ({}));
jest.mock('prismjs/components/prism-tsx', () => ({}));
jest.mock('prismjs/components/prism-css', () => ({}));
jest.mock('prismjs/components/prism-json', () => ({}));
jest.mock('prismjs/components/prism-markdown', () => ({}));

import CodeDiff, { FileDiff, Comment } from '../CodeDiff';

describe('CodeDiff Component', () => {
  const mockFileDiff: FileDiff = {
    path: 'src/example.ts',
    status: 'modified',
    additions: 5,
    deletions: 3,
    chunks: [
      {
        oldStart: 1,
        oldLines: 5,
        newStart: 1,
        newLines: 7,
        lines: [
          { type: 'context', content: 'function example() {', lineNumber: 1, oldLineNumber: 1, newLineNumber: 1 },
          { type: 'delete', content: '  console.log(\"old\");', lineNumber: 2, oldLineNumber: 2 },
          { type: 'add', content: '  console.log(\"new\");', lineNumber: 3, newLineNumber: 2 },
          { type: 'add', content: '  console.log(\"added\");', lineNumber: 4, newLineNumber: 3 },
          { type: 'context', content: '}', lineNumber: 5, oldLineNumber: 3, newLineNumber: 4 },
        ],
      },
    ],
  };

  const mockComment: Comment = {
    id: 'comment-1',
    author: 'John Doe',
    content: 'This looks good!',
    createdAt: new Date('2024-01-01'),
    lineNumber: 3,
    fileName: 'src/example.ts',
  };

  describe('Basic Rendering', () => {
    it('should render file diff with correct file name', () => {
      render(<CodeDiff files={[mockFileDiff]} />);
      expect(screen.getByText('src/example.ts')).toBeInTheDocument();
    });

    it('should display file status badge', () => {
      render(<CodeDiff files={[mockFileDiff]} />);
      expect(screen.getByText('modified')).toBeInTheDocument();
    });

    it('should display additions and deletions count', () => {
      render(<CodeDiff files={[mockFileDiff]} />);
      expect(screen.getByText('+5')).toBeInTheDocument();
      expect(screen.getByText('-3')).toBeInTheDocument();
    });

    it('should display total files changed count', () => {
      render(<CodeDiff files={[mockFileDiff]} />);
      expect(screen.getByText('Files Changed (1)')).toBeInTheDocument();
    });

    it('should display total additions and deletions in header', () => {
      render(<CodeDiff files={[mockFileDiff]} />);
      expect(screen.getByText(/5 additions/)).toBeInTheDocument();
      expect(screen.getByText(/3 deletions/)).toBeInTheDocument();
    });
  });

  describe('File Expansion', () => {
    it('should expand file by default', () => {
      render(<CodeDiff files={[mockFileDiff]} />);
      expect(screen.getByText('function example() {')).toBeInTheDocument();
    });

    it('should collapse file when clicking header', async () => {
      render(<CodeDiff files={[mockFileDiff]} />);
      
      const fileHeader = screen.getByRole('button', { name: /src\/example\.ts/ });
      await userEvent.click(fileHeader);
      
      await waitFor(() => {
        expect(screen.queryByText('function example() {')).not.toBeInTheDocument();
      });
    });
  });

  describe('Inline Comments', () => {
    it('should display existing comments', () => {
      render(<CodeDiff files={[mockFileDiff]} comments={[mockComment]} />);
      expect(screen.getByText('This looks good!')).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    it('should show comment button when onAddComment is provided', () => {
      const onAddComment = jest.fn();
      const { container } = render(
        <CodeDiff files={[mockFileDiff]} onAddComment={onAddComment} />
      );
      
      const commentButtons = container.querySelectorAll('button[title=\"Add comment\"]');
      expect(commentButtons.length).toBeGreaterThan(0);
    });
  });

  describe('Pagination', () => {
    const createLargeFile = (lineCount: number): FileDiff => {
      const lines = Array.from({ length: lineCount }, (_, i) => ({
        type: 'context' as const,
        content: `Line `,
        lineNumber: i + 1,
        oldLineNumber: i + 1,
        newLineNumber: i + 1,
      }));

      return {
        path: 'large-file.ts',
        status: 'modified',
        additions: 0,
        deletions: 0,
        chunks: [
          {
            oldStart: 1,
            oldLines: lineCount,
            newStart: 1,
            newLines: lineCount,
            lines,
          },
        ],
      };
    };

    it('should not show pagination for files under 1000 lines', () => {
      const smallFile = createLargeFile(500);
      render(<CodeDiff files={[smallFile]} />);
      
      expect(screen.queryByText(/Page/)).not.toBeInTheDocument();
    });

    it('should show pagination for files over 1000 lines', () => {
      const largeFile = createLargeFile(1500);
      render(<CodeDiff files={[largeFile]} />);
      
      // Use getAllByText since pagination appears at top and bottom
      const pageIndicators = screen.getAllByText(/Page 1 of 2/);
      expect(pageIndicators.length).toBeGreaterThan(0);
    });

    it('should display correct line range in pagination', () => {
      const largeFile = createLargeFile(1500);
      render(<CodeDiff files={[largeFile]} />);
      
      expect(screen.getByText(/Showing lines 1 - 1000 of 1500/)).toBeInTheDocument();
    });

    it('should respect custom linesPerPage prop', () => {
      const largeFile = createLargeFile(600);
      render(<CodeDiff files={[largeFile]} linesPerPage={300} />);
      
      // Use getAllByText since pagination appears at top and bottom
      const pageIndicators = screen.getAllByText(/Page 1 of 2/);
      expect(pageIndicators.length).toBeGreaterThan(0);
      expect(screen.getByText(/Showing lines 1 - 300 of 600/)).toBeInTheDocument();
    });

    it('should disable pagination when enablePagination is false', () => {
      const largeFile = createLargeFile(1500);
      render(<CodeDiff files={[largeFile]} enablePagination={false} />);
      
      expect(screen.queryByText(/Page/)).not.toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty files array', () => {
      render(<CodeDiff files={[]} />);
      
      expect(screen.getByText('Files Changed (0)')).toBeInTheDocument();
      expect(screen.getByText(/0 additions/)).toBeInTheDocument();
      expect(screen.getByText(/0 deletions/)).toBeInTheDocument();
    });

    it('should handle file with no chunks', () => {
      const emptyFile: FileDiff = {
        path: 'empty.ts',
        status: 'modified',
        additions: 0,
        deletions: 0,
        chunks: [],
      };
      
      render(<CodeDiff files={[emptyFile]} />);
      expect(screen.getByText('empty.ts')).toBeInTheDocument();
    });
  });
});
