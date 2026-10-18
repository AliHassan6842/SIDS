import { Link, Outlet, useLocation } from "react-router-dom";
import { Icon, type IconName } from "./Icon";

const navigation: Array<{ to: string; label: string; icon: IconName }> = [
  { to: "/home", label: "Home", icon: "home" },
  { to: "/identify", label: "Identify", icon: "camera" },
  { to: "/identify?mode=GENERAL_INSECT", label: "General", icon: "search" },
  { to: "/pests", label: "Pests", icon: "bug" },
  { to: "/history", label: "History", icon: "clock" },
  { to: "/profile", label: "Profile", icon: "profile" },
];

const activeNavigationIndex = (pathname: string, search: string): number => {
  if ((pathname.startsWith("/identify") || pathname.startsWith("/result/")) && search.includes("GENERAL_INSECT")) return 2;
  if (pathname.startsWith("/identify") || pathname.startsWith("/result/")) return 1;
  if (pathname.startsWith("/pests")) return 3;
  if (pathname.startsWith("/history")) return 4;
  if (pathname.startsWith("/profile")) return 5;
  return 0;
};

export function AppShell() {
  const { pathname, search } = useLocation();
  const activeIndex = activeNavigationIndex(pathname, search);

  return (
    <div className="app-frame">
      <main className="app-content">
        <Outlet />
      </main>
      <nav className="bottom-nav" aria-label="Main navigation" data-active-index={activeIndex}>
        <span className="bottom-nav__indicator" aria-hidden="true" />
        {navigation.map((item, index) => (
          <Link
            key={item.to}
            to={item.to}
            aria-current={activeIndex === index ? "page" : undefined}
            className={`bottom-nav__item${activeIndex === index ? " is-active" : ""}`}
          >
            <span className="bottom-nav__icon"><Icon name={item.icon} /></span>
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>
    </div>
  );
}
