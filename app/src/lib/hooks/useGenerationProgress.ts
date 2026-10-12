import { useQueryClient } from '@tanstack/react-query';
import { useEffect, useRef } from 'react';
import { useToast } from '@/components/ui/use-toast';
import { apiClient } from '@/lib/api/client';
import { useGenerationSettings } from '@/lib/hooks/useSettings';
import { useGenerationStore } from '@/stores/generationStore';
import { usePlayerStore } from '@/stores/playerStore';

interface StatusEvent {
  id: string;
  status: 'loading_model' | 'generating' | 'completed' | 'failed' | 'not_found';
  duration?: number;
  error?: string;
  source?: string;
}
interface Connection { source: EventSource | null; timer: number | null; finishing: boolean; cancelled: boolean; origin?: string }
const AGENT_SOURCES = new Set(['mcp', 'rest']);

export function useGenerationProgress() {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const pendingIds = useGenerationStore((s) => s.pendingGenerationIds);
  const { settings } = useGenerationSettings();
  const autoplayRef = useRef(true);
  autoplayRef.current = settings?.autoplay_on_generate ?? true;
  const connections = useRef(new Map<string, Connection>());
  useEffect(() => {
    const all = connections.current;
    return () => {
      for (const connection of all.values()) {
        connection.cancelled = true; connection.source?.close();
        if (connection.timer !== null) clearTimeout(connection.timer);
      }
      all.clear();
    };
  }, []);

  useEffect(() => {
    const all = connections.current;
    for (const [id, connection] of all) if (!pendingIds.has(id)) {
      connection.cancelled = true; connection.source?.close();
      if (connection.timer !== null) clearTimeout(connection.timer);
      all.delete(id);
    }
    for (const id of pendingIds) {
      if (all.has(id)) continue;
      const connection: Connection = { source: null, timer: null, finishing: false, cancelled: false };
      all.set(id, connection);
      const accept = async (data: StatusEvent) => {
        if (connection.cancelled || connection.finishing) return;
        if (data.source) connection.origin = data.source;
        const store = useGenerationStore.getState();
        if (data.status === 'loading_model' || data.status === 'generating') {
          store.updateGenerationStage(id, data.status);
          return;
        }
        if (!['completed', 'failed', 'not_found'].includes(data.status)) return;
        connection.finishing = true;
        connection.source?.close();
        if (connection.timer !== null) clearTimeout(connection.timer);
        const generation = await apiClient.getGeneration(id).catch(() => null);
        if (connection.cancelled) return;
        store.finishGeneration({ id, status: data.status === 'completed' ? 'completed' : 'failed', text: generation?.text, profileId: generation?.profile_id, error: data.error || (data.status === 'not_found' ? 'No se encontró esta generación.' : undefined) });
        store.removePendingGeneration(id);
        queryClient.invalidateQueries({ queryKey: ['history'] });
        const storyId = store.removePendingStoryAdd(id);
        if (data.status !== 'completed') {
          toast({ title: 'No se pudo generar el audio', description: data.error || 'Recupera el texto y vuelve a intentarlo.', variant: 'destructive' });
          return;
        }
        if (storyId) apiClient.addStoryItem(storyId, { generation_id: id }).then(() => {
          queryClient.invalidateQueries({ queryKey: ['stories'] });
          toast({ title: 'Audio añadido a la historia' });
        }).catch(() => toast({ title: 'Audio listo', description: 'No se pudo añadir a la historia. Sigue disponible en el historial.', variant: 'destructive' }));
        const player = usePlayerStore.getState();
        if (autoplayRef.current && !player.isPlaying && !AGENT_SOURCES.has(connection.origin ?? '')) {
          player.setAudioWithAutoPlay(apiClient.getAudioUrl(id), id, generation?.profile_id ?? null, generation?.text.slice(0, 60));
        }
      };
      // A lost progress stream does not mean that generation has finished.
      // Poll the saved job until its actual terminal state is known.
      const poll = async () => {
        if (connection.cancelled || connection.finishing) return;
        try {
          const generation = await apiClient.getGeneration(id);
          await accept({ id, status: (generation.status || 'completed') as StatusEvent['status'], duration: generation.duration ?? undefined, error: generation.error ?? undefined });
        } catch (error) {
          if (error instanceof Error && /generation not found|404/i.test(error.message)) {
            await accept({ id, status: 'not_found' });
          }
          if (!connection.cancelled && !connection.finishing) useGenerationStore.getState().updateGenerationStage(id, 'reconnecting');
        }
        if (!connection.cancelled && !connection.finishing) connection.timer = window.setTimeout(poll, 1500);
      };
      const fallback = () => {
        if (connection.cancelled || connection.finishing || connection.timer !== null) return;
        connection.source?.close(); connection.source = null;
        useGenerationStore.getState().updateGenerationStage(id, 'reconnecting');
        connection.timer = window.setTimeout(poll, 500);
      };
      try {
        const source = new EventSource(apiClient.getGenerationStatusUrl(id));
        connection.source = source;
        source.onmessage = (event) => { try { void accept(JSON.parse(event.data)); } catch { /* heartbeat */ } };
        source.onerror = fallback;
      } catch { fallback(); }
    }
  }, [pendingIds, queryClient, toast]);
}
