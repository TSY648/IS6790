import { Link } from "react-router-dom";

export default function HomePage({ levels, loading, error }) {
  return (
    <div className="page-shell hero-page">
      <section className="hero-card">
        <p className="eyebrow">Data Literacy Game</p>
        <h1>数据素养决策游戏</h1>
        <p className="hero-copy">
          进入超市经营情境，阅读数据、解锁信息、提交订货决策，并根据结果拿到你的学习反馈。
        </p>

        <div className="hero-actions">
          <Link className="button button--primary" to={levels[0] ? `/story/${levels[0].levelId}` : "/"}>
            开始游戏
          </Link>
          <a className="button button--ghost" href="#levels">
            查看关卡
          </a>
        </div>
      </section>

      <section className="panel" id="levels">
        <div className="panel__header">
          <h2>关卡列表</h2>
          <p>配置驱动加载，当前前端会直接请求后端 `/api/levels`。</p>
        </div>

        {loading ? <p>正在加载关卡...</p> : null}
        {error ? <p className="text-danger">{error}</p> : null}

        <div className="level-grid">
          {levels.map((level) => (
            <article className="level-card" key={level.levelId}>
              <div className="level-card__meta">
                <span>#{level.order}</span>
                <span>{level.difficulty}</span>
              </div>
              <h3>{level.title}</h3>
              <Link className="button button--secondary" to={`/story/${level.levelId}`}>
                进入剧情
              </Link>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
