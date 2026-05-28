import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff } from 'lucide-react';
import { Button, Input, Alert, LoadingSpinner } from '../components';
import { authService } from '../services/authService';

export const LoginPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const response = await authService.login(formData.email, formData.password);
      localStorage.setItem('access_token', response.data.access_token);
      setSuccess('Login successful!');
      setTimeout(() => navigate('/dashboard'), 1500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-dark-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-primary-600 to-primary-400 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-glow">
            <span className="text-3xl font-bold">D</span>
          </div>
          <h1 className="text-3xl font-bold text-white">DevOps Dashboard</h1>
          <p className="text-dark-400 mt-2">AI-Powered Platform Management</p>
        </div>

        {/* Form Card */}
        <div className="glass-card p-8 rounded-2xl">
          {error && <Alert type="error" message={error} onClose={() => setError('')} />}
          {success && <Alert type="success" message={success} />}

          <form onSubmit={handleSubmit} className="space-y-5 mt-6">
            <div className="relative">
              <Mail className="absolute left-3 top-3 w-5 h-5 text-dark-400" />
              <Input
                type="email"
                name="email"
                placeholder="Email address"
                value={formData.email}
                onChange={handleChange}
                className="pl-10"
                required
              />
            </div>

            <div className="relative">
              <Lock className="absolute left-3 top-3 w-5 h-5 text-dark-400" />
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  placeholder="Password"
                  value={formData.password}
                  onChange={handleChange}
                  className="input-field pl-10 pr-10"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-2.5 text-dark-400 hover:text-white"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              className="w-full mt-6 flex items-center justify-center"
              disabled={loading}
            >
              {loading ? (
                <>
                  <LoadingSpinner size="sm" className="mr-2" />
                  Logging in...
                </>
              ) : (
                'Sign In'
              )}
            </Button>
          </form>

          {/* Demo Credentials */}
          {/* Footer */}
          <p className="text-center text-sm text-dark-400 mt-6">
            Don't have an account?{' '}
            <Link to="/register" className="text-primary-400 hover:text-primary-300 font-semibold">
              Sign up
            </Link>
          </p>
        </div>

        {/* Features */}
        <div className="mt-12 grid grid-cols-3 gap-4 text-center">
          {[
            { icon: '🚀', label: 'Real-time Monitoring' },
            { icon: '🤖', label: 'AI Powered' },
            { icon: '🔒', label: 'Secure' },
          ].map((feature, idx) => (
            <div key={idx}>
              <div className="text-2xl mb-2">{feature.icon}</div>
              <p className="text-xs text-dark-400">{feature.label}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
