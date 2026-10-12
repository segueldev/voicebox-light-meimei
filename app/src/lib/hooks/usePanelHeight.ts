import { useEffect, type RefObject } from 'react';
export function usePanelHeight(ref: RefObject<HTMLElement>, setHeight: (height: number) => void, visible = true) {
  useEffect(() => {
    const element = ref.current;
    if (!visible || !element) { setHeight(0); return; }
    const measure = () => setHeight(Math.ceil(element.getBoundingClientRect().height));
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(element);
    return () => { observer.disconnect(); setHeight(0); };
  }, [ref, setHeight, visible]);
}
