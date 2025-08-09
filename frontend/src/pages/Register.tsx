import React from 'react';
import { useNavigate } from 'react-router-dom';

const Register: React.FC = () => {
  const navigate = useNavigate();

  // For demo purposes, redirect to login
  React.useEffect(() => {
    navigate('/login');
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
            Register
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Redirecting to login...
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
