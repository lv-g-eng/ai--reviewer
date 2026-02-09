'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
    Plus,
    Eye,
    Network,
    AlertTriangle
} from 'lucide-react'

export function QuickActions() {
    return (
        <Card className="col-span-3">
            <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>
                    Common tasks and shortcuts
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
                <Button variant="outline" className="w-full justify-start">
                    <Plus className="mr-2 h-4 w-4" />
                    Add New Project
                </Button>
                <Button variant="outline" className="w-full justify-start">
                    <Eye className="mr-2 h-4 w-4" />
                    View All Reviews
                </Button>
                <Button variant="outline" className="w-full justify-start">
                    <Network className="mr-2 h-4 w-4" />
                    Architecture Overview
                </Button>
                <Button variant="outline" className="w-full justify-start">
                    <AlertTriangle className="mr-2 h-4 w-4" />
                    View Critical Issues
                </Button>
            </CardContent>
        </Card>
    )
}
