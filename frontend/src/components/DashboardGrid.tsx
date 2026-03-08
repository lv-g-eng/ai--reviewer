/**
 * Dashboard Grid Component
 * 
 * Grid layout system for dashboard widgets
 */

import React, { useState } from 'react';
import { Widget, WidgetPosition } from '../types/dashboard';

interface DashboardGridProps {
  widgets: Widget[];
  columns: number;
  onLayoutChange?: (widgets: Widget[]) => void;
  editable?: boolean;
  renderWidget: (widget: Widget) => React.ReactNode;
}

/**
 * Grid layout component for dashboard widgets
 * Provides drag-and-drop functionality for widget positioning
 */
export const DashboardGrid: React.FC<DashboardGridProps> = ({
  widgets,
  columns = 12,
  onLayoutChange,
  editable = false,
  renderWidget
}) => {
  const [draggingWidget, setDraggingWidget] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  const cellSize = 100; // Base cell size in pixels
  const gap = 16; // Gap between widgets

  /**
   * Calculate widget style based on position
   */
  const getWidgetStyle = (position: WidgetPosition): React.CSSProperties => {
    return {
      position: 'absolute',
      left: `${(position.x * (cellSize + gap))}px`,
      top: `${(position.y * (cellSize + gap))}px`,
      width: `${(position.w * cellSize) + ((position.w - 1) * gap)}px`,
      height: `${(position.h * cellSize) + ((position.h - 1) * gap)}px`,
      transition: draggingWidget ? 'none' : 'all 0.3s ease',
    };
  };

  /**
   * Handle drag start
   */
  const handleDragStart = (e: React.MouseEvent, widgetId: string) => {
    if (!editable) return;

    const widget = widgets.find(w => w.id === widgetId);
    if (!widget) return;

    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    setDragOffset({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    });
    setDraggingWidget(widgetId);
  };

  /**
   * Handle drag move
   */
  const handleDragMove = (e: React.MouseEvent) => {
    if (!draggingWidget || !editable) return;

    const widget = widgets.find(w => w.id === draggingWidget);
    if (!widget) return;

    const container = e.currentTarget as HTMLElement;
    const rect = container.getBoundingClientRect();
    
    const x = Math.max(0, Math.min(
      columns - widget.position.w,
      Math.round((e.clientX - rect.left - dragOffset.x) / (cellSize + gap))
    ));
    
    const y = Math.max(0, Math.round((e.clientY - rect.top - dragOffset.y) / (cellSize + gap)));

    if (x !== widget.position.x || y !== widget.position.y) {
      const updatedWidgets = widgets.map(w =>
        w.id === draggingWidget
          ? { ...w, position: { ...w.position, x, y } }
          : w
      );

      if (onLayoutChange) {
        onLayoutChange(updatedWidgets);
      }
    }
  };

  /**
   * Handle drag end
   */
  const handleDragEnd = () => {
    setDraggingWidget(null);
  };

  /**
   * Calculate grid height
   */
  const getGridHeight = (): number => {
    if (widgets.length === 0) return cellSize;
    
    const maxY = Math.max(...widgets.map(w => w.position.y + w.position.h));
    return (maxY * cellSize) + ((maxY - 1) * gap) + gap;
  };

  return (
    <div
      className="relative bg-gray-50 rounded-lg p-4"
      style={{
        height: `${getGridHeight()}px`,
        minHeight: '400px'
      }}
      onMouseMove={handleDragMove}
      onMouseUp={handleDragEnd}
      onMouseLeave={handleDragEnd}
    >
      {/* Grid background */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage: `
            linear-gradient(to right, #e5e7eb 1px, transparent 1px),
            linear-gradient(to bottom, #e5e7eb 1px, transparent 1px)
          `,
          backgroundSize: `${cellSize + gap}px ${cellSize + gap}px`,
          opacity: editable ? 0.5 : 0
        }}
      />

      {/* Widgets */}
      {widgets.map((widget) => (
        <div
          key={widget.id}
          style={getWidgetStyle(widget.position)}
          className={`bg-white rounded-lg shadow-md overflow-hidden ${
            editable ? 'cursor-move' : ''
          } ${draggingWidget === widget.id ? 'opacity-70 z-50' : 'z-10'}`}
          onMouseDown={(e) => handleDragStart(e, widget.id)}
        >
          {/* Widget header (only in edit mode) */}
          {editable && (
            <div className="bg-gray-100 px-3 py-2 border-b border-gray-200 flex items-center justify-between">
              <span className="text-xs font-medium text-gray-600">
                Widget {widget.id.slice(0, 8)}
              </span>
              <div className="flex gap-1">
                <button
                  className="text-gray-400 hover:text-gray-600"
                  title="Resize"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                  </svg>
                </button>
              </div>
            </div>
          )}

          {/* Widget content */}
          <div className="p-4 h-full overflow-auto">
            {renderWidget(widget)}
          </div>
        </div>
      ))}

      {/* Empty state */}
      {widgets.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center text-gray-400">
            <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 0v10" />
            </svg>
            <p className="text-lg font-medium">No widgets yet</p>
            <p className="text-sm mt-1">Add widgets to customize your dashboard</p>
          </div>
        </div>
      )}
    </div>
  );
};
