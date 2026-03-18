export default function StatusBanner({ tone = "info", children }) {
  return <div className={`status-banner status-banner--${tone}`}>{children}</div>;
}
