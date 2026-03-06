import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { PageHeader } from '@/components/PageHeader';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export function ChangePassword() {
  const { changePassword } = useAuth();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    old_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.new_password !== formData.confirm_password) {
      setError('New passwords do not match');
      return;
    }

    if (formData.new_password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setIsLoading(true);
    try {
      await changePassword(formData.old_password, formData.new_password);
      navigate('/profile');
    } catch (error) {
      console.error('Password change failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <PageHeader title="Change Password" description="Update your account password" />

      <Card className="max-w-md">
        <CardContent className="pt-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="old_password" className="block text-sm font-medium mb-2">
                Current Password
              </label>
              <Input
                id="old_password"
                name="old_password"
                type="password"
                value={formData.old_password}
                onChange={handleChange}
                required
              />
            </div>

            <div>
              <label htmlFor="new_password" className="block text-sm font-medium mb-2">
                New Password
              </label>
              <Input
                id="new_password"
                name="new_password"
                type="password"
                value={formData.new_password}
                onChange={handleChange}
                required
              />
            </div>

            <div>
              <label htmlFor="confirm_password" className="block text-sm font-medium mb-2">
                Confirm New Password
              </label>
              <Input
                id="confirm_password"
                name="confirm_password"
                type="password"
                value={formData.confirm_password}
                onChange={handleChange}
                required
              />
            </div>

            {error && (
              <p className="text-sm text-destructive">{error}</p>
            )}

            <div className="flex gap-2">
              <Button type="submit" disabled={isLoading}>
                {isLoading ? 'Changing...' : 'Change Password'}
              </Button>
              <Button type="button" variant="outline" onClick={() => navigate('/profile')}>
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
