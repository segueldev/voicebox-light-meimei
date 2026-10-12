import { create } from 'zustand';

export type GenerationStage = 'queued' | 'loading_model' | 'generating' | 'reconnecting';
export interface GenerationResult {
  id: string;
  status: 'completed' | 'failed';
  text?: string;
  profileId?: string;
  error?: string;
}
interface GenerationState {
  pendingGenerationIds: Set<string>;
  isGenerating: boolean;
  pendingStoryAdds: Map<string, string>;
  jobs: Record<string, { stage: GenerationStage; startedAt: number; text?: string }>;
  lastResult: GenerationResult | null;
  addPendingGeneration: (id: string, text?: string) => void;
  updateGenerationStage: (id: string, stage: GenerationStage) => void;
  finishGeneration: (result: GenerationResult) => void;
  removePendingGeneration: (id: string) => void;
  addPendingStoryAdd: (generationId: string, storyId: string) => void;
  removePendingStoryAdd: (generationId: string) => string | undefined;
  setActiveGenerationId: (id: string | null) => void;
  activeGenerationId: string | null;
}
export const useGenerationStore = create<GenerationState>((set, get) => ({
  pendingGenerationIds: new Set(), isGenerating: false, activeGenerationId: null,
  pendingStoryAdds: new Map(), jobs: {}, lastResult: null,
  addPendingGeneration: (id, text) => set((state) => {
    const next = new Set(state.pendingGenerationIds); next.add(id);
    return { pendingGenerationIds: next, isGenerating: true, lastResult: null,
      jobs: { ...state.jobs, [id]: state.jobs[id] ?? { stage: 'queued', startedAt: Date.now(), text } } };
  }),
  updateGenerationStage: (id, stage) => set((state) => state.jobs[id]
    ? { jobs: { ...state.jobs, [id]: { ...state.jobs[id], stage } } } : {}),
  finishGeneration: (result) => set((state) => ({ lastResult: { ...result, text: result.text ?? state.jobs[result.id]?.text } })),
  removePendingGeneration: (id) => set((state) => {
    const next = new Set(state.pendingGenerationIds); next.delete(id);
    const jobs = { ...state.jobs }; delete jobs[id];
    return { pendingGenerationIds: next, isGenerating: next.size > 0, jobs };
  }),
  addPendingStoryAdd: (generationId, storyId) => set((state) => {
    const next = new Map(state.pendingStoryAdds); next.set(generationId, storyId);
    return { pendingStoryAdds: next };
  }),
  removePendingStoryAdd: (generationId) => {
    const storyId = get().pendingStoryAdds.get(generationId);
    if (storyId) set((state) => { const next = new Map(state.pendingStoryAdds); next.delete(generationId); return { pendingStoryAdds: next }; });
    return storyId;
  },
  setActiveGenerationId: (id) => set({ activeGenerationId: id }),
}));
