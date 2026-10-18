import type { SVGProps } from "react";

export type IconName =
  | "arrow"
  | "back"
  | "bug"
  | "camera"
  | "chevron"
  | "clock"
  | "gallery"
  | "home"
  | "info"
  | "leaf"
  | "profile"
  | "refresh"
  | "search"
  | "switch"
  | "warning";

const paths: Record<IconName, React.ReactNode> = {
  arrow: <path d="M5 12h14m-5-5 5 5-5 5" />,
  back: <path d="m15 18-6-6 6-6" />,
  bug: <><path d="M8 8h8v8a4 4 0 0 1-8 0V8Z"/><path d="M9 8 7 5m6 3 2-3M5 11h3m8 0h3M5 16h3m8 0h3"/></>,
  camera: <><path d="M4 7h3l1.5-2h7L17 7h3v12H4Z"/><circle cx="12" cy="13" r="4"/></>,
  chevron: <path d="m9 18 6-6-6-6" />,
  clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
  gallery: <><rect x="3" y="4" width="18" height="16" rx="2"/><path d="m5 17 5-5 4 4 2-2 3 3"/><circle cx="8" cy="8" r="1"/></>,
  home: <><path d="m3 11 9-8 9 8"/><path d="M5 10v10h14V10M9 20v-6h6v6"/></>,
  info: <><circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10h.01"/></>,
  leaf: <><path d="M20 4C12 4 5 8 5 15c0 3 2 5 5 5 7 0 10-8 10-16Z"/><path d="M5 21c2-6 6-10 12-13"/></>,
  profile: <><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></>,
  refresh: <><path d="M20 7v5h-5"/><path d="M19 12a7 7 0 1 0-2 5"/></>,
  search: <><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></>,
  switch: <><path d="M7 7h11l-3-3m2 13H6l3 3"/><rect x="3" y="5" width="18" height="14" rx="3"/></>,
  warning: <><path d="M12 3 2.5 20h19Z"/><path d="M12 9v4m0 3h.01"/></>,
};

interface IconProps extends SVGProps<SVGSVGElement> {
  name: IconName;
  label?: string;
}

export function Icon({ name, label, ...props }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden={label ? undefined : true}
      aria-label={label}
      role={label ? "img" : undefined}
      {...props}
    >
      {paths[name]}
    </svg>
  );
}
