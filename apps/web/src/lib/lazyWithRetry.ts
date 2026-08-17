import { lazy } from "react";

export const lazyWithRetry = (fn: () => Promise<any>) =>
  lazy(() =>
    fn().catch(() =>
      fn().catch(() => fn())
    )
  );
