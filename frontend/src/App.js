import React, { useState, useEffect } from 'react';
import './App.css';
import { airtableIntegration } from './integrations/airtable';
import { notionIntegration } from './integrations/notion';
import { hubspotIntegration } from './integrations/hubspot';
import { AlertCircle, X } from 'lucide-react';

function App() {
  const [selectedIntegration, setSelectedIntegration] = useState(null);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [connectingIntegration, setConnectingIntegration] = useState(null);
  const [error, setError] = useState(null);
  const [credentials, setCredentials] = useState(null);

  const integrations = [
    airtableIntegration,
    notionIntegration,
    hubspotIntegration
  ];

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const state = urlParams.get('state');
    const pathname = window.location.pathname;

    if (state && pathname.includes('/success')) {
      const integrationName = pathname.split('/')[2];
      handleOAuthSuccess(integrationName, state);
    } else if (pathname.includes('/error')) {
      const message = urlParams.get('message');
      setError(message || 'Authentication failed');
    }
  }, []);

  const handleOAuthSuccess = async (integrationName, state) => {
    setLoading(true);
    setError(null);

    try {
      const integration = integrations.find(i => i.name.toLowerCase() === integrationName);
      if (!integration) {
        throw new Error('Integration not found');
      }

      const creds = await integration.getCredentials(state);
      setCredentials(creds);
      setSelectedIntegration(integration);

      const fetchedItems = await integration.getItems(creds);
      setItems(fetchedItems);
    } catch (err) {
      setError(err.message || 'Failed to complete authentication');
    } finally {
      setLoading(false);
      window.history.replaceState({}, document.title, '/');
    }
  };

  const handleConnect = async (integration) => {
    setConnectingIntegration(integration.name);
    setError(null);
    setItems([]);
    setCredentials(null);

    try {
      const authUrl = await integration.authorize();
      window.location.href = authUrl;
    } catch (err) {
      setError(err.message || 'Failed to initiate authorization');
      setConnectingIntegration(null);
    }
  };

  const handleFetchItems = async () => {
    if (!selectedIntegration || !credentials) return;

    setLoading(true);
    setError(null);

    try {
      const fetchedItems = await selectedIntegration.getItems(credentials);
      setItems(fetchedItems);
    } catch (err) {
      setError(err.message || 'Failed to fetch items');
    } finally {
      setLoading(false);
    }
  };

  const IntegrationIcon = ({ icon: Icon }) => {
    return <Icon size={48} strokeWidth={1.5} />;
  };

  const IntegrationIconLarge = ({ icon: Icon }) => {
    return <Icon size={32} strokeWidth={1.5} />;
  };

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>VectorShift Integrations</h1>
          <p>Connect your favorite services and manage your data</p>
        </header>

        {error && (
          <div className="error-banner">
            <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertCircle size={20} />
              {error}
            </span>
            <button onClick={() => setError(null)} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
              <X size={20} />
            </button>
          </div>
        )}

        {!selectedIntegration ? (
          <div className="integrations-grid">
            {integrations.map((integration) => (
              <div key={integration.name} className="integration-card">
                <div className="integration-icon">
                  <IntegrationIcon icon={integration.icon} />
                </div>
                <h3>{integration.name}</h3>
                <p>{integration.description}</p>
                <button
                  className="connect-button"
                  onClick={() => handleConnect(integration)}
                  disabled={connectingIntegration !== null}
                >
                  {connectingIntegration === integration.name ? 'Connecting...' : 'Connect'}
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="connected-view">
            <div className="connected-header">
              <div className="connected-info">
                <span className="integration-icon-large">
                  <IntegrationIconLarge icon={selectedIntegration.icon} />
                </span>
                <div>
                  <h2>{selectedIntegration.name}</h2>
                  <span className="status-badge">Connected</span>
                </div>
              </div>
              <button
                className="disconnect-button"
                onClick={() => {
                  setSelectedIntegration(null);
                  setItems([]);
                  setCredentials(null);
                }}
              >
                Disconnect
              </button>
            </div>

            <div className="actions-bar">
              <button
                className="fetch-button"
                onClick={handleFetchItems}
                disabled={loading}
              >
                {loading ? 'Loading...' : 'Fetch Items'}
              </button>
              <span className="items-count">
                {items.length > 0 ? `${items.length} items found` : 'No items yet'}
              </span>
            </div>

            {items.length > 0 && (
              <div className="items-container">
                <h3>Items</h3>
                <div className="items-list">
                  {items.map((item, index) => (
                    <div key={item.id || index} className="item-card">
                      <div className="item-header">
                        <span className="item-type">{item.type}</span>
                        {item.url && (
                          <a
                            href={item.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="item-link"
                          >
                            Open →
                          </a>
                        )}
                      </div>
                      <h4>{item.name || 'Untitled'}</h4>
                      <div className="item-details">
                        <span>ID: {item.id}</span>
                        {item.parent_name && (
                          <span>Parent: {item.parent_name}</span>
                        )}
                        {item.created_time && (
                          <span>Created: {new Date(item.created_time).toLocaleDateString()}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;