import { useAuth } from '@/contexts/AuthContext';
import { PageHeader } from '@/components/PageHeader';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { FileText, Building, Users, Camera, Shield } from 'lucide-react';
import { Link } from 'react-router-dom';

export function Home() {
  const { user, isAdmin } = useAuth();

  const features = [
    {
      title: 'Malpractice Log',
      description: 'View and manage malpractice detection logs',
      icon: FileText,
      link: '/malpractice-log',
      color: 'text-blue-600',
    },
    ...(isAdmin
      ? [
          {
            title: 'Manage Lecture Halls',
            description: 'Add and assign lecture halls to teachers',
            icon: Building,
            link: '/manage-lecture-halls',
            color: 'text-green-600',
          },
          {
            title: 'View Teachers',
            description: 'View all registered teachers and their assignments',
            icon: Users,
            link: '/view-teachers',
            color: 'text-purple-600',
          },
          {
            title: 'Run Cameras',
            description: 'Start and stop camera monitoring scripts',
            icon: Camera,
            link: '/run-cameras',
            color: 'text-red-600',
          },
        ]
      : []),
  ];

  return (
    <div>
      <PageHeader
        title={`Welcome back, ${user?.first_name || user?.username}!`}
        description="DetectSus - Automated Malpractice Detection System"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature) => (
          <Link key={feature.title} to={feature.link}>
            <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
              <CardHeader>
                <feature.icon className={`w-12 h-12 ${feature.color} mb-4`} />
                <CardTitle>{feature.title}</CardTitle>
                <CardDescription>{feature.description}</CardDescription>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </div>

      <Card className="mt-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="w-6 h-6 text-primary" />
            About DetectSus
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">
            DetectSus is an advanced AI-powered system designed to detect and prevent malpractice
            during examinations. Using computer vision and machine learning, the system monitors
            multiple camera angles to identify suspicious behaviors such as mobile phone usage,
            paper passing, unusual body postures, and other forms of cheating.
          </p>
          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-2xl font-bold text-blue-600">Real-time</p>
              <p className="text-sm text-gray-600">Detection</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-2xl font-bold text-green-600">Multi-angle</p>
              <p className="text-sm text-gray-600">Monitoring</p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <p className="text-2xl font-bold text-purple-600">AI-powered</p>
              <p className="text-sm text-gray-600">Analysis</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
