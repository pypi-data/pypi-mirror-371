#!/usr/bin/env node

/**
 * Server-Side Rendering script for Django React Kit
 * Usage: node ssr.js <url_path> <data_json>
 */

const React = require('react');
const { renderToString } = require('react-dom/server');
const path = require('path');

// Mock React components for SSR
// In a real implementation, these would be loaded from the built components
const Layout = ({ children, initialData }) => {
  return React.createElement('div', { className: 'container' }, [
    React.createElement('nav', { 
      key: 'nav',
      style: { padding: '20px 0', borderBottom: '1px solid #eee' } 
    }, [
      React.createElement('a', { 
        key: 'home',
        href: '/', 
        style: { marginRight: '20px', textDecoration: 'none', color: '#0066cc' } 
      }, 'Home'),
      React.createElement('a', { 
        key: 'about',
        href: '/about', 
        style: { marginRight: '20px', textDecoration: 'none', color: '#0066cc' } 
      }, 'About')
    ]),
    React.createElement('main', { 
      key: 'main',
      style: { padding: '40px 0' } 
    }, children),
    React.createElement('footer', { 
      key: 'footer',
      style: { padding: '20px 0', borderTop: '1px solid #eee', color: '#666' } 
    }, React.createElement('p', {}, 'Powered by Django React Kit'))
  ]);
};

const HomePage = ({ data }) => {
  return React.createElement('div', {}, [
    React.createElement('h1', { key: 'title' }, 'Welcome to Django React Kit!'),
    React.createElement('p', { key: 'desc' }, 
      'This is a server-side rendered React page within a Django application.'
    ),
    data ? React.createElement('div', {
      key: 'data',
      style: { 
        marginTop: '30px', 
        padding: '20px', 
        backgroundColor: '#f8f9fa', 
        borderRadius: '8px' 
      }
    }, [
      React.createElement('h3', { key: 'data-title' }, 'Server Data:'),
      React.createElement('pre', {
        key: 'data-content',
        style: { 
          backgroundColor: '#fff', 
          padding: '15px', 
          borderRadius: '4px',
          overflow: 'auto' 
        }
      }, JSON.stringify(data, null, 2))
    ]) : null,
    React.createElement('div', {
      key: 'features',
      style: { marginTop: '30px' }
    }, [
      React.createElement('h3', { key: 'features-title' }, 'Features:'),
      React.createElement('ul', { key: 'features-list' }, [
        React.createElement('li', { key: 'f1' }, '✅ Server-Side Rendering (SSR)'),
        React.createElement('li', { key: 'f2' }, '✅ File-based routing'),
        React.createElement('li', { key: 'f3' }, '✅ Django ORM integration'),
        React.createElement('li', { key: 'f4' }, '✅ Hot Module Replacement (HMR)'),
        React.createElement('li', { key: 'f5' }, '✅ TypeScript support')
      ])
    ])
  ]);
};

const AboutPage = ({ data }) => {
  const userWelcome = data && data.user && data.user.is_authenticated 
    ? React.createElement('div', {
        style: { 
          marginTop: '40px', 
          padding: '20px', 
          backgroundColor: '#d4edda', 
          borderRadius: '8px',
          border: '1px solid #c3e6cb'
        }
      }, [
        React.createElement('h3', { key: 'welcome-title' }, `Welcome back, ${data.user.username}! 👋`),
        React.createElement('p', { key: 'welcome-text' }, 'You\'re viewing this page as an authenticated user.')
      ])
    : null;

  return React.createElement('div', {}, [
    React.createElement('h1', { key: 'title' }, 'About Django React Kit'),
    React.createElement('p', {
      key: 'description',
      style: { fontSize: '18px', lineHeight: '1.6', color: '#333' }
    }, 'Django React Kit is a powerful integration package that brings modern React development to Django projects with server-side rendering capabilities.'),
    React.createElement('div', { key: 'benefits', style: { marginTop: '40px' } }, [
      React.createElement('h2', { key: 'benefits-title' }, 'Key Benefits'),
      React.createElement('div', {
        key: 'benefits-grid',
        style: { 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
          gap: '20px',
          marginTop: '20px'
        }
      }, [
        React.createElement('div', {
          key: 'benefit-1',
          style: { 
            padding: '20px', 
            backgroundColor: '#fff', 
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }
        }, [
          React.createElement('h3', { key: 'b1-title', style: { color: '#0066cc' } }, '🚀 Performance'),
          React.createElement('p', { key: 'b1-text' }, 'Server-side rendering for faster initial page loads and better SEO.')
        ]),
        React.createElement('div', {
          key: 'benefit-2',
          style: { 
            padding: '20px', 
            backgroundColor: '#fff', 
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }
        }, [
          React.createElement('h3', { key: 'b2-title', style: { color: '#0066cc' } }, '🔧 Developer Experience'),
          React.createElement('p', { key: 'b2-text' }, 'Hot Module Replacement and modern React development tools.')
        ]),
        React.createElement('div', {
          key: 'benefit-3',
          style: { 
            padding: '20px', 
            backgroundColor: '#fff', 
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }
        }, [
          React.createElement('h3', { key: 'b3-title', style: { color: '#0066cc' } }, '🎯 Integration'),
          React.createElement('p', { key: 'b3-text' }, 'Seamless integration with Django ORM, authentication, and middleware.')
        ])
      ])
    ]),
    userWelcome
  ]);
};

// Route mapping
const routes = {
  '/': HomePage,
  '/about': AboutPage,
  '/about/': AboutPage
};

function renderPage(urlPath, data) {
  // Determine which component to render based on the URL path
  let PageComponent = routes[urlPath];
  
  // Default to HomePage if route not found
  if (!PageComponent) {
    PageComponent = HomePage;
  }
  
  // Create the page element with data
  const pageElement = React.createElement(PageComponent, { data });
  
  // Wrap in layout
  const appElement = React.createElement(Layout, { initialData: data }, pageElement);
  
  // Render to string
  return renderToString(appElement);
}

// Main execution
function main() {
  const args = process.argv.slice(2);
  
  if (args.length < 2) {
    console.error('Usage: node ssr.js <url_path> <data_json>');
    process.exit(1);
  }
  
  const urlPath = args[0];
  const dataJson = args[1];
  
  try {
    const data = JSON.parse(dataJson);
    const html = renderPage(urlPath, data);
    console.log(html);
  } catch (error) {
    console.error('SSR Error:', error.message);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = { renderPage };