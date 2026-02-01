/**
 * Example test file to ensure Jest is working correctly
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

// Simple component for testing
const TestComponent = () => {
  return <div>Hello World</div>;
};

describe('Example Test Suite', () => {
  test('renders hello world', () => {
    render(<TestComponent />);
    expect(screen.getByText('Hello World')).toBeInTheDocument();
  });

  test('basic math works', () => {
    expect(2 + 2).toBe(4);
  });

  test('async test example', async () => {
    const promise = Promise.resolve('test');
    const result = await promise;
    expect(result).toBe('test');
  });
});