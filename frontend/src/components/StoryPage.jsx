import { Link } from "react-router-dom";

export default function StoryPage({ level }) {
  if (!level) {
    return null;
  }

  return (
    <div className="page-shell narrow-page">
      <section className="panel story-panel">
        <p className="eyebrow">Scenario Intro</p>
        <h1>{level.title}</h1>
        <p className="story-text">{level.story?.intro}</p>
        <p className="story-description">{level.description}</p>

        <div className="objective-list">
          <h2>目标</h2>
          <ul>
            {level.objectives?.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>

        <div className="hero-actions">
          <Link className="button button--ghost" to="/">
            返回首页
          </Link>
          <Link className="button button--primary" to={`/level/${level.id}`}>
            进入关卡
          </Link>
        </div>
      </section>
    </div>
  );
}
