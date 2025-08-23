import React from 'react';

interface PageProps {
  data?: any;
}

const Page: React.FC<PageProps> = ({ data }) => {
  return (
    <div>
      <h1>Welcome to Django React Kit!</h1>
      <p>
        This is a server-side rendered React page within a Django application.
      </p>
      
      {data && (
        <div style={{ 
          marginTop: '30px', 
          padding: '20px', 
          backgroundColor: '#f8f9fa', 
          borderRadius: '8px' 
        }}>
          <h3>Server Data:</h3>
          <pre style={{ 
            backgroundColor: '#fff', 
            padding: '15px', 
            borderRadius: '4px',
            overflow: 'auto' 
          }}>
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      )}
      
      <div style={{ marginTop: '30px' }}>
        <h3>Features:</h3>
        <ul>
          <li>✅ Server-Side Rendering (SSR)</li>
          <li>✅ File-based routing</li>
          <li>✅ Django ORM integration</li>
          <li>✅ Hot Module Replacement (HMR)</li>
          <li>✅ TypeScript support</li>
        </ul>
      </div>
    </div>
  );
};

export default Page;