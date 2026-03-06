import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/contexts/AuthContext';
import { Toaster } from '@/components/ui/toaster';
import { Layout } from '@/components/Layout';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { Login } from '@/pages/Login';
import { Register } from '@/pages/Register';
import { Home } from '@/pages/Home';
import { Profile } from '@/pages/Profile';
import { EditProfile } from '@/pages/EditProfile';
import { ChangePassword } from '@/pages/ChangePassword';
import { MalpracticeLog } from '@/pages/MalpracticeLog';
import { ManageLectureHalls } from '@/pages/ManageLectureHalls';
import { ViewTeachers } from '@/pages/ViewTeachers';
import { RunCameras } from '@/pages/RunCameras';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route element={<Layout />}>
              {/* Public routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              
              {/* Protected routes */}
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <Home />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <Profile />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/profile/edit"
                element={
                  <ProtectedRoute>
                    <EditProfile />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/profile/change-password"
                element={
                  <ProtectedRoute>
                    <ChangePassword />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/malpractice-log"
                element={
                  <ProtectedRoute>
                    <MalpracticeLog />
                  </ProtectedRoute>
                }
              />
              
              {/* Admin-only routes */}
              <Route
                path="/manage-lecture-halls"
                element={
                  <ProtectedRoute requireAdmin>
                    <ManageLectureHalls />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/view-teachers"
                element={
                  <ProtectedRoute requireAdmin>
                    <ViewTeachers />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/run-cameras"
                element={
                  <ProtectedRoute requireAdmin>
                    <RunCameras />
                  </ProtectedRoute>
                }
              />
              
              {/* Catch all */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Routes>
          <Toaster />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
