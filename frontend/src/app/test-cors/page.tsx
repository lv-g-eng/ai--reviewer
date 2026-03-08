'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function TestCorsPage() {
    const [result, setResult] = useState<string>('');
    const [loading, setLoading] = useState(false);

    const testCors = async () => {
        setLoading(true);
        setResult('');
        
        try {
            const response = await fetch('http://localhost:8000/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            
            if (response.ok) {
                const data = await response.json();
                setResult(`✅ CORStestSuccess！\nresponse: ${JSON.stringify(data, null, 2)}`);
            } else {
                setResult(`❌ HTTPerror: ${response.status} ${response.statusText}`);
            }
        } catch (error: any) {
            setResult(`❌ CORSerror: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const testHealthEndpoint = async () => {
        setLoading(true);
        setResult('');
        
        try {
            const response = await fetch('http://localhost:8000/health', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            
            if (response.ok) {
                const data = await response.json();
                setResult(`✅ Healthchecksuccess！\nresponse: ${JSON.stringify(data, null, 2)}`);
            } else {
                setResult(`❌ HTTPerror: ${response.status} ${response.statusText}`);
            }
        } catch (error: any) {
            setResult(`❌ requesterror: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container mx-auto p-6">
            <Card>
                <CardHeader>
                    <CardTitle>CORS test页面</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="flex space-x-4">
                        <Button 
                            onClick={testCors} 
                            disabled={loading}
                            variant="default"
                        >
                            {loading ? 'test中...' : 'test根path (/)'}
                        </Button>
                        
                        <Button 
                            onClick={testHealthEndpoint} 
                            disabled={loading}
                            variant="outline"
                        >
                            {loading ? 'test中...' : 'test健康check (/health)'}
                        </Button>
                    </div>
                    
                    {result && (
                        <div className="mt-4">
                            <h3 className="text-lg font-semibold mb-2">testresult:</h3>
                            <pre className="bg-gray-100 p-4 rounded-lg text-sm whitespace-pre-wrap">
                                {result}
                            </pre>
                        </div>
                    )}
                    
                    <div className="mt-6 text-sm text-gray-600">
                        <h4 className="font-semibold">desc:</h4>
                        <ul className="list-disc list-inside mt-2 space-y-1">
                            <li>这item页面test前端是否能够success访问后端API</li>
                            <li>如果看到CORSerror，desc跨域config有问题</li>
                            <li>确保后端service器在 http://localhost:8000 上run</li>
                        </ul>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}