export interface AccountSnapshot {
  id?: number | null;
  account_id: string;
  name: string;
  cash: number;
  equity: number;
  created_at: string;
}