import axios from 'axios';
import { Table } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

export const airtableIntegration = {
  name: 'Airtable',
  icon: Table,
  description: 'Connect to your Airtable bases and tables to access and manage your data.',

  authorize: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/integrations/airtable/authorize`);
      return response.data.auth_url;
    } catch (error) {
      console.error('Airtable authorization error:', error);
      throw new Error('Failed to initiate Airtable authorization');
    }
  },

  getCredentials: async (state) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/integrations/airtable/credentials/${state}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get Airtable credentials:', error);
      throw new Error('Failed to retrieve Airtable credentials');
    }
  },

  getItems: async (credentials) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/integrations/airtable/items`, credentials);
      console.log('Airtable Items:', response.data.items);
      return response.data.items;
    } catch (error) {
      console.error('Failed to fetch Airtable items:', error);
      throw new Error('Failed to fetch items from Airtable');
    }
  }
};