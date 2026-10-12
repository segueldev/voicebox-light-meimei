import { Sparkles, Upload } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FloatingGenerateBox } from '@/components/Generation/FloatingGenerateBox';
import { HistoryTable } from '@/components/History/HistoryTable';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { useToast } from '@/components/ui/use-toast';
import { ProfileList } from '@/components/VoiceProfiles/ProfileList';

import { useImportProfile } from '@/lib/hooks/useProfiles';
import { useLayoutStore } from '@/stores/layoutStore';
import { usePlayerStore } from '@/stores/playerStore';
import { useUIStore } from '@/stores/uiStore';

export function MainEditor() {
  const { t } = useTranslation();
  const playerHeight = useLayoutStore((s) => s.playerHeight);
  const audioUrl = usePlayerStore((state) => state.audioUrl);
  const rootRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;
    const scrollHistory = (event: WheelEvent) => {
      const target = event.target as HTMLElement;
      if (target.closest('[data-history-scroll],textarea,input,[role="slider"],[data-generation-feedback]')) return;
      if (Math.abs(event.deltaY) <= Math.abs(event.deltaX)) return;
      const history = root.querySelector<HTMLElement>('[data-history-scroll]');
      if (!history || history.scrollHeight <= history.clientHeight) return;
      event.preventDefault();
      const scale = event.deltaMode === 1 ? 20 : event.deltaMode === 2 ? history.clientHeight : 1;
      history.scrollTop += event.deltaY * scale;
    };
    root.addEventListener('wheel', scrollHistory, { passive: false });
    return () => root.removeEventListener('wheel', scrollHistory);
  }, []);
  const setDialogOpen = useUIStore((state) => state.setProfileDialogOpen);
  const importProfile = useImportProfile();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { toast } = useToast();

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.endsWith('.voicebox.zip')) {
        toast({
          title: t('main.import.invalidTitle'),
          description: t('main.import.invalidDescription'),
          variant: 'destructive',
        });
        return;
      }
      setSelectedFile(file);
      setImportDialogOpen(true);
    }
  };

  const handleImportConfirm = () => {
    if (selectedFile) {
      importProfile.mutate(selectedFile, {
        onSuccess: () => {
          setImportDialogOpen(false);
          setSelectedFile(null);
          if (fileInputRef.current) {
            fileInputRef.current.value = '';
          }
          toast({
            title: t('main.import.successTitle'),
            description: t('main.import.successDescription'),
          });
        },
        onError: (error) => {
          toast({
            title: t('main.import.failedTitle'),
            description: error.message,
            variant: 'destructive',
          });
        },
      });
    }
  };

  return (
    <div ref={rootRef} style={{ paddingBottom: playerHeight ? playerHeight + 8 : 8 }} className="flex flex-col h-full min-h-0 overflow-hidden relative">
      <div className="shrink-0 flex flex-col overflow-hidden relative">


        <div className="shrink-0">
          <div className="flex items-center justify-between mb-4 px-1">
            <div><h2 className="text-2xl font-bold">Voice Box</h2><p className="text-sm text-muted-foreground">Edición Light Meimei</p></div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={handleImportClick}>
                <Upload className="mr-2 h-4 w-4" />
                {t('main.importVoice')}
              </Button>
              <input
                ref={fileInputRef}
                type="file"
                accept=".voicebox.zip"
                onChange={handleFileChange}
                className="hidden"
              />
              <Button onClick={() => setDialogOpen(true)}>
                <Sparkles className="mr-2 h-4 w-4" />
                {t('main.createVoice')}
              </Button>
            </div>
          </div>
        </div>

<div className="shrink-0 pb-3" data-voice-strip>
          <div className="flex flex-col gap-6">
            <div className="shrink-0 flex flex-col">
              <ProfileList compact />
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
        <h2 className="text-sm font-semibold py-2">Audios generados</h2>
        <HistoryTable />
      </div>

      <FloatingGenerateBox isPlayerOpen={!!audioUrl} docked />

      <Dialog open={importDialogOpen} onOpenChange={setImportDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('main.import.dialogTitle')}</DialogTitle>
            <DialogDescription>
              {t('main.import.dialogDescription', { name: selectedFile?.name })}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setImportDialogOpen(false);
                setSelectedFile(null);
                if (fileInputRef.current) {
                  fileInputRef.current.value = '';
                }
              }}
            >
              {t('common.cancel')}
            </Button>
            <Button
              onClick={handleImportConfirm}
              disabled={importProfile.isPending || !selectedFile}
            >
              {importProfile.isPending ? t('main.import.importing') : t('main.import.action')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
