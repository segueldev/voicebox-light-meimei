import { CheckCircle2, Loader2, Pause, Play, AlertCircle } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api/client';
import { useGenerationStore } from '@/stores/generationStore';
import { usePlayerStore } from '@/stores/playerStore';

export function GenerationFeedback({ submitting, onRestoreText }: { submitting: boolean; onRestoreText: (text: string) => void }) {
  const { jobs, lastResult } = useGenerationStore();
  const player = usePlayerStore();
  const [, tick] = useState(0);
  const entries = Object.values(jobs);
  const job = entries[0];
  useEffect(() => {
    if (!job) return;
    const timer = window.setInterval(() => tick((n) => n + 1), 1000);
    return () => clearInterval(timer);
  }, [job?.startedAt]);
  if (!job && !submitting && !lastResult) return null;
  const busy = !!job || submitting;
  const failed = !busy && lastResult?.status === 'failed';
  const activeAudio = !busy && lastResult?.id === player.audioId;
  const playing = activeAudio && player.isPlaying;
  const loadingAudio = activeAudio && !player.playbackError && (player.shouldAutoPlay || player.duration === 0);
  const ended = activeAudio && player.duration > 0 && player.currentTime >= player.duration - 0.05;
  const paused = activeAudio && !playing && !loadingAudio && player.currentTime > 0 && !ended;
  const stage = job?.stage;
  const title = busy
    ? submitting && !job ? 'Enviando texto…' : stage === 'loading_model' ? 'Preparando la voz…' : stage === 'reconnecting' ? 'Comprobando la generación…' : stage === 'queued' ? 'Esperando turno…' : 'Generando audio…'
    : failed ? 'No se pudo generar el audio' : playing ? 'Audio listo · Reproduciendo' : loadingAudio ? 'Audio listo · Cargando para reproducir…' : activeAudio && player.playbackError ? 'Audio generado · No se pudo reproducir' : ended ? 'Audio listo · Reproducción terminada' : paused ? 'Audio listo · Pausado' : 'Audio listo';
  const seconds = job ? Math.floor((Date.now() - job.startedAt) / 1000) : 0;
  const detail = busy
    ? stage === 'reconnecting' ? 'Se perdió la conexión de progreso. Estamos comprobando el resultado.' : stage === 'loading_model' ? 'La primera vez tarda más mientras se carga la voz.' : entries.length > 1 ? `${entries.length} audios pendientes. Puedes seguir escribiendo.` : 'Puedes seguir escribiendo. Te avisaremos cuando termine.'
    : failed ? lastResult?.error || 'Recupera el texto y vuelve a intentarlo.' : playing ? 'Puedes pausarlo desde aquí o desde el reproductor.' : loadingAudio ? 'La reproducción comenzará en cuanto cargue.' : activeAudio && player.playbackError ? player.playbackError : paused ? 'Pulsa Continuar para seguir desde donde lo pausaste.' : 'Pulsa Escuchar para reproducirlo o volver a escucharlo.';
  return <div className={`mb-3 rounded-xl border px-3 py-2 ${failed ? 'border-destructive/40 bg-destructive/5' : 'border-accent/30 bg-accent/5'}`} data-generation-feedback>
    <div className="flex items-center gap-2">
      {busy || loadingAudio ? <Loader2 className="h-4 w-4 animate-spin shrink-0" aria-hidden="true" /> : failed ? <AlertCircle className="h-4 w-4 text-destructive shrink-0" /> : <CheckCircle2 className="h-4 w-4 text-accent shrink-0" />}
      <div className="flex-1 min-w-0" role="status" aria-live="polite">
        <p className="text-sm font-medium">{title}</p>
        <p className="text-xs text-muted-foreground">{detail}</p>
      </div>
      {job && <span className="text-xs text-muted-foreground tabular-nums" aria-hidden="true">{Math.floor(seconds / 60)}:{String(seconds % 60).padStart(2, '0')}</span>}
      {!busy && failed && lastResult?.text && <Button type="button" size="sm" variant="outline" onClick={() => onRestoreText(lastResult.text!)}>Recuperar texto</Button>}
      {!busy && !failed && !loadingAudio && lastResult && <Button type="button" size="sm" variant="outline" onClick={() => {
        if (playing) player.setIsPlaying(false);
        else if (activeAudio && player.playbackError) player.setAudioWithAutoPlay(apiClient.getAudioUrl(lastResult.id) + '?retry=' + Date.now(), lastResult.id, lastResult.profileId ?? null, lastResult.text?.slice(0, 60));
        else if (activeAudio && !ended) player.setIsPlaying(true);
        else if (activeAudio) player.restartCurrentAudio();
        else player.setAudioWithAutoPlay(apiClient.getAudioUrl(lastResult.id), lastResult.id, lastResult.profileId ?? null, lastResult.text?.slice(0, 60));
      }}>{playing ? <Pause className="h-3.5 w-3.5 mr-1" /> : <Play className="h-3.5 w-3.5 mr-1" />}{playing ? 'Pausar' : paused ? 'Continuar' : 'Escuchar'}</Button>}
    </div>
  </div>;
}
