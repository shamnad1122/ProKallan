import { useAuth } from '@/contexts/AuthContext';
import { PageHeader } from '@/components/PageHeader';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';
import { Edit, Lock, Mail, Phone, User, Building } from 'lucide-react';

export function Profile() {
  const { user, profile } = useAuth();

  if (!user) return null;

  return (
    <div>
      <PageHeader
        title="My Profile"
        description="View and manage your account information"
        action={
          <div className="flex gap-2">
            <Link to="/profile/edit">
              <Button>
                <Edit className="w-4 h-4 mr-2" />
                Edit Profile
              </Button>
            </Link>
            <Link to="/profile/change-password">
              <Button variant="outline">
                <Lock className="w-4 h-4 mr-2" />
                Change Password
              </Button>
            </Link>
          </div>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-1">
          <CardHeader>
            <CardTitle>Profile Picture</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center">
            <img
              src={profile?.profile_picture || '/static/img/default_profile.jpeg'}
              alt="Profile"
              className="w-32 h-32 rounded-full object-cover border-4 border-primary"
            />
            <h3 className="mt-4 text-xl font-semibold">
              {user.first_name} {user.last_name}
            </h3>
            <p className="text-sm text-gray-600">@{user.username}</p>
            {user.is_superuser && (
              <span className="mt-2 px-3 py-1 bg-primary text-white text-xs rounded-full">
                Administrator
              </span>
            )}
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Account Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <User className="w-5 h-5 text-gray-600" />
              <div>
                <p className="text-sm text-gray-600">Full Name</p>
                <p className="font-medium">
                  {user.first_name} {user.last_name}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <Mail className="w-5 h-5 text-gray-600" />
              <div>
                <p className="text-sm text-gray-600">Email</p>
                <p className="font-medium">{user.email}</p>
              </div>
            </div>

            {profile?.phone && (
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <Phone className="w-5 h-5 text-gray-600" />
                <div>
                  <p className="text-sm text-gray-600">Phone</p>
                  <p className="font-medium">{profile.phone}</p>
                </div>
              </div>
            )}

            {profile?.lecture_hall && (
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <Building className="w-5 h-5 text-gray-600" />
                <div>
                  <p className="text-sm text-gray-600">Assigned Lecture Hall</p>
                  <p className="font-medium">
                    {profile.lecture_hall.building} - {profile.lecture_hall.hall_name}
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
