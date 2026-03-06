import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import api from '@/lib/api';
import { PageHeader } from '@/components/PageHeader';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { Camera, Play, Square, AlertCircle } from 'lucide-react';

export function RunCameras() {
  const { toast } = useToast();
  const [isRunning, setIsRunning] = useState(false);

  const startMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post('/api/cameras/start/');
      return response.data;
    },
    onSuccess: () => {
      setIsRunning(true);
      toast({
        title: 'Success',
        description: 'Camera scripts started successfully',
      });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to start camera scripts',
        variant: 'destructive',
      });
    },
  });

  const stopMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post('/api/cameras/stop/');
      return response.data;
    },
    onSuccess: () => {
      setIsRunning(false);
      toast({
        title: 'Success',
        description: 'Camera scripts stopped successfully',
      });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to stop camera scripts',
        variant: 'destructive',
      });
    },
  });

  const handleStart = () => {
    startMutation.mutate();
  };

  const handleStop = () => {
    stopMutation.mutate();
  };

  return (
    <div>
      <PageHeader
        title="Run Cameras"
        description="Start and stop camera monitoring scripts"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Camera className="w-6 h-6 text-primary" />
              Camera Control
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-center p-8 bg-gray-50 rounded-lg">
              <div className="text-center">
                <div
                  className={`w-24 h-24 mx-auto rounded-full flex items-center justify-center ${
                    isRunning ? 'bg-green-100' : 'bg-gray-200'
                  }`}
                >
                  <Camera
                    className={`w-12 h-12 ${isRunning ? 'text-green-600' : 'text-gray-400'}`}
                  />
                </div>
                <p className="mt-4 text-lg font-semibold">
                  {isRunning ? 'Cameras Running' : 'Cameras Stopped'}
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <Button
                className="flex-1"
                onClick={handleStart}
                disabled={isRunning || startMutation.isPending}
              >
                <Play className="w-4 h-4 mr-2" />
                {startMutation.isPending ? 'Starting...' : 'Start Cameras'}
              </Button>
              <Button
                className="flex-1"
                variant="destructive"
                onClick={handleStop}
                disabled={!isRunning || stopMutation.isPending}
              >
                <Square className="w-4 h-4 mr-2" />
                {stopMutation.isPending ? 'Stopping...' : 'Stop Cameras'}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="w-6 h-6 text-yellow-600" />
              Important Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <h4 className="font-semibold">Before Starting:</h4>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                <li>Ensure all camera hardware is properly connected</li>
                <li>Verify network connectivity for remote cameras</li>
                <li>Check that all required scripts are configured</li>
                <li>Ensure sufficient storage space for recordings</li>
              </ul>
            </div>

            <div className="space-y-2">
              <h4 className="font-semibold">Detection Features:</h4>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                <li>Mobile phone detection</li>
                <li>Paper passing detection</li>
                <li>Unusual posture detection (leaning, turning back)</li>
                <li>Hand raising detection</li>
                <li>Multi-angle monitoring</li>
              </ul>
            </div>

            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">
                <strong>Note:</strong> Camera scripts will run in the background. Monitor the
                malpractice log for detected incidents.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
