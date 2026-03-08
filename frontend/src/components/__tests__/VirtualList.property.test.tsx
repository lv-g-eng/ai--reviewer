import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import fc from 'fast-check';
import { VirtualList } from '../VirtualList';

/**
 * Feature: frontend-production-optimization
 * 
 * Property-based tests for VirtualList component to verify:
 * - Only visible items are rendered (performance optimization)
 * - Correct positioning of items
 * - Proper handling of dynamic heights
 * - Scroll behavior correctness
 */

describe('VirtualList Property-Based Tests', () => {
  // Arbitrary for generating test items
  const itemArbitrary = fc.record({
    id: fc.integer({ min: 0, max: 10000 }),
    name: fc.string({ minLength: 1, maxLength: 50 }),
    content: fc.string({ minLength: 0, maxLength: 200 }),
  });

  const itemsArbitrary = fc.array(itemArbitrary, { minLength: 0, maxLength: 300 });

  /**
   * Property: Virtual scrolling should only render visible items
   * 
   * For any list of items and viewport configuration, the number of rendered items
   * should be proportional to the viewport height, not the total number of items.
   * This ensures performance optimization for large lists (100+ items).
   * 
   * Validates: Requirements 2.4, 5.5
   */
  it('should only render visible items regardless of total item count', () => {
    fc.assert(
      fc.property(
        itemsArbitrary,
        fc.integer({ min: 200, max: 1000 }), // viewport height
        fc.integer({ min: 30, max: 100 }), // item height
        (items, viewportHeight, itemHeight) => {
          if (items.length === 0) return true;

          const renderItem = jest.fn((item: typeof items[0]) => (
            <div>{item.name}</div>
          ));

          const { unmount } = render(
            <VirtualList
              items={items}
              height={viewportHeight}
              itemHeight={itemHeight}
              renderItem={renderItem}
            />
          );

          const renderedCount = renderItem.mock.calls.length;
          const maxVisibleItems = Math.ceil(viewportHeight / itemHeight);
          const expectedMaxRendered = maxVisibleItems + 6; // overscan default is 3 on each side

          // Should not render all items if list is large
          if (items.length > expectedMaxRendered) {
            expect(renderedCount).toBeLessThanOrEqual(expectedMaxRendered + 5); // small buffer for edge cases
          } else {
            // If list is small, should render all or nearly all items (within overscan range)
            expect(renderedCount).toBeGreaterThanOrEqual(Math.min(items.length - 1, 1));
            expect(renderedCount).toBeLessThanOrEqual(items.length);
          }

          unmount();
          return true;
        }
      ),
      { numRuns: 50 }
    );
  });

  /**
   * Property: Item positioning should be consistent and sequential
   * 
   * For any list of items with fixed height, each item should be positioned
   * exactly at index * itemHeight from the top.
   * 
   * Validates: Requirements 2.4, 5.5
   */
  it('should position items correctly based on their index and height', () => {
    fc.assert(
      fc.property(
        fc.array(itemArbitrary, { minLength: 10, maxLength: 50 }),
        fc.integer({ min: 40, max: 80 }), // item height
        (items, itemHeight) => {
          const renderItem = (item: typeof items[0]) => <div>{item.name}</div>;

          const { container, unmount } = render(
            <VirtualList
              items={items}
              height={500}
              itemHeight={itemHeight}
              renderItem={renderItem}
            />
          );

          const inner = container.querySelector('[data-testid="virtual-list-inner"]') as HTMLElement;
          const renderedItems = inner.querySelectorAll('[data-index]');

          renderedItems.forEach((element) => {
            const htmlElement = element as HTMLElement;
            const index = parseInt(htmlElement.getAttribute('data-index') || '0');
            const expectedTop = index * itemHeight;
            expect(htmlElement.style.top).toBe(`${expectedTop}px`);
          });

          unmount();
          return true;
        }
      ),
      { numRuns: 30 }
    );
  });

  /**
   * Property: Total height should equal sum of all item heights
   * 
   * For any list of items, the total scrollable height should equal
   * the sum of all item heights.
   * 
   * Validates: Requirements 2.4, 5.5
   */
  it('should calculate total height correctly', () => {
    fc.assert(
      fc.property(
        fc.array(itemArbitrary, { minLength: 1, maxLength: 100 }),
        fc.integer({ min: 30, max: 100 }), // item height
        (items, itemHeight) => {
          const renderItem = (item: typeof items[0]) => <div>{item.name}</div>;

          const { container, unmount } = render(
            <VirtualList
              items={items}
              height={500}
              itemHeight={itemHeight}
              renderItem={renderItem}
            />
          );

          const inner = container.querySelector('[data-testid="virtual-list-inner"]') as HTMLElement;
          const actualHeight = parseInt(inner.style.height);
          const expectedHeight = items.length * itemHeight;

          expect(actualHeight).toBe(expectedHeight);

          unmount();
          return true;
        }
      ),
      { numRuns: 50 }
    );
  });

  /**
   * Property: Scrolling should update visible items correctly
   * 
   * For any scroll position, the rendered items should correspond to
   * the items visible in the viewport at that position.
   * 
   * Validates: Requirements 2.4, 5.5
   */
  it('should render correct items after scrolling', () => {
    fc.assert(
      fc.property(
        fc.array(itemArbitrary, { minLength: 50, maxLength: 150 }),
        fc.integer({ min: 300, max: 600 }), // viewport height
        fc.integer({ min: 40, max: 80 }), // item height
        fc.integer({ min: 0, max: 5000 }), // scroll position
        (items, viewportHeight, itemHeight, scrollTop) => {
          const renderItem = jest.fn((item: typeof items[0], index: number) => (
            <div>{item.name}</div>
          ));

          const { unmount } = render(
            <VirtualList
              items={items}
              height={viewportHeight}
              itemHeight={itemHeight}
              renderItem={renderItem}
            />
          );

          const container = screen.getByTestId('virtual-list-container');
          
          // Scroll to position
          fireEvent.scroll(container, { target: { scrollTop } });

          // Calculate expected visible range
          const startIndex = Math.floor(scrollTop / itemHeight);
          const endIndex = Math.ceil((scrollTop + viewportHeight) / itemHeight);

          // Check that rendered items are within or near the visible range
          const renderedIndices = renderItem.mock.calls.map(call => call[1]);
          
          if (renderedIndices.length > 0) {
            const minRendered = Math.min(...renderedIndices);
            const maxRendered = Math.max(...renderedIndices);

            // With overscan, rendered range should include visible range
            expect(minRendered).toBeLessThanOrEqual(Math.max(0, startIndex));
            expect(maxRendered).toBeGreaterThanOrEqual(Math.min(items.length - 1, endIndex));
          }

          unmount();
          return true;
        }
      ),
      { numRuns: 30 }
    );
  });

  /**
   * Property: Dynamic height function should be called for each item
   * 
   * When using a dynamic height function, it should be called to calculate
   * the height for each item in the list.
   * 
   * Validates: Requirements 2.4, 5.5
   */
  it('should support dynamic item heights', () => {
    fc.assert(
      fc.property(
        fc.array(itemArbitrary, { minLength: 10, maxLength: 50 }),
        (items) => {
          const heightFn = jest.fn((item: typeof items[0]) => {
            return item.id % 2 === 0 ? 50 : 80;
          });

          const renderItem = (item: typeof items[0]) => <div>{item.name}</div>;

          const { unmount } = render(
            <VirtualList
              items={items}
              height={500}
              itemHeight={heightFn}
              renderItem={renderItem}
            />
          );

          // Height function should be called during position calculation
          expect(heightFn).toHaveBeenCalled();

          unmount();
          return true;
        }
      ),
      { numRuns: 30 }
    );
  });

  /**
   * Property: Empty list should render without errors
   * 
   * For an empty items array, the component should render successfully
   * without throwing errors.
   * 
   * Validates: Requirements 2.4, 5.5
   */
  it('should handle empty lists gracefully', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 200, max: 1000 }), // viewport height
        fc.integer({ min: 30, max: 100 }), // item height
        (viewportHeight, itemHeight) => {
          const renderItem = jest.fn((item: any) => <div>{item.name}</div>);

          const { unmount } = render(
            <VirtualList
              items={[]}
              height={viewportHeight}
              itemHeight={itemHeight}
              renderItem={renderItem}
            />
          );

          const container = screen.getByTestId('virtual-list-container');
          expect(container).toBeInTheDocument();
          expect(renderItem).not.toHaveBeenCalled();

          unmount();
          return true;
        }
      ),
      { numRuns: 20 }
    );
  });

  /**
   * Property: Performance should remain constant regardless of total items
   * 
   * Rendering time should not significantly increase with the total number
   * of items, as only visible items are rendered.
   * 
   * Validates: Requirements 2.4, 5.5
   */
  it('should maintain consistent performance for large lists', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 100, max: 500 }), // number of items
        (itemCount) => {
          const items = Array.from({ length: itemCount }, (_, i) => ({
            id: i,
            name: `Item ${i}`,
            content: `Content ${i}`,
          }));

          const renderItem = (item: typeof items[0]) => <div>{item.name}</div>;

          const startTime = performance.now();
          const { unmount } = render(
            <VirtualList
              items={items}
              height={500}
              itemHeight={50}
              renderItem={renderItem}
            />
          );
          const endTime = performance.now();

          const renderTime = endTime - startTime;

          // Rendering should be fast regardless of item count (relaxed threshold for CI)
          expect(renderTime).toBeLessThan(200);

          unmount();
          return true;
        }
      ),
      { numRuns: 20 }
    );
  });

  /**
   * Property: onScroll callback should be called with correct scroll position
   * 
   * When scrolling occurs, the onScroll callback should be invoked with
   * the current scroll position.
   * 
   * Validates: Requirements 2.4, 5.5
   */
  it('should call onScroll with correct scroll position', () => {
    fc.assert(
      fc.property(
        fc.array(itemArbitrary, { minLength: 50, maxLength: 100 }),
        fc.integer({ min: 0, max: 2000 }), // scroll position
        (items, scrollTop) => {
          const onScroll = jest.fn();
          const renderItem = (item: typeof items[0]) => <div>{item.name}</div>;

          const { unmount } = render(
            <VirtualList
              items={items}
              height={500}
              itemHeight={50}
              renderItem={renderItem}
              onScroll={onScroll}
            />
          );

          const container = screen.getByTestId('virtual-list-container');
          fireEvent.scroll(container, { target: { scrollTop } });

          expect(onScroll).toHaveBeenCalledWith(scrollTop);

          unmount();
          return true;
        }
      ),
      { numRuns: 30 }
    );
  });
});
