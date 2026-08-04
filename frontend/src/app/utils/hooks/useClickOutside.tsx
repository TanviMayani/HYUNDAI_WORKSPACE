// src/hooks/useOnClickOutside.ts
import { useEffect, useCallback, useRef } from "react";

type EventType = MouseEvent | null;

export const useOnClickOutside = (handler: (event: EventType) => void) => {
  const ref = useRef<HTMLDivElement | null>(null);

  const handleClickOutside = useCallback(
    (event: Event) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        /* @ts-expect-error: ignore this error */
        handler(event);
      }
    },
    [handler]
  );

  useEffect(() => {
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [handleClickOutside]);

  return ref;
};
