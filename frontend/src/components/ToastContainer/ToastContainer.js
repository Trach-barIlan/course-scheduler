import React from 'react';
import ToastNotification from '../ToastNotification/ToastNotification';

const ToastContainer = ({ toasts, onRemoveToast, position = 'top-right' }) => {
  if (!toasts || toasts.length === 0) {
    return null;
  }

  return (
    <div className={`toast-container ${position}`}>
      {toasts.map((toast) => (
        <ToastNotification
          key={toast.id}
          {...toast}
          onClose={onRemoveToast}
        />
      ))}
    </div>
  );
};

export default ToastContainer;