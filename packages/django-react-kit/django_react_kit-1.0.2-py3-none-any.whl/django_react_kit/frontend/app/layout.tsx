import React from 'react';

interface LayoutProps {
  children?: React.ReactNode;
  initialData?: any;
}

const Layout: React.FC<LayoutProps> = ({ children, initialData }) => {
  return (
    <html lang="en">
      <head>
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Django React Kit</title>
      </head>
      <body>
        <div className="container">
          <nav style={{ padding: '20px 0', borderBottom: '1px solid #eee' }}>
            <a href="/" style={{ marginRight: '20px', textDecoration: 'none', color: '#0066cc' }}>
              Home
            </a>
            <a href="/about" style={{ marginRight: '20px', textDecoration: 'none', color: '#0066cc' }}>
              About
            </a>
          </nav>
          <main style={{ padding: '40px 0' }}>
            {children}
          </main>
          <footer style={{ padding: '20px 0', borderTop: '1px solid #eee', color: '#666' }}>
            <p>Powered by Django React Kit</p>
          </footer>
        </div>
      </body>
    </html>
  );
};

export default Layout;