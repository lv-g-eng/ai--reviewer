'use client';

import React, { useState } from 'react';
import { VirtualList } from '../VirtualList';

interface Project {
  id: number;
  name: string;
  status: 'active' | 'archived';
  createdAt: Date;
}

/**
 * Example usage of VirtualList component for rendering large project lists
 * 
 * This demonstrates:
 * - Fixed height items
 * - Efficient rendering of 100+ items
 * - Scroll position tracking
 */
export function VirtualListExample() {
  // Generate sample data (100+ projects)
  const [projects] = useState<Project[]>(() =>
    Array.from({ length: 150 }, (_, i) => ({
      id: i,
      name: `Project ${i + 1}`,
      status: i % 3 === 0 ? 'archived' : 'active',
      createdAt: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000),
    }))
  );

  const [scrollPosition, setScrollPosition] = useState(0);

  return (
    <div className="p-4">
      <div className="mb-4">
        <h2 className="text-2xl font-bold">Virtual List Example</h2>
        <p className="text-gray-600">
          Rendering {projects.length} projects efficiently
        </p>
        <p className="text-sm text-gray-500">
          Scroll Position: {Math.round(scrollPosition)}px
        </p>
      </div>

      <VirtualList
        items={projects}
        height={600}
        itemHeight={80}
        onScroll={setScrollPosition}
        className="border rounded-lg shadow-sm"
        renderItem={(project) => (
          <div className="p-4 border-b hover:bg-gray-50 transition-colors">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-semibold text-lg">{project.name}</h3>
                <p className="text-sm text-gray-600">
                  Created: {project.createdAt.toLocaleDateString()}
                </p>
              </div>
              <span
                className={`px-3 py-1 rounded-full text-sm ${
                  project.status === 'active'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                {project.status}
              </span>
            </div>
          </div>
        )}
      />
    </div>
  );
}

/**
 * Example with dynamic heights based on content
 */
interface Task {
  id: number;
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high';
}

export function VirtualListDynamicExample() {
  const [tasks] = useState<Task[]>(() =>
    Array.from({ length: 100 }, (_, i) => ({
      id: i,
      title: `Task ${i + 1}`,
      description: i % 3 === 0 ? `This is a longer description for task ${i + 1}` : undefined,
      priority: (['low', 'medium', 'high'] as const)[i % 3],
    }))
  );

  // Calculate dynamic height based on whether task has description
  const getItemHeight = (task: Task) => {
    return task.description ? 100 : 60;
  };

  return (
    <div className="p-4">
      <div className="mb-4">
        <h2 className="text-2xl font-bold">Dynamic Height Example</h2>
        <p className="text-gray-600">
          Tasks with variable heights based on content
        </p>
      </div>

      <VirtualList
        items={tasks}
        height={600}
        itemHeight={getItemHeight}
        className="border rounded-lg shadow-sm"
        renderItem={(task) => (
          <div className="p-4 border-b hover:bg-gray-50 transition-colors">
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-semibold">{task.title}</h3>
              <span
                className={`px-2 py-1 rounded text-xs ${
                  task.priority === 'high'
                    ? 'bg-red-100 text-red-800'
                    : task.priority === 'medium'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-blue-100 text-blue-800'
                }`}
              >
                {task.priority}
              </span>
            </div>
            {task.description && (
              <p className="text-sm text-gray-600">{task.description}</p>
            )}
          </div>
        )}
      />
    </div>
  );
}
