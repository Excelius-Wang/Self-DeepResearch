export type ThoughtType = 'planner' | 'researcher' | 'reviewer' | 'error';

export type ResearchPhase = 'planner' | 'researcher' | 'reviewer' | 'reporter';

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

export interface ResearchProgress {
  currentLoop: number;
  maxLoops: number;
  phase: ResearchPhase;
  message: string;
}

export interface HistoryItem {
  id: number;
  task: string;
  created_at: string;
  notes_count?: number;
}
