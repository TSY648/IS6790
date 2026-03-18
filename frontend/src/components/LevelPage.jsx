export default function LevelPage({
  level,
  userId,
  orderQuantity,
  setOrderQuantity,
  unlockedIds,
  readItems,
  onReadDataSource,
  onSaveDraft,
  onSubmitResult,
  saveStatus,
  submitStatus
}) {
  if (!level) {
    return null;
  }

  return (
    <div className="page-shell gameplay-page">
      <header className="topbar panel">
        <div>
          <p className="eyebrow">当前用户</p>
          <strong>{userId}</strong>
        </div>
        <div>
          <p className="eyebrow">当前关卡</p>
          <strong>{level.title}</strong>
        </div>
      </header>

      <div className="game-layout">
        <aside className="panel sidebar">
          <h2>任务目标</h2>
          <ul>
            {level.objectives?.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>

          <div className="rule-box">
            <h3>判定规则</h3>
            <ul>
              {level.evaluation?.successRules?.map((rule) => (
                <li key={rule}>{rule}</li>
              ))}
            </ul>
          </div>
        </aside>

        <main className="panel workspace">
          <h2>订货决策</h2>
          <p>请拖动滑块，决定草莓本周订货量。</p>

          <div className="slider-card">
            <label htmlFor="orderQuantity">订货量：{orderQuantity}</label>
            <input
              id="orderQuantity"
              type="range"
              min={level.decision?.min ?? 0}
              max={level.decision?.max ?? 300}
              step={level.decision?.step ?? 10}
              value={orderQuantity}
              onChange={(event) => setOrderQuantity(Number(event.target.value))}
            />
            <div className="slider-scale">
              <span>{level.decision?.min ?? 0}</span>
              <span>{level.decision?.max ?? 300}</span>
            </div>
          </div>

          <div className="action-row">
            <button className="button button--ghost" onClick={onSaveDraft} type="button">
              保存草稿
            </button>
            <button className="button button--primary" onClick={onSubmitResult} type="button">
              提交结果
            </button>
          </div>

          {saveStatus ? <p className="helper-text">{saveStatus}</p> : null}
          {submitStatus ? <p className="helper-text">{submitStatus}</p> : null}
        </main>

        <aside className="panel sidebar">
          <h2>数据入口</h2>
          <div className="datasource-list">
            {level.dataSources?.map((source) => {
              const isUnlocked = source.initialVisible || unlockedIds.includes(source.id);
              const hasRead = readItems.includes(source.id);

              return (
                <article className="datasource-card" key={source.id}>
                  <div className="datasource-card__header">
                    <h3>{source.title}</h3>
                    <span>{source.type}</span>
                  </div>
                  <p>{isUnlocked ? "已解锁，可查看内容。" : "未解锁，请先阅读前置资料。"}</p>
                  <button
                    className="button button--secondary"
                    disabled={!isUnlocked}
                    onClick={() => onReadDataSource(source.id)}
                    type="button"
                  >
                    {hasRead ? "再次查看" : "标记已读"}
                  </button>
                </article>
              );
            })}
          </div>
        </aside>
      </div>
    </div>
  );
}
