import { pool } from "../config/db.js";

export async function saveLevelResult(payload) {
  const {
    userId,
    levelCode,
    status,
    failType = null,
    score = null,
    decisionPayload = {}
  } = payload;

  if (!userId || !levelCode || !status) {
    const error = new Error("userId, levelCode and status are required");
    error.statusCode = 400;
    throw error;
  }

  await pool.execute(
    `
    INSERT INTO level_results
      (user_id, level_code, status, fail_type, score, decision_payload_json)
    VALUES (?, ?, ?, ?, ?, ?)
    `,
    [
      userId,
      levelCode,
      status,
      failType,
      score,
      JSON.stringify(decisionPayload)
    ]
  );

  return { success: true };
}
