import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { PageHeader } from '@/components/PageHeader';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import type { User } from '@/types';

export function ViewTeachers() {
  const [filters, setFilters] = useState({
    assigned: '',
    building: '',
  });

  const { data: teachers = [], isLoading } = useQuery({
    queryKey: ['teachers', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      const response = await api.get(`/view_teachers/?${params}`);
      return response.data.teachers || [];
    },
  });

  const { data: metadata } = useQuery({
    queryKey: ['teachers-metadata'],
    queryFn: async () => {
      const response = await api.get('/view_teachers/');
      return {
        buildings: response.data.buildings || [],
      };
    },
  });

  return (
    <div>
      <PageHeader
        title="View Teachers"
        description="View all registered teachers and their assignments"
      />

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <select
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
              value={filters.assigned}
              onChange={(e) => setFilters({ ...filters, assigned: e.target.value })}
            >
              <option value="">All Teachers</option>
              <option value="assigned">Assigned</option>
              <option value="unassigned">Unassigned</option>
            </select>
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
          </div>
        </CardContent>
      </Card>

      {/* Teachers Table */}
      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="text-center py-8">Loading...</div>
          ) : teachers.length === 0 ? (
            <div className="text-center py-8 text-gray-500">No teachers found</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-3">Name</th>
                    <th className="text-left p-3">Username</th>
                    <th className="text-left p-3">Email</th>
                    <th className="text-left p-3">Assigned Hall</th>
                    <th className="text-left p-3">Building</th>
                  </tr>
                </thead>
                <tbody>
                  {teachers.map((teacher: any) => (
                    <tr key={teacher.id} className="border-b hover:bg-gray-50">
                      <td className="p-3">
                        {teacher.first_name} {teacher.last_name}
                      </td>
                      <td className="p-3">{teacher.username}</td>
                      <td className="p-3">{teacher.email}</td>
                      <td className="p-3">
                        {teacher.lecturehall ? (
                          <span className="text-sm">{teacher.lecturehall.hall_name}</span>
                        ) : (
                          <span className="text-sm text-gray-500">Not assigned</span>
                        )}
                      </td>
                      <td className="p-3">
                        {teacher.lecturehall ? (
                          <span className="text-sm">{teacher.lecturehall.building}</span>
                        ) : (
                          <span className="text-sm text-gray-500">-</span>
                        )}
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
