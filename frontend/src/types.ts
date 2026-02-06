export type ThoughtType = 'planner' | 'researcher' | 'reviewer' | 'error';

export interface Source {
  title: string;
  url: string;
  content: string;
}

export interface ThoughtStep {
  id: string;
  type: ThoughtType;
  title: string;
  content: string | string[]; // Planner: sub_queries[], Researcher: current_query, Reviewer: feedback
  status: 'pending' | 'processing' | 'completed' | 'error';
  sources?: Source[]; // Only for Researcher
  timestamp: number;
}
