import React from 'react';

interface AboutPageProps {
  data?: any;
}

const AboutPage: React.FC<AboutPageProps> = ({ data }) => {
  return (
    <div>
      <h1>About Django React Kit</h1>
      
      <p style={{ fontSize: '18px', lineHeight: '1.6', color: '#333' }}>
        Django React Kit is a powerful integration package that brings modern React 
        development to Django projects with server-side rendering capabilities.
      </p>
      
      <div style={{ marginTop: '40px' }}>
        <h2>Key Benefits</h2>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
          gap: '20px',
          marginTop: '20px'
        }}>
          <div style={{ 
            padding: '20px', 
            backgroundColor: '#fff', 
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ color: '#0066cc' }}>🚀 Performance</h3>
            <p>Server-side rendering for faster initial page loads and better SEO.</p>
          </div>
          
          <div style={{ 
            padding: '20px', 
            backgroundColor: '#fff', 
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ color: '#0066cc' }}>🔧 Developer Experience</h3>
            <p>Hot Module Replacement and modern React development tools.</p>
          </div>
          
          <div style={{ 
            padding: '20px', 
            backgroundColor: '#fff', 
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ color: '#0066cc' }}>🎯 Integration</h3>
            <p>Seamless integration with Django ORM, authentication, and middleware.</p>
          </div>
        </div>
      </div>
      
      {data && data.user && data.user.is_authenticated && (
        <div style={{ 
          marginTop: '40px', 
          padding: '20px', 
          backgroundColor: '#d4edda', 
          borderRadius: '8px',
          border: '1px solid #c3e6cb'
        }}>
          <h3>Welcome back, {data.user.username}! 👋</h3>
          <p>You're viewing this page as an authenticated user.</p>
        </div>
      )}
    </div>
  );
};

export default AboutPage;