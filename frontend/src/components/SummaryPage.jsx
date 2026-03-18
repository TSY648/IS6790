import { Link } from "react-router-dom";

export default function SummaryPage({ level, result, certificate, onReset }) {
  return (
    <div className="page-shell narrow-page">
      <section className="panel summary-panel">
        <p className="eyebrow">Level Complete</p>
        <h1>{level?.title || "关卡结算"}</h1>

        <div className="summary-grid">
          <div className="summary-card">
            <h2>本次结果</h2>
            <p>状态：{result?.status || "未提交"}</p>
            <p>得分：{result?.score ?? "--"}</p>
            <p>订货量：{result?.decisionPayload?.orderQuantity ?? "--"}</p>
          </div>

          <div className="summary-card">
            <h2>证书信息</h2>
            {certificate ? (
              <>
                <p>证书编号：{certificate.certificateNo}</p>
                <p>总分：{certificate.totalScore}</p>
                <p>签发时间：{String(certificate.issuedAt)}</p>
              </>
            ) : (
              <p>当前还没有证书记录，可在后端插入证书数据后展示。</p>
            )}
          </div>
        </div>

        <div className="hero-actions">
          <button className="button button--ghost" onClick={onReset} type="button">
            重置本地进度
          </button>
          <Link className="button button--primary" to="/">
            返回首页
          </Link>
        </div>
      </section>
    </div>
  );
}
