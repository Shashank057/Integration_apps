import axios from 'axios';
import { FileText } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

export const notionIntegration = {
  name: 'Notion',
  icon: FileText,
  description: 'Access your Notion pages and databases to retrieve and organize your content.',

  authorize: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/integrations/notion/authorize`);
      return response.data.auth_url;
    } catch (error) {
      console.error('Notion authorization error:', error);
      throw new Error('Failed to initiate Notion authorization');
    }
  },

  getCredentials: async (state) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/integrations/notion/credentials/${state}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get Notion credentials:', error);
      throw new Error('Failed to retrieve Notion credentials');
    }
  },

  getItems: async (credentials) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/integrations/notion/items`, credentials);
      console.log('Notion Items:', response.data.items);
      return response.data.items;
    } catch (error) {
      console.error('Failed to fetch Notion items:', error);
      throw new Error('Failed to fetch items from Notion');
    }
  }
};