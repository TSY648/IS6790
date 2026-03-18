import { pool } from "../config/db.js";

export async function getCertificateByUserId(userId) {
  if (!userId) {
    const error = new Error("userId is required");
    error.statusCode = 400;
    throw error;
  }

  const [rows] = await pool.execute(
    `
    SELECT user_id, certificate_no, total_score, issued_at
    FROM certificate_records
    WHERE user_id = ?
    ORDER BY issued_at DESC, id DESC
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
    certificateNo: row.certificate_no,
    totalScore: row.total_score,
    issuedAt: row.issued_at
  };
}
