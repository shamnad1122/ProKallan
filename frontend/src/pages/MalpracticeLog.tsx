import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { PageHeader } from '@/components/PageHeader';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { Eye, Check, X } from 'lucide-react';
import type { MalpracticeLog as MalpracticeLogType } from '@/types';

export function MalpracticeLog() {
  const { isAdmin } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  const [filters, setFilters] = useState({
    date: '',
    time: '',
    malpractice_type: '',
    building: '',
    q: '',
    faculty: '',
    assigned: '',
    review: 'not_reviewed',
  });
  
  const [selectedMedia, setSelectedMedia] = useState<string | null>(null);

  const { data: logsData, isLoading } = useQuery({
    queryKey: ['malpractice-logs', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      const response = await api.get(`/api/malpractice-logs/?${params}`);
      return response.data;
    },
  });

  const logs = logsData?.logs || [];

  const { data: hallsData } = useQuery({
    queryKey: ['lecture-halls-for-filters'],
    queryFn: async () => {
      const response = await api.get('/api/lecture-halls/');
      return response.data;
    },
  });

  const { data: teachersData } = useQuery({
    queryKey: ['teachers-for-filters'],
    queryFn: async () => {
      const response = await api.get('/api/teachers/');
      return response.data;
    },
    enabled: isAdmin,
  });

  const metadata = {
    buildings: hallsData?.buildings || [],
    faculty_list: teachersData?.teachers || [],
  };

  const reviewMutation = useMutation({
    mutationFn: async ({ id, decision }: { id: number; decision: 'yes' | 'no' }) => {
      const response = await api.post('/api/malpractice-logs/review/', { id, decision });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['malpractice-logs'] });
      toast({
        title: 'Success',
        description: 'Malpractice reviewed successfully',
      });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to review malpractice',
        variant: 'destructive',
      });
    },
  });

  const handleReview = (id: number, decision: 'yes' | 'no') => {
    reviewMutation.mutate({ id, decision });
  };

  const handleFilterChange = (key: string, value: string) => {
    setFilters({ ...filters, [key]: value });
  };

  return (
    <div>
      <PageHeader
        title="Malpractice Log"
        description="View and manage detected malpractice incidents"
      />

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Input
              placeholder="Search hall name..."
              value={filters.q}
              onChange={(e) => handleFilterChange('q', e.target.value)}
            />
            <Input
              type="date"
              value={filters.date}
              onChange={(e) => handleFilterChange('date', e.target.value)}
            />
            <select
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
              value={filters.time}
              onChange={(e) => handleFilterChange('time', e.target.value)}
            >
              <option value="">All Times</option>
              <option value="FN">Forenoon</option>
              <option value="AN">Afternoon</option>
            </select>
            <select
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
              value={filters.building}
              onChange={(e) => handleFilterChange('building', e.target.value)}
            >
              <option value="">All Buildings</option>
              {metadata?.buildings.map((building: string) => (
                <option key={building} value={building}>
                  {building}
                </option>
              ))}
            </select>
            {isAdmin && (
              <select
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                value={filters.review}
                onChange={(e) => handleFilterChange('review', e.target.value)}
              >
                <option value="not_reviewed">Not Reviewed</option>
                <option value="reviewed">Reviewed</option>
              </select>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Logs Table */}
      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="text-center py-8">Loading...</div>
          ) : logs.length === 0 ? (
            <div className="text-center py-8 text-gray-500">No malpractice logs found</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-3">Date</th>
                    <th className="text-left p-3">Time</th>
                    <th className="text-left p-3">Type</th>
                    <th className="text-left p-3">Hall</th>
                    <th className="text-left p-3">Building</th>
                    <th className="text-left p-3">Status</th>
                    <th className="text-left p-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log: MalpracticeLogType) => (
                    <tr key={log.id} className="border-b hover:bg-gray-50">
                      <td className="p-3">{log.date}</td>
                      <td className="p-3">{log.time}</td>
                      <td className="p-3">
                        <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded">
                          {log.malpractice}
                        </span>
                      </td>
                      <td className="p-3">{log.lecture_hall?.hall_name || 'N/A'}</td>
                      <td className="p-3">{log.lecture_hall?.building || 'N/A'}</td>
                      <td className="p-3">
                        {log.verified ? (
                          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                            Reviewed
                          </span>
                        ) : (
                          <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded">
                            Pending
                          </span>
                        )}
                      </td>
                      <td className="p-3">
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setSelectedMedia(log.proof)}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          {isAdmin && !log.verified && (
                            <>
                              <Button
                                size="sm"
                                variant="default"
                                onClick={() => handleReview(log.id, 'yes')}
                              >
                                <Check className="w-4 h-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="destructive"
                                onClick={() => handleReview(log.id, 'no')}
                              >
                                <X className="w-4 h-4" />
                              </Button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Media Modal */}
      {selectedMedia && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onClick={() => setSelectedMedia(null)}
        >
          <div className="bg-white p-4 rounded-lg max-w-4xl max-h-[90vh] overflow-auto">
            <video src={selectedMedia} controls className="w-full" />
            <Button className="mt-4" onClick={() => setSelectedMedia(null)}>
              Close
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
