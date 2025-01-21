import React, { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartData,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { format } from 'date-fns';
import { AccountSnapshot } from '../types';
import { getSnapshots } from '../api';
import { LineChart, BarChart, Edit2, X, Check } from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

type ChartMode = 'individual' | 'comparison';
type DataType = 'equity' | 'cash';

interface AccountSettings {
  nickname: string;
  color: string;
}

interface AccountSettingsMap {
  [key: string]: AccountSettings;
}

const STORAGE_KEY = 'account_settings';

// Colors that work well in both Tailwind and Chart.js
const CHART_COLORS = [
  { name: 'Blue', value: 'rgb(59, 130, 246)', tailwind: 'bg-blue-500' },
  { name: 'Red', value: 'rgb(239, 68, 68)', tailwind: 'bg-red-500' },
  { name: 'Green', value: 'rgb(34, 197, 94)', tailwind: 'bg-green-500' },
  { name: 'Purple', value: 'rgb(168, 85, 247)', tailwind: 'bg-purple-500' },
  { name: 'Yellow', value: 'rgb(234, 179, 8)', tailwind: 'bg-yellow-500' },
  { name: 'Pink', value: 'rgb(236, 72, 153)', tailwind: 'bg-pink-500' },
  { name: 'Indigo', value: 'rgb(99, 102, 241)', tailwind: 'bg-indigo-500' },
  { name: 'Teal', value: 'rgb(20, 184, 166)', tailwind: 'bg-teal-500' },
];

interface NicknameModalProps {
  isOpen: boolean;
  onClose: () => void;
  accounts: string[];
  settings: AccountSettingsMap;
  onSave: (accountId: string, settings: AccountSettings) => void;
}

const NicknameModal: React.FC<NicknameModalProps> = ({
  isOpen,
  onClose,
  accounts,
  settings,
  onSave,
}) => {
  const [editedSettings, setEditedSettings] = useState<AccountSettingsMap>({});

  useEffect(() => {
    setEditedSettings(settings);
  }, [settings]);

  if (!isOpen) return null;

  const handleSave = () => {
    Object.entries(editedSettings).forEach(([accountId, newSettings]) => {
      const oldSettings = settings[accountId];
      if (!oldSettings || 
          oldSettings.nickname !== newSettings.nickname || 
          oldSettings.color !== newSettings.color) {
        onSave(accountId, newSettings);
      }
    });
    onClose();
  };

  const handleColorSelect = (accountId: string, color: string) => {
    setEditedSettings(prev => ({
      ...prev,
      [accountId]: {
        ...prev[accountId],
        color,
      },
    }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold">Edit Account Settings</h3>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-full"
          >
            <X size={20} />
          </button>
        </div>
        <div className="space-y-6 mb-6">
          {accounts.map((accountId) => {
            const accountSettings = editedSettings[accountId] || { nickname: '', color: CHART_COLORS[0].value };
            return (
              <div key={accountId} className="space-y-2">
                <div className="flex items-center gap-4">
                  <label className="w-32 text-sm text-gray-600">Account {accountId}</label>
                  <input
                    type="text"
                    className="flex-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={accountSettings.nickname || ''}
                    onChange={(e) =>
                      setEditedSettings(prev => ({
                        ...prev,
                        [accountId]: {
                          ...prev[accountId],
                          nickname: e.target.value,
                        },
                      }))
                    }
                    placeholder="Enter nickname"
                  />
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-32 text-sm text-gray-600">Color</div>
                  <div className="flex flex-wrap gap-2">
                    {CHART_COLORS.map((color) => (
                      <button
                        key={color.value}
                        onClick={() => handleColorSelect(accountId, color.value)}
                        className={`w-8 h-8 rounded-full ${color.tailwind} flex items-center justify-center transition-transform hover:scale-110 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
                        title={color.name}
                      >
                        {accountSettings.color === color.value && (
                          <Check size={16} className="text-white" />
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        <div className="flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-md"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          >
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
};

export const SnapshotChart: React.FC = () => {
  const [snapshots, setSnapshots] = useState<AccountSnapshot[]>([]);
  const [mode, setMode] = useState<ChartMode>('individual');
  const [selectedAccount, setSelectedAccount] = useState<string>('');
  const [dataType, setDataType] = useState<DataType>('equity');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [accountSettings, setAccountSettings] = useState<AccountSettingsMap>({});
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    const loadSettings = () => {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        setAccountSettings(JSON.parse(saved));
      }
    };

    loadSettings();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getSnapshots();
        setSnapshots(data);
        if (data.length > 0) {
          setSelectedAccount(data[0].account_id);
        }
      } catch (err) {
        setError('Failed to fetch snapshots');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const uniqueAccounts = [...new Set(snapshots.map(s => s.account_id))];

  const saveSettings = (accountId: string, settings: AccountSettings) => {
    const updatedSettings = { ...accountSettings, [accountId]: settings };
    setAccountSettings(updatedSettings);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedSettings));
  };

  const getAccountLabel = (accountId: string) => {
    return accountSettings[accountId]?.nickname || `Account ${accountId}`;
  };

  const getAccountColor = (accountId: string, index: number) => {
    return accountSettings[accountId]?.color || CHART_COLORS[index % CHART_COLORS.length].value;
  };

  const prepareChartData = (): ChartData<'line'> => {
    if (mode === 'individual') {
      const accountData = snapshots.filter(s => s.account_id === selectedAccount);
      return {
        labels: accountData.map(s => format(new Date(s.created_at), 'MM/dd/yyyy HH:mm')),
        datasets: [
          {
            label: `${dataType.charAt(0).toUpperCase() + dataType.slice(1)}`,
            data: accountData.map(s => s[dataType]),
            borderColor: getAccountColor(selectedAccount, 0),
            backgroundColor: getAccountColor(selectedAccount, 0),
          },
        ],
      };
    } else {
      return {
        labels: [...new Set(snapshots.map(s => format(new Date(s.created_at), 'MM/dd/yyyy HH:mm')))],
        datasets: uniqueAccounts.map((accountId, index) => ({
          label: getAccountLabel(accountId),
          data: snapshots
            .filter(s => s.account_id === accountId)
            .map(s => s[dataType]),
          borderColor: getAccountColor(accountId, index),
          backgroundColor: getAccountColor(accountId, index),
        })),
      };
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-96">Loading...</div>;
  }

  if (error) {
    return <div className="text-red-500 text-center">{error}</div>;
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Account Snapshots</h2>
        <div className="flex gap-4">
          <button
            onClick={() => setMode('individual')}
            className={`flex items-center gap-2 px-4 py-2 rounded ${
              mode === 'individual'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            <LineChart size={20} />
            Individual
          </button>
          <button
            onClick={() => setMode('comparison')}
            className={`flex items-center gap-2 px-4 py-2 rounded ${
              mode === 'comparison'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            <BarChart size={20} />
            Comparison
          </button>
        </div>
      </div>

      <div className="flex gap-4 mb-6">
        {mode === 'individual' && (
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsModalOpen(true)}
              className="p-2 hover:bg-gray-100 rounded-md"
              title="Edit Account Settings"
            >
              <Edit2 size={16} />
            </button>
            <select
              value={selectedAccount}
              onChange={(e) => setSelectedAccount(e.target.value)}
              className="px-4 py-2 border rounded-md"
            >
              {uniqueAccounts.map((account) => (
                <option key={account} value={account}>
                  {getAccountLabel(account)}
                </option>
              ))}
            </select>
          </div>
        )}
        <select
          value={dataType}
          onChange={(e) => setDataType(e.target.value as DataType)}
          className="px-4 py-2 border rounded-md"
        >
          <option value="equity">Equity</option>
          <option value="cash">Cash</option>
        </select>
      </div>

      <div className="h-[600px]">
        <Line
          data={prepareChartData()}
          options={{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'top' as const,
              },
              title: {
                display: true,
                text: mode === 'individual' 
                  ? `${getAccountLabel(selectedAccount)} ${dataType} Over Time`
                  : `Account ${dataType} Comparison`,
              },
            },
            scales: {
              y: {
                beginAtZero: false,
              },
            },
          }}
        />
      </div>

      <NicknameModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        accounts={uniqueAccounts}
        settings={accountSettings}
        onSave={saveSettings}
      />
    </div>
  );
};