import { AlertCircle, Download, RefreshCw } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { useAutoUpdater } from '@/hooks/useAutoUpdater';
import { usePlatform } from '@/platform/PlatformContext';

export function UpdateStatus() {
  const platform = usePlatform();
  const { status, checkForUpdates, downloadAndInstall, restartAndInstall } = useAutoUpdater(false);
  const [currentVersion, setCurrentVersion] = useState<string>('');
  const isDev = !import.meta.env?.PROD;

  useEffect(() => {
    platform.metadata
      .getVersion()
      .then(setCurrentVersion)
      .catch(() => setCurrentVersion('Unknown'));
  }, [platform]);

  return (
    <Card role="region" aria-label="Actualizaciones de la aplicación" tabIndex={0}>
      <CardHeader>
        <CardTitle>Actualizaciones de la aplicación</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <div className="text-sm font-medium">Current Version</div>
            <div className="text-sm text-muted-foreground">
              v{currentVersion}
              {isDev ? " (desarrollo)" : ''}
            </div>
          </div>
          {!isDev && (
            <Button
              onClick={checkForUpdates}
              disabled={status.checking || status.downloading || status.readyToInstall}
              variant="outline"
              size="sm"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${status.checking ? 'animate-spin' : ''}`} />
              Buscar actualizaciones</Button>
          )}
        </div>

        {isDev ? (
          <div className="text-sm text-muted-foreground">
            Las actualizaciones automáticas están desactivadas en modo de desarrollo.</div>
        ) : (
          <>
            {status.checking && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <RefreshCw className="h-4 w-4 animate-spin" />
                Buscando actualizaciones…</div>
            )}

            {status.error && (
              <div className="flex items-center gap-2 text-sm text-destructive">
                <AlertCircle className="h-4 w-4" />
                {status.error}
              </div>
            )}

            {status.available && !status.downloading && !status.readyToInstall && (
              <div className="space-y-3 p-4 border rounded-lg bg-primary/5">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold">Actualización disponible</div>
                    <div className="text-sm text-muted-foreground">Versión{status.version}</div>
                  </div>
                  <Badge>Nuevo</Badge>
                </div>
                <Button onClick={downloadAndInstall} className="w-full" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Descargar actualización</Button>
              </div>
            )}

            {status.downloading && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <Download className="h-4 w-4" />
                    Descargando actualización…</div>
                  {status.downloadProgress !== undefined && (
                    <span className="text-muted-foreground">{status.downloadProgress}%</span>
                  )}
                </div>
                <Progress value={status.downloadProgress} />
                {status.downloadedBytes !== undefined &&
                  status.totalBytes !== undefined &&
                  status.totalBytes > 0 && (
                    <div className="text-xs text-muted-foreground">
                      {(status.downloadedBytes / 1024 / 1024).toFixed(1)} MB /{' '}
                      {(status.totalBytes / 1024 / 1024).toFixed(1)} MB
                    </div>
                  )}
              </div>
            )}

            {status.readyToInstall && (
              <div className="space-y-3 p-4 border rounded-lg bg-accent/30 border-accent/50">
                <div className="flex items-center gap-2">
                  <div>
                    <div className="font-semibold">Actualización lista para instalar</div>
                    <div className="text-sm text-muted-foreground">
                      Versión{status.version} se ha descargado</div>
                  </div>
                </div>
                <div className="text-sm text-muted-foreground">
                  The app needs to restart to complete the installation. You can do this now or
                  later at your convenience.
                </div>
                <Button onClick={restartAndInstall} className="w-full" size="sm">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Reiniciar ahora</Button>
              </div>
            )}

            {!status.available && !status.checking && !status.error && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                Tienes la versión más reciente</div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
