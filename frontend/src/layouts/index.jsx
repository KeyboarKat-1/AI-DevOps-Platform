import React, { useState } from 'react';
import { Sidebar, Navbar } from '../components/navigation';
import { AIAssistant } from '../components/specialized';

export const MainLayout = ({ children, user, onLogout }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen bg-dark-950">
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onLogout={onLogout}
      />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Navbar
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          user={user}
        />

        <main className="flex-1 overflow-y-auto">
          <div className="p-6">{children}</div>
        </main>
      </div>

      <AIAssistant />
    </div>
  );
};

export const AuthLayout = ({ children }) => {
  return (
    <div className="min-h-screen bg-dark-950">
      {children}
    </div>
  );
};
