import axios from 'axios';
import { AccountSnapshot } from './types';

const API_BASE_URL = ''; // Update this with your actual API URL

export const getSnapshots = async (): Promise<AccountSnapshot[]> => {
  const response = await axios.get(`${API_BASE_URL}/snapshots`);
  return response.data;
};
