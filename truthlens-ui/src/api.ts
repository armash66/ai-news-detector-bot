import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface EventResponse {
  id: string;
  title: string;
  summary: string | null;
  category: string;
  status: string;
  significance_score: number;
  trust_score: number;
  article_count: number;
  source_count: number;
  first_seen_at: string;
  last_updated_at: string;
  peak_at?: string | null;
  primary_location?: Record<string, any> | null;
  primary_entities?: Record<string, string>[] | null;
  sentiment_distribution?: Record<string, number> | null;
  parent_event_id?: string | null;
}

export interface EventDetail extends EventResponse {
  articles: any[];
  timeline: any[];
  claims: any[];
}

export interface AlertResponse {
  id: string;
  event_id?: string | null;
  alert_type: string;
  severity: string;
  title: string;
  description?: string | null;
  triggered_at: string;
  acknowledged: boolean;
}

export interface SearchResponse {
  data: EventResponse[];
  meta: Record<string, any>;
}

export const api = {
  getEvents: async (limit = 20, sort_by = 'significance_score') => {
    const res = await apiClient.get<{data: EventResponse[], meta: any}>('/events', { params: { limit, sort_by } });
    return res.data.data;
  },
  
  getEventDetail: async (eventId: string) => {
    const res = await apiClient.get<EventDetail>(`/events/${eventId}`);
    return res.data;
  },
  
  getAlerts: async (limit = 20) => {
    const res = await apiClient.get<{data: AlertResponse[], meta: any}>('/alerts', { params: { limit } });
    return res.data.data;
  },
  
  search: async (query: string, search_type = 'keyword') => {
    const res = await apiClient.get<SearchResponse>('/search', { params: { query, search_type } });
    return res.data.data;
  }
};
