'use client';

/**
 * Health Metrics Dashboard Component
 */
import { Shield, Code, Layers, TestTube } from 'lucide-react';

interface HealthMetricsProps {
    code_quality?: number;
    security_rating?: number;
    architecture_health?: number;
    test_coverage?: number;
}

export default function HealthMetrics({
    code_quality = 0,
    security_rating = 0,
    architecture_health = 0,
    test_coverage = 0,
}: HealthMetricsProps) {
    const metrics = [
        {
            name: 'Code Quality',
            value: code_quality,
            icon: Code,
            color: 'text-blue-600 dark:text-blue-400',
            bgColor: 'bg-blue-100 dark:bg-blue-900/30',
        },
        {
            name: 'Security Rating',
            value: security_rating,
            icon: Shield,
            color: 'text-green-600 dark:text-green-400',
            bgColor: 'bg-green-100 dark:bg-green-900/30',
        },
        {
            name: 'Architecture Health',
            value: architecture_health,
            icon: Layers,
            color: 'text-purple-600 dark:text-purple-400',
            bgColor: 'bg-purple-100 dark:bg-purple-900/30',
        },
        {
            name: 'Test Coverage',
            value: test_coverage,
            icon: TestTube,
            color: 'text-orange-600 dark:text-orange-400',
            bgColor: 'bg-orange-100 dark:bg-orange-900/30',
        },
    ];

    const getScoreColor = (score: number) => {
        if (score >= 80) return 'text-green-600 dark:text-green-400';
        if (score >= 60) return 'text-yellow-600 dark:text-yellow-400';
        return 'text-red-600 dark:text-red-400';
    };

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {metrics.map((metric) => {
                const Icon = metric.icon;
                return (
                    <div
                        key={metric.name}
                        className="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6"
                    >
                        <div className="flex items-center justify-between mb-4">
                            <div className={`p-2 rounded-lg ${metric.bgColor}`}>
                                <Icon className={`h-6 w-6 ${metric.color}`} />
                            </div>
                            <span className={`text-2xl font-bold ${getScoreColor(metric.value)}`}>
                                {metric.value}%
                            </span>
                        </div>

                        <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                            {metric.name}
                        </h3>

                        {/* Progress Bar */}
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div
                                className={`h-2 rounded-full transition-all duration-500 ${metric.value >= 80
                                        ? 'bg-green-500'
                                        : metric.value >= 60
                                            ? 'bg-yellow-500'
                                            : 'bg-red-500'
                                    }`}
                                style={{ width: `${metric.value}%` }}
                            />
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
