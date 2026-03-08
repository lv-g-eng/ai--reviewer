import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { VirtualList } from '../VirtualList';

describe('VirtualList', () => {
  const mockItems = Array.from({ length: 200 }, (_, i) => ({
    id: i,
    name: `Item ${i}`,
  }));

  const mockRenderItem = jest.fn((item: typeof mockItems[0], index: number) => (
    <div data-testid={`item-${item.id}`}>{item.name}</div>
  ));

  beforeEach(() => {
    mockRenderItem.mockClear();
  });

  it('should render only visible items', () => {
    render(
      <VirtualList
        items={mockItems}
        height={500}
        itemHeight={50}
        renderItem={mockRenderItem}
      />
    );

    const container = screen.getByTestId('virtual-list-container');
    expect(container).toBeInTheDocument();

    // Should render approximately 500/50 = 10 items + overscan
    // With default overscan of 3, we expect around 16 items (10 + 3*2)
    expect(mockRenderItem).toHaveBeenCalled();
    const callCount = mockRenderItem.mock.calls.length;
    expect(callCount).toBeGreaterThan(10);
    expect(callCount).toBeLessThan(mockItems.length); // Should not render all 200 items
  });

  it('should render all items when list is short', () => {
    const shortItems = mockItems.slice(0, 5);
    render(
      <VirtualList
        items={shortItems}
        height={500}
        itemHeight={50}
        renderItem={mockRenderItem}
      />
    );

    // With overscan, might render a few more than the actual count
    expect(mockRenderItem.mock.calls.length).toBeGreaterThanOrEqual(shortItems.length);
  });

  it('should update visible items on scroll', async () => {
    const { rerender } = render(
      <VirtualList
        items={mockItems}
        height={500}
        itemHeight={50}
        renderItem={mockRenderItem}
      />
    );

    const container = screen.getByTestId('virtual-list-container');
    const initialCallCount = mockRenderItem.mock.calls.length;

    // Scroll down
    fireEvent.scroll(container, { target: { scrollTop: 1000 } });

    // Wait for state update
    await waitFor(() => {
      expect(mockRenderItem.mock.calls.length).toBeGreaterThan(initialCallCount);
    });

    // Check that different items are rendered
    const lastCall = mockRenderItem.mock.calls[mockRenderItem.mock.calls.length - 1];
    expect(lastCall[1]).toBeGreaterThan(10); // Index should be greater than initial visible range
  });

  it('should call onScroll callback when scrolling', () => {
    const onScroll = jest.fn();
    render(
      <VirtualList
        items={mockItems}
        height={500}
        itemHeight={50}
        renderItem={mockRenderItem}
        onScroll={onScroll}
      />
    );

    const container = screen.getByTestId('virtual-list-container');
    fireEvent.scroll(container, { target: { scrollTop: 500 } });

    expect(onScroll).toHaveBeenCalledWith(500);
  });

  it('should support dynamic item heights with function', () => {
    const dynamicHeightFn = jest.fn((item: typeof mockItems[0]) => {
      return item.id % 2 === 0 ? 50 : 100;
    });

    render(
      <VirtualList
        items={mockItems}
        height={500}
        itemHeight={dynamicHeightFn}
        renderItem={mockRenderItem}
      />
    );

    expect(dynamicHeightFn).toHaveBeenCalled();
    expect(mockRenderItem).toHaveBeenCalled();
  });

  it('should apply custom className', () => {
    render(
      <VirtualList
        items={mockItems}
        height={500}
        itemHeight={50}
        renderItem={mockRenderItem}
        className="custom-class"
      />
    );

    const container = screen.getByTestId('virtual-list-container');
    expect(container).toHaveClass('custom-class');
  });

  it('should handle empty items array', () => {
    render(
      <VirtualList
        items={[]}
        height={500}
        itemHeight={50}
        renderItem={mockRenderItem}
      />
    );

    const container = screen.getByTestId('virtual-list-container');
    expect(container).toBeInTheDocument();
    expect(mockRenderItem).not.toHaveBeenCalled();
  });

  it('should set correct total height based on items', () => {
    render(
      <VirtualList
        items={mockItems}
        height={500}
        itemHeight={50}
        renderItem={mockRenderItem}
      />
    );

    const inner = screen.getByTestId('virtual-list-inner');
    const expectedHeight = mockItems.length * 50;
    expect(inner).toHaveStyle({ height: `${expectedHeight}px` });
  });

  it('should support custom overscan value', () => {
    render(
      <VirtualList
        items={mockItems}
        height={500}
        itemHeight={50}
        overscan={5}
        renderItem={mockRenderItem}
      />
    );

    // With overscan of 5, should render more items
    const callCount = mockRenderItem.mock.calls.length;
    expect(callCount).toBeGreaterThan(10);
  });

  it('should handle large lists efficiently (100+ items)', () => {
    const largeItems = Array.from({ length: 150 }, (_, i) => ({
      id: i,
      name: `Item ${i}`,
    }));

    const startTime = performance.now();
    render(
      <VirtualList
        items={largeItems}
        height={500}
        itemHeight={50}
        renderItem={mockRenderItem}
      />
    );
    const endTime = performance.now();

    // Should render quickly (less than 200ms for CI environments)
    expect(endTime - startTime).toBeLessThan(200);

    // Should not render all items
    expect(mockRenderItem.mock.calls.length).toBeLessThan(largeItems.length);
  });

  it('should position items correctly', () => {
    render(
      <VirtualList
        items={mockItems.slice(0, 10)}
        height={500}
        itemHeight={50}
        renderItem={mockRenderItem}
      />
    );

    const inner = screen.getByTestId('virtual-list-inner');
    const items = inner.querySelectorAll('[data-index]');

    items.forEach((item, index) => {
      const element = item as HTMLElement;
      const expectedTop = index * 50;
      expect(element.style.top).toBe(`${expectedTop}px`);
    });
  });

  it('should handle scroll to bottom', async () => {
    render(
      <VirtualList
        items={mockItems}
        height={500}
        itemHeight={50}
        renderItem={mockRenderItem}
      />
    );

    const container = screen.getByTestId('virtual-list-container');
    const inner = screen.getByTestId('virtual-list-inner');
    const totalHeight = parseInt(inner.style.height);

    // Scroll to bottom
    fireEvent.scroll(container, { target: { scrollTop: totalHeight - 500 } });

    await waitFor(() => {
      // Should render items near the end
      const lastCall = mockRenderItem.mock.calls[mockRenderItem.mock.calls.length - 1];
      expect(lastCall[1]).toBeGreaterThan(mockItems.length - 20);
    });
  });

  it('should maintain performance with frequent scrolling', async () => {
    const onScroll = jest.fn();
    render(
      <VirtualList
        items={mockItems}
        height={500}
        itemHeight={50}
        renderItem={mockRenderItem}
        onScroll={onScroll}
      />
    );

    const container = screen.getByTestId('virtual-list-container');

    // Simulate rapid scrolling
    const startTime = performance.now();
    for (let i = 0; i < 10; i++) {
      fireEvent.scroll(container, { target: { scrollTop: i * 100 } });
    }
    const endTime = performance.now();

    // Should handle rapid scrolling efficiently (relaxed for CI)
    expect(endTime - startTime).toBeLessThan(200);
    expect(onScroll).toHaveBeenCalledTimes(10);
  });
});
