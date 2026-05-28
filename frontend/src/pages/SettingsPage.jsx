import React, { useState, useEffect } from 'react';
import { Settings, User, Bell, Shield, Palette } from 'lucide-react';
import { Card, Button, Input } from '../components';
import { useAuth } from '../context/AuthContext';

export const SettingsPage = () => {
  const [activeTab, setActiveTab] = useState('profile');
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
  });
  const [settings, setSettings] = useState({
    emailNotifications: true,
    pushNotifications: true,
    slackIntegration: false,
    darkMode: true,
  });
  const [saving, setSaving] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [statusType, setStatusType] = useState('');
  const { user, updateProfile } = useAuth();

  useEffect(() => {
    if (user) {
      setFormData((prev) => ({
        ...prev,
        name: user.name || user.username || '',
        email: user.email || '',
      }));
    }
  }, [user]);

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSettingToggle = (key) => {
    setSettings((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSave = async () => {
    setStatusMessage('');
    setStatusType('');
    setSaving(true);
    const payload = {
      username: formData.name,
      email: formData.email,
    };
    const result = await updateProfile(payload);
    if (result.success) {
      setStatusType('success');
      setStatusMessage('Profile updated successfully.');
    } else {
      setStatusType('error');
      setStatusMessage(result.message || 'Failed to update profile.');
    }
    setSaving(false);
  };

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'appearance', label: 'Appearance', icon: Palette },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Settings</h1>
        <p className="text-dark-400 mt-1">Manage your account and preferences</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-white/10 overflow-x-auto">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-3 border-b-2 whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-400'
                  : 'border-transparent text-dark-400 hover:text-white'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold text-white mb-6">Profile Settings</h2>
          <div className="space-y-4">
            <Input
              label="Full Name"
              name="name"
              value={formData.name}
              onChange={handleFormChange}
            />
            <Input
              label="Email Address"
              type="email"
              name="email"
              value={formData.email}
              onChange={handleFormChange}
            />
            <Input
              label="Phone Number"
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleFormChange}
            />
                  {statusMessage && (
                    <div className={`p-3 rounded-lg ${statusType === 'success' ? 'bg-green-900/30 text-green-300' : 'bg-red-900/30 text-red-300'}`}>
                      {statusMessage}
                    </div>
                  )}
            <div className="pt-4">
              <Button variant="primary" onClick={handleSave} disabled={saving}>
                {saving ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Notifications Tab */}
      {activeTab === 'notifications' && (
        <div className="space-y-4">
          <Card className="p-6">
            <h2 className="text-xl font-semibold text-white mb-6">Notification Preferences</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-dark-700/30 rounded-lg">
                <div>
                  <p className="font-medium text-white">Email Notifications</p>
                  <p className="text-sm text-dark-400">Receive alerts via email</p>
                </div>
                <button
                  onClick={() => handleSettingToggle('emailNotifications')}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    settings.emailNotifications ? 'bg-primary-600' : 'bg-dark-600'
                  }`}
                >
                  <div
                    className={`w-5 h-5 bg-white rounded-full transition-transform ${
                      settings.emailNotifications ? 'translate-x-6' : 'translate-x-0.5'
                    }`}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-dark-700/30 rounded-lg">
                <div>
                  <p className="font-medium text-white">Push Notifications</p>
                  <p className="text-sm text-dark-400">Send desktop notifications</p>
                </div>
                <button
                  onClick={() => handleSettingToggle('pushNotifications')}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    settings.pushNotifications ? 'bg-primary-600' : 'bg-dark-600'
                  }`}
                >
                  <div
                    className={`w-5 h-5 bg-white rounded-full transition-transform ${
                      settings.pushNotifications ? 'translate-x-6' : 'translate-x-0.5'
                    }`}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-dark-700/30 rounded-lg">
                <div>
                  <p className="font-medium text-white">Slack Integration</p>
                  <p className="text-sm text-dark-400">Send alerts to Slack</p>
                </div>
                <button
                  onClick={() => handleSettingToggle('slackIntegration')}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    settings.slackIntegration ? 'bg-primary-600' : 'bg-dark-600'
                  }`}
                >
                  <div
                    className={`w-5 h-5 bg-white rounded-full transition-transform ${
                      settings.slackIntegration ? 'translate-x-6' : 'translate-x-0.5'
                    }`}
                  />
                </button>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Security Tab */}
      {activeTab === 'security' && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold text-white mb-6">Security Settings</h2>
          <div className="space-y-4">
            <Button variant="secondary" className="w-full">
              Change Password
            </Button>
            <Button variant="secondary" className="w-full">
              Enable Two-Factor Authentication
            </Button>
            <Button variant="secondary" className="w-full">
              View Active Sessions
            </Button>
            <Button variant="danger" className="w-full">
              Logout All Other Sessions
            </Button>
          </div>
        </Card>
      )}

      {/* Appearance Tab */}
      {activeTab === 'appearance' && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold text-white mb-6">Appearance</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-dark-700/30 rounded-lg">
              <div>
                <p className="font-medium text-white">Dark Mode</p>
                <p className="text-sm text-dark-400">Use dark theme</p>
              </div>
              <button
                onClick={() => handleSettingToggle('darkMode')}
                className={`w-12 h-6 rounded-full transition-colors ${
                  settings.darkMode ? 'bg-primary-600' : 'bg-dark-600'
                }`}
              >
                <div
                  className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    settings.darkMode ? 'translate-x-6' : 'translate-x-0.5'
                  }`}
                />
              </button>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};
