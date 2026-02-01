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
                setResult(`✅ CORS测试成功！\n响应: ${JSON.stringify(data, null, 2)}`);
            } else {
                setResult(`❌ HTTP错误: ${response.status} ${response.statusText}`);
            }
        } catch (error: any) {
            setResult(`❌ CORS错误: ${error.message}`);
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
                setResult(`✅ Health检查成功！\n响应: ${JSON.stringify(data, null, 2)}`);
            } else {
                setResult(`❌ HTTP错误: ${response.status} ${response.statusText}`);
            }
        } catch (error: any) {
            setResult(`❌ 请求错误: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container mx-auto p-6">
            <Card>
                <CardHeader>
                    <CardTitle>CORS 测试页面</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="flex space-x-4">
                        <Button 
                            onClick={testCors} 
                            disabled={loading}
                            variant="default"
                        >
                            {loading ? '测试中...' : '测试根路径 (/)'}
                        </Button>
                        
                        <Button 
                            onClick={testHealthEndpoint} 
                            disabled={loading}
                            variant="outline"
                        >
                            {loading ? '测试中...' : '测试健康检查 (/health)'}
                        </Button>
                    </div>
                    
                    {result && (
                        <div className="mt-4">
                            <h3 className="text-lg font-semibold mb-2">测试结果:</h3>
                            <pre className="bg-gray-100 p-4 rounded-lg text-sm whitespace-pre-wrap">
                                {result}
                            </pre>
                        </div>
                    )}
                    
                    <div className="mt-6 text-sm text-gray-600">
                        <h4 className="font-semibold">说明:</h4>
                        <ul className="list-disc list-inside mt-2 space-y-1">
                            <li>这个页面测试前端是否能够成功访问后端API</li>
                            <li>如果看到CORS错误，说明跨域配置有问题</li>
                            <li>确保后端服务器在 http://localhost:8000 上运行</li>
                        </ul>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}