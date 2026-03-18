import { pool } from "../config/db.js";

export async function saveProgress(payload) {
  const {
    userId,
    currentLevelCode,
    unlockedLevels = [],
    readItems = [],
    decisionDraft = {}
  } = payload;

  if (!userId || !currentLevelCode) {
    const error = new Error("userId and currentLevelCode are required");
    error.statusCode = 400;
    throw error;
  }

  await pool.execute(
    `
    INSERT INTO user_progress
      (user_id, current_level_code, unlocked_levels_json, read_items_json, decision_draft_json)
    VALUES (?, ?, ?, ?, ?)
    ON DUPLICATE KEY UPDATE
      current_level_code = VALUES(current_level_code),
      unlocked_levels_json = VALUES(unlocked_levels_json),
      read_items_json = VALUES(read_items_json),
      decision_draft_json = VALUES(decision_draft_json)
    `,
    [
      userId,
      currentLevelCode,
      JSON.stringify(unlockedLevels),
      JSON.stringify(readItems),
      JSON.stringify(decisionDraft)
    ]
  );

  return { success: true };
}

export async function getProgress(userId) {
  const [rows] = await pool.execute(
    `
    SELECT user_id, current_level_code, unlocked_levels_json, read_items_json, decision_draft_json, updated_at
    FROM user_progress
    WHERE user_id = ?
    LIMIT 1
    `,
    [userId]
  );

  if (rows.length === 0) {
    return null;
  }

  const row = rows[0];

  return {
    userId: row.user_id,
    currentLevelCode: row.current_level_code,
    unlockedLevels: JSON.parse(row.unlocked_levels_json || "[]"),
    readItems: JSON.parse(row.read_items_json || "[]"),
    decisionDraft: JSON.parse(row.decision_draft_json || "{}"),
    updatedAt: row.updated_at
  };
}
