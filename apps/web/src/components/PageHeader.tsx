import { useNavigate } from "react-router-dom";
import { Icon } from "./Icon";

export function PageHeader({ title, back = false, action }: { title: string; back?: boolean; action?: React.ReactNode }) {
  const navigate = useNavigate();
  return (
    <header className="page-header">
      {back ? (
        <button className="icon-button" type="button" onClick={() => navigate(-1)} aria-label="Go back">
          <Icon name="back" />
        </button>
      ) : <span className="page-header__spacer" />}
      <h1>{title}</h1>
      <div className="page-header__action">{action}</div>
    </header>
  );
}
