import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './app/layout';

// Client-side hydration
const container = document.getElementById('root');
if (container) {
  const root = createRoot(container);
  
  // Get initial data from server
  const initialData = (window as any).__INITIAL_DATA__ || {};
  const initialPath = (window as any).__INITIAL_PATH__ || '/';
  
  root.render(
    <BrowserRouter>
      <App initialData={initialData} />
    </BrowserRouter>
  );
}