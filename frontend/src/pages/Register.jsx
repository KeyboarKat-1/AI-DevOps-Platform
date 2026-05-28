import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Eye, EyeOff } from 'lucide-react';
import { Button, Input, Alert, LoadingSpinner } from '../components';
import { authService } from '../services/authService';

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const validateForm = () => {
    if (!formData.fullName.trim()) {
      return 'Full name is required.';
    }
    if (!formData.email.trim()) {
      return 'Email address is required.';
    }
    if (!emailPattern.test(formData.email.trim())) {
      return 'Please enter a valid email address.';
    }
    if (!formData.password) {
      return 'Password is required.';
    }
    if (formData.password.length < 8) {
      return 'Password must be at least 8 characters long.';
    }
    if (formData.password !== formData.confirmPassword) {
      return 'Passwords do not match.';
    }
    return null;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSuccess('');

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);

    try {
      await authService.register(formData.fullName, formData.email, formData.password);
      setSuccess('Account created successfully. Redirecting to login...');
      setTimeout(() => navigate('/login'), 1400);
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        err.message ||
        'Registration failed. Please try again.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-dark-950 flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-lg">
        <div className="text-center mb-10 animate-fade-in">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-3xl bg-gradient-to-br from-primary-500 to-sky-500 shadow-glow mb-4">
            <span className="text-3xl font-bold text-white">AI</span>
          </div>
          <h1 className="text-4xl font-bold text-white tracking-tight">Create your account</h1>
          <p className="mt-3 text-sm text-dark-400 sm:text-base">
            Securely sign up to access your AI DevOps dashboard and start monitoring your infrastructure.
          </p>
        </div>

        <div className="glass-card border border-white/10 p-8 shadow-glow animate-slide-up">
          {error && <Alert type="error" message={error} onClose={() => setError('')} />}
          {success && <Alert type="success" message={success} />}

          <form onSubmit={handleSubmit} className="space-y-5 mt-6">
            <div className="relative">
              <User className="absolute left-3 top-3 w-5 h-5 text-dark-400" />
              <Input
                type="text"
                name="fullName"
                placeholder="Full Name"
                value={formData.fullName}
                onChange={handleChange}
                className="pl-10"
                required
              />
            </div>

            <div className="relative">
              <Mail className="absolute left-3 top-3 w-5 h-5 text-dark-400" />
              <Input
                type="email"
                name="email"
                placeholder="Email Address"
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
                  onClick={() => setShowPassword((current) => !current)}
                  className="absolute right-3 top-2.5 text-dark-400 hover:text-white"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <div className="relative">
              <Lock className="absolute left-3 top-3 w-5 h-5 text-dark-400" />
              <Input
                type="password"
                name="confirmPassword"
                placeholder="Confirm Password"
                value={formData.confirmPassword}
                onChange={handleChange}
                className="pl-10"
                required
              />
            </div>

            <Button
              type="submit"
              variant="primary"
              className="w-full mt-4 py-3 flex items-center justify-center gap-3"
              disabled={loading}
            >
              {loading ? (
                <>
                  <LoadingSpinner size="sm" className="mr-2" />
                  Creating account...
                </>
              ) : (
                'Sign Up'
              )}
            </Button>
          </form>

          <div className="mt-7 border-t border-white/10 pt-5 text-center text-sm text-dark-400">
            Already have an account?{' '}
            <Link to="/login" className="text-primary-400 hover:text-primary-300 font-semibold">
              Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
