'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
    GitPullRequest,
    AlertTriangle,
    FolderGit2,
    Network
} from 'lucide-react'

interface RecentActivityProps {
    isLoading: boolean
}

export function RecentActivity({ isLoading }: RecentActivityProps) {
    return (
        <Card className="col-span-4">
            <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>
                    Latest updates from your projects
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {isLoading ? (
                        <>
                            {[...Array(5)].map((_, i) => (
                                <div key={i} className="flex items-center space-x-4">
                                    <Skeleton className="h-10 w-10 rounded-full" />
                                    <div className="space-y-2 flex-1">
                                        <Skeleton className="h-4 w-full" />
                                        <Skeleton className="h-3 w-24" />
                                    </div>
                                </div>
                            ))}
                        </>
                    ) : (
                        <>
                            <div className="flex items-start space-x-4">
                                <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                                    <GitPullRequest className="h-5 w-5 text-primary" />
                                </div>
                                <div className="flex-1 space-y-1">
                                    <p className="text-sm font-medium">
                                        New PR review completed for <span className="text-primary">user-auth-service</span>
                                    </p>
                                    <p className="text-xs text-muted-foreground">2 minutes ago</p>
                                </div>
                                <Badge variant="success">Passed</Badge>
                            </div>

                            <div className="flex items-start space-x-4">
                                <div className="h-10 w-10 rounded-full bg-yellow-500/10 flex items-center justify-center">
                                    <AlertTriangle className="h-5 w-5 text-yellow-600" />
                                </div>
                                <div className="flex-1 space-y-1">
                                    <p className="text-sm font-medium">
                                        Architecture drift detected in <span className="text-primary">payment-service</span>
                                    </p>
                                    <p className="text-xs text-muted-foreground">15 minutes ago</p>
                                </div>
                                <Badge variant="warning">Warning</Badge>
                            </div>

                            <div className="flex items-start space-x-4">
                                <div className="h-10 w-10 rounded-full bg-green-500/10 flex items-center justify-center">
                                    <FolderGit2 className="h-5 w-5 text-green-600" />
                                </div>
                                <div className="flex-1 space-y-1">
                                    <p className="text-sm font-medium">
                                        New project <span className="text-primary">api-gateway</span> added
                                    </p>
                                    <p className="text-xs text-muted-foreground">1 hour ago</p>
                                </div>
                                <Badge>New</Badge>
                            </div>

                            <div className="flex items-start space-x-4">
                                <div className="h-10 w-10 rounded-full bg-red-500/10 flex items-center justify-center">
                                    <AlertTriangle className="h-5 w-5 text-red-600" />
                                </div>
                                <div className="flex-1 space-y-1">
                                    <p className="text-sm font-medium">
                                        Critical security issue found in <span className="text-primary">auth-service</span>
                                    </p>
                                    <p className="text-xs text-muted-foreground">3 hours ago</p>
                                </div>
                                <Badge variant="destructive">Critical</Badge>
                            </div>

                            <div className="flex items-start space-x-4">
                                <div className="h-10 w-10 rounded-full bg-blue-500/10 flex items-center justify-center">
                                    <Network className="h-5 w-5 text-blue-600" />
                                </div>
                                <div className="flex-1 space-y-1">
                                    <p className="text-sm font-medium">
                                        Architecture analysis completed for <span className="text-primary">microservices</span>
                                    </p>
                                    <p className="text-xs text-muted-foreground">5 hours ago</p>
                                </div>
                                <Badge variant="info">Info</Badge>
                            </div>
                        </>
                    )}
                </div>
            </CardContent>
        </Card>
    )
}
