import axios from 'axios';
import { Rocket } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

export const hubspotIntegration = {
  name: 'HubSpot',
  icon: Rocket,
  description: 'Connect to HubSpot CRM to access your contacts, companies, and deals.',

  authorize: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/integrations/hubspot/authorize`);
      return response.data.auth_url;
    } catch (error) {
      console.error('HubSpot authorization error:', error);
      throw new Error('Failed to initiate HubSpot authorization');
    }
  },

  getCredentials: async (state) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/integrations/hubspot/credentials/${state}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get HubSpot credentials:', error);
      throw new Error('Failed to retrieve HubSpot credentials');
    }
  },

  getItems: async (credentials) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/integrations/hubspot/items`, credentials);
      console.log('HubSpot Items:', response.data.items);
      return response.data.items;
    } catch (error) {
      console.error('Failed to fetch HubSpot items:', error);
      throw new Error('Failed to fetch items from HubSpot');
    }
  }
};