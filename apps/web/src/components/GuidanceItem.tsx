import { Icon } from "./Icon";

export function GuidanceItem({ title, content }: { title: string; content: string | string[] }) {
  return (
    <section className="guidance-item">
      <Icon name="leaf" />
      <div>
        <h2>{title}</h2>
        {Array.isArray(content) ? <ul>{content.map((line, index) => <li key={`${index}-${line}`}>{line}</li>)}</ul> : <p>{content}</p>}
      </div>
    </section>
  );
}
