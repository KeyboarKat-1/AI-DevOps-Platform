import React from 'react';

export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  className = '',
  ...props
}) => {
  const baseStyles = 'font-semibold rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed';
  const variantStyles = {
    primary: 'bg-primary-600 hover:bg-primary-700 text-white',
    secondary: 'bg-dark-700 hover:bg-dark-600 text-white border border-white/10',
    ghost: 'hover:bg-dark-700 text-white',
    danger: 'bg-red-600 hover:bg-red-700 text-white',
  };
  const sizeStyles = {
    sm: 'py-1 px-3 text-sm',
    md: 'py-2 px-4 text-base',
    lg: 'py-3 px-6 text-lg',
  };

  return (
    <button
      className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};

export const Input = ({
  label,
  error,
  className = '',
  type = 'text',
  ...props
}) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-white mb-2">
          {label}
        </label>
      )}
      <input
        type={type}
        className={`input-field ${error ? 'border-red-500' : ''} ${className}`}
        {...props}
      />
      {error && <p className="text-red-400 text-sm mt-1">{error}</p>}
    </div>
  );
};

export const Card = ({
  children,
  className = '',
  hoverable = true,
  ...props
}) => {
  return (
    <div
      className={`glass-card ${hoverable ? 'hover:shadow-glow' : ''} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export const Badge = ({ children, variant = 'info', className = '' }) => {
  const variantMap = {
    success: 'badge-success',
    warning: 'badge-warning',
    error: 'badge-error',
    info: 'badge-info',
  };

  return (
    <span className={`${variantMap[variant]} ${className}`}>
      {children}
    </span>
  );
};

export const LoadingSpinner = ({ size = 'md', className = '' }) => {
  const sizeClass = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  }[size];

  return (
    <div className={`${sizeClass} border-4 border-dark-700 border-t-primary-500 rounded-full animate-spin ${className}`} />
  );
};

export const Tooltip = ({ text, children, position = 'top' }) => {
  return (
    <div className="relative group inline-block">
      {children}
      <div
        className={`absolute hidden group-hover:block bg-dark-800 text-white text-xs px-3 py-2 rounded-lg whitespace-nowrap z-10 ${
          position === 'top' ? 'bottom-full mb-2' : 'top-full mt-2'
        }`}
      >
        {text}
      </div>
    </div>
  );
};

export const Modal = ({ isOpen, onClose, title, children, actions }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      <div className="glass-card relative z-10 w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-white">{title}</h2>
          <button
            onClick={onClose}
            className="text-dark-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>
        <div className="mb-6">{children}</div>
        <div className="flex gap-3 justify-end">
          {actions && actions.map((action, idx) => (
            <Button
              key={idx}
              variant={action.variant || 'secondary'}
              onClick={action.onClick}
            >
              {action.label}
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
};

export const Alert = ({ type = 'info', title, message, onClose }) => {
  const typeStyles = {
    success: 'bg-green-900/20 border-green-700/30 text-green-400',
    warning: 'bg-yellow-900/20 border-yellow-700/30 text-yellow-400',
    error: 'bg-red-900/20 border-red-700/30 text-red-400',
    info: 'bg-blue-900/20 border-blue-700/30 text-blue-400',
  };

  return (
    <div
      className={`glass-card border ${typeStyles[type]} p-4 flex items-start gap-3`}
    >
      <div className="flex-1">
        {title && <h3 className="font-semibold mb-1">{title}</h3>}
        <p className="text-sm">{message}</p>
      </div>
      {onClose && (
        <button onClick={onClose} className="text-current hover:opacity-70">
          ✕
        </button>
      )}
    </div>
  );
};

export const Pagination = ({ currentPage, totalPages, onPageChange }) => {
  const pages = [];
  for (let i = Math.max(1, currentPage - 1); i <= Math.min(totalPages, currentPage + 1); i++) {
    pages.push(i);
  }

  return (
    <div className="flex items-center gap-2 justify-center mt-6">
      <Button
        variant="secondary"
        size="sm"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
      >
        Previous
      </Button>
      {currentPage > 2 && (
        <>
          <Button variant="ghost" size="sm" onClick={() => onPageChange(1)}>
            1
          </Button>
          {currentPage > 3 && <span className="text-dark-400">...</span>}
        </>
      )}
      {pages.map((page) => (
        <Button
          key={page}
          variant={page === currentPage ? 'primary' : 'ghost'}
          size="sm"
          onClick={() => onPageChange(page)}
        >
          {page}
        </Button>
      ))}
      {currentPage < totalPages - 1 && (
        <>
          {currentPage < totalPages - 2 && <span className="text-dark-400">...</span>}
          <Button variant="ghost" size="sm" onClick={() => onPageChange(totalPages)}>
            {totalPages}
          </Button>
        </>
      )}
      <Button
        variant="secondary"
        size="sm"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
      >
        Next
      </Button>
    </div>
  );
};
