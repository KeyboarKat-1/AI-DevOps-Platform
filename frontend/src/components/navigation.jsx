import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Box,
  AlertCircle,
  Zap,
  Settings,
  LogOut,
  Menu,
  X,
  ChevronDown,
  MessageSquare,
} from 'lucide-react';
import { Card } from './common';

export const Sidebar = ({ isOpen, onClose, onLogout }) => {
  const location = useLocation();
  const [expandedItem, setExpandedItem] = useState(null);

  const menuItems = [
    { icon: LayoutDashboard, label: 'Dashboard', href: '/dashboard' },
    { icon: Box, label: 'Docker', href: '/docker' },
    { icon: AlertCircle, label: 'Incidents', href: '/incidents' },
    { icon: Zap, label: 'Deployments', href: '/deployments' },
    { icon: MessageSquare, label: 'AI Assistant', href: '/ai-assistant' },
    { icon: Settings, label: 'Settings', href: '/settings' },
  ];

  const isActive = (href) => location.pathname === href;

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 md:hidden"
          onClick={onClose}
        />
      )}

      <div
        className={`fixed md:static left-0 top-0 h-screen w-64 glass-card rounded-0 md:rounded-xl transition-transform duration-300 z-40 ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        <div className="p-6 border-b border-white/10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-primary-400 rounded-lg flex items-center justify-center">
                <span className="font-bold text-lg">D</span>
              </div>
              <h1 className="text-xl font-bold hidden md:block">DevOps</h1>
            </div>
            <button onClick={onClose} className="md:hidden btn-icon">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <nav className="flex-1 p-4 overflow-y-auto space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);

            return (
              <Link
                key={item.href}
                to={item.href}
                onClick={onClose}
                className={`sidebar-item ${active ? 'active' : ''}`}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                <span className="text-sm font-medium flex-1">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-white/10">
          <button
            onClick={onLogout}
            className="w-full sidebar-item text-red-400 hover:bg-red-900/30"
          >
            <LogOut className="w-5 h-5 flex-shrink-0" />
            <span className="text-sm font-medium">Logout</span>
          </button>
        </div>
      </div>
    </>
  );
};

export const Navbar = ({ onMenuClick, user, onNotificationClick }) => {
  const [showNotifications, setShowNotifications] = useState(false);

  return (
    <Card className="rounded-none md:rounded-xl sticky top-0 z-20 bg-glass-light">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-4">
          <button onClick={onMenuClick} className="md:hidden btn-icon">
            <Menu className="w-6 h-6" />
          </button>
          <div className="hidden md:flex items-center gap-4 text-sm text-dark-400">
            <span>Welcome back, <span className="text-white font-medium">{user?.name || user?.username || 'User'}</span></span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative btn-icon hover:bg-dark-700/50"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            </button>

            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 glass-card p-4">
                <h3 className="font-semibold text-white mb-3">Notifications</h3>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  <div className="text-sm text-dark-400 p-3 rounded-lg bg-dark-700/50">
                    No new notifications
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="h-8 w-px bg-white/10" />

          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-primary-600 to-primary-400 rounded-lg flex items-center justify-center text-sm font-semibold">
              {(user?.name || user?.username || 'U')?.charAt(0) || 'U'}
            </div>
            <div className="hidden sm:block">
              <p className="text-sm font-medium text-white">{user?.name || user?.username || 'User'}</p>
              <p className="text-xs text-dark-400">{user?.email || 'user@example.com'}</p>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};

export const MobileMenu = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-20 bg-black/50 md:hidden" onClick={onClose} />
  );
};
