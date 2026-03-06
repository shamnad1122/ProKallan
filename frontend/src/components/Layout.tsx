import { Link, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { LogOut, User, Home, FileText, Building, Users, Camera } from 'lucide-react';

export function Layout() {
  const { user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-8">
              <Link to="/" className="flex items-center space-x-2">
                <span className="text-xl font-bold text-primary">DetectSus</span>
              </Link>
              
              {user && (
                <div className="hidden md:flex space-x-4">
                  <Link to="/">
                    <Button variant="ghost" size="sm">
                      <Home className="w-4 h-4 mr-2" />
                      Home
                    </Button>
                  </Link>
                  <Link to="/malpractice-log">
                    <Button variant="ghost" size="sm">
                      <FileText className="w-4 h-4 mr-2" />
                      Malpractice Log
                    </Button>
                  </Link>
                  {isAdmin && (
                    <>
                      <Link to="/manage-lecture-halls">
                        <Button variant="ghost" size="sm">
                          <Building className="w-4 h-4 mr-2" />
                          Lecture Halls
                        </Button>
                      </Link>
                      <Link to="/view-teachers">
                        <Button variant="ghost" size="sm">
                          <Users className="w-4 h-4 mr-2" />
                          Teachers
                        </Button>
                      </Link>
                      <Link to="/run-cameras">
                        <Button variant="ghost" size="sm">
                          <Camera className="w-4 h-4 mr-2" />
                          Run Cameras
                        </Button>
                      </Link>
                    </>
                  )}
                </div>
              )}
            </div>

            <div className="flex items-center space-x-4">
              {user ? (
                <>
                  <Link to="/profile">
                    <Button variant="ghost" size="sm">
                      <User className="w-4 h-4 mr-2" />
                      {user.first_name || user.username}
                    </Button>
                  </Link>
                  <Button variant="ghost" size="sm" onClick={handleLogout}>
                    <LogOut className="w-4 h-4 mr-2" />
                    Logout
                  </Button>
                </>
              ) : (
                <>
                  <Link to="/login">
                    <Button variant="ghost" size="sm">Login</Button>
                  </Link>
                  <Link to="/register">
                    <Button size="sm">Register</Button>
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
}
