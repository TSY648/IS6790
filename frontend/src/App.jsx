import { useCallback, useEffect, useMemo, useState } from "react";
import { Navigate, Route, Routes, useNavigate, useParams } from "react-router-dom";
import HomePage from "./components/HomePage.jsx";
import LevelPage from "./components/LevelPage.jsx";
import StatusBanner from "./components/StatusBanner.jsx";
import StoryPage from "./components/StoryPage.jsx";
import SummaryPage from "./components/SummaryPage.jsx";
import {
  fetchCertificate,
  fetchLevel,
  fetchLevels,
  fetchProgress,
  saveProgress,
  submitResult
} from "./lib/api.js";
import { clearLocalState, getDefaultUserId, mergeLocalState, readLocalState } from "./data/localProgress.js";

function inferScore(orderQuantity) {
  if (orderQuantity >= 100 && orderQuantity <= 140) {
    return 85;
  }

  if (orderQuantity >= 80 && orderQuantity <= 180) {
    return 70;
  }

  return 55;
}

function inferStatus(orderQuantity) {
  return orderQuantity >= 100 && orderQuantity <= 140 ? "success" : "failed";
}

function useGameData() {
  const [levels, setLevels] = useState([]);
  const [levelsLoading, setLevelsLoading] = useState(true);
  const [globalError, setGlobalError] = useState("");
  const [levelCache, setLevelCache] = useState({});
  const [progress, setProgress] = useState(readLocalState());
  const [certificate, setCertificate] = useState(null);
  const userId = useMemo(() => progress.userId || getDefaultUserId(), [progress.userId]);

  useEffect(() => {
    async function loadLevels() {
      try {
        const data = await fetchLevels();
        setLevels(data);
      } catch (error) {
        setGlobalError(error.message);
      } finally {
        setLevelsLoading(false);
      }
    }

    loadLevels();
  }, []);

  useEffect(() => {
    async function syncProgress() {
      try {
        const remoteProgress = await fetchProgress(userId);
        if (remoteProgress) {
          const nextState = mergeLocalState({ ...remoteProgress, userId });
          setProgress(nextState);
        } else {
          const nextState = mergeLocalState({ userId });
          setProgress(nextState);
        }
      } catch {
        const nextState = mergeLocalState({ userId });
        setProgress(nextState);
      }
    }

    syncProgress();
  }, [userId]);

  const ensureLevel = useCallback(async (levelId) => {
    if (levelCache[levelId]) {
      return levelCache[levelId];
    }

    const level = await fetchLevel(levelId);
    setLevelCache((current) => ({
      ...current,
      [levelId]: level
    }));
    return level;
  }, [levelCache]);

  const loadCertificate = useCallback(async () => {
    try {
      const data = await fetchCertificate(userId);
      setCertificate(data);
    } catch {
      setCertificate(null);
    }
  }, [userId]);

  const updateProgress = useCallback((patch) => {
    const nextState = mergeLocalState({ userId, ...patch });
    setProgress(nextState);
    return nextState;
  }, [userId]);

  const resetProgress = useCallback(() => {
    clearLocalState();
    const nextState = { userId: getDefaultUserId() };
    mergeLocalState(nextState);
    setProgress(nextState);
    setCertificate(null);
  }, []);

  return {
    levels,
    levelsLoading,
    globalError,
    progress,
    certificate,
    userId,
    ensureLevel,
    updateProgress,
    resetProgress,
    loadCertificate
  };
}

function StoryRoute({ ensureLevel }) {
  const { levelId } = useParams();
  const [level, setLevel] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    ensureLevel(levelId).then(setLevel).catch((err) => setError(err.message));
  }, [ensureLevel, levelId]);

  if (error) {
    return <StatusBanner tone="error">{error}</StatusBanner>;
  }

  return <StoryPage level={level} />;
}

function LevelRoute({ ensureLevel, progress, updateProgress, userId }) {
  const { levelId } = useParams();
  const navigate = useNavigate();
  const [level, setLevel] = useState(null);
  const [saveStatus, setSaveStatus] = useState("");
  const [submitStatus, setSubmitStatus] = useState("");
  const [error, setError] = useState("");
  const existingDraft = progress.decisionDraft?.orderQuantity;
  const [orderQuantity, setOrderQuantity] = useState(existingDraft ?? 120);
  const readItems = progress.readItems || [];
  const unlockedLevels = progress.unlockedLevels || [levelId];
  const unlockedIds = level?.dataSources
    ?.filter((source) => source.initialVisible || readItems.includes(source.unlockCondition?.readItem))
    .map((source) => source.id) || [];

  useEffect(() => {
    ensureLevel(levelId)
      .then((data) => {
        setLevel(data);
        if (existingDraft != null) {
          setOrderQuantity(existingDraft);
        } else if (data.decision?.min != null) {
          setOrderQuantity(Math.max(120, data.decision.min));
        }
      })
      .catch((err) => setError(err.message));
  }, [ensureLevel, existingDraft, levelId]);

  function markRead(sourceId) {
    const nextReadItems = Array.from(new Set([...readItems, sourceId]));
    updateProgress({
      currentLevelCode: levelId,
      unlockedLevels: Array.from(new Set([...unlockedLevels, levelId])),
      readItems: nextReadItems,
      decisionDraft: { orderQuantity }
    });
  }

  async function handleSaveDraft() {
    const payload = {
      userId,
      currentLevelCode: levelId,
      unlockedLevels: Array.from(new Set([...unlockedLevels, levelId])),
      readItems,
      decisionDraft: { orderQuantity }
    };

    try {
      await saveProgress(payload);
      updateProgress(payload);
      setSaveStatus("草稿已保存到后端，并同步到本地。");
    } catch (err) {
      updateProgress(payload);
      setSaveStatus(`后端保存失败，已保存在浏览器本地：${err.message}`);
    }
  }

  async function handleSubmitResult() {
    const result = {
      userId,
      levelCode: levelId,
      status: inferStatus(orderQuantity),
      failType: inferStatus(orderQuantity) === "success" ? null : "inventory_risk",
      score: inferScore(orderQuantity),
      decisionPayload: { orderQuantity }
    };

    try {
      await submitResult(result);
      setSubmitStatus("结果已提交到后端。正在跳转结算页...");
    } catch (err) {
      setSubmitStatus(`后端提交失败，已在前端生成本地结果：${err.message}`);
    }

    updateProgress({
      currentLevelCode: levelId,
      unlockedLevels: Array.from(new Set([...unlockedLevels, levelId])),
      readItems,
      decisionDraft: { orderQuantity },
      latestResult: result
    });

    navigate(`/summary/${levelId}`);
  }

  if (error) {
    return <StatusBanner tone="error">{error}</StatusBanner>;
  }

  return (
    <LevelPage
      level={level}
      userId={userId}
      orderQuantity={orderQuantity}
      setOrderQuantity={setOrderQuantity}
      unlockedIds={unlockedIds}
      readItems={readItems}
      onReadDataSource={markRead}
      onSaveDraft={handleSaveDraft}
      onSubmitResult={handleSubmitResult}
      saveStatus={saveStatus}
      submitStatus={submitStatus}
    />
  );
}

function SummaryRoute({ ensureLevel, progress, certificate, loadCertificate, resetProgress }) {
  const { levelId } = useParams();
  const [level, setLevel] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    ensureLevel(levelId).then(setLevel).catch((err) => setError(err.message));
    loadCertificate();
  }, [ensureLevel, levelId, loadCertificate]);

  if (error) {
    return <StatusBanner tone="error">{error}</StatusBanner>;
  }

  return (
    <SummaryPage
      level={level}
      result={progress.latestResult}
      certificate={certificate}
      onReset={resetProgress}
    />
  );
}

export default function App() {
  const game = useGameData();

  return (
    <div className="app-root">
      {game.globalError ? <StatusBanner tone="error">{game.globalError}</StatusBanner> : null}
      <Routes>
        <Route
          path="/"
          element={<HomePage levels={game.levels} loading={game.levelsLoading} error={game.globalError} />}
        />
        <Route path="/story/:levelId" element={<StoryRoute ensureLevel={game.ensureLevel} />} />
        <Route
          path="/level/:levelId"
          element={
            <LevelRoute
              ensureLevel={game.ensureLevel}
              progress={game.progress}
              updateProgress={game.updateProgress}
              userId={game.userId}
            />
          }
        />
        <Route
          path="/summary/:levelId"
          element={
            <SummaryRoute
              ensureLevel={game.ensureLevel}
              progress={game.progress}
              certificate={game.certificate}
              loadCertificate={game.loadCertificate}
              resetProgress={game.resetProgress}
            />
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}
