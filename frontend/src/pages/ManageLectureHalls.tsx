import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import { PageHeader } from '@/components/PageHeader';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { Plus } from 'lucide-react';
import type { LectureHall } from '@/types';

export function ManageLectureHalls() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  const [filters, setFilters] = useState({
    q: '',
    building: '',
    assigned: '',
  });
  
  const [showAddForm, setShowAddForm] = useState(false);
  const [newHall, setNewHall] = useState({ hall_name: '', building: '' });

  const { data: hallsData, isLoading } = useQuery({
    queryKey: ['lecture-halls', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      const response = await api.get(`/api/lecture-halls/?${params}`);
      return response.data;
    },
  });

  const halls = hallsData?.halls || [];

  const { data: teachersData } = useQuery({
    queryKey: ['teachers-for-assignment'],
    queryFn: async () => {
      const response = await api.get('/api/teachers/');
      return response.data;
    },
  });

  const metadata = {
    teachers: teachersData?.teachers || [],
    buildings: hallsData?.buildings || [],
  };

  const addHallMutation = useMutation({
    mutationFn: async (data: { hall_name: string; building: string }) => {
      const response = await api.post('/api/lecture-halls/add/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lecture-halls'] });
      toast({ title: 'Success', description: 'Lecture hall added successfully' });
      setShowAddForm(false);
      setNewHall({ hall_name: '', building: '' });
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.response?.data?.error || 'Failed to add lecture hall',
        variant: 'destructive',
      });
    },
  });

  const mapTeacherMutation = useMutation({
    mutationFn: async ({ hall_id, teacher_id }: { hall_id: number; teacher_id: number }) => {
      const response = await api.post('/api/lecture-halls/assign/', { hall_id, teacher_id });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lecture-halls'] });
      toast({ title: 'Success', description: 'Teacher assigned successfully' });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to assign teacher',
        variant: 'destructive',
      });
    },
  });

  const handleAddHall = (e: React.FormEvent) => {
    e.preventDefault();
    addHallMutation.mutate(newHall);
  };

  const handleMapTeacher = (hallId: number, teacherId: string) => {
    if (teacherId) {
      mapTeacherMutation.mutate({ hall_id: hallId, teacher_id: parseInt(teacherId) });
    }
  };

  return (
    <div>
      <PageHeader
        title="Manage Lecture Halls"
        description="Add lecture halls and assign teachers"
        action={
          <Button onClick={() => setShowAddForm(!showAddForm)}>
            <Plus className="w-4 h-4 mr-2" />
            Add Lecture Hall
          </Button>
        }
      />

      {/* Add Hall Form */}
      {showAddForm && (
        <Card className="mb-6">
          <CardContent className="pt-6">
            <form onSubmit={handleAddHall} className="flex gap-4">
              <Input
                placeholder="Hall Name"
                value={newHall.hall_name}
                onChange={(e) => setNewHall({ ...newHall, hall_name: e.target.value })}
                required
              />
              <Input
                placeholder="Building"
                value={newHall.building}
                onChange={(e) => setNewHall({ ...newHall, building: e.target.value })}
                required
              />
              <Button type="submit">Add</Button>
              <Button type="button" variant="outline" onClick={() => setShowAddForm(false)}>
                Cancel
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              placeholder="Search hall name..."
              value={filters.q}
              onChange={(e) => setFilters({ ...filters, q: e.target.value })}
            />
            <select
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
              value={filters.building}
              onChange={(e) => setFilters({ ...filters, building: e.target.value })}
            >
              <option value="">All Buildings</option>
              {metadata?.buildings.map((building: string) => (
                <option key={building} value={building}>
                  {building}
                </option>
              ))}
            </select>
            <select
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
              value={filters.assigned}
              onChange={(e) => setFilters({ ...filters, assigned: e.target.value })}
            >
              <option value="">All</option>
              <option value="assigned">Assigned</option>
              <option value="unassigned">Unassigned</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Halls Table */}
      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="text-center py-8">Loading...</div>
          ) : halls.length === 0 ? (
            <div className="text-center py-8 text-gray-500">No lecture halls found</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-3">Hall Name</th>
                    <th className="text-left p-3">Building</th>
                    <th className="text-left p-3">Assigned Teacher</th>
                    <th className="text-left p-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {halls.map((hall: LectureHall) => (
                    <tr key={hall.id} className="border-b hover:bg-gray-50">
                      <td className="p-3">{hall.hall_name}</td>
                      <td className="p-3">{hall.building}</td>
                      <td className="p-3">
                        {hall.assigned_teacher ? (
                          <span className="text-sm">
                            {(hall.assigned_teacher as any).full_name || 
                             `${hall.assigned_teacher.first_name} ${hall.assigned_teacher.last_name}`}
                          </span>
                        ) : (
                          <span className="text-sm text-gray-500">Not assigned</span>
                        )}
                      </td>
                      <td className="p-3">
                        <select
                          className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                          onChange={(e) => handleMapTeacher(hall.id, e.target.value)}
                          value={hall.assigned_teacher?.id || ''}
                        >
                          <option value="">Select Teacher</option>
                          {metadata?.teachers.map((teacher: any) => (
                            <option key={teacher.id} value={teacher.id}>
                              {teacher.full_name || `${teacher.first_name} ${teacher.last_name}`}
                            </option>
                          ))}
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
