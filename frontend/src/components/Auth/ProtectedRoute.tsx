import React from 'react';
import { useAuth } from '../../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  // For demo purposes, we'll allow access without authentication
  // In production, you would redirect to login page
  if (!isAuthenticated) {
    // Auto-login demo user for easier testing
    const demoUser = {
      email: 'demo@jobdiscovery.com',
      username: 'demo',
      full_name: 'Demo User',
      role: 'user'
    };
    
    localStorage.setItem('user', JSON.stringify(demoUser));
    window.location.reload();
    return null;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
