import { create } from 'zustand';
export const useLayoutStore = create<{
  playerHeight: number; composerHeight: number;
  setPlayerHeight: (height: number) => void;
  setComposerHeight: (height: number) => void;
}>((set) => ({
  playerHeight: 0, composerHeight: 0,
  setPlayerHeight: (height) => set((state) => state.playerHeight === height ? {} : { playerHeight: height }),
  setComposerHeight: (height) => set((state) => state.composerHeight === height ? {} : { composerHeight: height }),
}));
