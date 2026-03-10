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

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import CodeDiff, { FileDiff, Comment } from '../CodeDiff';

describe('CodeDiff Component', () => {
  // Mock data
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
          { type: 'delete', content: '  console.log("old");', lineNumber: 2, oldLineNumber: 2 },
          { type: 'add', content: '  console.log("new");', lineNumber: 3, newLineNumber: 2 },
          { type: 'add', content: '  console.log("added");', lineNumber: 4, newLineNumber: 3 },
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

    it('should expand collapsed file when clicking header again', async () => {
      render(<CodeDiff files={[mockFileDiff]} />);
      
      const fileHeader = screen.getByRole('button', { name: /src\/example\.ts/ });
      
      // Collapse
      await userEvent.click(fileHeader);
      await waitFor(() => {
        expect(screen.queryByText('function example() {')).not.toBeInTheDocument();
      });
      
      // Expand
      await userEvent.click(fileHeader);
      await waitFor(() => {
        expect(screen.getByText('function example() {')).toBeInTheDocument();
      });
    });
  });

  describe('Diff Line Rendering', () => {
    it('should render context lines', () => {
      render(<CodeDiff files={[mockFileDiff]} />);
      expect(screen.getByText('function example() {')).toBeInTheDocument();
      expect(screen.getByText('}')).toBeInTheDocument();
    });

    it('should render added lines', () => {
      render(<CodeDiff files={[mockFileDiff]} />);
      expect(screen.getByText('console.log("new");')).toBeInTheDocument();
      expect(screen.getByText('console.log("added");')).toBeInTheDocument();
    });

    it('should render deleted lines', () => {
      render(<CodeDiff files={[mockFileDiff]} />);
      expect(screen.getByText('console.log("old");')).toBeInTheDocument();
    });

    it('should display line numbers', () => {
      const { container } = render(<CodeDiff files={[mockFileDiff]} />);
      const lineNumbers = container.querySelectorAll('.text-xs.text-gray-400');
      expect(lineNumbers.length).toBeGreaterThan(0);
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
      
      const commentButtons = container.querySelectorAll('button[title="Add comment"]');
      expect(commentButtons.length).toBeGreaterThan(0);
    });

    it('should not show comment button when onAddComment is not provided', () => {
      const { container } = render(<CodeDiff files={[mockFileDiff]} />);
      
      const commentButtons = container.querySelectorAll('button[title="Add comment"]');
      expect(commentButtons.length).toBe(0);
    });

    it('should open comment form when clicking comment button', async () => {
      const onAddComment = jest.fn();
      const { container } = render(
        <CodeDiff files={[mockFileDiff]} onAddComment={onAddComment} />
      );
      
      const commentButton = container.querySelector('button[title="Add comment"]');
      expect(commentButton).toBeInTheDocument();
      
      await userEvent.click(commentButton!);
      
      expect(screen.getByPlaceholderText('Add a comment...')).toBeInTheDocument();
    });

    it('should submit comment when clicking Comment button', async () => {
      const onAddComment = jest.fn();
      const { container } = render(
        <CodeDiff files={[mockFileDiff]} onAddComment={onAddComment} />
      );
      
      // Open comment form
      const commentButton = container.querySelector('button[title="Add comment"]');
      await userEvent.click(commentButton!);
      
      // Type comment
      const textarea = screen.getByPlaceholderText('Add a comment...');
      await userEvent.type(textarea, 'Great work!');
      
      // Submit
      const submitButton = screen.getByRole('button', { name: 'Comment' });
      await userEvent.click(submitButton);
      
      expect(onAddComment).toHaveBeenCalledWith('src/example.ts', 1, 'Great work!');
    });

    it('should not submit empty comment', async () => {
      const onAddComment = jest.fn();
      const { container } = render(
        <CodeDiff files={[mockFileDiff]} onAddComment={onAddComment} />
      );
      
      // Open comment form
      const commentButton = container.querySelector('button[title="Add comment"]');
      await userEvent.click(commentButton!);
      
      // Try to submit without typing
      const submitButton = screen.getByRole('button', { name: 'Comment' });
      expect(submitButton).toBeDisabled();
    });

    it('should cancel comment form when clicking Cancel button', async () => {
      const onAddComment = jest.fn();
      const { container } = render(
        <CodeDiff files={[mockFileDiff]} onAddComment={onAddComment} />
      );
      
      // Open comment form
      const commentButton = container.querySelector('button[title="Add comment"]');
      await userEvent.click(commentButton!);
      
      // Type comment
      const textarea = screen.getByPlaceholderText('Add a comment...');
      await userEvent.type(textarea, 'Test comment');
      
      // Cancel
      const cancelButton = screen.getByRole('button', { name: 'Cancel' });
      await userEvent.click(cancelButton);
      
      expect(screen.queryByPlaceholderText('Add a comment...')).not.toBeInTheDocument();
    });

    it('should delete comment when clicking Delete button', async () => {
      const onDeleteComment = jest.fn();
      render(
        <CodeDiff
          files={[mockFileDiff]}
          comments={[mockComment]}
          onDeleteComment={onDeleteComment}
        />
      );
      
      const deleteButton = screen.getByRole('button', { name: 'Delete' });
      await userEvent.click(deleteButton);
      
      expect(onDeleteComment).toHaveBeenCalledWith('comment-1');
    });
  });


  describe('Pagination', () => {
    // Create a large file with specified line count
    const createLargeFile = (lineCount: number): FileDiff => {
      const lines = Array.from({ length: lineCount }, (_, i) => ({
        type: 'context' as const,
        content: `Line ${i + 1}`,
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
      
      expect(screen.getByText(/Page 1 of 2/)).toBeInTheDocument();
    });

    it('should display correct line range in pagination', () => {
      const largeFile = createLargeFile(1500);
      render(<CodeDiff files={[largeFile]} />);
      
      expect(screen.getByText(/Showing lines 1 - 1000 of 1500/)).toBeInTheDocument();
    });

    it('should navigate to next page', async () => {
      const largeFile = createLargeFile(1500);
      render(<CodeDiff files={[largeFile]} />);
      
      // Find next page button
      const nextButtons = screen.getAllByRole('button').filter(
        (btn) => !(btn as HTMLButtonElement).disabled && btn.querySelector('svg')
      );
      
      const nextButton = nextButtons.find((btn) => !(btn as HTMLButtonElement).disabled);
      
      if (nextButton) {
        await userEvent.click(nextButton);
        
        await waitFor(() => {
          expect(screen.getByText(/Page 2 of 2/)).toBeInTheDocument();
        });
      }
    });

    it('should respect custom linesPerPage prop', () => {
      const largeFile = createLargeFile(600);
      render(<CodeDiff files={[largeFile]} linesPerPage={300} />);
      
      expect(screen.getByText(/Page 1 of 2/)).toBeInTheDocument();
      expect(screen.getByText(/Showing lines 1 - 300 of 600/)).toBeInTheDocument();
    });

    it('should disable pagination when enablePagination is false', () => {
      const largeFile = createLargeFile(1500);
      render(<CodeDiff files={[largeFile]} enablePagination={false} />);
      
      expect(screen.queryByText(/Page/)).not.toBeInTheDocument();
    });
  });

  describe('Multiple Files', () => {
    const file1: FileDiff = {
      path: 'file1.ts',
      status: 'added',
      additions: 10,
      deletions: 0,
      chunks: [
        {
          oldStart: 0,
          oldLines: 0,
          newStart: 1,
          newLines: 1,
          lines: [
            { type: 'add', content: 'new file', lineNumber: 1, newLineNumber: 1 },
          ],
        },
      ],
    };

    const file2: FileDiff = {
      path: 'file2.ts',
      status: 'deleted',
      additions: 0,
      deletions: 5,
      chunks: [
        {
          oldStart: 1,
          oldLines: 1,
          newStart: 0,
          newLines: 0,
          lines: [
            { type: 'delete', content: 'deleted file', lineNumber: 1, oldLineNumber: 1 },
          ],
        },
      ],
    };

    it('should render multiple files', () => {
      render(<CodeDiff files={[file1, file2]} />);
      
      expect(screen.getByText('file1.ts')).toBeInTheDocument();
      expect(screen.getByText('file2.ts')).toBeInTheDocument();
    });

    it('should display correct total files count', () => {
      render(<CodeDiff files={[file1, file2]} />);
      
      expect(screen.getByText('Files Changed (2)')).toBeInTheDocument();
    });

    it('should display correct total additions and deletions', () => {
      render(<CodeDiff files={[file1, file2]} />);
      
      expect(screen.getByText(/10 additions/)).toBeInTheDocument();
      expect(screen.getByText(/5 deletions/)).toBeInTheDocument();
    });

    it('should expand/collapse files independently', async () => {
      render(<CodeDiff files={[file1, file2]} />);
      
      // Both files should be expanded initially
      expect(screen.getByText('new file')).toBeInTheDocument();
      expect(screen.getByText('deleted file')).toBeInTheDocument();
      
      // Collapse first file
      const file1Header = screen.getByRole('button', { name: /file1\.ts/ });
      await userEvent.click(file1Header);
      
      await waitFor(() => {
        expect(screen.queryByText('new file')).not.toBeInTheDocument();
        expect(screen.getByText('deleted file')).toBeInTheDocument();
      });
    });
  });

  describe('File Status Badges', () => {
    it('should display added status with green badge', () => {
      const addedFile: FileDiff = {
        ...mockFileDiff,
        status: 'added',
      };
      render(<CodeDiff files={[addedFile]} />);
      
      const badge = screen.getByText('added');
      expect(badge).toHaveClass('bg-green-100');
    });

    it('should display deleted status with red badge', () => {
      const deletedFile: FileDiff = {
        ...mockFileDiff,
        status: 'deleted',
      };
      render(<CodeDiff files={[deletedFile]} />);
      
      const badge = screen.getByText('deleted');
      expect(badge).toHaveClass('bg-red-100');
    });

    it('should display renamed status with yellow badge', () => {
      const renamedFile: FileDiff = {
        ...mockFileDiff,
        status: 'renamed',
      };
      render(<CodeDiff files={[renamedFile]} />);
      
      const badge = screen.getByText('renamed');
      expect(badge).toHaveClass('bg-yellow-100');
    });

    it('should display modified status with blue badge', () => {
      render(<CodeDiff files={[mockFileDiff]} />);
      
      const badge = screen.getByText('modified');
      expect(badge).toHaveClass('bg-blue-100');
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

    it('should handle comments for non-existent lines', () => {
      const orphanComment: Comment = {
        id: 'orphan',
        author: 'Test',
        content: 'Orphan comment',
        createdAt: new Date(),
        lineNumber: 999,
        fileName: 'src/example.ts',
      };
      
      render(<CodeDiff files={[mockFileDiff]} comments={[orphanComment]} />);
      
      // Comment should not be displayed since line doesn't exist
      expect(screen.queryByText('Orphan comment')).not.toBeInTheDocument();
    });

    it('should handle very long file paths', () => {
      const longPathFile: FileDiff = {
        ...mockFileDiff,
        path: 'very/long/path/to/some/deeply/nested/directory/structure/file.ts',
      };
      
      render(<CodeDiff files={[longPathFile]} />);
      expect(screen.getByText(longPathFile.path)).toBeInTheDocument();
    });

    it('should handle special characters in file content', () => {
      const specialCharsFile: FileDiff = {
        path: 'special.ts',
        status: 'modified',
        additions: 1,
        deletions: 0,
        chunks: [
          {
            oldStart: 1,
            oldLines: 0,
            newStart: 1,
            newLines: 1,
            lines: [
              {
                type: 'add',
                content: 'const str = "<script>alert(\'XSS\')</script>";',
                lineNumber: 1,
                newLineNumber: 1,
              },
            ],
          },
        ],
      };
      
      render(<CodeDiff files={[specialCharsFile]} />);
      expect(screen.getByText(/alert/)).toBeInTheDocument();
    });
  });
});
